import pytest
from src.core.fault import Fault, Hotspot, ShortCircuit, OpenCircuit, Shadowing

# --- Base Class Tests ---

def test_fault_abstract_instantiation():
    """
    While Fault is an ABC, it does not have abstract methods. 
    We test its basic property behavior via a concrete implementation.
    """
    class ConcreteFault(Fault):
        pass
    
    f = ConcreteFault("Test Fault")
    assert f.get_fault_type == "Test Fault"

# --- Hotspot Tests ---

def test_hotspot_initialization():
    """Tests that Hotspot defaults to 'Hotspot' type and starts with empty data."""
    h = Hotspot()
    assert h.get_fault_type == "Hotspot"
    assert h.get_image_array() == []

def test_hotspot_add_image():
    """Verifies image data accumulation."""
    h = Hotspot()
    fake_img = [0, 255, 128] # Simulating a small pixel array or object
    h.add_image(fake_img)
    
    assert len(h.get_image_array()) == 1
    assert h.get_image_array()[0] == fake_img

# --- Electrical Fault Tests (ShortCircuit, OpenCircuit, Shadowing) ---

@pytest.mark.parametrize("fault_class, default_type", [
    (ShortCircuit, "Short Circuit"),
    (OpenCircuit, "Open Circuit"),
    (Shadowing, "Shadowing"),
])
def test_electrical_fault_types(fault_class, default_type):
    """Verifies that all electrical fault subclasses initialize with correct names."""
    fault_instance = fault_class()
    assert fault_instance.get_fault_type == default_type
    assert fault_instance.get_reading_array() == []

def test_short_circuit_add_reading():
    """Verifies electrical reading storage in ShortCircuit."""
    sc = ShortCircuit()
    reading = "String 1: 0.5A"
    sc.add_reading(reading)
    
    assert sc.get_reading_array() == [reading]

def test_open_circuit_add_reading():
    """Verifies electrical reading storage in OpenCircuit."""
    oc = OpenCircuit()
    reading = "String 2: 0.0A"
    oc.add_reading(reading)
    
    assert oc.get_reading_array() == [reading]

def test_shadowing_add_reading():
    """Verifies electrical reading storage in Shadowing."""
    sh = Shadowing()
    reading = "String 3: Partial Drop"
    sh.add_reading(reading)
    
    assert sh.get_reading_array() == [reading]

# --- Inheritance & Type Checking ---

def test_fault_inheritance_integrity():
    """Ensures all specific faults are recognized as instances of the base Fault class."""
    assert isinstance(Hotspot(), Fault)
    assert isinstance(ShortCircuit(), Fault)
    assert isinstance(OpenCircuit(), Fault)
    assert isinstance(Shadowing(), Fault)
