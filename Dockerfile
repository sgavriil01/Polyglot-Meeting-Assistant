FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Create necessary directories
RUN mkdir -p backend/uploads backend/data/search_index

# Set environment variables
ENV PYTHONPATH=/app/backend/src
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Command to run the API
CMD ["python", "-m", "uvicorn", "backend.src.api:app", "--host", "0.0.0.0", "--port", "8000"]
