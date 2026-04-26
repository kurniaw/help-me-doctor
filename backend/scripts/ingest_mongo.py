#!/usr/bin/env python3
"""Load all CSV knowledge base files into MongoDB collections.

Usage:
    python scripts/ingest_mongo.py [--data-dir ../data] [--drop]

Options:
    --data-dir PATH   Path to the data directory (default: ../data)
    --drop            Drop existing collections before inserting
"""
import argparse
import asyncio
import logging
import os
from pathlib import Path

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CSV_COLLECTION_MAP = {
    "medical_condition_knowledge_base.csv": "medical_conditions",
    "singapore_doctors_database.csv": "doctors",
    "singapore_hospitals_database.csv": "hospitals",
    "legal_medicine_knowledge_base.csv": "legal_cases",
    "legal_medicine_specialists_directory.csv": "forensic_specialists",
    "master_legal_medicine_knowledge_base.csv": "legal_master",
    "master_medical_knowledge_base.csv": "medical_master",
    "chas_clinics_singapore.csv": "chas_clinics",
}

INDEXES: dict[str, list] = {
    "medical_conditions": [
        [("Symptoms", "text")],
        [("Urgency_Level", 1)],
        [("Triage_Color", 1)],
        [("Recommended_Specialty", 1)],
        [("_vertex_id", 1)],
    ],
    "doctors": [
        [("Specialty", 1)],
        [("On_Call_24Hr", 1)],
        [("Registration_Status", 1)],
        [("CHAS_Accredited", 1)],
    ],
    "hospitals": [
        [("Departments", "text"), ("Key_Specialties", "text")],
        [("24Hr_Emergency", 1)],
    ],
    "legal_cases": [
        [("Case_Type", "text")],
        [("Police_Report_Needed", 1)],
    ],
    "forensic_specialists": [
        [("Forensic_Focus", "text")],
        [("Expert_Witness", 1)],
        [("Available_24Hr", 1)],
    ],
    "legal_master": [
        [("Case_Type", 1)],
    ],
    "medical_master": [
        [("Condition", 1)],
        [("Primary_Specialty", 1)],
    ],
    "chas_clinics": [
        [("location", "2dsphere")],
        [("Division", 1)],
    ],
}


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("yes", "true", "1", "y")
    return bool(value)


def _transform_record(collection_name: str, record: dict) -> dict:
    """Apply collection-specific transformations to a record."""

    # Convert boolean-like fields
    bool_fields_map: dict[str, list[str]] = {
        "doctors": ["On_Call_24Hr", "CHAS_Accredited", "Healthier_SG_Clinic", "Board_Certified"],
        "hospitals": ["24Hr_Emergency", "ICU_Available", "Teaching_Hospital", "Government_Hospital",
                      "Ambulance_Available", "Parking_Available", "Wheelchair_Accessible"],
        "legal_cases": ["Police_Report_Needed", "Urgent_Examination", "Medical_Examiner_Required",
                        "Evidence_Preservation", "Chain_of_Custody", "Timeline_Critical",
                        "Photos_Required", "Forensic_Lab_Required", "Court_Testimony_Required"],
        "forensic_specialists": ["Court_Experience", "Expert_Witness", "Autopsy_Qualified",
                                  "DNA_Analysis_Experience", "Sexual_Assault_Trained",
                                  "Child_Abuse_Trained", "Available_24Hr", "Insurance_Assessments"],
        "medical_master": ["CHAS_Coverage"],
    }

    for field in bool_fields_map.get(collection_name, []):
        if field in record and record[field] is not None:
            record[field] = _parse_bool(record[field])

    # CHAS_Coverage in medical_conditions is "Yes"/"No" string — keep as string
    # but add boolean version for easy querying
    if collection_name == "medical_conditions" and "CHAS_Coverage" in record:
        record["CHAS_Eligible"] = _parse_bool(record.get("CHAS_Coverage"))

    # Build GeoJSON point for chas_clinics
    if collection_name == "chas_clinics":
        try:
            lat = float(record.get("Latitude", 0) or 0)
            lng = float(record.get("Longitude", 0) or 0)
            if lat and lng:
                record["location"] = {"type": "Point", "coordinates": [lng, lat]}
        except (TypeError, ValueError):
            pass

    return record


async def ingest(data_dir: Path, mongo_uri: str, db_name: str, drop: bool) -> None:
    client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_uri)  # type: ignore[type-arg]
    db = client[db_name]

    for csv_filename, collection_name in CSV_COLLECTION_MAP.items():
        csv_path = data_dir / csv_filename
        if not csv_path.exists():
            logger.warning("CSV not found, skipping: %s", csv_path)
            continue

        logger.info("Processing %s → %s", csv_filename, collection_name)

        # Read CSV
        df = pd.read_csv(csv_path, dtype=str)
        df = df.where(pd.notnull(df), None)  # type: ignore[arg-type]
        records: list[dict] = df.to_dict(orient="records")  # type: ignore[assignment]

        # Add vertex_id for medical_conditions (row index as string)
        if collection_name == "medical_conditions":
            for i, rec in enumerate(records):
                rec["_vertex_id"] = str(i)

        # Apply transformations
        records = [_transform_record(collection_name, rec) for rec in records]

        collection = db[collection_name]

        if drop:
            await collection.drop()
            logger.info("  Dropped collection: %s", collection_name)

        # Insert
        if records:
            result = await collection.insert_many(records, ordered=False)
            logger.info("  Inserted %d documents", len(result.inserted_ids))

        # Create indexes
        for index_spec in INDEXES.get(collection_name, []):
            try:
                # Check if it's a text index (cannot combine with other text indexes easily)
                index_name = await collection.create_index(index_spec)
                logger.info("  Index created: %s", index_name)
            except Exception as e:
                logger.warning("  Index creation skipped (%s): %s", index_spec, e)

    client.close()
    logger.info("Ingestion complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest CSV data into MongoDB")
    parser.add_argument("--data-dir", default="../data", help="Path to data directory")
    parser.add_argument(
        "--mongo-uri",
        default=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        help="MongoDB connection URI",
    )
    parser.add_argument(
        "--db-name",
        default=os.getenv("MONGO_DB_NAME", "helpmedoctor"),
        help="MongoDB database name",
    )
    parser.add_argument("--drop", action="store_true", help="Drop collections before inserting")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    logger.info("Data directory: %s", data_dir)
    logger.info("MongoDB: %s / %s", args.mongo_uri, args.db_name)

    asyncio.run(ingest(data_dir, args.mongo_uri, args.db_name, args.drop))


if __name__ == "__main__":
    main()
