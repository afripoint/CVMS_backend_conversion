#!/bin/sh

echo "Running Migrations..."
python manage.py migrate --noinput || echo "Migrations applied/ignored"

echo "Collecting Static Files..."
python manage.py collectstatic --noinput

echo "Creating Superuser..."
python manage.py create_superuser

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 180 api.wsgi:application