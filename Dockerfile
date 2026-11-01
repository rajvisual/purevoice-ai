FROM python:3.12-slim

# Install system dependencies (FFmpeg for audio & video processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set up user for Hugging Face Spaces (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PORT=7860

WORKDIR $HOME/app

# Copy application files with ownership
COPY --chown=user . $HOME/app

# Ensure writable upload and output directories
RUN mkdir -p $HOME/app/uploads $HOME/app/outputs && \
    chmod -R 777 $HOME/app/uploads $HOME/app/outputs

# Expose Hugging Face default port
EXPOSE 7860

# Launch server
CMD ["python", "server.py", "7860"]
