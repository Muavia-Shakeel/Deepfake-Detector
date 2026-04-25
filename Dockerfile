# Stage 1: Build stage
FROM python:3.10-slim-buster AS builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies into a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.10-slim-buster

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set path to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Download and cache models (this layer will be cached by Docker)
# We run the predictor loading part of the API startup logic here
RUN python -c "from src.utils.config_loader import load_config; from src.inference.predictor import Predictor; cfg = load_config(); Predictor(cfg)"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
