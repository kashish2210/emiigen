from django.contrib import admin
from .models import GIBSLayer, WorldviewImageOfWeek, UserLayerConfig


@admin.register(GIBSLayer)
class GIBSLayerAdmin(admin.ModelAdmin):
    list_display = ['title', 'layer_id', 'category', 'format_type', 'projection', 'temporal_resolution', 'created_at']
    list_filter = ['category', 'format_type', 'projection', 'temporal_resolution']
    search_fields = ['title', 'layer_id', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('layer_id', 'title', 'subtitle', 'description')
        }),
        ('Layer Properties', {
            'fields': ('format_type', 'projection', 'wraparound')
        }),
        ('Temporal Properties', {
            'fields': ('start_date', 'end_date', 'temporal_resolution')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'source')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorldviewImageOfWeek)
class WorldviewImageOfWeekAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_date', 'location', 'satellite', 'featured', 'created_at']
    list_filter = ['published_date', 'featured', 'satellite']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'featured')
        }),
        ('Image Data', {
            'fields': ('image_url', 'thumbnail_url')
        }),
        ('Date Information', {
            'fields': ('published_date', 'capture_date')
        }),
        ('Location Data', {
            'fields': ('location', 'coordinates')
        }),
        ('Layer Information', {
            'fields': ('layers_used', 'satellite', 'instrument')
        }),
        ('Links', {
            'fields': ('permalink',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserLayerConfig)
class UserLayerConfigAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'center_lat', 'center_lon', 'zoom_level', 'projection', 'current_date', 'updated_at']
    list_filter = ['projection', 'current_date']
    search_fields = ['session_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Session', {
            'fields': ('session_id',)
        }),
        ('Layer Configuration', {
            'fields': ('active_layers', 'layer_opacity')
        }),
        ('View Configuration', {
            'fields': ('center_lat', 'center_lon', 'zoom_level', 'projection')
        }),
        ('Temporal Configuration', {
            'fields': ('current_date',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )