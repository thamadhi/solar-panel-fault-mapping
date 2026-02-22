from ultralytics import YOLO
import os

def main():
    # 1. Load the model (YOLO26 is native NMS-free and edge-optimized)
    model = YOLO("yolo26n.pt")

    # 2. Train the model
    # We use imgsz=512 for better hotspot detail (vs 416)
    # batch=2 to compensate for the higher resolution on 2GB VRAM
    results = model.train(
        data="myfile.yaml",
        epochs=100,
        imgsz=512,
        batch=2,
        device=0,
        workers=2,
        amp=True,
        # YOLO26 specific: STAL & ProgLoss are active by default
        # We can increase the 'box' gain to help precise hotspot localization
        box=10.0,
        cls=1.5
    )

    # 3. Validation
    metrics = model.val()
    print(f"mAP50-95: {metrics.box.map}")

    # 4. Run Prediction (Test it on a new thermal image)
    # Replace 'path/to/thermal_image.jpg' with an actual file path
    test_image = "thermal_test.jpg"
    if os.path.exists(test_image):
        predict_results = model.predict(source=test_image, save=True, imgsz=512, conf=0.25)
        print(f"Results saved to: {predict_results[0].save_dir}")

if __name__ == '__main__':
    main()

# Perform object detection on an image
#results = model("C:\\Users\\Extra\\Desktop\2nd-Year-DGSP-Github\Dataset\Yolo\HotspotDataset")
#results[0].show()  # Display results

# Export the model to ONNX format for deployment
#path = model.export(format="onnx")  # Returns the path to the exported model