import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from dataclasses import dataclass
from typing import Optional, Tuple, Union
from src.core.logger import LoggerFactory


@dataclass
class LocalizationResult:
    """
    Holds the complete output of hotspot localization for one image.

    Attributes:
        is_hotspot      : True if model predicted a hotspot
        confidence      : Probability score from sigmoid output (0-1)
        bounding_box    : (x, y, w, h) in pixels, or None if not detected
        heatmap         : 2D float32 array (224x224), values in [0, 1]
        overlay_image   : BGR uint8 array with heatmap blended on image
        annotated_image : BGR uint8 array with bounding box drawn
        string_reliable : Always True for image model
        error           : Non-empty string if something failed
    """

    is_hotspot: bool = False
    confidence: float = 0.0
    bounding_box: Optional[Tuple[int, int, int, int]] = None
    heatmap: Optional[np.ndarray] = None
    overlay_image: Optional[np.ndarray] = None
    annotated_image: Optional[np.ndarray] = None
    string_reliable: bool = True
    error: str = ""


class ImagePreprocessor:
    """
    Preprocesses thermal images for the DenseNet121 hotspot classifier.

    Steps:
        1. Load image from disk (BGR via OpenCV)
        2. Convert BGR to grayscale
        3. Apply Gaussian blur for noise reduction
        4. Resize to (224, 224)
        5. Normalize pixel values to [0, 1]
        6. Stack to 3 channels so DenseNet121 receives expected shape
        7. Add batch dimension -> shape (1, 224, 224, 3)

    These steps must exactly match what was done inside ImageDataGenerator
    during training. The .keras file does not include preprocessing so the
    same steps must always be applied before model.predict().
    """

    def __init__(self) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__IMAGE_SIZE = (224, 224)

    def preprocess(self, data: str) -> Optional[np.ndarray]:
        """
        Preprocess a thermal image for hotspot classification.

        Args:
            data: File path to the input image.

        Returns:
            Float32 array of shape (1, 224, 224, 3), or None on failure.
        """
        img = cv2.imread(data)
        if img is None:
            self.__logger.error(f"Failed to load image: {data}")
            return None

        if len(img.shape) == 3:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img_gray = img

        img_blurred = cv2.GaussianBlur(img_gray, (3, 3), 0)
        img_resized = cv2.resize(img_blurred, self.__IMAGE_SIZE)
        img_normalized = img_resized.astype(np.float32) / 255.0
        img_3ch = np.stack([img_normalized] * 3, axis=-1)
        img_batch = np.expand_dims(img_3ch, axis=0)

        return img_batch


