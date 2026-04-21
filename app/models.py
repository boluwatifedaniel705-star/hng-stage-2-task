from sqlalchemy import Column, String, Float, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid6 import uuid7
from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name = Column(String, unique=True, nullable=False)
    gender = Column(String, nullable=False)
    gender_probability = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    country_id = Column(String(2), nullable=False)
    country_name = Column(String, nullable=False)
    country_probability = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_profiles_gender", "gender"),
        Index("ix_profiles_age_group", "age_group"),
        Index("ix_profiles_country_id", "country_id"),
        Index("ix_profiles_age", "age"),
        Index("ix_profiles_created_at", "created_at"),
        Index("ix_profiles_gender_probability", "gender_probability"),
        Index("ix_profiles_country_probability", "country_probability"),
    )