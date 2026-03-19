import pandas as pd
import numpy as np
import shap
import pickle
from src.preprocessing.electrical_Severity_preprocessor import ElectricalPreprocesor

class SeverityExplainer:
    def __init__(self, model_path):
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)
        
        self.model = model_data["xgb_model"]
        self.features = model_data["features"]
        self.preprocessor = ElectricalPreprocesor()

        # Grouping features into your specific technical components
        self.component_mapping = {
            "vdc1": "Power Loss", "vdc2": "Power Loss",
            "irr": "Power Loss", "p_meas": "Power Loss", "p_theo": "Power Loss",
            "idc1": "Power Loss / String Mismatch", 
            "idc2": "Power Loss / String Mismatch",
            "delta_str": "Power Loss / String Mismatch",
            "pvt": "Thermal Stress"
        }

    def get_explanation(self, raw_dict):
        """Calculates rounded SHAP values after running preprocessing."""
        # 1. Feature Engineering
        processed_df = self.preprocessor.preprocess([raw_dict])
        df_aligned = processed_df[self.features]
        
        # 2. SHAP Analysis
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(df_aligned)
        contributions = shap_values[0]

        component_contrib = {}
        feature_impacts = []

        for feature, val in zip(self.features, contributions):
            # Rounding to 3 decimals for internal data, UI will show 2
            rounded_val = round(float(val), 3)
            
            feature_impacts.append({
                "Feature": feature,
                "Impact": rounded_val,
                "Direction": "increased" if val > 0 else "reduced"
            })
            
            comp = self.component_mapping.get(feature, "Auxiliary")
            component_contrib[comp] = component_contrib.get(comp, 0) + val

        # Aggregating component-level results
        comp_summary = [
            {
                "Component": k, 
                "Impact": round(abs(v), 2), 
                "Direction": "increased" if v > 0 else "reduced"
            } 
            for k, v in component_contrib.items()
        ]
        
        # Sort by most influential component
        comp_summary = sorted(comp_summary, key=lambda x: x["Impact"], reverse=True)
            
        return comp_summary, pd.DataFrame(feature_impacts)
