from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Create superuser for Render if not exists'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_NAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'password123')
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser {username} already exists'))
