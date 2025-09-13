# Docker build for development and local deployment
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Setup Python backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY backend/ ./backend/

# Copy built React frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create cache and data directories with proper permissions
RUN mkdir -p .cache/whisper .cache/huggingface data/search_index data/sessions && \
    chmod -R 777 .cache && \
    chmod -R 777 data

# Set environment variables
ENV PYTHONPATH=/app/backend/src
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start the backend API server
CMD ["python", "backend/src/api.py"]
