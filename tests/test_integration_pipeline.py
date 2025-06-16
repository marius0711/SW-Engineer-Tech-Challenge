# Datei: tests/test_integration_pipeline.py

import os
import pytest
import httpx
import pydicom
import uuid
from httpx import ASGITransport, AsyncClient
from server.main import app
from server.db import SessionLocal
from server.models import SeriesData
from fastapi import status

# Utility function to extract metadata from a DICOM file
def extract_metadata_from_dicom(path: str) -> dict:
    """
    Reads a DICOM file and extracts relevant metadata for testing.
    """

    ds = pydicom.dcmread(path)

    return {
        "PatientID": str(ds.PatientID),
        "PatientName": str(ds.PatientName),
        "StudyInstanceUID": str(ds.StudyInstanceUID),   # Use random UUID to avoid uniqueness conflicts in test database
        "SeriesInstanceUID": str(uuid.uuid4()),
        "NumInstances": 1
    }

@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    """
    Integration test that verifies the entire flow:
    1. Extract metadata from a sample DICOM file.
    2. Send metadata to the API.
    3. Verify that the data is correctly persisted in the database.
    """

    # GIVEN: Load metadata from a real DICOM file
    dicom_path = "tests/data/0000.dcm"
    payload = extract_metadata_from_dicom(dicom_path)

    # WHEN: Send the payload to the FastAPI endpoint
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/upload-series", json=payload)

    # THEN: Ensure the server responded successfully
    assert response.status_code == status.HTTP_200_OK

    # Check whether the entry was persisted in the database
    db = SessionLocal()
    db_result = db.query(SeriesData).filter_by(SeriesInstanceUID=payload["SeriesInstanceUID"]).first()
    assert db_result is not None
    assert db_result.PatientID == payload["PatientID"]
    assert db_result.NumInstances == 1

    # Cleanup: remove the test entry to keep DB clean
    db.delete(db_result)
    db.commit()
    db.close()