from django.db import models
from django.utils import timezone


class GIBSLayer(models.Model):
    """Store GIBS visualization layers"""
    layer_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    
    # Layer properties
    format_type = models.CharField(max_length=50)  # png, jpeg
    projection = models.CharField(max_length=100)  # EPSG:4326, EPSG:3857, etc.
    
    # Temporal properties
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    temporal_resolution = models.CharField(max_length=50, blank=True)  # daily, monthly, yearly
    
    # Categories
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Metadata
    source = models.CharField(max_length=255, blank=True)
    wraparound = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['layer_id']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title


class WorldviewImageOfWeek(models.Model):
    """Store Worldview Image of the Week entries"""
    title = models.CharField(max_length=500)
    description = models.TextField()
    
    # Image data
    image_url = models.URLField(max_length=1000)
    thumbnail_url = models.URLField(max_length=1000, blank=True)
    
    # Date information
    published_date = models.DateField()
    capture_date = models.DateField(null=True, blank=True)
    
    # Location data
    location = models.CharField(max_length=255, blank=True)
    coordinates = models.JSONField(null=True, blank=True)  # {"lat": x, "lon": y}
    
    # Layer information
    layers_used = models.JSONField(default=list, blank=True)
    satellite = models.CharField(max_length=255, blank=True)
    instrument = models.CharField(max_length=255, blank=True)
    
    # Metadata
    permalink = models.URLField(max_length=1000, blank=True)
    featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_date']
        verbose_name = "Worldview Image of the Week"
        verbose_name_plural = "Worldview Images of the Week"
        indexes = [
            models.Index(fields=['-published_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.published_date}"


class UserLayerConfig(models.Model):
    """Store user's custom layer configurations and preferences"""
    session_id = models.CharField(max_length=255, db_index=True)
    
    # Layer configuration
    active_layers = models.JSONField(default=list)
    layer_opacity = models.JSONField(default=dict)
    
    # View configuration
    center_lat = models.FloatField(default=0.0)
    center_lon = models.FloatField(default=0.0)
    zoom_level = models.IntegerField(default=2)
    projection = models.CharField(max_length=50, default='EPSG:4326')
    
    # Temporal configuration
    current_date = models.DateField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Config for {self.session_id}"