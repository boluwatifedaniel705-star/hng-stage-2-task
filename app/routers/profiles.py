from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import Profile
from app.schemas import ProfileResponse
from app.services.nlp_parser import parse_natural_language

router = APIRouter()

VALID_GENDERS = {"male", "female"}
VALID_AGE_GROUPS = {"child", "teenager", "adult", "senior"}
VALID_SORT_BY = {"age", "created_at", "gender_probability"}
VALID_ORDERS = {"asc", "desc"}


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )


def build_profile_list_response(profiles, total: int, page: int, limit: int):
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [ProfileResponse.model_validate(p).model_dump() for p in profiles],
    }


@router.get("/profiles/search")
def search_profiles(
    q: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    if not q or not q.strip():
        return error_response(400, "Invalid query parameters")

    filters = parse_natural_language(q.strip())

    if filters is None:
        return error_response(400, "Unable to interpret query")

    query = db.query(Profile)

    if "gender" in filters:
        query = query.filter(Profile.gender == filters["gender"])
    if "age_group" in filters:
        query = query.filter(Profile.age_group == filters["age_group"])
    if "country_id" in filters:
        query = query.filter(Profile.country_id == filters["country_id"])
    if "min_age" in filters:
        query = query.filter(Profile.age >= filters["min_age"])
    if "max_age" in filters:
        query = query.filter(Profile.age <= filters["max_age"])

    total = query.count()
    offset = (page - 1) * limit
    profiles = query.offset(offset).limit(limit).all()

    return build_profile_list_response(profiles, total, page, limit)


@router.get("/profiles")
def get_profiles(
    gender: Optional[str] = Query(default=None),
    age_group: Optional[str] = Query(default=None),
    country_id: Optional[str] = Query(default=None),
    min_age: Optional[int] = Query(default=None),
    max_age: Optional[int] = Query(default=None),
    min_gender_probability: Optional[float] = Query(default=None),
    min_country_probability: Optional[float] = Query(default=None),
    sort_by: Optional[str] = Query(default=None),
    order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    if gender is not None and gender not in VALID_GENDERS:
        return error_response(400, "Invalid query parameters")
    if age_group is not None and age_group not in VALID_AGE_GROUPS:
        return error_response(400, "Invalid query parameters")
    if sort_by is not None and sort_by not in VALID_SORT_BY:
        return error_response(400, "Invalid query parameters")
    if order not in VALID_ORDERS:
        return error_response(400, "Invalid query parameters")
    if min_age is not None and min_age < 0:
        return error_response(422, "Invalid query parameters")
    if max_age is not None and max_age < 0:
        return error_response(422, "Invalid query parameters")
    if min_age is not None and max_age is not None and min_age > max_age:
        return error_response(400, "Invalid query parameters")
    if min_gender_probability is not None and not (0.0 <= min_gender_probability <= 1.0):
        return error_response(422, "Invalid query parameters")
    if min_country_probability is not None and not (0.0 <= min_country_probability <= 1.0):
        return error_response(422, "Invalid query parameters")

    query = db.query(Profile)

    if gender is not None:
        query = query.filter(Profile.gender == gender)
    if age_group is not None:
        query = query.filter(Profile.age_group == age_group)
    if country_id is not None:
        query = query.filter(Profile.country_id == country_id.upper())
    if min_age is not None:
        query = query.filter(Profile.age >= min_age)
    if max_age is not None:
        query = query.filter(Profile.age <= max_age)
    if min_gender_probability is not None:
        query = query.filter(Profile.gender_probability >= min_gender_probability)
    if min_country_probability is not None:
        query = query.filter(Profile.country_probability >= min_country_probability)

    if sort_by is not None:
        sort_column = getattr(Profile, sort_by)
        query = query.order_by(
            sort_column.desc() if order == "desc" else sort_column.asc()
        )

    total = query.count()
    offset = (page - 1) * limit
    profiles = query.offset(offset).limit(limit).all()

    return build_profile_list_response(profiles, total, page, limit)