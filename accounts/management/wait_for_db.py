import os
import time
from django.core.management.base import BaseCommand
import psycopg2

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        while True:
            try:
                conn = psycopg2.connect(
                    dbname=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD'),
                    host=os.getenv('DB_HOST'),
                    port=os.getenv('DB_PORT'),
                    connect_timeout=5
                )
                conn.close()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except psycopg2.OperationalError as e:
                self.stdout.write(f'Database unavailable: {e}, retrying...')
                time.sleep(3)