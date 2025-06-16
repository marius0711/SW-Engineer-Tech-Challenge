# Datei: server/persistence.py

# Handles database persistence logic for storing series metadata

from server.models import SeriesMetadata, SeriesData
from server.db import SessionLocal

def save_series_metadata(series: SeriesMetadata):
    """
    Save the provided series metadata into the database.

    Args:
        series (SeriesMetadata): Series data received from the client.
    """
    
    db = SessionLocal()
    db_series = SeriesData(**series.model_dump()) # Convert Pydantic to SQLAlchemy model
    db.add(db_series)
    db.commit()
    db.close()
