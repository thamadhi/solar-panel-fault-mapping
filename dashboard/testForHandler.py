import sys
import os

# --- IDLE PATH FIX ---
# Adds the project root to sys.path so 'dashboard' can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from dashboard.handlers.fault_Severity_handler import FaultSeverityHandler

def test_severity_pipeline():
    # 1. Initialize Handler (using your specific paths)
    #handler = FaultSeverityHandler(
       # electrical_model_path="dashboard/models/solar_rf_severity_v1.pkl",
       # image_model_path="dashboard/models/tuned_model.keras"
    #)

    # 2. Mock Data (matching your 9-feature requirement)
    mock_raw_data = [{
        "vdc1": 150.0, "vdc2": 310.0, 
        "idc1": 2.1,   "idc2": 8.5,
        "irr": 980,  # Is it 'irr' or 'irradiance'?
        "pvt": 45,   # Is it 'pvt' or 'temperature'?
        "f_nv":3
    }]

    print("--- Starting SolarGuard AI Pipeline Test ---")

    # 3. Pre-process (Uses the snake_case name 'pre_process_data')
    #handler.pre_process_data(string_data=mock_raw_data)
    
    # 4. Apply Model
    #handler.apply_model()

    # 5. Present Results
    #handler.present_results()
    handler=FaultSeverityHandler()
    res=handler.start_flow(mock_raw_data)

    # 6. Final Output
    #res = handler.result
    if res:
        print(f"\n[PIPELINE SUCCESS]")
        print(f"Final Assessment: {res.result}")
        print(f"Confidence:       {res.reading_confidence:.2f}%")
    else:
        print("\n[PIPELINE FAILED] No result generated.")

if __name__ == "__main__":
    test_severity_pipeline()
