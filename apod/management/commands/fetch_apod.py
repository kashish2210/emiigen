# apod/management/commands/fetch_apod.py
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
import requests
from apod.models import APODImage
from django.conf import settings

class Command(BaseCommand):
    help = 'Fetch NASA APOD for a specific date'

    def add_arguments(self, parser):
        parser.add_argument(
            'date',
            type=str,
            nargs='?',
            default=None,
            help='Date in YYYY-MM-DD format (optional)'
        )
        parser.add_argument(
            '--backfill',
            type=int,
            default=0,
            help='Number of days to backfill from today'
        )

    def handle(self, *args, **options):
        if options['backfill'] > 0:
            # Backfill multiple days
            days = options['backfill']
            self.stdout.write(f'Backfilling {days} days of APOD images...')
            
            from django.utils import timezone
            today = timezone.now().date()
            success_count = 0
            
            for i in range(days):
                date = today - timedelta(days=i+1)
                if self.fetch_single_apod(date):
                    success_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'\nCompleted! Successfully fetched {success_count}/{days} images'
            ))
        
        elif options['date']:
            # Fetch specific date
            date = parse_date(options['date'])
            if not date:
                self.stderr.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
            self.fetch_single_apod(date)
        
        else:
            # Fetch today
            from django.utils import timezone
            today = timezone.now().date()
            # Try yesterday since today might not exist yet
            yesterday = today - timedelta(days=1)
            self.fetch_single_apod(yesterday)

    def fetch_single_apod(self, date):
        try:
            self.stdout.write(f'Fetching APOD for {date}...')
            
            response = requests.get(
                settings.NASA_APOD_URL,
                params={
                    'api_key': settings.NASA_API_KEY,
                    'date': date.strftime('%Y-%m-%d')
                },
                timeout=10
            )
            
            if response.status_code != 200:
                self.stderr.write(self.style.ERROR(f'API Error: {response.status_code}'))
                return False

            data = response.json()
            
            # Save to database
            apod, created = APODImage.objects.update_or_create(
                date=date,
                defaults={
                    'title': data.get('title', ''),
                    'explanation': data.get('explanation', ''),
                    'url': data.get('url', ''),
                    'hdurl': data.get('hdurl', ''),
                    'media_type': data.get('media_type', 'image'),
                    'copyright': data.get('copyright', ''),
                    'thumbnail_url': data.get('thumbnail_url', '')
                }
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ {"Created" if created else "Updated"}: {apod.title}'
            ))
            return True

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f'  ✗ Network error: {str(e)}'))
            return False
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
            return False