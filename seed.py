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

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("ERROR: CSV file is empty.")
        sys.exit(1)

    col = resolve_columns(list(rows[0].keys()))
    print(f"Column mapping: {col}")

    db = Session()
    inserted = 0
    skipped = 0
    errors = 0

    try:
        for i, row in enumerate(rows, 1):
            try:
                name = row[col["name"]].strip()
                gender = row[col["gender"]].strip().lower()
                gender_probability = float(row[col["gender_probability"]])
                age = int(float(row[col["age"]]))
                age_group = row[col["age_group"]].strip().lower()
                country_id = row[col["country_id"]].strip().upper()
                country_name = row[col["country_name"]].strip()
                country_probability = float(row[col["country_probability"]])

                stmt = text("""
                    INSERT INTO profiles
                        (id, name, gender, gender_probability, age, age_group,
                         country_id, country_name, country_probability)
                    VALUES
                        (:id, :name, :gender, :gender_probability, :age, :age_group,
                         :country_id, :country_name, :country_probability)
                    ON CONFLICT (name) DO NOTHING
                """)

                result = db.execute(stmt, {
                    "id": str(uuid7()),
                    "name": name,
                    "gender": gender,
                    "gender_probability": gender_probability,
                    "age": age,
                    "age_group": age_group,
                    "country_id": country_id,
                    "country_name": country_name,
                    "country_probability": country_probability,
                })

                if result.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1

            except Exception as e:
                errors += 1
                print(f"  Row {i} error: {e} | data: {dict(row)}")

            if i % 100 == 0:
                db.commit()
                print(f"  Progress: {i}/{len(rows)} rows processed...")

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"FATAL ERROR: {e}")
        raise
    finally:
        db.close()

    print(f"\nSeeding complete!")
    print(f"  Inserted : {inserted}")
    print(f"  Skipped  : {skipped} (already exist)")
    print(f"  Errors   : {errors}")
    print(f"  Total    : {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed.py <path-to-csv>")
        print("Example: python seed.py profiles.csv")
        sys.exit(1)

    seed(sys.argv[1])