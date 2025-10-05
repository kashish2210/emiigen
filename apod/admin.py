# apod/admin.py
from django.contrib import admin
from .models import APODImage, CelestialCoordinate, SystemLog

@admin.register(APODImage)
class APODImageAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'media_type', 'copyright', 'created_at')
    list_filter = ('media_type', 'date', 'created_at')
    search_fields = ('title', 'explanation', 'copyright')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('date', 'title', 'media_type')
        }),
        ('Content', {
            'fields': ('explanation', 'url', 'hdurl', 'thumbnail_url')
        }),
        ('Attribution', {
            'fields': ('copyright',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CelestialCoordinate)
class CelestialCoordinateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'body', 'latitude', 'longitude', 'apod_image')
    list_filter = ('type', 'body')
    search_fields = ('name', 'description')
    autocomplete_fields = ['apod_image']
    
    fieldsets = (
        ('Object Information', {
            'fields': ('name', 'type', 'body')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Details', {
            'fields': ('description', 'apod_image')
        }),
    )

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'level', 'message_preview', 'has_details')
    list_filter = ('level', 'timestamp')
    search_fields = ('message',)
    readonly_fields = ('timestamp', 'level', 'message', 'details')
    date_hierarchy = 'timestamp'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
    
    def has_details(self, obj):
        return bool(obj.details)
    has_details.boolean = True
    has_details.short_description = 'Has Details'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    actions = ['delete_selected']