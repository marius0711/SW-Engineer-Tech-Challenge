# Datei: server/main.py

# FastAPI application that handles incoming series metadata

from fastapi import FastAPI, HTTPException
from server.models import SeriesMetadata
from server.db import Base, engine
from server.persistence import save_series_metadata

# Initialize FastAPI app
app = FastAPI()

# Create tables in the database
Base.metadata.create_all(bind=engine)

@app.post("/upload-series")
async def upload_series(data: SeriesMetadata):
    """
    API endpoint to receive series metadata and store it in the database.

    Args:
        data (SeriesMetadata): Metadata received from the client.

    Returns:
        JSON response with status information.
    """
    
    try:
        save_series_metadata(data)
        return {"status": "success"}
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
