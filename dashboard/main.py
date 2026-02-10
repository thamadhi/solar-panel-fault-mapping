import pandas as pd
import os
from handlers.fault_detection_handler import FaultDetectionHandler

# Set model and scaler paths
MODEL_PATH = "models/best_neural_network.keras"
SCALER_PATH = "models/ann_scaler.pkl"

handler = FaultDetectionHandler(
    electrical_model_path=MODEL_PATH,
    scaler_path=SCALER_PATH
)

def detect_from_csv(csv_file):
    """
    CSV fault detection
    
    Args:
        csv_file: The file being read
    """
    global handler
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        return

    df = pd.read_csv(csv_file)
    required_cols = ['vdc1', 'vdc2', 'idc1', 'idc2', 'irradiance', 'temperature']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        print(f"Missing columns in CSV: {missing_cols}")
        return

    data = df[required_cols].to_dict('records')
    result = handler.start_flow(string_data=data)
    if result:
        print(f"Overall Fault Type: {result.result}")
        print(f"Confidence: {result.reading_confidence:.1%}")

        print("\nDetailed Predictions per string:")
        for d in result.result_readings:
            print(f"String {d['string_id']}: {d['fault_type']} ({d['confidence']:.1%})")


def detect_manual():
    """
    Manual fault detection for a single record
    """
    print("Enter manual values for electrical strings:")

    vdc1 = float(input("vdc1 (Voltage String 1): "))
    vdc2 = float(input("vdc2 (Voltage String 2): "))
    idc1 = float(input("idc1 (Current String 1): "))
    idc2 = float(input("idc2 (Current String 2): "))
    irradiance = float(input("Irradiance (W/m²): "))
    temperature = float(input("Temperature (°C): "))

    test_data = [{
        'vdc1': vdc1,
        'vdc2': vdc2,
        'idc1': idc1,
        'idc2': idc2,
        'irradiance': irradiance,
        'temperature': temperature
    }]

    final_report = handler.start_flow(string_data=test_data)
    if final_report:
        print(f"Main Result: {final_report.result}")
        print(f"Confidence: {final_report.reading_confidence:.2%}")
        
        # Loop through individual string predictions if they exist
        for reading in final_report.result_readings:
            print(f"String {reading['string_id']}: {reading['fault_type']} ({reading['confidence']:.1%})")


def main():
    print("Electrical Fault Detection Tester (Terminal)")
    print("Options:")
    print("1. Detect faults from CSV")
    print("2. Enter manual values")
    print("3. Enter an image")
    choice = input("Choose option (1/2): ")

    if choice == "1":
        csv_file = input("Enter CSV file path: ")
        detect_from_csv(csv_file)
    elif choice == "2":
        detect_manual()
    elif choice == "3":
        path = input("Enter image path: ")
        if not os.path.exists(path):
            print(f"Image not found at: {path}")

        else:
            result = handler.start_flow(image_data=path, string_data=None)
            if result:
                print(f"Overall fault type: {result.result}")
                print(f"Confidence: {result.reading_confidence:.1f}")

                if result.result_readings:
                    print("Detailed predictions:")
                    for idx, d in enumerate(result.result_readings, start=1):
                        print(f"Region {idx}: {d['fault_type']} ({d['confidence']:.1%})")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
