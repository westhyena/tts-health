#!/bin/bash

# Configuration
SERVICE_NAME="ollama-server"
REGION="asia-northeast3"

echo "Deploying $SERVICE_NAME to Cloud Run (Region: $REGION)..."

# Deploy Ollama Server with high specs (8GB RAM, 4 CPU)
gcloud run deploy "$SERVICE_NAME" \
    --source ./ollama_server \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 11434 \
    --memory 8Gi \
    --cpu 4 \
    --timeout 300
