FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# ffmpeg is required for audio processing
# Install system dependencies
# ffmpeg is required for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models to bake them into the image
# This avoids downloading them on instance startup which saves time and bandwidth
# We download both 'base' and 'small' as per the app capabilities
RUN python -c "from faster_whisper import download_model; download_model('base'); download_model('small')"

# Copy application code
COPY . .

# Cloud Run injects the PORT environment variable
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Make the start script executable just in case
RUN chmod +x bin/start_server.sh

# Run the application using the custom start script
CMD ["./bin/start_server.sh"]
