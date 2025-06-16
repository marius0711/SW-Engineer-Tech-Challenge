# Datei: server/models.py

# Pydantic and SQLAlchemy models used for validation and database interaction

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from server.db import Base

# Pydantic Model (for request validation)
class SeriesMetadata(BaseModel):
    PatientID: str
    PatientName: str
    StudyInstanceUID: str
    SeriesInstanceUID: str
    NumInstances: int

# SQLAlchemy model representing the series_data table in the database
class SeriesData(Base):
    __tablename__ = "series_data"

    id = Column(Integer, primary_key=True, index=True)
    PatientID = Column(String)
    PatientName = Column(String)
    StudyInstanceUID = Column(String)
    SeriesInstanceUID = Column(String, unique=True)
    NumInstances = Column(Integer)
