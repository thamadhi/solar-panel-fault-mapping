# src/preprocessing/electrical_localisation_preprocessor.py

import pickle
import numpy as np
import pandas as pd
from typing import Optional, Tuple, Dict, Any
from src.core.logger import LoggerFactory


class ElectricalLocalisationPreprocessor:
    """
    Preprocesses 32-string inverter data for the CNN-BiLSTM fault
    localizer models.

    Responsibilities:
        - Scale voltage, current, and meta features using the fitted
          MinMaxScalers from training
        - Reshape to (N, 32, 2) expected by the model
        - Return separate arrays for the string branch and meta branch

    Args:
        scaler_string_path : Path to scaler_string.pkl
        scaler_meta_path   : Path to scaler_meta.pkl
    """

    N_STRINGS = 32
    V_COLS = [f"Vstr{i}(V)" for i in range(1, 33)]
    I_COLS = [f"Istr{i}(A)" for i in range(1, 33)]
    META_COLS = [
        "Ppv(W)",
        "INVTemp(℃)",
        "AMTemp1(℃)",
        "BTTemp(℃)",
        "OUTTemp(℃)",
        "AMTemp2(℃)",
    ]
    ALL_FEATURE_COLS = V_COLS + I_COLS + META_COLS

    def __init__(self, scaler_string_path: str, scaler_meta_path: str) -> None:
        self.__logger = LoggerFactory.get_logger(self.__class__.__name__)
        self.__scaler_string = self.__load_pickle(scaler_string_path)
        self.__scaler_meta = self.__load_pickle(scaler_meta_path)

    def __load_pickle(self, path: str):
        try:
            with open(path, "rb") as f:
                obj = pickle.load(f)
            self.__logger.info(f"Loaded: {path}")
            return obj
        except Exception as e:
            self.__logger.error(f"Failed to load {path}: {e}")
            return None

    @property
    def ready(self) -> bool:
        """True if both scalers loaded successfully."""
        return self.__scaler_string is not None and self.__scaler_meta is not None

    def preprocess(self, data: Any) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Preprocesses raw inverter data into model-ready arrays.

        Args:
            data: pd.DataFrame, list of dicts, or np.ndarray.
                  Must contain all 70 feature columns.

        Returns:
            Tuple (X_3d, X_meta) where:
                X_3d   : float32 array (N, 32, 2) — string branch input
                X_meta : float32 array (N, 6)     — meta branch input
            Returns None if preprocessing fails.
        """
        if not self.ready:
            self.__logger.error("Scalers not loaded — cannot preprocess.")
            return None

        try:
            df = self.__to_dataframe(data)
            if df is None:
                return None

            missing = [c for c in self.ALL_FEATURE_COLS if c not in df.columns]
            if missing:
                self.__logger.error(
                    f"Missing {len(missing)} required columns: " f"{missing[:5]}..."
                )
                return None

            X_raw = (
                df[self.ALL_FEATURE_COLS]
                .apply(pd.to_numeric, errors="coerce")
                .fillna(0)
                .values.astype(np.float32)
            )

            X_str = self.__scaler_string.transform(X_raw[:, :64])
            X_meta = self.__scaler_meta.transform(X_raw[:, 64:])

            X_3d = np.zeros((len(X_str), self.N_STRINGS, 2), dtype=np.float32)
            for s in range(self.N_STRINGS):
                X_3d[:, s, 0] = X_str[:, s]
                X_3d[:, s, 1] = X_str[:, s + self.N_STRINGS]

            self.__logger.info(
                f"Preprocessed {len(df)} rows. "
                f"X_3d: {X_3d.shape}, X_meta: {X_meta.shape}"
            )
            return X_3d, X_meta

        except Exception as e:
            self.__logger.error(f"Preprocessing error: {e}")
            return None

    def __to_dataframe(self, data: Any) -> Optional[pd.DataFrame]:
        if isinstance(data, pd.DataFrame):
            return data.copy()
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, np.ndarray):
            if data.shape[1] == len(self.ALL_FEATURE_COLS):
                return pd.DataFrame(data, columns=self.ALL_FEATURE_COLS)
            self.__logger.error(
                f"Array has {data.shape[1]} columns, "
                f"expected {len(self.ALL_FEATURE_COLS)}."
            )
            return None
        self.__logger.error(f"Unsupported data type: {type(data)}")
        return None
