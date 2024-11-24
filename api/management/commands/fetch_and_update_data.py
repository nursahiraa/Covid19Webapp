from django.core.management.base import BaseCommand
from api.utils import fetch_and_update_data

class Command(BaseCommand):
    help = 'Fetch and update COVID-19 data'

    def handle(self, *args, **kwargs):
        fetch_and_update_data()
        self.stdout.write("Data updated successfully.")
