# apod/models.py
from django.db import models
from django.utils import timezone

class APODImage(models.Model):
    date = models.DateField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    explanation = models.TextField()
    url = models.URLField(max_length=500)
    hdurl = models.URLField(max_length=500, blank=True, null=True)
    media_type = models.CharField(max_length=20, default='image')
    copyright = models.CharField(max_length=255, blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'APOD Image'
        verbose_name_plural = 'APOD Images'
    
    def __str__(self):
        return f"{self.date} - {self.title}"

class CelestialCoordinate(models.Model):
    BODY_CHOICES = [
        ('Moon', 'Moon'),
        ('Mars', 'Mars'),
        ('Space', 'Space'),
        ('Earth', 'Earth'),
        ('Jupiter', 'Jupiter'),
        ('Saturn', 'Saturn'),
        ('Other', 'Other'),
    ]
    
    TYPE_CHOICES = [
        ('crater', 'Crater'),
        ('mountain', 'Mountain'),
        ('galaxy', 'Galaxy'),
        ('nebula', 'Nebula'),
        ('star', 'Star'),
        ('planet', 'Planet'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    body = models.CharField(max_length=50, choices=BODY_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    apod_image = models.ForeignKey(
        APODImage, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='coordinates'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'body']
    
    def __str__(self):
        return f"{self.name} ({self.body})"

class SystemLog(models.Model):
    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    message = models.TextField()
    details = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.level}: {self.message[:50]}"