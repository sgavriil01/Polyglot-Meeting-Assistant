FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create cache and data directories with proper permissions
RUN mkdir -p .cache/whisper .cache/huggingface data/search_index data/sessions && \
    chmod -R 777 .cache && \
    chmod -R 777 data

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=7860
ENV XDG_CACHE_HOME=/app/.cache
ENV WHISPER_CACHE_DIR=/app/.cache
ENV TRANSFORMERS_CACHE=/app/.cache
ENV HF_HOME=/app/.cache

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
