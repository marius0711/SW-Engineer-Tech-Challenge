# Datei: server/persistence.py

# Handles database persistence logic for storing series metadata

from server.models import SeriesMetadata, SeriesData
from server.db import SessionLocal
from contextlib import contextmanager
from .db import get_db

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


def save_series_metadata(series: SeriesMetadata) -> None:
    """
    Save the provided series metadata into the database.

    Args:
        series (SeriesMetadata): Series data received from the client.
    """
    from server.models import SeriesData

    series_entry = SeriesData(
        patient_id=series.patient_id,
        patient_name=series.patient_name,
        study_instance_uid=series.study_instance_uid,
        series_instance_uid=series.series_instance_uid,
        num_instances=series.num_instances,
    )

    with get_db() as db:
        db.add(series_entry)
