FROM python:3.10-slim-buster AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libdbus-1-dev \
    meson \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --no-deps --force-reinstall -r requirements.txt && \
    pip install gunicorn

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Copy the entire application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Final Stage
FROM python:3.10-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Create necessary directories in final stage
RUN mkdir -p /app/staticfiles /app/media

# Copy dependencies from the builder stage
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy static and media files from the builder stage
COPY --from=builder /app/staticfiles /app/staticfiles
COPY --from=builder /app/media /app/media

# Copy the rest of the application code
COPY --from=builder /app .

# Set permissions
RUN chown -R www-data:www-data /app/staticfiles /app/media

# Expose port and start the application
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "180", "api.wsgi:application"]