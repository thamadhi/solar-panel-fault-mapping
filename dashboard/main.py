import pandas as pd
import os
from handlers.electrical_ann_strategy import ElectricalANN

# Set model and scaler paths
MODEL_PATH = "best_ANN_2.20.keras"
SCALER_PATH = "ann_scaler.pkl"

# Initialize the ANN model
ann_model = ElectricalANN(MODEL_PATH, SCALER_PATH)

def detect_from_csv(csv_file):
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
    result = ann_model.detect(data)
    print(f"Overall Fault Type: {result['fault_type']}")
    print(f"Confidence: {result['confidence']:.1%}")

    print("\nDetailed Predictions per string:")
    for d in result.get('detailed_predictions', []):
        print(f"String {d['string_id']}: {d['fault_type']} ({d['confidence']:.1%})")


def detect_manual():
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

    result = ann_model.detect(test_data)
    print(f"Fault Type: {result['fault_type']}")
    print(f"Confidence: {result['confidence']:.1%}")


def main():
    print("Electrical Fault Detection Tester (Terminal)")
    print("Options:")
    print("1. Detect faults from CSV")
    print("2. Enter manual values")
    choice = input("Choose option (1/2): ")

    if choice == "1":
        csv_file = input("Enter CSV file path: ")
        detect_from_csv(csv_file)
    elif choice == "2":
        detect_manual()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
