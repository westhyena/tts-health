#!/bin/bash

# Default values
SERVICE_NAME="stt-summary-api"
REGION="asia-northeast3" # Seoul region

echo "Deploying $SERVICE_NAME to Cloud Run (Region: $REGION)..."

# Build and Deploy directly using Google Cloud Build and Cloud Run
# This command builds the container image, builds it in Cloud Build, and deploys it.
# It requires the 'gcloud' CLI to be installed and configured.
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080

# Note:
# --source . : Uploads the source code and builds it using Cloud Build (requires Dockerfile)
# --allow-unauthenticated : Makes the service publicly accessible. Remove this if you want authentication.
