#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT:-prefab-fabric-479602-c5}"
REGION="${GCP_REGION:-us-central1}"
REPO="mlops-docker"
IMAGE="taxi-prediction-api"
TAG="${1:-latest}"

REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}:${TAG}"

echo "==> Building Docker image..."
docker build -f docker/serving/Dockerfile -t "${REGISTRY}" .

echo "==> Pushing to Artifact Registry..."
docker push "${REGISTRY}"

echo "==> Deploying to Cloud Run..."
gcloud run deploy taxi-prediction-api \
  --image="${REGISTRY}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080

echo "==> Deployment complete."
gcloud run services describe taxi-prediction-api \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format='value(status.url)'
