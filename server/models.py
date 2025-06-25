# Datei: server/models.py

# Pydantic and SQLAlchemy models used for validation and database interaction

from pydantic import BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column
from server.db import Base

# Pydantic Model (for request validation)
class SeriesMetadata(BaseModel):
    patient_id: str = Field(..., alias="PatientID")
    patient_name: str = Field(..., alias="PatientName")
    study_instance_uid: str = Field(..., alias="StudyInstanceUID")
    series_instance_uid: str = Field(..., alias="SeriesInstanceUID")
    num_instances: int = Field(..., alias="NumInstances")

    class Config:
        populate_by_name = True

# SQLAlchemy model representing the series_data table in the database
class SeriesData(Base):
    __tablename__ = "series_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[str] = mapped_column()
    patient_name: Mapped[str] = mapped_column()
    study_instance_uid: Mapped[str] = mapped_column()
    series_instance_uid: Mapped[str] = mapped_column(unique=True)
    num_instances: Mapped[int] = mapped_column()
