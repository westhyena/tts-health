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
    # Start Ollama in the background
    echo "Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!

    # Wait for Ollama to start
    echo "Waiting for Ollama to become available..."
    until ollama list > /dev/null 2>&1; do
        echo "Waiting for Ollama..."
        sleep 1
    done

    echo "Ollama is ready."

    # Check/Pull model if needed (optional check)
    echo "Checking available models..."
    ollama list
fi

# Start the main application
echo "Starting application on port ${PORT:-8080}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
