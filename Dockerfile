FROM python:3.12-slim

# Install system dependencies (FFmpeg is required for audio & video processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
COPY . /app

# Create upload and output directories
RUN mkdir -p /app/uploads /app/outputs

# Expose port 8000 (standard web port, can be overridden by $PORT)
EXPOSE 8000

# Start server
CMD ["python", "server.py", "8000"]
