from typing import Dict, Any, List
from typing_extensions import override
from base_strategy import FaultDetectionStrategy


class ElectricalStrategy(FaultDetectionStrategy):
    """
    Detects electrical faults from string measurements
    """

    def __init__(self) -> None:
        # Threshold values for faulty strings
        self.__thresholds = {
            'open_circuit_current': 0.1,    # < 0.1A implies open circuit
            'short_circuit_current': 12.0,  # > 12.0A implies short circuit
            'minimum_voltage': 5.0,        # Minimum expected voltage
            'shadowing_current_ratio': 0.5  # current < 50% of expected
        }
        # reference values for a healthy string
        self.__reference = {
            'nominal_current': 8.0,
            'nominal_voltage': 40.0,
            'nominal_power': 320.0
        }
    

    @override
    def detect(self, string_data: List[dict]) -> Dict[str, Any]:
        """
        Detects electrical faults from string measurements
        
        Args:
            string_data: List of measurements with keys:
                - 'current_A' (float): Current in amps
                - 'voltage_A' (float): Voltage in volts
                - 'Irradiance_Wm2' (float): Solar irradiance
                - 'temperature_C' (float): Panel temperature

        Returns:
            Dictionary with 'fault_type', 'confidence' and 'evidence' 
        """

        if not string_data:
            return {'fault_type': 'Normal Operation', 'confidence': 0.0, 
                    'evidence': 'No data'}
        
        # Analyze each string
        faults = []
        for i, measurement in enumerate(string_data):
            current = measurement.get("current_A", 0)
            voltage = measurement.get("voltage_V", 0)
            irradiance = measurement.get("Irradiance_Wm2", 0)
            temperature = measurement.get("temperature_C", 25)
            power = voltage * current

            # Calculate expected values
            irradiance_factor = irradiance / 1000.0 if irradiance > 0 else 0
            temperature_factor = 1 - 0.004 * (temperature - 25)
            expected_current = self.__reference['nominal_current'] * irradiance_factor * temperature_factor
            expected_voltage = self.__reference['nominal_voltage'] * temperature_factor
            expected_power = expected_voltage * expected_current

            # Detect faults
            fault_info = {'string_id': i, 'confidence': 0.0}

            # Open circuit detection
            if current < self.__thresholds['open_circuit_current']:
                fault_info['fault_type'] = 'Open Circuit'
                fault_info['confidence'] = min(1.0, 
                                               (self.__thresholds['open_circuit_current']
                                               - current)
                                               / self.__thresholds['open_circuit_current'])
                fault_info['evidence'] = f"Current ({current}A) below open circuit threshold"

            elif current > self.__thresholds['short_circuit_current']:
                fault_info['fault_type'] = 'Short-Circuit'
                fault_info['confidence'] = min(1.0, (current
                                        - self.__thresholds['short_circuit_current'])
                                        / self.__thresholds['short_circuit_current'])
                
            elif (current / expected_current if expected_current > 0 else 0) \
            < self.__thresholds['shadowing_current_ratio']:
                fault_info['fault_type'] = 'Shadowing'
                current_ratio = current / expected_current
                fault_info['confidence'] = 1.0 - current_ratio
                fault_info['evidence'] = f"Current ({current}A) significantly below" \
                f"expected ({expected_current:.1f}A)"
        
            # Normal operation
            else:
                fault_info['fault_type'] = 'Normal Operation'
                # Confidence based on how close to expected values
                current_diff = abs(current - expected_current) / expected_current \
                if expected_current > 0 else 1.0

                voltage_diff = abs(voltage - expected_voltage) / expected_voltage \
                if expected_voltage > 0 else 1.0
                
                fault_info['confidence'] = max(0.0, 1.0 - (current_diff + voltage_diff) / 2)
                fault_info['evidence'] = "Within normal operating range"

            faults.append(fault_info)

        return max(faults, key=lambda x: x['confidence'])

    @property
    def thresholds(self) -> Dict[str, float]:
        """Returns the thresholds for fault detection."""
        return self.__thresholds
    

    @property
    def reference(self) -> Dict[str, float]:
        """Returns the reference nominal values."""
        return self.__reference
