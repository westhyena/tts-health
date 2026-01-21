FROM ubuntu:22.04

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Bake Llama 3.1 model into the image
# Start server, pull model, then stop server
RUN ollama serve & \
    sleep 5 && \
    ollama pull llama3.1 && \
    pkill ollama

# Environment variables
ENV OLLAMA_HOST=0.0.0.0

# Expose Ollama port
EXPOSE 11434

# Start Ollama
CMD ["ollama", "serve"]
