from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
import json

from .models import GIBSLayer, WorldviewImageOfWeek, UserLayerConfig
from .services import GIBSService


def explorer_view(request):
    """Main GIBS Explorer view with interactive map"""
    context = {
        'page_title': 'GIBS Explorer',
        'default_date': timezone.now().date(),
    }
    return render(request, 'gibs/explorer.html', context)


def image_of_week_view(request):
    """Worldview Image of the Week archive with calendar view"""
    # Get year and month from query params or use current
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month
    
    # Get images for the selected month
    images = WorldviewImageOfWeek.objects.filter(
        published_date__year=year,
        published_date__month=month
    )
    
    # Get all available months with images
    available_dates = WorldviewImageOfWeek.objects.dates('published_date', 'month', order='DESC')
    
    context = {
        'page_title': 'Worldview Image of the Week',
        'images': images,
        'current_year': year,
        'current_month': month,
        'available_dates': available_dates,
        'next_month': (datetime(year, month, 1) + timedelta(days=32)).replace(day=1),
        'prev_month': (datetime(year, month, 1) - timedelta(days=1)).replace(day=1),
    }
    return render(request, 'gibs/image_of_week.html', context)


def image_detail_view(request, pk):
    """Detailed view of a specific Worldview Image"""
    image = get_object_or_404(WorldviewImageOfWeek, pk=pk)
    
    # Get related images (same month or similar location)
    related_images = WorldviewImageOfWeek.objects.filter(
        published_date__year=image.published_date.year,
        published_date__month=image.published_date.month
    ).exclude(pk=pk)[:6]
    
    context = {
        'page_title': image.title,
        'image': image,
        'related_images': related_images,
    }
    return render(request, 'gibs/image_detail.html', context)


def layers_catalog_view(request):
    """Browse available GIBS layers"""
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    layers = GIBSLayer.objects.all()
    
    if category:
        layers = layers.filter(category=category)
    
    if search:
        layers = layers.filter(
            models.Q(title__icontains=search) |
            models.Q(description__icontains=search)
        )
    
    # Get all unique categories
    categories = GIBSLayer.objects.values_list('category', flat=True).distinct()
    
    # Pagination
    paginator = Paginator(layers, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'GIBS Layers Catalog',
        'page_obj': page_obj,
        'categories': sorted(filter(None, categories)),
        'current_category': category,
        'search_query': search,
    }
    return render(request, 'gibs/layers_catalog.html', context)


@require_http_methods(["GET"])
def api_get_layer_info(request, layer_id):
    """API endpoint to get layer information"""
    try:
        layer = GIBSLayer.objects.get(layer_id=layer_id)
        data = {
            'id': layer.layer_id,
            'title': layer.title,
            'subtitle': layer.subtitle,
            'description': layer.description,
            'format': layer.format_type,
            'projection': layer.projection,
            'startDate': layer.start_date.isoformat() if layer.start_date else None,
            'endDate': layer.end_date.isoformat() if layer.end_date else None,
            'temporalResolution': layer.temporal_resolution,
            'category': layer.category,
            'tags': layer.tags,
        }
        return JsonResponse(data)
    except GIBSLayer.DoesNotExist:
        return JsonResponse({'error': 'Layer not found'}, status=404)


@require_http_methods(["GET"])
def api_search_layers(request):
    """API endpoint to search layers - returns ALL layers by default"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    limit = request.GET.get('limit', None)  # No default limit
    
    layers = GIBSLayer.objects.all().order_by('category', 'title')
    
    if query:
        layers = layers.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(layer_id__icontains=query)
        )
    
    if category and category != 'all':
        layers = layers.filter(category=category)
    
    total_count = layers.count()
    
    # Only apply limit if specified
    if limit:
        layers = layers[:int(limit)]
    
    data = [{
        'id': layer.layer_id,
        'title': layer.title,
        'category': layer.category or 'Other',
        'description': layer.description[:100] if layer.description else '',
        'format': layer.format_type or 'jpg',
        'startDate': layer.start_date.isoformat() if layer.start_date else None,
        'endDate': layer.end_date.isoformat() if layer.end_date else None,
    } for layer in layers]
    
    return JsonResponse({
        'layers': data, 
        'total': total_count,
        'returned': len(data)
    })


@require_http_methods(["POST"])
def api_save_config(request):
    """API endpoint to save user's layer configuration"""
    try:
        data = json.loads(request.body)
        session_id = request.session.session_key
        
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        config, created = UserLayerConfig.objects.get_or_create(
            session_id=session_id
        )
        
        config.active_layers = data.get('activeLayers', [])
        config.layer_opacity = data.get('layerOpacity', {})
        config.center_lat = data.get('centerLat', 0.0)
        config.center_lon = data.get('centerLon', 0.0)
        config.zoom_level = data.get('zoomLevel', 2)
        config.projection = data.get('projection', 'EPSG:4326')
        
        if 'currentDate' in data:
            config.current_date = datetime.fromisoformat(data['currentDate']).date()
        
        config.save()
        
        return JsonResponse({'status': 'success', 'message': 'Configuration saved'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["GET"])
def api_get_config(request):
    """API endpoint to retrieve user's saved configuration"""
    session_id = request.session.session_key
    
    if not session_id:
        return JsonResponse({'status': 'no_config'})
    
    try:
        config = UserLayerConfig.objects.get(session_id=session_id)
        data = {
            'activeLayers': config.active_layers,
            'layerOpacity': config.layer_opacity,
            'centerLat': config.center_lat,
            'centerLon': config.center_lon,
            'zoomLevel': config.zoom_level,
            'projection': config.projection,
            'currentDate': config.current_date.isoformat(),
        }
        return JsonResponse(data)
    except UserLayerConfig.DoesNotExist:
        return JsonResponse({'status': 'no_config'})