# my_app/management/commands/welcome.py

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'Displays a welcome message if the database connection is available'

    def handle(self, *args, **kwargs):
        db_conn = connections['default']
        try:
            db_conn.cursor()
            self.stdout.write(self.style.SUCCESS('Database connection available!'))
            self.stdout.write(self.style.SUCCESS('Welcome to my website Dashboard'))
        except OperationalError:
            self.stdout.write(self.style.ERROR('Database connection unavailable!'))

