from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
import time
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = "Create a superuser if one does not exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Wait for the database to be ready (helps with Docker)
        retries = 5
        while retries > 0:
            try:
                if User.objects.exists():  # Check if DB is ready
                    break
            except OperationalError:
                self.stdout.write(self.style.WARNING("Waiting for database to be ready..."))
                time.sleep(5)  # Wait 5 seconds before retrying
                retries -= 1
        else:
            self.stdout.write(self.style.ERROR("Database not available. Skipping superuser creation."))
            return

        # Get environment variables
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        # Ensure essential environment variables are set
        if not email or not password:
            self.stdout.write(self.style.ERROR("DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD must be set."))
            return

        # Check if superuser exists
        if not User.objects.filter(is_superuser=True).exists():
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create superuser: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser already exists."))
