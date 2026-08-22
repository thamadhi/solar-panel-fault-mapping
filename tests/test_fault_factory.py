import pytest
from src.core.fault_factory import FaultFactory
from src.core.fault import Fault, Hotspot, OpenCircuit, Shadowing, ShortCircuit

def test_create_open_circuit():
    """Verify factory returns an OpenCircuit instance for 'Open Circuit'."""
    fault = FaultFactory.create_fault("Open Circuit")
    assert isinstance(fault, OpenCircuit)
    # Testing inherited or specific behavior
    assert fault.get_fault_type() == "Open Circuit"

def test_create_short_circuit():
    """Verify factory returns a ShortCircuit instance for 'Short-Circuit'."""
    fault = FaultFactory.create_fault("Short-Circuit")
    assert isinstance(fault, ShortCircuit)
    assert fault.get_fault_type() == "Short-Circuit"

def test_create_shadowing():
    """Verify factory returns a Shadowing instance for 'Shadowing'."""
    fault = FaultFactory.create_fault("Shadowing")
    assert isinstance(fault, Shadowing)
    assert fault.get_fault_type() == "Shadowing"

def test_create_hotspot():
    """Verify factory returns a Hotspot instance for 'Hotspot'."""
    fault = FaultFactory.create_fault("Hotspot")
    assert isinstance(fault, Hotspot)
    assert fault.get_fault_type() == "Hotspot"

def test_create_normal_operation():
    """Verify 'Normal Operation' returns the base Fault class."""
    fault = FaultFactory.create_fault("Normal Operation")
    # Based on the code, cls is mapping.get("Normal Operation", Fault) -> Fault
    assert type(fault) is Fault
    assert fault.get_fault_type() == "Normal Operation"

def test_create_unknown_fault_defaults_to_base():
    """Verify unknown strings default to a base Fault instance."""
    unknown_name = "Alien Interference"
    fault = FaultFactory.create_fault(unknown_name)

    assert type(fault) is Fault
    assert fault.get_fault_type() == unknown_name

@pytest.mark.parametrize("fault_name, expected_class", [
    ("Open Circuit", OpenCircuit),
    ("Short-Circuit", ShortCircuit),
    ("Shadowing", Shadowing),
    ("Hotspot", Hotspot),
])
def test_fault_subclass_initialization(fault_name, expected_class):
    """Parametrized test to ensure subclasses don't require extra arguments."""
    # This confirms the 'else: return cls()' branch works for all mapped subclasses
    fault = FaultFactory.create_fault(fault_name)
    assert isinstance(fault, expected_class)
