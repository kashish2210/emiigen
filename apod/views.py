# apod/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import APODImage, CelestialCoordinate, SystemLog
import requests
from django.conf import settings
from datetime import datetime, timedelta
import json

def home(request):
    """Display today's APOD with calendar data"""
    from datetime import date as date_class
    
    # Get image_id from query parameter if provided
    image_id = request.GET.get('image')
    
    if image_id:
        # If specific image requested, show that one
        try:
            apod = APODImage.objects.get(id=image_id)
        except APODImage.DoesNotExist:
            apod = None
    else:
        # Get the most recent APOD
        apod = None
        today = timezone.now().date()
        
        # Try today first
        apod = APODImage.objects.filter(date=today).first()
        
        # If not found, get most recent
        if not apod:
            apod = APODImage.objects.order_by('-date').first()
        
        # If still no APOD, try fetching today's or yesterday's
        if not apod:
            apod = fetch_and_save_apod(today)
            if not apod:
                yesterday = today - timedelta(days=1)
                apod = fetch_and_save_apod(yesterday)
    
    # If still no APOD, show error
    if not apod:
        context = {
            'error': 'Unable to fetch APOD data. Please use the terminal to fetch some data first.',
            'current_time': timezone.now().strftime('%H:%M:%S')
        }
        return render(request, 'apod/error.html', context)
    
    # Get all APOD images for the calendar
    apod_images = APODImage.objects.all().order_by('-date')
    
    context = {
        'apod': apod,
        'apod_images': apod_images,
        'current_time': timezone.now().strftime('%H:%M:%S')
    }
    
    SystemLog.objects.create(
        level='info',
        message=f'APOD home page accessed - {apod.title} ({apod.date})'
    )
    
    return render(request, 'apod/home.html', context)

def archive(request):
    """Display archive with calendar view"""
    apod_images = APODImage.objects.all().order_by('-date')
    
    # If no images, show setup message
    if not apod_images.exists():
        context = {
            'error': 'No APOD archive available. Please fetch data using management commands or the terminal.',
            'current_time': timezone.now().strftime('%H:%M:%S')
        }
        return render(request, 'apod/error.html', context)
    
    context = {
        'apod_images': apod_images,
        'has_more': APODImage.objects.count() > 30
    }
    
    return render(request, 'apod/archive.html', context)

def coordinates_view(request):
    """Display celestial coordinates"""
    coordinates = CelestialCoordinate.objects.all()
    
    context = {
        'coordinates': coordinates
    }
    
    return render(request, 'apod/coordinates.html', context)

def terminal_view(request):
    """Terminal interface view"""
    return render(request, 'apod/terminal.html', {
        'current_time': timezone.now().strftime('%H:%M:%S')
    })

