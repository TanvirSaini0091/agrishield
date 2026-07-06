# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest

from app.agent import (
    AGENT_STATE,
    REGIONAL_ALERTS,
    analyze_plant_pathology,
    get_weather_telemetry,
)


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset any global runtime state tracking dictionaries between test runs."""
    AGENT_STATE["last_humidity"] = None
    AGENT_STATE["last_temperature"] = None
    REGIONAL_ALERTS.clear()


def test_weather_parameter_validation_out_of_bounds():
    """Verify that get_weather_telemetry returns an error if coordinates are out of bounds."""
    # Out of bounds latitude (> 90)
    res_lat_high = get_weather_telemetry(95.0, 45.0)
    assert "Error: Validation Failed" in res_lat_high
    assert "Latitude must be between -90.0 and 90.0" in res_lat_high

    # Out of bounds latitude (< -90)
    res_lat_low = get_weather_telemetry(-91.0, 45.0)
    assert "Error: Validation Failed" in res_lat_low
    assert "Latitude must be between -90.0 and 90.0" in res_lat_low

    # Out of bounds longitude (> 180)
    res_lon_high = get_weather_telemetry(10.0, 185.5)
    assert "Error: Validation Failed" in res_lon_high
    assert "Longitude must be between -180.0 and 180.0" in res_lon_high

    # Out of bounds longitude (< -180)
    res_lon_low = get_weather_telemetry(10.0, -181.0)
    assert "Error: Validation Failed" in res_lon_low
    assert "Longitude must be between -180.0 and 180.0" in res_lon_low


def test_state_dependency_integration():
    """Verify that high humidity (> 75%) updates AGENT_STATE and is handled by pathology."""
    # 1. Under normal conditions (latitude = 45.0 -> 60% humidity)
    res_normal = get_weather_telemetry(45.0, 45.0)
    assert "Relative Humidity=60%" in res_normal
    assert AGENT_STATE["last_humidity"] == "60%"

    res_pathology_normal = analyze_plant_pathology("tomato", "yellow spots")
    assert "Early Blight" in res_pathology_normal
    assert "Late Blight" not in res_pathology_normal

    # 2. Under equatorial conditions (latitude = 5.0 -> 90% humidity)
    res_humid = get_weather_telemetry(5.0, 45.0)
    assert "Relative Humidity=90%" in res_humid
    assert AGENT_STATE["last_humidity"] == "90%"

    # Pathology tool should detect high humidity from AGENT_STATE and flag critical Late Blight
    res_pathology_humid = analyze_plant_pathology("tomato", "yellow spots")
    assert "Late Blight" in res_pathology_humid
    assert "exacerbated by high humidity (>75%)" in res_pathology_humid
    assert "Critical" in res_pathology_humid

    # Verify it also handles water-soaked spots
    res_pathology_soaked = analyze_plant_pathology("tomato", "water-soaked spots")
    assert "Late Blight" in res_pathology_soaked
    assert "Critical" in res_pathology_soaked

    # Verify it also handles white fuzzy growth
    res_pathology_fuzzy = analyze_plant_pathology("tomato", "white fuzzy growth")
    assert "Late Blight" in res_pathology_fuzzy
    assert "Critical" in res_pathology_fuzzy


def test_plant_pathology_input_sanitization():
    """Verify that analyze_plant_pathology rejects empty or malicious inputs."""
    # Empty string crop name
    res_empty_crop = analyze_plant_pathology("", "yellow spots")
    assert "Error: Validation Failed" in res_empty_crop
    assert "cannot be empty" in res_empty_crop

    # Whitespace crop name
    res_whitespace_crop = analyze_plant_pathology("   ", "yellow spots")
    assert "Error: Validation Failed" in res_whitespace_crop
    assert "cannot be empty" in res_whitespace_crop

    # Malicious script input in leaf_condition
    res_malicious_script = analyze_plant_pathology(
        "tomato", "<script>alert(1)</script>"
    )
    assert "Error: Validation Failed" in res_malicious_script
    assert "injection attack detected" in res_malicious_script

    # Malicious eval keyword in crop_name
    res_malicious_eval = analyze_plant_pathology("tomato; eval('bad')", "yellow spots")
    assert "Error: Validation Failed" in res_malicious_eval
    assert "injection attack detected" in res_malicious_eval


def test_coordinate_exact_boundaries():
    """Asserts that validation passes cleanly at maximum limits (90.0, 180.0) but throws a Pydantic ValidationError if exceeded by even 0.1."""
    from pydantic import ValidationError

    from app.agent import WeatherTelemetryInput

    # Validation passes cleanly at maximum limits
    assert WeatherTelemetryInput(latitude=90.0, longitude=180.0)
    assert WeatherTelemetryInput(latitude=-90.0, longitude=-180.0)

    # Raises ValidationError if exceeded by even 0.1
    with pytest.raises(ValidationError):
        WeatherTelemetryInput(latitude=90.1, longitude=180.0)
    with pytest.raises(ValidationError):
        WeatherTelemetryInput(latitude=90.0, longitude=180.1)
    with pytest.raises(ValidationError):
        WeatherTelemetryInput(latitude=-90.1, longitude=-180.0)
    with pytest.raises(ValidationError):
        WeatherTelemetryInput(latitude=-90.0, longitude=-180.1)


def test_pathology_dry_equatorial_safety():
    """Asserts that if coordinates are equatorial but humidity is simulated/forced low (<50%), the diagnosis is NOT upgraded to Critical Late Blight, avoiding false positives."""
    AGENT_STATE["last_humidity"] = "40%"
    res = analyze_plant_pathology("tomato", "yellow spots")
    assert "Early Blight" in res
    assert "Late Blight" not in res


def test_symptom_input_sanitization_robustness():
    """Asserts that passing long gibberish strings or injection attempts into analyze_plant_pathology fails safely or defaults to low/unknown risk rather than crashing the runtime."""
    # Long gibberish strings exceeding 500 max_length
    long_symptom = "a" * 501
    res_long = analyze_plant_pathology("tomato", long_symptom)
    assert "Error: Validation Failed" in res_long

    # Script injection attempt
    res_script = analyze_plant_pathology("tomato", "<script>alert(1)</script>")
    assert "Error: Validation Failed" in res_script


def test_missing_state_graceful_fallback():
    """Asserts that calling the pathology tool before the weather tool initializes the global state dict handles the missing keys gracefully without raising a KeyError."""
    if "last_humidity" in AGENT_STATE:
        del AGENT_STATE["last_humidity"]
    if "last_temperature" in AGENT_STATE:
        del AGENT_STATE["last_temperature"]

    try:
        res = analyze_plant_pathology("tomato", "yellow spots")
        assert "Early Blight" in res
    except KeyError:
        pytest.fail("Raised KeyError on missing AGENT_STATE keys")


def test_pathology_gemini_fallback_out_of_scope():
    """Asserts that if the crop and symptoms do not trigger local rules, it calls Gemini.
    If the prompt is out-of-scope (like PC hardware), it returns the block phrase.
    """
    from unittest.mock import MagicMock, patch

    mock_response = MagicMock()
    mock_response.text = "I can only assist with agricultural issues such as crop telemetry, plant pathology, or farming support. This request is out of scope."

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.return_value = mock_response

        res = analyze_plant_pathology("grapes", "Optimize PC hardware")
        assert "I can only assist with agricultural issues" in res

        # Verify generate_content was called with correct arguments
        mock_client.models.generate_content.assert_called_once()
        _, kwargs = mock_client.models.generate_content.call_args
        assert kwargs["model"] == "gemini-flash-latest"
        assert "Optimize PC hardware" in kwargs["contents"]
        assert "grapes" in kwargs["contents"]
        assert "agronomic advice" in kwargs["config"].system_instruction


def test_pathology_gemini_server_error_fallback():
    """Asserts that if the Gemini API call fails with a server error, it falls back gracefully to local rules."""
    from unittest.mock import MagicMock, patch

    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        # Simulate a 503 Service Unavailable exception
        mock_client.models.generate_content.side_effect = Exception(
            "503 Service Unavailable"
        )

        # Grapes normal (low humidity) fallback
        res = analyze_plant_pathology("grapes", "yellow spots")
        assert (
            "[Notice: High server load detected. Displaying local rule-based diagnostic engine fallback]"
            in res
        )
        assert "General nutritional deficiency" in res

        # Grapes high humidity fallback
        AGENT_STATE["last_humidity"] = "90%"
        res_humid = analyze_plant_pathology("grapes", "yellow spots")
        assert (
            "[Notice: High server load detected. Displaying local rule-based diagnostic engine fallback]"
            in res_humid
        )
        assert "Elevated fungal disease risk" in res_humid