class ScoreCAM:
    """
    Generates a spatial activation heatmap using Score-CAM.

    This version avoids building any sub-model entirely.
    Instead it calls the densenet121 layer directly as a callable
    to get intermediate feature maps, which works regardless of
    how the model was saved or what Keras version is being used.

    Args:
        model     : Trained Keras DenseNet121 hotspot classifier
        batch_size: Channel masks processed per forward pass.
                    Reduce to 4 if GPU memory errors occur.
    """

    def __init__(self, model: keras.Model, batch_size: int = 8) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__model = model
        self.__batch_size = batch_size
        self.__IMAGE_SIZE = (224, 224)
        self.__densenet = None
        self.__last_conv = None
        self.__setup_layers()

    def __setup_layers(self) -> None:
        """
        Store references to the densenet base and last conv layer.
        No Model building — just layer references.
        """
        try:
            self.__densenet = self.__model.get_layer("densenet121")
            self.__last_conv = self.__densenet.get_layer("conv5_block16_2_conv")
            self.__logger.info(
                "ScoreCAM layer references stored. " "No sub-model built."
            )
        except Exception as e:
            self.__logger.error(f"Could not find required layers: {e}")
            self.__densenet = None
            self.__last_conv = None

    def __get_feature_map(self, img_array: np.ndarray) -> np.ndarray:
        """
        Get the last conv layer feature map by intercepting the
        densenet forward pass using a GradientTape to watch
        the intermediate output.

        This avoids building a new Model entirely.
        """
        if self.__densenet is None or self.__last_conv is None:
            self.__logger.error("Layer references not available.")
            return np.zeros((7, 7, 1), dtype=np.float32)

        img_tensor = tf.constant(img_array, dtype=tf.float32)

        # Use a tape to capture the conv layer output during forward pass
        captured = {}

        # Register a hook by temporarily wrapping the call
        original_call = self.__last_conv.call

        def hooked_call(inputs, **kwargs):
            output = original_call(inputs, **kwargs)
            captured["feature_map"] = output
            return output

        self.__last_conv.call = hooked_call

        try:
            # Run the densenet forward pass — the hook captures conv output
            self.__densenet(img_tensor, training=False)
        except Exception as e:
            self.__logger.warning(f"Hook forward pass error: {e}")
        finally:
            # Always restore original call
            self.__last_conv.call = original_call

        if "feature_map" in captured:
            return captured["feature_map"].numpy()[0]

        # Fallback: use densenet full output (before GAP) as feature proxy
        self.__logger.warning(
            "Hook did not capture feature map. " "Using densenet output as fallback."
        )
        try:
            out = self.__densenet(img_tensor, training=False)
            return out.numpy()[0]
        except Exception as e2:
            self.__logger.error(f"Fallback also failed: {e2}")
            return np.zeros((7, 7, 1), dtype=np.float32)

    def generate(self, img_array: np.ndarray) -> np.ndarray:
        """
        Generate Score-CAM heatmap for the given preprocessed image.

        Args:
            img_array: Shape (1, 224, 224, 3), float32, values in [0, 1].

        Returns:
            2D float32 heatmap (224, 224), contrast-stretched to [0, 1].
        """
        feature_map = self.__get_feature_map(img_array)
        n_channels = feature_map.shape[-1]

        self.__logger.info(
            f"Feature map shape: {feature_map.shape}, " f"channels: {n_channels}"
        )

        # Build normalized channel masks
        masks = np.zeros((n_channels, *self.__IMAGE_SIZE), dtype=np.float32)
        for c in range(n_channels):
            ch = feature_map[:, :, c]
            ch_res = cv2.resize(ch, self.__IMAGE_SIZE)
            lo, hi = ch_res.min(), ch_res.max()
            if hi > lo:
                masks[c] = (ch_res - lo) / (hi - lo)

        # Score each mask by running through the full model
        base_img = img_array[0]
        scores = []
        for start in range(0, n_channels, self.__batch_size):
            end = min(start + self.__batch_size, n_channels)
            batch = [base_img * masks[c][:, :, np.newaxis] for c in range(start, end)]
            preds = self.__model.predict(np.array(batch, dtype=np.float32), verbose=0)
            scores.extend(preds[:, 0].tolist())

        scores = np.array(scores, dtype=np.float32)
        scores_exp = np.exp(scores - scores.max())
        weights = scores_exp / (scores_exp.sum() + 1e-8)

        heatmap = np.zeros(self.__IMAGE_SIZE, dtype=np.float32)
        for c in range(n_channels):
            heatmap += weights[c] * masks[c]

        heatmap = np.maximum(heatmap, 0)
        lo, hi = heatmap.min(), heatmap.max()
        if hi > lo:
            heatmap = (heatmap - lo) / (hi - lo)
        else:
            heatmap = np.zeros_like(heatmap)

        return heatmap


def _init_hotspot_localizer_corrected(self, model_path: str) -> None:
    """
    Load the Keras model and initialize HotspotLocalizer and ImagePreprocessor.
    Uses compile=False to avoid graph reconstruction errors on load.
    """
    try:
        from src.preprocessing.image_localization_preprocessing import (
            HotspotLocalizer,
            ImagePreprocessor,
        )

        model = tf.keras.models.load_model(model_path, compile=False)
        self.__logger.info(f"Image model loaded from: {model_path}")
        self.__logger.info(f"Input shape : {model.input_shape}")
        self.__logger.info(f"Output shape: {model.output_shape}")

        layer_names = [l.name for l in model.layers]
        self.__logger.info(f"Top-level layers: {layer_names}")

        if "densenet121" in layer_names:
            densenet = model.get_layer("densenet121")
            self.__logger.info(f"DenseNet input : {densenet.input_shape}")
            self.__logger.info(f"DenseNet output: {densenet.output_shape}")

        self.__hotspot_localizer = HotspotLocalizer(
            model=model,
            hotspot_threshold=0.5,
            heatmap_threshold=0.4,
            scorecam_batch=8,
            overlay_alpha=0.5,
        )
        self.__image_preprocessor = ImagePreprocessor()
        self.__logger.info("HotspotLocalizer initialized successfully.")

    except Exception as e:
        self.__logger.error(f"Failed to initialize HotspotLocalizer: {e}")
        self.__hotspot_localizer = None
        self.__image_preprocessor = None


