# Use python 3.10 as requested
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate model if not present (Crucial step added)
RUN python train_model.py

# Expose port
EXPOSE 8000

# Run API
# Run API with dynamic port for Render
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
