# Datei: tests/test_api.py 

# Server API Tests for Valid Inputs (async)

import pytest
import uuid
from httpx import AsyncClient
from httpx import ASGITransport
from starlette import status
from server.main import app

@pytest.mark.asyncio
async def test_upload_series_success():
    """
    Test that the /upload-series API endpoint successfully handles valid input data.

    This test simulates sending a valid DICOM series metadata object to the FastAPI server.
    It uses an asynchronous HTTP client and checks if the server returns a 200 OK response
    with a success message in the body.
    """
    # Given: Valid DICOM series data
    test_data = {
        "PatientID": "12345",
        "PatientName": "John Doe",
        "StudyInstanceUID": "1.2.3.4",
        "SeriesInstanceUID": str(uuid.uuid4()),  # Generate unique UID for each test run
        "NumInstances": 10
    }

    # When: Sending the data to the server API
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/upload-series", json=test_data)

    # Then: Expect success response
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "success"