@require_http_methods(["GET"])
def api_archive(request):
    """API endpoint for paginated archive"""
    page = request.GET.get('page', 1)
    images = APODImage.objects.all().order_by('-date')
    
    paginator = Paginator(images, 30)
    page_obj = paginator.get_page(page)
    
    data = {
        'images': [
            {
                'id': img.id,
                'title': img.title,
                'date': img.date.strftime('%b %d, %Y'),
                'url': img.url,
            }
            for img in page_obj
        ],
        'has_next': page_obj.has_next()
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_image_detail(request, image_id):
    """API endpoint for single image detail"""
    image = get_object_or_404(APODImage, id=image_id)
    
    data = {
        'id': image.id,
        'title': image.title,
        'date': image.date.strftime('%B %d, %Y'),
        'explanation': image.explanation,
        'url': image.url,
        'hdurl': image.hdurl,
        'copyright': image.copyright,
        'media_type': image.media_type
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_image_by_date(request):
    """API endpoint to get image by date"""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter required'}, status=400)
    
    try:
        from django.utils.dateparse import parse_date
        date = parse_date(date_str)
        image = APODImage.objects.filter(date=date).first()
        
        if image:
            return JsonResponse({
                'id': image.id,
                'title': image.title,
                'date': image.date.strftime('%Y-%m-%d')
            })
        else:
            return JsonResponse({'error': 'Image not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def api_coordinates(request):
    """API endpoint for coordinate search"""
    query = request.GET.get('q', '').lower()
    
    coordinates = CelestialCoordinate.objects.filter(
        name__icontains=query
    )[:10]
    
    data = {
        'results': [
            {
                'name': coord.name,
                'type': coord.type,
                'latitude': coord.latitude,
                'longitude': coord.longitude,
                'body': coord.body,
                'description': coord.description
            }
            for coord in coordinates
        ]
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_logs(request):
    """API endpoint for recent system logs"""
    logs = SystemLog.objects.all()[:10]
    
    data = {
        'logs': [
            {
                'timestamp': log.timestamp.strftime('%H:%M:%S'),
                'level': log.level,
                'message': log.message
            }
            for log in logs
        ]
    }
    
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["POST"])
def terminal_fetch(request):
    """Terminal API endpoint to fetch APOD"""
    try:
        data = json.loads(request.body)
        date_str = data.get('date', '')
        
        print(f"Terminal fetch called with date: {date_str}")
        
        if date_str.lower() == 'yesterday':
            date = timezone.now().date() - timedelta(days=1)
        else:
            from django.utils.dateparse import parse_date
            date = parse_date(date_str)
            if not date:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                })
        
        print(f"Fetching APOD for date: {date}")
        apod = fetch_and_save_apod(date)
        
        if apod:
            print(f"Successfully fetched: {apod.title}")
            return JsonResponse({
                'success': True,
                'message': 'Successfully fetched APOD',
                'title': apod.title,
                'date': apod.date.strftime('%Y-%m-%d')
            })
        else:
            print("Failed to fetch APOD")
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch APOD. Date might be in the future or API error.'
            })
    except Exception as e:
        print(f"Error in terminal_fetch: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def terminal_backfill(request):
    """Terminal API endpoint to backfill APOD"""
    try:
        data = json.loads(request.body)
        days = int(data.get('days', 7))
        
        today = timezone.now().date()
        results = []
        success_count = 0
        
        for i in range(days):
            date = today - timedelta(days=i+1)
            apod = fetch_and_save_apod(date)
            
            if apod:
                success_count += 1
                results.append({
                    'success': True,
                    'date': date.strftime('%Y-%m-%d'),
                    'title': apod.title
                })
            else:
                results.append({
                    'success': False,
                    'date': date.strftime('%Y-%m-%d'),
                    'error': 'Failed to fetch'
                })
        
        return JsonResponse({
            'success': True,
            'count': success_count,
            'total': days,
            'results': results
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["POST"])
def terminal_populate_coordinates(request):
    """Terminal API endpoint to populate coordinates"""
    try:
        coordinates_data = [
            {"name": "Tycho Crater", "type": "crater", "coordinates": [0.0, -43.3], "body": "Moon"},
            {"name": "Olympus Mons", "type": "mountain", "coordinates": [18.65, 133.8], "body": "Mars"},
            {"name": "Andromeda Galaxy", "type": "galaxy", "coordinates": [41.27, 121.17], "body": "Space"},
            {"name": "Gale Crater", "type": "crater", "coordinates": [-5.4, 137.8], "body": "Mars"},
            {"name": "Mare Tranquillitatis", "type": "other", "coordinates": [8.5, 31.4], "body": "Moon"},
            {"name": "Valles Marineris", "type": "other", "coordinates": [-14.0, -59.2], "body": "Mars"},
            {"name": "Orion Nebula", "type": "nebula", "coordinates": [-5.4, 83.8], "body": "Space"},
            {"name": "Crab Nebula", "type": "nebula", "coordinates": [22.0, 83.6], "body": "Space"},
            {"name": "Copernicus Crater", "type": "crater", "coordinates": [9.7, -20.1], "body": "Moon"},
            {"name": "Eagle Nebula", "type": "nebula", "coordinates": [-13.8, 275.0], "body": "Space"},
        ]
        
        created_count = 0
        for coord_data in coordinates_data:
            coord, created = CelestialCoordinate.objects.get_or_create(
                name=coord_data['name'],
                body=coord_data['body'],
                defaults={
                    'type': coord_data['type'],
                    'latitude': coord_data['coordinates'][0],
                    'longitude': coord_data['coordinates'][1],
                    'description': f"{coord_data['type'].title()} located on {coord_data['body']}"
                }
            )
            if created:
                created_count += 1
        
        return JsonResponse({
            'success': True,
            'count': created_count,
            'message': f'Created {created_count} new coordinates'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@require_http_methods(["GET"])
def terminal_status(request):
    """Terminal API endpoint to get status"""
    try:
        total_images = APODImage.objects.count()
        latest = APODImage.objects.order_by('-date').first()
        oldest = APODImage.objects.order_by('date').first()
        
        return JsonResponse({
            'success': True,
            'total_images': total_images,
            'latest_date': latest.date.strftime('%Y-%m-%d') if latest else None,
            'oldest_date': oldest.date.strftime('%Y-%m-%d') if oldest else None,
            'total_coordinates': CelestialCoordinate.objects.count(),
            'total_logs': SystemLog.objects.count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def fetch_and_save_apod(date):
    """Fetch APOD from NASA API and save to database"""
    try:
        url = settings.NASA_APOD_URL
        params = {
            'api_key': settings.NASA_API_KEY,
            'date': date.strftime('%Y-%m-%d'),
            'thumbs': True
        }
        
        print(f"Fetching APOD from: {url}")
        print(f"With params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"API Response: {data.get('title', 'No title')}")
        
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
        
        SystemLog.objects.create(
            level='success',
            message=f'Successfully fetched APOD for {date}',
            details={'title': data.get('title')}
        )
        
        print(f"Successfully saved APOD: {apod.title}")
        return apod
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        SystemLog.objects.create(
            level='error',
            message=f'Failed to fetch APOD for {date}',
            details={'error': str(e)}
        )
        return None
    except Exception as e:
        print(f"General error: {str(e)}")
        import traceback
        traceback.print_exc()
        SystemLog.objects.create(
            level='error',
            message=f'Error processing APOD data',
            details={'error': str(e)}
        )
        return None