#!/bin/bash

# Load .env file if it exists
if [ -f .env ]; then
  # Use set -a to export all variables
  set -a
  source .env
  set +a
fi



# Default LLM Provider to openai if not set
LLM_PROVIDER=${LLM_PROVIDER:-openai}

echo "Starting server with LLM_PROVIDER=$LLM_PROVIDER"

if [ "$LLM_PROVIDER" = "ollama" ]; then
    echo "Using External Ollama Provider."
    # Local startup logic removed for separation
fi

# Start the main application
echo "Starting application on port ${PORT:-8080}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
