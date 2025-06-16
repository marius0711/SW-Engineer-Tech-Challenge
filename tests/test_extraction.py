# Datei: test_extraction.py UNit-test for DICOM metadata extraction

import pytest
from pathlib import Path
from tests.test_integration_pipeline import extract_metadata_from_dicom
import pydicom

def test_extract_metadata_from_dicom_valid_file():
    """
    Unit test to verify metadata extraction from a valid DICOM file.
    """

    # Given: A path to a valid DICOM file
    dicom_path = Path("tests/data/0000.dcm")

    # When: Extracting metadata using the utility function
    metadata = extract_metadata_from_dicom(dicom_path)

    # Then: Verify correct output format and presence of required fields
    assert isinstance(metadata, dict)
    assert "PatientID" in metadata
    assert "PatientName" in metadata
    assert "StudyInstanceUID" in metadata
    assert "SeriesInstanceUID" in metadata
    assert "NumInstances" in metadata
    assert isinstance(metadata["NumInstances"], int)

def test_extract_metadata_from_nonexistent_file():
    """
    Unit test to verify behavior when a non-existent file path is provided.
    """
    
    # Given: A path to a non-existent DICOM file
    fake_path = Path("tests/data/nonexistent.dcm")

    # Then: Expect the function to raise a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        extract_metadata_from_dicom(fake_path)