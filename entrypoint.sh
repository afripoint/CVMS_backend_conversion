#!/bin/sh

echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started!"

echo " Running Migrations..."
python manage.py migrate --noinput || echo "Migration issue ignored (already applied)"

echo " Collecting Static Files..."
python manage.py collectstatic --noinput

echo " Checking if superuser exists..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

try:
    if not User.objects.filter(email="${DJANGO_SUPERUSER_EMAIL}").exists():
        User.objects.create_superuser(
            email="${DJANGO_SUPERUSER_EMAIL}",
            password="${DJANGO_SUPERUSER_PASSWORD}",
            phone_number="1234567890"  # Ensure phone_number is set
        )
        print("Superuser created.")
    else:
        print("Superuser already exists. Skipping creation.")
except Exception as e:
    print(f"Error creating superuser: {e}")
EOF

echo " Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 180 api.wsgi:application
