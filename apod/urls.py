# apod/urls.py
from django.urls import path
from . import views

app_name = 'apod'

urlpatterns = [
    # Main views
    path('', views.home, name='home'),
    path('archive/', views.archive, name='archive'),
    path('coordinates/', views.coordinates_view, name='coordinates'),
    path('terminal/', views.terminal_view, name='terminal'),
    
    # API endpoints for general data
    path('api/archive/', views.api_archive, name='api_archive'),
    path('api/image/<int:image_id>/', views.api_image_detail, name='api_image_detail'),
    path('api/image-by-date/', views.api_image_by_date, name='api_image_by_date'),
    path('api/coordinates/', views.api_coordinates, name='api_coordinates'),
    path('api/logs/', views.api_logs, name='api_logs'),
    
    # Terminal API endpoints
    path('api/terminal/fetch/', views.terminal_fetch, name='terminal_fetch'),
    path('api/terminal/backfill/', views.terminal_backfill, name='terminal_backfill'),
    path('api/terminal/populate-coordinates/', views.terminal_populate_coordinates, name='terminal_populate_coordinates'),
    path('api/terminal/status/', views.terminal_status, name='terminal_status'),
]