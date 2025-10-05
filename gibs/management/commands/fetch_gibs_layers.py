from django.core.management.base import BaseCommand
from gibs.models import GIBSLayer
from gibs.services import GIBSService
import requests
from datetime import datetime


class Command(BaseCommand):
    help = 'Fetch and update GIBS layers from NASA GIBS API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all layers even if they exist',
        )

    def handle(self, *args, **options):
        force_update = options['force']
        
        self.stdout.write(self.style.SUCCESS('Fetching GIBS layers...'))
        
        # Fetch Worldview configuration for metadata
        try:
            worldview_config = GIBSService.get_worldview_config()
            layers_config = worldview_config.get('layers', {})
            
            self.stdout.write(f'Found {len(layers_config)} layers in Worldview config')
            
            created_count = 0
            updated_count = 0
            
            for layer_id, layer_data in layers_config.items():
                # Skip if layer already exists and not forcing update
                if not force_update and GIBSLayer.objects.filter(layer_id=layer_id).exists():
                    continue
                
                # Extract layer information
                title = layer_data.get('title', layer_id)
                subtitle = layer_data.get('subtitle', '')
                description = layer_data.get('description', '')
                
                # Get temporal range
                start_date = None
                end_date = None
                temporal_resolution = ''
                
                if 'startDate' in layer_data:
                    try:
                        start_date = datetime.strptime(
                            layer_data['startDate'], '%Y-%m-%dT%H:%M:%SZ'
                        ).date()
                    except (ValueError, TypeError):
                        pass
                
                if 'endDate' in layer_data:
                    try:
                        end_date = datetime.strptime(
                            layer_data['endDate'], '%Y-%m-%dT%H:%M:%SZ'
                        ).date()
                    except (ValueError, TypeError):
                        pass
                
                if 'period' in layer_data:
                    temporal_resolution = layer_data['period']
                
                # Get format and projection
                format_type = layer_data.get('format', 'image/jpeg').split('/')[-1]
                
                projections = layer_data.get('projections', {})
                projection = 'EPSG:4326' if 'geographic' in projections else 'EPSG:3857'
                
                # Get category
                category = ''
                if 'group' in layer_data:
                    category = layer_data['group']
                elif 'category' in layer_data:
                    category = layer_data['category']
                
                # Get tags
                tags = layer_data.get('tags', [])
                if isinstance(tags, str):
                    tags = [tags]
                
                # Get source
                source = layer_data.get('source', '')
                
                # Create or update layer
                layer, created = GIBSLayer.objects.update_or_create(
                    layer_id=layer_id,
                    defaults={
                        'title': title,
                        'subtitle': subtitle,
                        'description': description,
                        'format_type': format_type,
                        'projection': projection,
                        'start_date': start_date,
                        'end_date': end_date,
                        'temporal_resolution': temporal_resolution,
                        'category': category,
                        'tags': tags,
                        'source': source,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created layer: {title}')
                else:
                    updated_count += 1
                    self.stdout.write(f'Updated layer: {title}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully processed GIBS layers\n'
                    f'Created: {created_count}\n'
                    f'Updated: {updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching layers: {str(e)}')
            )