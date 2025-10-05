# apod/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .models import APODImage, SystemLog
from .views import fetch_and_save_apod
import requests
from django.conf import settings

@shared_task
def fetch_latest_apod():
    """
    Fetch the latest APOD from NASA API
    Runs every night to get new image
    """
    today = timezone.now().date()
    
    existing = APODImage.objects.filter(date=today).first()
    if existing:
        SystemLog.objects.create(
            level='info',
            message=f'APOD for {today} already exists'
        )
        return
    
    apod = fetch_and_save_apod(today)
    
    if apod:
        SystemLog.objects.create(
            level='success',
            message=f'Successfully fetched latest APOD: {apod.title}'
        )
    else:
        SystemLog.objects.create(
            level='error',
            message=f'Failed to fetch APOD for {today}'
        )

@shared_task
def check_nasa_api_update():
    """
    Check if NASA has updated APOD
    Runs every 5 minutes during update window
    """
    try:
        url = settings.NASA_APOD_URL
        params = {
            'api_key': settings.NASA_API_KEY,
            'thumbs': True
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        existing = APODImage.objects.filter(date=date).first()
        
        if not existing:
            apod = APODImage.objects.create(
                date=date,
                title=data.get('title', ''),
                explanation=data.get('explanation', ''),
                url=data.get('url', ''),
                hdurl=data.get('hdurl', ''),
                media_type=data.get('media_type', 'image'),
                copyright=data.get('copyright', ''),
                thumbnail_url=data.get('thumbnail_url', '')
            )
            
            SystemLog.objects.create(
                level='success',
                message=f'New APOD detected and saved: {apod.title}'
            )
        elif existing.updated_at < timezone.now() - timedelta(hours=1):
            existing.title = data.get('title', existing.title)
            existing.explanation = data.get('explanation', existing.explanation)
            existing.url = data.get('url', existing.url)
            existing.hdurl = data.get('hdurl', existing.hdurl)
            existing.save()
            
            SystemLog.objects.create(
                level='info',
                message=f'Updated existing APOD: {existing.title}'
            )
            
    except Exception as e:
        SystemLog.objects.create(
            level='warning',
            message=f'APOD check failed: {str(e)}'
        )

@shared_task
def backfill_apod_archive(days=30):
    """
    Backfill APOD archive with historical images
    """
    today = timezone.now().date()
    
    for i in range(days):
        date = today - timedelta(days=i)
        
        if not APODImage.objects.filter(date=date).exists():
            fetch_and_save_apod(date)
    
    SystemLog.objects.create(
        level='success',
        message=f'Completed backfill of {days} days'
    )

@shared_task
def cleanup_old_logs():
    """
    Clean up system logs older than 7 days
    """
    cutoff = timezone.now() - timedelta(days=7)
    deleted_count = SystemLog.objects.filter(timestamp__lt=cutoff).delete()[0]
    
    SystemLog.objects.create(
        level='info',
        message=f'Cleaned up {deleted_count} old log entries'
    )


# celery.py (in your project config folder)
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('apod_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'fetch-latest-apod-midnight': {
        'task': 'apod.tasks.fetch_latest_apod',
        'schedule': crontab(hour=0, minute=5),  # Run at 00:05 every day
    },
    'check-nasa-update-every-5-min': {
        'task': 'apod.tasks.check_nasa_api_update',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-logs-weekly': {
        'task': 'apod.tasks.cleanup_old_logs',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday at 2 AM
    },
}