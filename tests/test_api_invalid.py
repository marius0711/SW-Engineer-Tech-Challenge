# Datei: tests/test_invalid_api.py 

#  Server API Tests for Invalid Inputs

from fastapi.testclient import TestClient
from server.main import app

# Create a test client for the FastAPI app
client = TestClient(app)

def test_upload_series_missing_field():
    """
    Test that a POST request with a missing required field (SeriesInstanceUID)
    results in a 422 Unprocessable Entity error.
    """
    response = client.post("/upload-series", json={
        "PatientID": "12345",
        "PatientName": "John Doe",
        "StudyInstanceUID": "1.2.3.4",
        "NumInstances": 10
        # SeriesInstanceUID missing
    })
    assert response.status_code == 422
    assert "SeriesInstanceUID" in response.text

def test_upload_series_invalid_num_instances_type():
    """
    Test that a POST request with an invalid data type (string instead of int)
    for the field 'NumInstances' is rejected with a 422 error.
    """
     
    # Testdata with invalid datatype for NumInstances (String instead Integer)
    invalid_data = {
        "PatientID": "12345",
        "PatientName": "John Doe",
        "StudyInstanceUID": "1.2.3.4",
        "SeriesInstanceUID": "1.2.3.4.5",
        "NumInstances": "zehn" # Invalid type, should be an integer
    }

    response = client.post("/upload-series", json=invalid_data)
    
    assert response.status_code == 422
    assert "NumInstances" in response.text

def test_upload_series_empty_json():
    """
    Test that an empty JSON body is rejected with a 422 error,
    indicating that required fields are missing.
    """
    empty_data = {}

    response = client.post("/upload-series", json=empty_data)

    assert response.status_code == 422
    assert "detail" in response.json()
