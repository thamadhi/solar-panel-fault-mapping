from dashboard.preprocessing.preprocessor import Preprocessor
import pandas as pd
import numpy as np
from typing import List, Dict

class ElectricalPreprocesor(Preprocessor):

    def __init__(self):
        super().__init__()
        # These are the raw columns we expect from the source
        self.__raw_cols = ["vdc1", "vdc2", "idc1", "idc2", 'irr', 'pvt', 'f_nv']
        
        # The final order must match exactly what the model was trained on
        self.__feature_order = ['vdc1', 'vdc2', 'idc1', 'idc2', 'irr', 'pvt', 'p_meas', 'p_theo', 'delta_str']

    def preprocess(self, data: List[Dict]) -> pd.DataFrame:
        """Main entry point for preprocessing."""
        df = pd.DataFrame(data)
        
        # Ensure all required raw columns exist
        for col in self.__raw_cols:
            if col not in df.columns:
                df[col] = 0.0
        
        # Filter out unwanted fault types (dropping 2/Shading as per your logic)
        df = df[df['f_nv'].isin([0, 1, 3, 4])].copy()
        
        return self._perform_feature_engineering(df)

    def _perform_feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:

        # 1. Setting up the scalar value (Your single number)
        p_rated_est = 4852.7240168804765

        # 2. CALCULATE FEATURES
        GAMMA = -0.004  # Temp coefficient
        REF_TEMP = 25
        
        # P_meas: Actual measured power
        df['p_meas'] = (df['vdc1'] * df['idc1']) + (df['vdc2'] * df['idc2'])
        
        # P_theo: Theoretical power adjusted for Irradiance and Temperature
        df['p_theo'] = p_rated_est * (df['irr'] / 1000) * (1 + GAMMA * (df['pvt'] - REF_TEMP))

        # delta_str: String Mismatch Component (normalized difference between strings)
        df['delta_str'] = np.abs((df['vdc1'] * df['idc1']) - (df['vdc2'] * df['idc2'])) / (df['p_meas'] + 1e-6)

        # 3. FINAL OUTPUT
        # Return only the features required by the model in the correct order
        return df[self.__feature_order].astype(float)
