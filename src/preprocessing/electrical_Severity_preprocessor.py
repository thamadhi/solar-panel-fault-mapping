from src.preprocessing.preprocessor import Preprocessor
import pandas as pd
from typing import List, Dict

class ElectricalPreprocesor(Preprocessor):

    def __init__(self):
        super().__init__()
        # These are the raw columns we expect from the source
        self.__raw_cols = ["vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature"]
        
        # The final order must match exactly what the model was trained on
        self.__feature_order = [
            "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
            "power_loss_ratio"
        ]

    def preprocess(self, data: List[Dict]) -> pd.DataFrame:
        """Main entry point for preprocessing."""
        # Convert list of dicts to DataFrame in one shot (more efficient)
        df = pd.DataFrame(data)
        
        # Ensure all required raw columns exist, fill missing with 0 or defaults
        for col in self.__raw_cols:
            if col not in df.columns:
                df[col] = 25.0 if col == "temperature" else 0.0
        
        return self._perform_feature_engineering(df)

    def _perform_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates engineered features using vectorized pandas operations."""
        
        # 1. Power Calculations
        p1 = df["vdc1"] * df["idc1"]
        p2 = df["vdc2"] * df["idc2"]
        total_p = p1 + p2

        # 2. Ratios (with epsilon to avoid DivisionByZero)
        epsilon = 1e-9
        df["voltage_ratio"] = df["vdc1"] / (df["vdc2"] + epsilon)
        df["current_ratio"] = df["idc1"] / (df["idc2"] + epsilon)

        # 3. Power Loss Ratio 
        # (Assuming theoretical max power is linked to irradiance)
        # We normalize total power by irradiance to see performance drops
        df["power_loss_ratio"] = total_p / (df["irradiance"] + epsilon)

        # 4. Final Cleanup
        # Ensure only the features the model expects are returned, in order
        return df[self.__feature_order].astype(float)