class BoundingBoxExtractor:
    """
    Extracts a bounding box from a Score-CAM heatmap by thresholding
    and finding the largest activated contour.

    Args:
        threshold        : Activation threshold for bounding box.
                           Lower = larger box, higher = tighter box.
        morph_kernel_size: Morphological closing kernel size used to merge
                           nearby activated regions before contouring.
    """

    def __init__(self, threshold: float = 0.4, morph_kernel_size: int = 20) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__threshold = threshold
        self.__morph_kernel_size = morph_kernel_size

    def extract(self, heatmap: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Extract bounding box from heatmap.

        Args:
            heatmap: 2D float32 array, values in [0, 1].

        Returns:
            (x, y, w, h) in pixel coordinates, or None if nothing found.
        """
        binary = (heatmap >= self.__threshold).astype(np.uint8)
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (self.__morph_kernel_size, self.__morph_kernel_size)
        )
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            self.__logger.warning(
                f"No region found above threshold {self.__threshold}. "
                "Try lowering heatmap_threshold."
            )
            return None

        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        return (x, y, w, h)


class LocalizationRenderer:
    """
    Renders the Score-CAM heatmap and bounding box onto the original image.

    Produces two output images:
        overlay_image   : Original image blended with heatmap colormap.
                          Bright regions show where the model is focusing.
        annotated_image : Original image with red bounding box drawn around
                          the detected hotspot location.

    Args:
        alpha: Heatmap blend strength (0 = no heatmap, 1 = only heatmap).
    """

    def __init__(self, alpha: float = 0.5) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__alpha = alpha

    def render_overlay(
        self, original_bgr: np.ndarray, heatmap: np.ndarray
    ) -> np.ndarray:
        """
        Blend Score-CAM heatmap onto the original image.

        Args:
            original_bgr: BGR uint8 image (H, W, 3).
            heatmap     : 2D float32 heatmap matching image dimensions.

        Returns:
            BGR uint8 blended image.
        """
        heatmap_color = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_HOT)

        base = (
            (original_bgr * 255).astype(np.uint8)
            if original_bgr.dtype != np.uint8
            else original_bgr.copy()
        )

        mask = heatmap > 0.15
        result = base.copy()
        blended = cv2.addWeighted(
            base, 1 - self.__alpha, heatmap_color, self.__alpha, 0
        )
        result[mask] = blended[mask]
        return result

    def render_bbox(
        self,
        original_bgr: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]],
        is_hotspot: bool,
    ) -> np.ndarray:
        """
        Draw bounding box on original image if hotspot was detected.

        Args:
            original_bgr: BGR uint8 image.
            bbox        : (x, y, w, h) or None.
            is_hotspot  : Returns unmodified image if False.

        Returns:
            BGR uint8 annotated image.
        """
        annotated = (
            (original_bgr * 255).astype(np.uint8)
            if original_bgr.dtype != np.uint8
            else original_bgr.copy()
        )

        if not is_hotspot or bbox is None:
            return annotated

        x, y, w, h = bbox

        overlay = annotated.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 255), -1)
        annotated = cv2.addWeighted(annotated, 0.80, overlay, 0.20, 0)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 3)

        label = f"Hotspot ({w}x{h}px)"
        label_y = max(y - 8, 14)
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(
            annotated, (x, label_y - lh - 4), (x + lw, label_y + 2), (255, 255, 255), -1
        )
        cv2.putText(
            annotated,
            label,
            (x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
        return annotated


class HotspotLocalizer:
    """
    End-to-end hotspot localization for thermal solar panel images.

    Combines ImagePreprocessor, ScoreCAM, BoundingBoxExtractor and
    LocalizationRenderer into a single call.

    Args:
        model             : Loaded Keras DenseNet121 hotspot classifier
        hotspot_threshold : Sigmoid threshold to classify as hotspot (0.5)
        heatmap_threshold : Activation threshold for bounding box (0.4)
        scorecam_batch    : Channels per ScoreCAM forward pass (reduce if OOM)
        overlay_alpha     : Heatmap blend strength over original image

    Usage:
        localizer = HotspotLocalizer(model)

        # Option A — pass a raw file path
        result = localizer.localize("/path/to/image.jpg")

        # Option B — pass an already-preprocessed (1, 224, 224, 3) array
        #            and optionally the original path for better rendering
        result = localizer.localize(
            preprocessed_array,
            original_image_path="/path/to/image.jpg"
        )
    """

    def __init__(
        self,
        model: keras.Model,
        hotspot_threshold: float = 0.5,
        heatmap_threshold: float = 0.4,
        scorecam_batch: int = 8,
        overlay_alpha: float = 0.5,
    ) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__model = model
        self.__hs_threshold = hotspot_threshold
        self.__preprocessor = ImagePreprocessor()
        self.__scorecam = ScoreCAM(model, batch_size=scorecam_batch)
        self.__bbox_extractor = BoundingBoxExtractor(threshold=heatmap_threshold)
        self.__renderer = LocalizationRenderer(alpha=overlay_alpha)

    def localize(
        self,
        image_input: Union[str, np.ndarray],
        original_image_path: Optional[str] = None,
    ) -> LocalizationResult:
        """
        Run the full localization pipeline on a thermal image.

        Args:
            image_input: Either —
                str       : Raw image file path. Preprocessing runs internally.
                np.ndarray: Already-preprocessed (1, 224, 224, 3) array.
                            Preprocessing is SKIPPED to avoid running twice.
            original_image_path: Path to the raw image used only for
                                  rendering overlay and bounding box.
                                  Required when image_input is np.ndarray.
                                  Ignored when image_input is str.

        Returns:
            LocalizationResult with all outputs populated, or with
            result.error set if something went wrong.
        """
        result = LocalizationResult()

        # Step 1: resolve preprocessed array and original BGR image
        if isinstance(image_input, str):
            img_array = self.__preprocessor.preprocess(image_input)
            if img_array is None:
                result.error = f"Could not load image: {image_input}"
                self.__logger.error(result.error)
                return result

            original_bgr = cv2.imread(image_input)
            if original_bgr is None:
                result.error = f"Could not reload for rendering: {image_input}"
                self.__logger.error(result.error)
                return result
            original_bgr = cv2.resize(original_bgr, (224, 224))

        elif isinstance(image_input, np.ndarray):
            if image_input.ndim != 4 or image_input.shape[1:] != (224, 224, 3):
                result.error = (
                    f"Expected array shape (1, 224, 224, 3), "
                    f"got {image_input.shape}"
                )
                self.__logger.error(result.error)
                return result

            img_array = image_input

            if original_image_path is not None:
                original_bgr = cv2.imread(original_image_path)
                if original_bgr is not None:
                    original_bgr = cv2.resize(original_bgr, (224, 224))
                else:
                    self.__logger.warning(
                        "Could not load original_image_path for rendering. "
                        "Reconstructing from preprocessed array."
                    )
                    original_bgr = (img_array[0] * 255).astype(np.uint8)
                    original_bgr = cv2.cvtColor(original_bgr, cv2.COLOR_RGB2BGR)
            else:
                self.__logger.warning(
                    "No original_image_path provided. "
                    "Reconstructing BGR from preprocessed array."
                )
                original_bgr = (img_array[0] * 255).astype(np.uint8)
                original_bgr = cv2.cvtColor(original_bgr, cv2.COLOR_RGB2BGR)

        else:
            result.error = (
                f"Unsupported image_input type: {type(image_input)}. "
                "Pass a file path (str) or preprocessed array (np.ndarray)."
            )
            self.__logger.error(result.error)
            return result

        # Step 2: classify
        try:
            pred_score = float(self.__model.predict(img_array, verbose=0)[0][0])
            result.confidence = round(pred_score, 4)
            result.is_hotspot = pred_score >= self.__hs_threshold
        except Exception as e:
            result.error = f"Model prediction failed: {e}"
            self.__logger.error(result.error)
            return result

        self.__logger.info(
            f"Hotspot: {result.is_hotspot} | " f"Confidence: {result.confidence:.4f}"
        )

        # Step 3: Score-CAM heatmap
        try:
            result.heatmap = self.__scorecam.generate(img_array)
        except Exception as e:
            result.error = f"Score-CAM failed: {e}"
            self.__logger.error(result.error)
            return result

        # Step 4: bounding box (only when hotspot detected)
        if result.is_hotspot:
            result.bounding_box = self.__bbox_extractor.extract(result.heatmap)
            if result.bounding_box is None:
                self.__logger.warning(
                    "Hotspot detected but bounding box not found. "
                    "Try lowering heatmap_threshold."
                )

        # Step 5: render overlay and annotated image
        result.overlay_image = self.__renderer.render_overlay(
            original_bgr, result.heatmap
        )
        result.annotated_image = self.__renderer.render_bbox(
            original_bgr, result.bounding_box, result.is_hotspot
        )

        return result
