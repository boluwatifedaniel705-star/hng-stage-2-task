import csv
import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from uuid6 import uuid7

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/insighta_db")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

COL_MAP = {
    "name": ["name", "Name", "full_name", "full name"],
    "gender": ["gender", "Gender"],
    "gender_probability": ["gender_probability", "Gender Probability", "gender probability", "genderProbability"],
    "age": ["age", "Age"],
    "age_group": ["age_group", "Age Group", "age group", "ageGroup"],
    "country_id": ["country_id", "Country ID", "country_code", "countryId", "country id"],
    "country_name": ["country_name", "Country Name", "country", "countryName", "country name"],
    "country_probability": ["country_probability", "Country Probability", "country probability", "countryProbability"],
}


def resolve_columns(header: list) -> dict:
    mapping = {}
    header_lower = {h: h.lower().strip() for h in header}

    for field, aliases in COL_MAP.items():
        for col in header:
            if col in aliases or col.strip() in aliases or header_lower[col] in [a.lower() for a in aliases]:
                mapping[field] = col
                break

    missing = [f for f in COL_MAP if f not in mapping]
    if missing:
        print(f"WARNING: Could not find columns for: {missing}")
        print(f"Available columns: {header}")
    return mapping


def seed(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)

    with open(csv_path, new