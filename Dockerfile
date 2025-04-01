# ==============================
# Stage 1: Builder
# ==============================
FROM python:3.10-alpine AS builder
 
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
 
WORKDIR /app
 
# Install system dependencies required for PostgreSQL and Pillow
RUN apk add --no-cache \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    libffi-dev \
    musl-dev \
    py3-psycopg2 \
    gettext
 
# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn
 
# Copy all necessary application files (app directories and manage.py)
COPY . /app/
 
# Create staticfiles directory and set permissions
RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles
 
# Run collectstatic
RUN python manage.py collectstatic --noinput
 
# ==============================
# Stage 2: Final Runtime Image
# ==============================
FROM python:3.10-alpine
 
# Install runtime dependencies
RUN apk add --no-cache postgresql-client
 
# Create a non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
 
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
 
WORKDIR /app
 
# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin/python3 /usr/local/bin/python3
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
 
# Copy all the files from the builder stage (including apps, manage.py, etc.)
COPY --from=builder /app /app
 
# Copy static files from builder stage
COPY --from=builder /app/staticfiles /app/staticfiles
 
# Copy entrypoint script *before* switching user
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
 
# Set proper ownership and permissions
RUN chown -R appuser:appgroup /app /entrypoint.sh /app/staticfiles
 
# Switch to non-root user
USER appuser  
 
# Expose port
EXPOSE 8000 
# Define entrypoint
ENTRYPOINT ["/entrypoint.sh"]
