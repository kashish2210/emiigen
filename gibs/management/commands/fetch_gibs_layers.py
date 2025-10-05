from django.core.management.base import BaseCommand
from gibs.models import GIBSLayer
from gibs.services import GIBSService
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Fetch and update GIBS layers from NASA GIBS WMTS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all layers even if they exist',
        )

    def handle(self, *args, **options):
        force_update = options['force']
        
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Fetching GIBS layers from NASA WMTS capabilities...'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        try:
            # Fetch layers from GIBS WMTS capabilities
            layers_data = GIBSService.fetch_capabilities()
            
            if not layers_data or len(layers_data) == 0:
                self.stdout.write(self.style.WARNING('WMTS fetch returned 0 layers. Using default layer set...'))
                layers_data = self.get_comprehensive_layers()
            
            self.stdout.write(self.style.SUCCESS(f'\nFound {len(layers_data)} layers to process\n'))
            
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            for idx, layer_data in enumerate(layers_data, 1):
                layer_id = layer_data['identifier']
                
                # Skip if layer already exists and not forcing update
                if not force_update and GIBSLayer.objects.filter(layer_id=layer_id).exists():
                    skipped_count += 1
                    if skipped_count <= 5:  # Only show first 5 skipped
                        self.stdout.write(f'  [{idx}/{len(layers_data)}] Skipped: {layer_id}')
                    continue
                
                title = layer_data.get('title', layer_id)
                description = layer_data.get('abstract', '')
                format_type = layer_data.get('format', 'jpg')
                category = layer_data.get('category', 'Other')
                
                # Set date range
                end_date = layer_data.get('end_date', datetime(2025, 10, 1).date())
                start_date = layer_data.get('start_date', (datetime.now() - timedelta(days=365*5)).date())
                
                # Create or update layer
                layer, created = GIBSLayer.objects.update_or_create(
                    layer_id=layer_id,
                    defaults={
                        'title': title,
                        'subtitle': '',
                        'description': description,
                        'format_type': format_type,
                        'projection': 'EPSG:4326',
                        'start_date': start_date,
                        'end_date': end_date,
                        'temporal_resolution': 'daily',
                        'category': category,
                        'tags': [category.lower()],
                        'source': 'NASA GIBS',
                        'wraparound': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  [{idx}/{len(layers_data)}] ✓ Created: {title[:60]}'))
                else:
                    updated_count += 1
                    self.stdout.write(f'  [{idx}/{len(layers_data)}] ↻ Updated: {title[:60]}')
            
            if skipped_count > 5:
                self.stdout.write(f'  ... and {skipped_count - 5} more skipped')
            
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('SUMMARY'))
            self.stdout.write('='*60)
            self.stdout.write(self.style.SUCCESS(f'Created:  {created_count}'))
            self.stdout.write(self.style.SUCCESS(f'Updated:  {updated_count}'))
            self.stdout.write(self.style.WARNING(f'Skipped:  {skipped_count}'))
            self.stdout.write(self.style.SUCCESS(f'Total in DB: {GIBSLayer.objects.count()}'))
            self.stdout.write('='*60 + '\n')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n✗ Error fetching layers: {str(e)}\n')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def get_comprehensive_layers(self):
        """Return comprehensive set of popular GIBS layers"""
        return [
            # Corrected Reflectance - True Color
            {'identifier': 'VIIRS_SNPP_CorrectedReflectance_TrueColor', 'title': 'VIIRS SNPP Corrected Reflectance (True Color)', 
             'abstract': 'True-color corrected reflectance from VIIRS on Suomi NPP', 'format': 'jpg', 'category': 'Corrected Reflectance'},
            {'identifier': 'MODIS_Terra_CorrectedReflectance_TrueColor', 'title': 'MODIS Terra Corrected Reflectance (True Color)', 
             'abstract': 'True-color corrected reflectance from MODIS on Terra', 'format': 'jpg', 'category': 'Corrected Reflectance'},
            {'identifier': 'MODIS_Aqua_CorrectedReflectance_TrueColor', 'title': 'MODIS Aqua Corrected Reflectance (True Color)', 
             'abstract': 'True-color corrected reflectance from MODIS on Aqua', 'format': 'jpg', 'category': 'Corrected Reflectance'},
            {'identifier': 'VIIRS_NOAA20_CorrectedReflectance_TrueColor', 'title': 'VIIRS NOAA-20 Corrected Reflectance (True Color)', 
             'abstract': 'True-color corrected reflectance from VIIRS on NOAA-20', 'format': 'jpg', 'category': 'Corrected Reflectance'},
            
            # Corrected Reflectance - Bands
            {'identifier': 'MODIS_Terra_CorrectedReflectance_Bands367', 'title': 'MODIS Terra Corrected Reflectance (Bands 3-6-7)', 
             'abstract': 'False color composite for fire detection', 'format': 'jpg', 'category': 'Corrected Reflectance'},
            {'identifier': 'MODIS_Aqua_CorrectedReflectance_Bands721', 'title': 'MODIS Aqua Corrected Reflectance (Bands 7-2-1)', 
             'abstract': 'False color for land/water boundaries', 'format': 'jpg', 'category': 'Corrected Reflectance'},
            
            # Fires and Thermal Anomalies
            {'identifier': 'MODIS_Aqua_Thermal_Anomalies_All', 'title': 'Fires and Thermal Anomalies (MODIS Aqua, Day and Night)', 
             'abstract': 'Thermal anomalies and fires detected by MODIS on Aqua', 'format': 'png', 'category': 'Fires'},
            {'identifier': 'MODIS_Terra_Thermal_Anomalies_All', 'title': 'Fires and Thermal Anomalies (MODIS Terra, Day and Night)', 
             'abstract': 'Thermal anomalies and fires detected by MODIS on Terra', 'format': 'png', 'category': 'Fires'},
            {'identifier': 'VIIRS_SNPP_Thermal_Anomalies_375m_Day', 'title': 'Fires and Thermal Anomalies (VIIRS SNPP, 375m, Day)', 
             'abstract': 'High-resolution thermal anomalies from VIIRS', 'format': 'png', 'category': 'Fires'},
            {'identifier': 'VIIRS_NOAA20_Thermal_Anomalies_375m_Day', 'title': 'Fires and Thermal Anomalies (VIIRS NOAA-20, 375m, Day)', 
             'abstract': 'High-resolution thermal anomalies from VIIRS NOAA-20', 'format': 'png', 'category': 'Fires'},
            
            # Aerosols
            {'identifier': 'MODIS_Combined_Value_Added_AOD', 'title': 'Aerosol Optical Depth (MODIS Combined)', 
             'abstract': 'Combined aerosol optical depth from Terra and Aqua', 'format': 'png', 'category': 'Aerosols'},
            {'identifier': 'OMI_Aerosol_Index', 'title': 'Aerosol Index (OMI)', 
             'abstract': 'UV aerosol index from OMI', 'format': 'png', 'category': 'Aerosols'},
            
            # Sea Ice
            {'identifier': 'AMSR2_Sea_Ice_Concentration_12km', 'title': 'Sea Ice Concentration (AMSR2, 12km)', 
             'abstract': 'Sea ice concentration from AMSR2', 'format': 'png', 'category': 'Sea Ice'},
            {'identifier': 'MODIS_Terra_Sea_Ice', 'title': 'Sea Ice (MODIS Terra)', 
             'abstract': 'Sea ice extent from MODIS Terra', 'format': 'png', 'category': 'Sea Ice'},
            
            # Snow Cover
            {'identifier': 'MODIS_Terra_Snow_Cover', 'title': 'Snow Cover (MODIS Terra, NDSI)', 
             'abstract': 'Normalized Difference Snow Index from MODIS Terra', 'format': 'png', 'category': 'Snow Cover'},
            {'identifier': 'MODIS_Aqua_Snow_Cover', 'title': 'Snow Cover (MODIS Aqua, NDSI)', 
             'abstract': 'Normalized Difference Snow Index from MODIS Aqua', 'format': 'png', 'category': 'Snow Cover'},
            
            # Land Surface Temperature
            {'identifier': 'MODIS_Terra_Land_Surface_Temp_Day', 'title': 'Land Surface Temperature (MODIS Terra, Day)', 
             'abstract': 'Daytime land surface temperature from MODIS Terra', 'format': 'png', 'category': 'Land Surface'},
            {'identifier': 'MODIS_Aqua_Land_Surface_Temp_Day', 'title': 'Land Surface Temperature (MODIS Aqua, Day)', 
             'abstract': 'Daytime land surface temperature from MODIS Aqua', 'format': 'png', 'category': 'Land Surface'},
            
            # Vegetation
            {'identifier': 'MODIS_Terra_NDVI_8Day', 'title': 'Vegetation Index (MODIS Terra, NDVI, 8-Day)', 
             'abstract': 'Normalized Difference Vegetation Index', 'format': 'png', 'category': 'Vegetation'},
            {'identifier': 'VIIRS_SNPP_NDVI', 'title': 'Vegetation Index (VIIRS SNPP, NDVI)', 
             'abstract': 'Vegetation health from VIIRS', 'format': 'png', 'category': 'Vegetation'},
            
            # Water Vapor
            {'identifier': 'AIRS_L2_Water_Vapor_Volume_Mixing_Ratio', 'title': 'Water Vapor (AIRS)', 
             'abstract': 'Atmospheric water vapor from AIRS', 'format': 'png', 'category': 'Water Vapor'},
            {'identifier': 'MODIS_Terra_Water_Vapor_5km', 'title': 'Water Vapor (MODIS Terra, 5km)', 
             'abstract': 'Water vapor from MODIS Terra', 'format': 'png', 'category': 'Water Vapor'},
            
            # Clouds
            {'identifier': 'MODIS_Terra_Cloud_Fraction_Day', 'title': 'Cloud Fraction (MODIS Terra, Day)', 
             'abstract': 'Cloud cover fraction from MODIS Terra', 'format': 'png', 'category': 'Clouds'},
            {'identifier': 'MODIS_Terra_Cloud_Top_Temp_Day', 'title': 'Cloud Top Temperature (MODIS Terra, Day)', 
             'abstract': 'Cloud top temperature from MODIS Terra', 'format': 'png', 'category': 'Clouds'},
            
            # Reference Layers
            {'identifier': 'BlueMarble_NextGeneration', 'title': 'Blue Marble: Next Generation', 
             'abstract': 'A cloud-free view of Earth based on data from 2004', 'format': 'jpg', 'category': 'Reference'},
            {'identifier': 'BlueMarble_ShadedRelief_Bathymetry', 'title': 'Blue Marble: Shaded Relief and Bathymetry', 
             'abstract': 'Topography and ocean floor relief', 'format': 'jpg', 'category': 'Reference'},
            {'identifier': 'Coastlines', 'title': 'Coastlines', 
             'abstract': 'World coastline boundaries', 'format': 'png', 'category': 'Reference'},
        ]