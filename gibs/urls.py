from django.urls import path
from . import views

app_name = 'gibs'

urlpatterns = [
    # Main views
    path('explore/', views.explorer_view, name='explorer'),
    path('image-of-week/', views.image_of_week_view, name='image_of_week'),
    path('image-of-week/<int:pk>/', views.image_detail_view, name='image_detail'),
    path('layers/', views.layers_catalog_view, name='layers_catalog'),
    
    # API endpoints
    path('api/layer/<str:layer_id>/', views.api_get_layer_info, name='api_layer_info'),
    path('api/search/', views.api_search_layers, name='api_search'),
    path('api/config/save/', views.api_save_config, name='api_save_config'),
    path('api/config/get/', views.api_get_config, name='api_get_config'),
]