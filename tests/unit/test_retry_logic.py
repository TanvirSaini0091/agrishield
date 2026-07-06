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
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.genai.errors import APIError

from app.agent import CustomGemini


@pytest.fixture
def mock_client_setup():
    """Fixture to patch google.genai.Client to return a mock client."""
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_models = AsyncMock()
        mock_client.aio.models = mock_models

        yield mock_client


@pytest.mark.asyncio
async def test_retry_on_transient_failure_and_recover(mock_client_setup):
    """Verify that transient 503/429 errors trigger retries, and it succeeds on recovery."""
    mock_client = mock_client_setup

    err503 = APIError(503, "Service Unavailable")
    err429 = APIError(429, "Too Many Requests")
    success_response = MagicMock(text="Successful Response")

    # Access the mock method before CustomGemini overrides it on the client
    original_gen_mock = mock_client.aio.models.generate_content
    original_gen_mock.side_effect = [
        err503,
        err429,
        success_response,
    ]

    model = CustomGemini(model="gemini-flash-latest")
    client = model.api_client

    # Patch sleeps to make tests run instantly
    with (
        patch("tenacity.nap.time.sleep", return_value=None),
        patch("anyio.sleep", return_value=None),
        patch("asyncio.sleep", return_value=None),
    ):
        response = await client.aio.models.generate_content("hello")

        assert response.text == "Successful Response"
        assert original_gen_mock.call_count == 3


@pytest.mark.asyncio
async def test_retry_fails_after_three_attempts(mock_client_setup):
    """Verify that it fails and propagates the exception after 3 failed attempts."""
    mock_client = mock_client_setup

    err503 = APIError(503, "Service Unavailable")
    original_gen_mock = mock_client.aio.models.generate_content
    original_gen_mock.side_effect = [err503, err503, err503]

    model = CustomGemini(model="gemini-flash-latest")
    client = model.api_client

    with (
        patch("tenacity.nap.time.sleep", return_value=None),
        patch("anyio.sleep", return_value=None),
        patch("asyncio.sleep", return_value=None),
    ):
        with pytest.raises(APIError) as exc_info:
            await client.aio.models.generate_content("hello")

        assert exc_info.value.code == 503
        assert original_gen_mock.call_count == 3


@pytest.mark.asyncio
async def test_no_retry_on_permanent_failure(mock_client_setup):
    """Verify that permanent errors (e.g. 401 Unauthorized) fail immediately on first attempt."""
    mock_client = mock_client_setup

    err401 = APIError(401, "Unauthorized")
    original_gen_mock = mock_client.aio.models.generate_content
    original_gen_mock.side_effect = [err401]

    model = CustomGemini(model="gemini-flash-latest")
    client = model.api_client

    with (
        patch("tenacity.nap.time.sleep", return_value=None),
        patch("anyio.sleep", return_value=None),
        patch("asyncio.sleep", return_value=None),
    ):
        with pytest.raises(APIError) as exc_info:
            await client.aio.models.generate_content("hello")

        assert exc_info.value.code == 401
        assert original_gen_mock.call_count == 1
