# Stage 1: Builder
FROM python:3.10-alpine AS builder

# Accept build arguments
ARG EMAIL_HOST_USER
ARG EMAIL_HOST_PASSWORD
ARG DEFAULT_FROM_EMAIL
ARG DJANGO_SETTINGS_MODULE

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EMAIL_HOST_USER=${EMAIL_HOST_USER} \
    EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD} \
    DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL} \
    DJANGO_SETTINGS_MODULE=api.settings

WORKDIR /app

# Install system dependencies and build tools
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    postgresql-dev \
    musl-dev \
    curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy the entire application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Final Image
FROM python:3.10-alpine

# Create a non-root user for better security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EMAIL_HOST_USER=${EMAIL_HOST_USER} \
    EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD} \
    DEFAULT_FROM_EMAIL=${DEFAULT_FROM_EMAIL} \
    DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

WORKDIR /app

# Copy dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin/python3 /usr/local/bin/python3
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy static and media files from the builder stage
COPY --from=builder /app/staticfiles /app/staticfiles
COPY --from=builder /app/media /app/media

# Copy the rest of the application code
COPY --from=builder /app .

# Set proper ownership and permissions
RUN chown -R appuser:appgroup /app
USER appuser  # Run container as non-root user

# Expose port and start the application
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "180", "api.wsgi:application"]
