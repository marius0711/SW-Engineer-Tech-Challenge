# Datei: tests/test_db_persistence.py Server-side tests for database persistence

import pytest
from httpx import AsyncClient
from fastapi import status
from server.main import app
from server.db import SessionLocal
from server.models import SeriesData
from fastapi.testclient import TestClient
from httpx import ASGITransport

@pytest.mark.asyncio
async def test_series_persistence_in_db():
    """
    This test verifies that metadata sent to the /upload-series endpoint
    is correctly persisted in the database.
    """
     # Given: Valid test metadata for a DICOM series
    test_data = {
        "PatientID": "98765",
        "PatientName": "Jane Smith",
        "StudyInstanceUID": "1.2.3.10",
        "SeriesInstanceUID": "1.2.3.10.5",
        "NumInstances": 15
    }

    # When: Sending the data to the FastAPI server using in-memory transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/upload-series", json=test_data)

    # Then: Expect HTTP 200 OK
    assert response.status_code == status.HTTP_200_OK

    # And: Verify that the data has been stored in the database
    db = SessionLocal()
    db_series = db.query(SeriesData).filter_by(SeriesInstanceUID=test_data["SeriesInstanceUID"]).first()
    
    assert db_series is not None
    assert db_series.PatientID == test_data["PatientID"]
    assert db_series.PatientName == test_data["PatientName"]
    assert db_series.StudyInstanceUID == test_data["StudyInstanceUID"]
    assert db_series.NumInstances == test_data["NumInstances"]

    # Clean up: Remove inserted record to avoid pollution of test environment
    db.delete(db_series)
    db.commit()
    db.close()

