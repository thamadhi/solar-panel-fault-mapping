import pytest
import pandas as pd

from src.preprocessing.electrical_preprocessor import ElectricalPreprocesor


@pytest.fixture
def preprocessor():
    return ElectricalPreprocesor()


def test_preprocess_returns_dataframe(preprocessor):

    # Make some data values
    data = [{
        "vdc1": 10, "vdc2": 20, "idc1": 2, "idc2": 4,
        "irradiance": 800, "temperature": 30
    }]

    # Preprocess it
    out = preprocessor.preprocess(data)

    # Check if dataframe and is 1 record
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


def test_columns_and_order(preprocessor):
    data = [{
        "vdc1": 1, "vdc2": 2, "idc1": 3, "idc2": 4,
        "irradiance": 5, "temperature": 6
    }]

    # Check if columns are the same
    out = preprocessor.preprocess(data)

    expected_cols = [
        "vdc1", "vdc2", "idc1", "idc2", "irradiance", "temperature",
        "power_string1", "power_string2", "total_power",
        "voltage_ratio", "current_ratio"
    ]
    assert list(out.columns) == expected_cols


def test_feature_engineering_values(preprocessor):
    data = [{
        "vdc1": 10, "vdc2": 20, "idc1": 2, "idc2": 4,
        "irradiance": 800, "temperature": 30
    }]

    out = preprocessor.preprocess(data).iloc[0]

    assert out["power_string1"] == 10 * 2
    assert out["power_string2"] == 20 * 4
    assert out["total_power"] == (10 * 2) + (20 * 4)

    # Safe divide
    assert out["voltage_ratio"] == pytest.approx(10 / 20, rel=1e-9)
    assert out["current_ratio"] == pytest.approx(2 / 4, rel=1e-9)


def test_missing_keys_use_defaults(preprocessor):

    # Only vdc1 provided
    data = [{"vdc1": 10}]

    out = preprocessor.preprocess(data).iloc[0]

    # Provided
    assert out["vdc1"] == 10.0

    # Defaults
    assert out["vdc2"] == 0.0
    assert out["idc1"] == 0.0
    assert out["idc2"] == 0.0
    assert out["irradiance"] == 0.0
    assert out["temperature"] == 25.0

    # Engineered from defaults
    assert out["power_string1"] == 0.0
    assert out["power_string2"] == 0.0
    assert out["total_power"] == 0.0


def test_safe_divide_does_not_crash(preprocessor):
    data = [{
        "vdc1": 10, "vdc2": 0,
        "idc1": 2, "idc2": 0,
        "irradiance": 100, "temperature": 25
    }]

    out = preprocessor.preprocess(data).iloc[0]

    # Should not raise ZeroDivisionError, ratios should be huge but finite
    assert pd.notna(out["voltage_ratio"])
    assert pd.notna(out["current_ratio"])


def test_multiple_rows(preprocessor):
    data = [
        {"vdc1": 1, "vdc2": 2, "idc1": 3, "idc2": 4, "irradiance": 500, "temperature": 20},
        {"vdc1": 5, "vdc2": 6, "idc1": 7, "idc2": 8, "irradiance": 600, "temperature": 30},
    ]

    out = preprocessor.preprocess(data)

    assert len(out) == 2
    assert out.iloc[0]["total_power"] == (1 * 3) + (2 * 4)
    assert out.iloc[1]["total_power"] == (5 * 7) + (6 * 8)


def test_non_numeric_values_raise(preprocessor):
    data = [{"vdc1": "abc"}]  # Should raise ValueError due to float("abc")

    with pytest.raises(ValueError):
        preprocessor.preprocess(data)
