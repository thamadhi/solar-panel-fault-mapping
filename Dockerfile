# ---- Solar PV Fault Localisation and Rectification System ----
# Multi-purpose image: the Flask API is the default entrypoint; the Streamlit
# dashboard is started by overriding the command in docker-compose.
#
# Build:  docker build -t pv-insight .
# Usage:  docker compose up

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# Create a non-root user to run the application.
RUN useradd --create-home --shell /usr/sbin/nologin appuser

# System libraries required by the opencv-python wheel (GUI/X11 backends).
# Kept in the image because the app imports cv2 (no GUI functions are used).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxi6 \
    libxrender1 \
    libxtst6 \
    libgdk-pixbuf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first so this layer is cached until requirements change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (secrets are never copied: .env is excluded via
# .dockerignore and must be provided through the environment at runtime).
COPY app.py Makefile pytest.ini pyproject.toml ./
COPY src ./src
COPY assets ./assets

# The SQLite database lives under /app/data; make it writable by the non-root
# user so init_db() can create it at startup.
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

# Flask API runs on 8000; the Streamlit dashboard on 8501.
EXPOSE 8000 8501

# Flask API (default). Streamlit overrides this command in docker-compose.
CMD ["python", "-m", "src.api"]