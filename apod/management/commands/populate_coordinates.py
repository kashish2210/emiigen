from django.core.management.base import BaseCommand
from apod.models import CelestialCoordinate

class Command(BaseCommand):
    help = 'Populate celestial coordinates database'

    def handle(self, *args, **options):
        # Sample coordinate data
        coordinates = [
            {
                'name': 'Polaris',
                'type': 'star',
                'latitude': '89°15′50.8″',
                'longitude': '37°57′07″',
                'body': 'Star',
                'description': 'The North Star'
            },
            {
                'name': 'Pleiades',
                'type': 'cluster',
                'latitude': '24°07′',
                'longitude': '56°19′',
                'body': 'Star Cluster',
                'description': 'The Seven Sisters star cluster'
            },
            # Add more coordinates as needed
        ]

        for coord in coordinates:
            CelestialCoordinate.objects.get_or_create(
                name=coord['name'],
                defaults={
                    'type': coord['type'],
                    'latitude': coord['latitude'],
                    'longitude': coord['longitude'],
                    'body': coord['body'],
                    'description': coord['description']
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Added coordinate: {coord["name"]}'))