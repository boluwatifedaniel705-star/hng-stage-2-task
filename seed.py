import json
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


def seed(json_path: str):
    if not os.path.exists(json_path):
        print(f"ERROR: File not found: {json_path}")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    rows = data.get("profiles", [])

    if not rows:
        print("ERROR: No profiles found in JSON file.")
        sys.exit(1)

    print(f"Found {len(rows)} profiles to seed...")

    db = Session()
    inserted = 0
    skipped = 0
    errors = 0

    try:
        for i, row in enumerate(rows, 1):
            try:
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
                    "name": row["name"].strip(),
                    "gender": row["gender"].strip().lower(),
                    "gender_probability": float(row["gender_probability"]),
                    "age": int(row["age"]),
                    "age_group": row["age_group"].strip().lower(),
                    "country_id": row["country_id"].strip().upper(),
                    "country_name": row["country_name"].strip(),
                    "country_probability": float(row["country_probability"]),
                })

                if result.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1

            except Exception as e:
                errors += 1
                print(f"  Row {i} error: {e} | data: {row}")

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
        print("Usage: python seed.py <path-to-json>")
        print("Example: python seed.py seed_profiles.json")
        sys.exit(1)

    seed(sys.argv[1])