# File: tests/test_bulk_series_upload.py
# Integration Test: Bulk PACS Transmission + Logging + Statistics (hardcoded path)

import pytest
import pydicom
import time
from pathlib import Path
from collections import defaultdict
from httpx import AsyncClient, ASGITransport
from server.main import app
from server.db import SessionLocal
from server.models import SeriesData
from fastapi import status
import logging
from datetime import datetime


def extract_metadata_from_dicom(path: Path) -> dict:
    """
    Extracts key metadata from a DICOM file.

    Args:
        path (Path): Path to the DICOM (.dcm) file.

    Returns:
        dict: Dictionary containing DICOM metadata (PatientID, PatientName,
              StudyInstanceUID, SeriesInstanceUID, NumInstances).
    """
    ds = pydicom.dcmread(path)
    return {
        "PatientID": str(ds.PatientID),
        "PatientName": str(ds.PatientName),
        "StudyInstanceUID": str(ds.StudyInstanceUID),
        "SeriesInstanceUID": str(ds.SeriesInstanceUID),
        "NumInstances": 1
    }

@pytest.mark.asyncio
async def test_bulk_series_upload_from_directory():
    """
    Performs an integration test simulating a bulk PACS DICOM upload.
    """
    # Configuration
    test_dir = Path("/Users/marize/Downloads/floy_challenge/data/dcm/2") #HARDCODED: Insert Link for Data Set to investigate
    dicom_files = list(test_dir.glob("*.dcm"))
    inserted_series_ids = set()
    skipped_duplicates = 0
    patient_series_counter = defaultdict(set)

    # Logging Setup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filename = f"bulk_test_{test_dir.name}_{timestamp}.log"
    log_path = log_dir / log_filename

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

    # Ensure no duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)

    # start testing
    start_time = time.time()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:  # Gap for server connection
        for dicom_file in dicom_files:
            metadata = extract_metadata_from_dicom(dicom_file)

            # Skip duplicates within this test run
            if metadata["SeriesInstanceUID"] in inserted_series_ids: # protect against duplicates intern
                continue

            response = await ac.post("/upload-series", json=metadata)

            # Detect and log duplicate entries based on DB constraint
            if response.status_code == 500 and "UNIQUE constraint failed" in response.text:
                skipped_duplicates += 1 # protect against duplicates in DB
                logger.info(f"⚠️ Duplicate skipped: {metadata['SeriesInstanceUID']}")
                continue

            # Ensure successful upload
            assert response.status_code == status.HTTP_200_OK
            inserted_series_ids.add(metadata["SeriesInstanceUID"])
            patient_series_counter[metadata["PatientID"]].add(metadata["SeriesInstanceUID"])

    duration = time.time() - start_time

    # Database Verification
    db = SessionLocal()
    for series_uid in inserted_series_ids:
        entry = db.query(SeriesData).filter_by(SeriesInstanceUID=series_uid).first()
        assert entry is not None
    db.close()

    # Summary Logging
    logger.info("=== Bulk Series Upload Test Summary ===")
    logger.info(f"Directory tested: {test_dir}")
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"Total DICOM files scanned: {len(dicom_files)}")
    logger.info(f"✅ Successfully inserted series: {len(inserted_series_ids)}")
    logger.info(f"⚠️ Skipped duplicates: {skipped_duplicates}")
    logger.info(f"⏱ Total processing time: {duration:.2f} seconds")

    if len(dicom_files) > 0:
        success_rate = (len(inserted_series_ids) / len(dicom_files)) * 100
        # logger.info(f"📊 Success rate: {success_rate:.1f}%")

    logger.info("👤 Series per patient:")
    for pid, series_set in patient_series_counter.items():
        logger.info(f"  - PatientID {pid}: {len(series_set)} series")

    logger.info("✅ Database verification: PASSED")

    # Clean up logger handlers
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)
