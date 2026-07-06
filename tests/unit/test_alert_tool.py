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

from app.agent import REGIONAL_ALERTS, update_regional_alert_status


@pytest.fixture(autouse=True)
def clear_alerts():
    """Clear the in-memory alerts registry before each test."""
    REGIONAL_ALERTS.clear()


def test_activate_alert_success():
    """Verify that an administrator can successfully activate an alert with valid parameters."""
    result = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning in northern sectors.",
        severity="high",
    )
    assert "Success: Alert activated" in result

    # Verify it is in registry (coordinates rounded to 4 decimals)
    coord_key = (12.3456, 78.9101)
    assert coord_key in REGIONAL_ALERTS
    assert REGIONAL_ALERTS[coord_key]["alert_type"] == "pest"
    assert REGIONAL_ALERTS[coord_key]["severity"] == "high"


def test_mutate_alert_success():
    """Verify that an administrator can successfully mutate an existing alert."""
    # First, activate an alert
    update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )

    # Mutate the alert
    result = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="mutate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="disease",
        details="Locust swarm dispersed. Rust outbreak identified.",
        severity="medium",
    )
    assert "Success: Alert mutated" in result

    # Verify updates in the registry
    coord_key = (12.3456, 78.9101)
    assert REGIONAL_ALERTS[coord_key]["alert_type"] == "disease"
    assert REGIONAL_ALERTS[coord_key]["severity"] == "medium"
    assert "Rust outbreak" in REGIONAL_ALERTS[coord_key]["details"]


def test_deactivate_alert_success():
    """Verify that an administrator can successfully deactivate an alert."""
    # First, activate an alert
    update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )

    # Deactivate the alert
    result = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="deactivate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Success: Alert deactivated" in result

    # Verify deletion from the registry
    coord_key = (12.3456, 78.9101)
    assert coord_key not in REGIONAL_ALERTS


def test_unauthenticated_session():
    """Verify that request fails if the admin token is invalid."""
    result = update_regional_alert_status(
        admin_token="INVALID-TOKEN",
        action="activate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Error: Unauthenticated Session" in result
    assert len(REGIONAL_ALERTS) == 0


def test_out_of_bounds_latitude():
    """Verify that out-of-bounds latitude values raise a validation error."""
    # Test latitude > 90
    result = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=95.0,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Error: Validation Failed" in result
    assert "Latitude must be between -90.0 and 90.0" in result

    # Test latitude < -90
    result2 = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=-100.5,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Error: Validation Failed" in result2
    assert "Latitude must be between -90.0 and 90.0" in result2
    assert len(REGIONAL_ALERTS) == 0


def test_out_of_bounds_longitude():
    """Verify that out-of-bounds longitude values raise a validation error."""
    # Test longitude > 180
    result = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=12.3456,
        longitude=181.0,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Error: Validation Failed" in result
    assert "Longitude must be between -180.0 and 180.0" in result

    # Test longitude < -180
    result2 = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=12.3456,
        longitude=-200.0,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Error: Validation Failed" in result2
    assert "Longitude must be between -180.0 and 180.0" in result2
    assert len(REGIONAL_ALERTS) == 0


def test_invalid_choices():
    """Verify that invalid enum selections fail Pydantic validation."""
    # Bad action
    result = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="delete",  # Invalid action
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="high",
    )
    assert "Error: Validation Failed" in result

    # Bad severity
    result2 = update_regional_alert_status(
        admin_token="AGRI-ADMIN-SECURE-2026",
        action="activate",
        latitude=12.3456,
        longitude=78.9101,
        alert_type="pest",
        details="Locust swarm warning.",
        severity="extremely-critical",  # Invalid severity
    )
    assert "Error: Validation Failed" in result2
    assert len(REGIONAL_ALERTS) == 0
