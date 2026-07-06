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
from unittest.mock import MagicMock, patch

import pytest

from app.agent import AGENT_STATE


@pytest.fixture(autouse=True)
def mock_gemini_client():
    """Autouse fixture to mock google.genai.Client for unit tests where live API is not configured."""
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        def mock_generate_content(model, contents, config=None, **kwargs):
            crop = ""
            symptoms = ""
            if isinstance(contents, str):
                contents_lower = contents.lower()
                if "crop:" in contents_lower:
                    try:
                        crop_line = next(
                            line
                            for line in contents.split("\n")
                            if "crop:" in line.lower()
                        )
                        crop = crop_line.split(":")[1].strip().lower()
                    except Exception:
                        pass
                if "symptoms/condition:" in contents_lower:
                    try:
                        sym_line = next(
                            line
                            for line in contents.split("\n")
                            if "symptoms/condition:" in line.lower()
                        )
                        symptoms = sym_line.split(":")[1].strip().lower()
                    except Exception:
                        pass

            # Check humidity from AGENT_STATE
            humidity_str = AGENT_STATE.get("last_humidity")
            high_humidity = False
            if humidity_str:
                try:
                    humidity_val = int(humidity_str.replace("%", ""))
                    if humidity_val > 75:
                        high_humidity = True
                except Exception:
                    pass

            response = MagicMock()
            if "tomato" in crop:
                if any(
                    kw in symptoms
                    for kw in [
                        "yellow",
                        "spot",
                        "fuzz",
                        "patch",
                        "water-soaked",
                        "fuzzy",
                        "blight",
                    ]
                ):
                    if high_humidity:
                        response.text = (
                            "Diagnosis: Late Blight (Phytophthora infestans) "
                            "exacerbated by high humidity (>75%). Risk: Critical. "
                            "Action: Apply immediate copper fungicide and isolate crops."
                        )
                    else:
                        response.text = (
                            "Diagnosis: Early Blight (Alternaria solani). "
                            "Risk: High. Action: Apply copper-based fungicide and remove affected lower leaves."
                        )
                else:
                    response.text = (
                        "Diagnosis: General nutritional deficiency or stress. "
                        "Risk: Low."
                    )
            else:
                response.text = (
                    "I can only assist with agricultural issues such as crop telemetry, "
                    "plant pathology, or farming support. This request is out of scope."
                )

            return response

        mock_client.models.generate_content.side_effect = mock_generate_content
        yield mock_client
