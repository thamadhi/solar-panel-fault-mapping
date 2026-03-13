from src.preprocessing.preprocessor import Preprocessor
import pandas as pd
from typing import List, Dict


class ElectricalPreprocesor(Preprocessor):

    def __init__(self):
        super().__init__()
        self.__raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]
        self.__feature_order = [
            "vdc1",
            "vdc2",
            "idc1",
            "idc2",
            "irradiance",
            "temperature",
            "power_string1",
            "power_string2",
            "total_power",
            "voltage_ratio",
            "current_ratio",
        ]

    def preprocess(self, data: List[Dict[str, float]]) -> pd.DataFrame:
        """
        Performs feature engineering on raw electrical data
        and converts it into a structured Dataframe ready for predictions.

        Args:
            data (List[Dict[str, float]]):
                List of dictionaries containing raw electrical measurements.
                Each dictionary should include:
                    - vdc1, vdc2
                    - idc1, idc2,
                    - irradiance
                    - temperature

        Returns:
            pd.DataFrame: Processed DataFrame with engineered features in
            the correct order expected by the electrical Random Forest model.
        """
        data = self._perform_feature_engineering(data)
        return data

    def _perform_feature_engineering(
        self, data: List[Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Extracts features from electrical data for the random forest.

        Args:
            data (List[Dict]): The data containing the features.

        Returns:
            pd.DataFrame: Dataframe containing all the features.
        """

        # Get raw features
        rows = []

        for row in data:
            rows.append(
                {
                    "vdc1": float(row.get("vdc1", 0.0)),
                    "vdc2": float(row.get("vdc2", 0.0)),
                    "idc1": float(row.get("idc1", 0.0)),
                    "idc2": float(row.get("idc2", 0.0)),
                    "irradiance": float(row.get("irradiance", 0.0)),
                    "temperature": float(row.get("temperature", 25.0)),
                }
            )

        X = pd.DataFrame(rows, columns=self.__raw_cols)

        # Create engineered features
        X["power_string1"] = X["vdc1"] * X["idc1"]
        X["power_string2"] = X["vdc2"] * X["idc2"]
        X["total_power"] = X["power_string1"] + X["power_string2"]

        # Safe divide
        X["voltage_ratio"] = X["vdc1"] / (X["vdc2"] + 1e-9)
        X["current_ratio"] = X["idc1"] / (X["idc2"] + 1e-9)

        # Ensure correct feature order
        X = X[self.__feature_order]
        return X
