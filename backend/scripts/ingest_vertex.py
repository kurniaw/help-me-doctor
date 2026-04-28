#!/usr/bin/env python3
"""Embed medical conditions and upload to Vertex AI Vector Search.

Usage:
    python scripts/ingest_vertex.py \
        --project your-project-id \
        --region asia-southeast1 \
        --bucket your-project-hmd-data \
        [--data-dir ../data]

Prerequisites:
    - GOOGLE_APPLICATION_CREDENTIALS set or gcloud auth application-default login
    - GCS bucket already created (by Terraform)
    - google-cloud-aiplatform installed
"""
import argparse
import json
import logging
import os
import tempfile
from pathlib import Path

import pandas as pd
from google.cloud import aiplatform, storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-004"
DIMENSIONS = 768
BATCH_SIZE = 50
INDEX_DISPLAY_NAME = "hmd-medical-conditions"
ENDPOINT_DISPLAY_NAME = "hmd-medical-endpoint"
DEPLOYED_INDEX_ID = "hmd-medical-deployed"


def _batch_embed(texts: list[str], project: str, region: str) -> list[list[float]]:
    """Embed texts in batches using Vertex AI text embeddings."""
    from vertexai.language_models import TextEmbeddingModel

    aiplatform.init(project=project, location=region)
    model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        logger.info("  Embedding batch %d/%d (%d texts)", i // BATCH_SIZE + 1,
                    (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE, len(batch))
        embeddings = model.get_embeddings(batch)
        all_embeddings.extend([e.values for e in embeddings])

    return all_embeddings


def _build_datapoints(
    df: pd.DataFrame, embeddings: list[list[float]]
) -> list[dict]:
    """Build Vertex AI datapoints from embeddings."""
    datapoints = []
    for i, (_, row) in enumerate(df.iterrows()):
        urgency = str(row.get("Urgency_Level", "MEDIUM"))
        triage = str(row.get("Triage_Color", "GREEN"))

        datapoints.append({
            "id": str(i),
            "embedding": embeddings[i],
            "restricts": [
                {"namespace": "urgency", "allow": [urgency]},
                {"namespace": "triage", "allow": [triage]},
            ],
        })
    return datapoints


def _upload_to_gcs(datapoints: list[dict], bucket_name: str) -> str:
    """Write datapoints as JSONL and upload to GCS. Returns gs:// URI."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for dp in datapoints:
            f.write(json.dumps(dp) + "\n")
        tmp_path = f.name

    blob_name = "embeddings/medical_conditions.jsonl"
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(tmp_path)
    os.unlink(tmp_path)

    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    logger.info("Uploaded embeddings to %s", gcs_uri)
    return gcs_uri


def _create_or_update_index(
    project: str, region: str, gcs_uri: str
) -> aiplatform.MatchingEngineIndex:
    """Create or update Vertex AI Matching Engine index."""
    aiplatform.init(project=project, location=region)

    # Check if index exists
    existing = aiplatform.MatchingEngineIndex.list(
        filter=f'display_name="{INDEX_DISPLAY_NAME}"'
    )

    if existing:
        index = existing[0]
        logger.info("Updating existing index: %s", index.resource_name)
        index.update_embeddings(contents_delta_uri=gcs_uri)
    else:
        logger.info("Creating new index: %s", INDEX_DISPLAY_NAME)
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=INDEX_DISPLAY_NAME,
            contents_delta_uri=gcs_uri,
            dimensions=DIMENSIONS,
            approximate_neighbors_count=10,
            distance_measure_type="DOT_PRODUCT_DISTANCE",
            leaf_node_embedding_count=500,
            leaf_nodes_to_search_percent=7,
            description="Medical conditions embeddings for Help Me Doctor",
        )
        logger.info("Index created: %s", index.resource_name)

    return index


def _deploy_index(
    project: str, region: str, index: aiplatform.MatchingEngineIndex
) -> aiplatform.MatchingEngineIndexEndpoint:
    """Deploy index to endpoint, creating endpoint if needed."""
    aiplatform.init(project=project, location=region)

    # Check if endpoint exists
    existing = aiplatform.MatchingEngineIndexEndpoint.list(
        filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"'
    )

    if existing:
        endpoint = existing[0]
        logger.info("Using existing endpoint: %s", endpoint.resource_name)
    else:
        logger.info("Creating endpoint: %s", ENDPOINT_DISPLAY_NAME)
        endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
            display_name=ENDPOINT_DISPLAY_NAME,
            public_endpoint_enabled=True,
        )

    # Check if already deployed
    deployed_ids = [di.id for di in endpoint.deployed_indexes]
    if DEPLOYED_INDEX_ID not in deployed_ids:
        logger.info("Deploying index to endpoint (this takes ~30 minutes)...")
        endpoint.deploy_index(
            index=index,
            deployed_index_id=DEPLOYED_INDEX_ID,
            display_name=DEPLOYED_INDEX_ID,
            min_replica_count=1,
            max_replica_count=1,
        )
        logger.info("Deployment complete.")
    else:
        logger.info("Index already deployed.")

    return endpoint


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest embeddings into Vertex AI Vector Search")
    parser.add_argument("--project", default=os.getenv("GCP_PROJECT_ID", ""), required=True)
    parser.add_argument("--region", default=os.getenv("GCP_REGION", "asia-southeast1"))
    parser.add_argument("--bucket", required=True, help="GCS bucket name (without gs://)")
    parser.add_argument("--data-dir", default="../data")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    csv_path = data_dir / "medical_condition_knowledge_base.csv"

    logger.info("Loading medical conditions from %s", csv_path)
    df = pd.read_csv(csv_path, dtype=str)
    df = df.where(pd.notnull(df), None)  # type: ignore[arg-type]

    # Build text representations for embedding
    texts = []
    for _, row in df.iterrows():
        condition = str(row.get("Condition", ""))
        symptoms = str(row.get("Symptoms", ""))
        specialty = str(row.get("Recommended_Specialty", ""))
        texts.append(f"{condition}: {symptoms}. Specialty: {specialty}")

    logger.info("Embedding %d medical conditions...", len(texts))
    embeddings = _batch_embed(texts, args.project, args.region)

    logger.info("Building datapoints...")
    datapoints = _build_datapoints(df, embeddings)

    logger.info("Uploading to GCS...")
    gcs_uri = _upload_to_gcs(datapoints, args.bucket)

    logger.info("Creating/updating Vertex AI index...")
    index = _create_or_update_index(args.project, args.region, gcs_uri)

    logger.info("Deploying index...")
    endpoint = _deploy_index(args.project, args.region, index)

    logger.info("\n✅ Done!")
    logger.info("Index ID:          %s", index.name)
    logger.info("Endpoint ID:       %s", endpoint.name)
    logger.info("Deployed Index ID: %s", DEPLOYED_INDEX_ID)
    logger.info(
        "\nAdd these to your .env / GCP Secrets:\n"
        "  VERTEX_INDEX_ID=%s\n"
        "  VERTEX_INDEX_ENDPOINT_ID=%s\n"
        "  VERTEX_DEPLOYED_INDEX_ID=%s",
        index.name,
        endpoint.name,
        DEPLOYED_INDEX_ID,
    )


if __name__ == "__main__":
    main()
