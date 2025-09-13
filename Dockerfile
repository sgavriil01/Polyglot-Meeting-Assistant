# Multi-stage Docker build for Polyglot Meeting Assistant
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build the React app for production
RUN npm run build

# Stage 2: Setup Python backend (can be used standalone for development)
FROM python:3.11-slim AS python-backend

# Set working directory
WORKDIR /app

# Install system dependencies needed for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY backend/ ./backend/

# Create necessary directories with proper permissions
RUN mkdir -p \
    data/search_index \
    data/sessions \
    backend/uploads \
    && chmod -R 755 data backend/uploads

# Set environment variables
ENV PYTHONPATH=/app/backend/src
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Start the backend API server
CMD ["python", "backend/src/api.py"]

# Stage 3: Full application with frontend and backend
FROM python-backend AS full-app

# Copy built React frontend from stage 1
COPY --from=frontend-builder /app/frontend/build ./static/

# Create additional cache directories for AI models
RUN mkdir -p .cache/whisper .cache/huggingface && \
    chmod -R 755 .cache

# Create a simple startup script that serves static files and API
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Polyglot Meeting Assistant..."\n\
echo "📁 Frontend available at http://localhost:8000/static/"\n\
echo "🔧 API available at http://localhost:8000/api/v1/"\n\
echo "📚 API docs at http://localhost:8000/docs"\n\
cd /app\n\
python backend/src/api.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start the full application
CMD ["/app/start.sh"]
