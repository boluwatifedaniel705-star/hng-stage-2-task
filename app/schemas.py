from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid


class ProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    gender: str
    gender_probability: float
    age: int
    age_group: str
    country_id: str
    country_name: str
    country_probability: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileListResponse(BaseModel):
    status: str
    page: int
    limit: int
    total: int
    data: List[ProfileResponse]