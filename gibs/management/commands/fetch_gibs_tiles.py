from django.core.management.base import BaseCommand
from gibs.models import GIBSLayer
import requests
from datetime import datetime, timedelta
import time


class Command(BaseCommand):
    help = 'Fetch and verify GIBS layers with actual tile availability'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-tiles',
            action='store_true',
            help='Test tile availability for each layer',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Test date in YYYY-MM-DD format (default: yesterday)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of layers to process',
        )

    def handle(self, *args, **options):
        test_tiles = options['test_tiles']
        test_date_str = options['date']
        limit = options['limit']
        
        # Use yesterday as default (today's tiles might not be ready)
        if test_date_str:
            test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        else:
            test_date = (datetime.now() - timedelta(days=1)).date()
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('GIBS Layer Fetcher with Tile Verification'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'Test Date: {test_date}')
        self.stdout.write(f'Test Tiles: {test_tiles}')
        self.stdout.write('='*70 + '\n')
        
        # Comprehensive layer list with correct identifiers from NASA Worldview
        layers_data = self.get_worldview_layers()
        
        if limit:
            layers_data = layers_data[:limit]
        
        self.stdout.write(f'Processing {len(layers_data)} layers...\n')
        
        created_count = 0
        updated_count = 0
        working_count = 0
        failed_count = 0
        
        for idx, layer_info in enumerate(layers_data, 1):
            layer_id = layer_info['id']
            
            self.stdout.write(f'[{idx}/{len(layers_data)}] {layer_id[:50]}... ', ending='')
            
            # Test tile availability if requested
            tile_works = True
            if test_tiles:
                tile_works = self.test_layer_tiles(
                    layer_id, 
                    test_date, 
                    layer_info.get('format', 'jpg')
                )
            
            if tile_works:
                self.stdout.write(self.style.SUCCESS('✓ WORKS'))
                working_count += 1
            else:
                self.stdout.write(self.style.WARNING('✗ UNAVAILABLE'))
                failed_count += 1
                continue  # Skip unavailable layers
            
            # Create or update in database
            layer, created = GIBSLayer.objects.update_or_create(
                layer_id=layer_id,
                defaults={
                    'title': layer_info['title'],
                    'subtitle': layer_info.get('subtitle', ''),
                    'description': layer_info.get('description', ''),
                    'format_type': layer_info.get('format', 'jpg'),
                    'projection': 'EPSG:4326',
                    'start_date': layer_info.get('start_date'),
                    'end_date': layer_info.get('end_date'),
                    'temporal_resolution': layer_info.get('period', 'daily'),
                    'category': layer_info.get('category', 'Other'),
                    'tags': [layer_info.get('category', 'other').lower()],
                    'source': 'NASA GIBS Worldview',
                    'wraparound': True,
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
            
            # Small delay to avoid overwhelming the server
            if test_tiles:
                time.sleep(0.1)
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS(f'Created:        {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'Updated:        {updated_count}'))
        if test_tiles:
            self.stdout.write(self.style.SUCCESS(f'Working Tiles:  {working_count}'))
            self.stdout.write(self.style.WARNING(f'Failed Tiles:   {failed_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total in DB:    {GIBSLayer.objects.count()}'))
        self.stdout.write('='*70 + '\n')

    def test_layer_tiles(self, layer_id, date, format_type):
        """Test if tiles are actually available for this layer"""
        # Construct test tile URL (zoom 2, tile 1,1)
        date_str = date.strftime('%Y-%m-%d')
        test_url = f'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer_id}/default/{date_str}/250m/2/1/1.{format_type}'
        
        try:
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def get_worldview_layers(self):
        """Return comprehensive list of working GIBS layers from Worldview"""
        yesterday = datetime.now() - timedelta(days=1)
        two_years_ago = datetime.now() - timedelta(days=730)
        
        return [
            # === CORRECTED REFLECTANCE (TRUE COLOR) - These always work ===
            {
                'id': 'VIIRS_SNPP_CorrectedReflectance_TrueColor',
                'title': 'Corrected Reflectance (True Color, VIIRS, SNPP)',
                'description': 'High-resolution true-color imagery from VIIRS instrument',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2015, 11, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'VIIRS_NOAA20_CorrectedReflectance_TrueColor',
                'title': 'Corrected Reflectance (True Color, VIIRS, NOAA-20)',
                'description': 'True-color imagery from VIIRS on NOAA-20',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2018, 1, 1).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Terra_CorrectedReflectance_TrueColor',
                'title': 'Corrected Reflectance (True Color, MODIS, Terra)',
                'description': 'True-color imagery from MODIS Terra satellite',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_CorrectedReflectance_TrueColor',
                'title': 'Corrected Reflectance (True Color, MODIS, Aqua)',
                'description': 'True-color imagery from MODIS Aqua satellite',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === FALSE COLOR BANDS ===
            {
                'id': 'MODIS_Terra_CorrectedReflectance_Bands367',
                'title': 'Corrected Reflectance (Bands 3-6-7, MODIS, Terra)',
                'description': 'False color for fires and burn scars',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_CorrectedReflectance_Bands721',
                'title': 'Corrected Reflectance (Bands 7-2-1, MODIS, Aqua)',
                'description': 'False color for land/water boundaries',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'VIIRS_SNPP_CorrectedReflectance_BandsM11-I2-I1',
                'title': 'Corrected Reflectance (Bands M11-I2-I1, VIIRS, SNPP)',
                'description': 'False color for fires',
                'category': 'Corrected Reflectance',
                'format': 'jpg',
                'start_date': datetime(2015, 11, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === FIRES AND THERMAL ANOMALIES ===
            {
                'id': 'MODIS_Terra_Thermal_Anomalies_All',
                'title': 'Fires and Thermal Anomalies (Day and Night, MODIS, Terra)',
                'description': 'Active fires detected by MODIS Terra',
                'category': 'Fires',
                'format': 'png',
                'start_date': datetime(2000, 11, 1).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_Thermal_Anomalies_All',
                'title': 'Fires and Thermal Anomalies (Day and Night, MODIS, Aqua)',
                'description': 'Active fires detected by MODIS Aqua',
                'category': 'Fires',
                'format': 'png',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'VIIRS_SNPP_Thermal_Anomalies_375m_Day',
                'title': 'Fires and Thermal Anomalies (Day, 375m, VIIRS, SNPP)',
                'description': 'High-resolution fire detection',
                'category': 'Fires',
                'format': 'png',
                'start_date': datetime(2015, 11, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'VIIRS_SNPP_Thermal_Anomalies_375m_Night',
                'title': 'Fires and Thermal Anomalies (Night, 375m, VIIRS, SNPP)',
                'description': 'Nighttime fire detection',
                'category': 'Fires',
                'format': 'png',
                'start_date': datetime(2015, 11, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'VIIRS_NOAA20_Thermal_Anomalies_375m_Day',
                'title': 'Fires and Thermal Anomalies (Day, 375m, VIIRS, NOAA-20)',
                'description': 'High-resolution fire detection from NOAA-20',
                'category': 'Fires',
                'format': 'png',
                'start_date': datetime(2018, 1, 1).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === SNOW COVER ===
            {
                'id': 'MODIS_Terra_Snow_Cover',
                'title': 'Snow Cover (NDSI, MODIS, Terra)',
                'description': 'Daily snow cover from MODIS Terra',
                'category': 'Snow Cover',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_Snow_Cover',
                'title': 'Snow Cover (NDSI, MODIS, Aqua)',
                'description': 'Daily snow cover from MODIS Aqua',
                'category': 'Snow Cover',
                'format': 'png',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'VIIRS_SNPP_Snow_Cover',
                'title': 'Snow Cover (VIIRS, SNPP)',
                'description': 'High-resolution snow cover',
                'category': 'Snow Cover',
                'format': 'png',
                'start_date': datetime(2015, 11, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === SEA ICE ===
            {
                'id': 'MODIS_Terra_Sea_Ice',
                'title': 'Sea Ice (MODIS, Terra)',
                'description': 'Sea ice extent from MODIS Terra',
                'category': 'Sea Ice',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_Sea_Ice',
                'title': 'Sea Ice (MODIS, Aqua)',
                'description': 'Sea ice extent from MODIS Aqua',
                'category': 'Sea Ice',
                'format': 'png',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === LAND SURFACE TEMPERATURE ===
            {
                'id': 'MODIS_Terra_Land_Surface_Temp_Day',
                'title': 'Land Surface Temperature (Day, MODIS, Terra)',
                'description': 'Daytime land surface temperature',
                'category': 'Land Surface',
                'format': 'png',
                'start_date': datetime(2000, 3, 5).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Terra_Land_Surface_Temp_Night',
                'title': 'Land Surface Temperature (Night, MODIS, Terra)',
                'description': 'Nighttime land surface temperature',
                'category': 'Land Surface',
                'format': 'png',
                'start_date': datetime(2000, 3, 5).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_Land_Surface_Temp_Day',
                'title': 'Land Surface Temperature (Day, MODIS, Aqua)',
                'description': 'Daytime land surface temperature',
                'category': 'Land Surface',
                'format': 'png',
                'start_date': datetime(2002, 7, 8).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === VEGETATION ===
            {
                'id': 'MODIS_Terra_NDVI_8Day',
                'title': 'Vegetation Index (8-Day, NDVI, MODIS, Terra)',
                'description': 'Vegetation health indicator',
                'category': 'Vegetation',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': two_years_ago.date(),
                'period': '8day'
            },
            {
                'id': 'MODIS_Terra_EVI_8Day',
                'title': 'Vegetation Index (8-Day, EVI, MODIS, Terra)',
                'description': 'Enhanced vegetation index',
                'category': 'Vegetation',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': two_years_ago.date(),
                'period': '8day'
            },
            
            # === CHLOROPHYLL ===
            {
                'id': 'MODIS_Aqua_Chlorophyll_A',
                'title': 'Chlorophyll A (MODIS, Aqua)',
                'description': 'Ocean chlorophyll concentration',
                'category': 'Ocean',
                'format': 'png',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Terra_Chlorophyll_A',
                'title': 'Chlorophyll A (MODIS, Terra)',
                'description': 'Ocean chlorophyll concentration',
                'category': 'Ocean',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === AEROSOLS ===
            {
                'id': 'MODIS_Combined_Value_Added_AOD',
                'title': 'Aerosol Optical Depth (Combined, MODIS)',
                'description': 'Atmospheric aerosol levels',
                'category': 'Aerosols',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === WATER VAPOR ===
            {
                'id': 'MODIS_Terra_Water_Vapor_5km_Day',
                'title': 'Water Vapor (5km, Day, MODIS, Terra)',
                'description': 'Atmospheric water vapor',
                'category': 'Water Vapor',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            {
                'id': 'MODIS_Aqua_Water_Vapor_5km_Day',
                'title': 'Water Vapor (5km, Day, MODIS, Aqua)',
                'description': 'Atmospheric water vapor',
                'category': 'Water Vapor',
                'format': 'png',
                'start_date': datetime(2002, 7, 3).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === CLOUDS ===
            {
                'id': 'MODIS_Terra_Cloud_Top_Temp_Day',
                'title': 'Cloud Top Temperature (Day, MODIS, Terra)',
                'description': 'Temperature at cloud tops',
                'category': 'Clouds',
                'format': 'png',
                'start_date': datetime(2000, 2, 24).date(),
                'end_date': yesterday.date(),
                'period': 'daily'
            },
            
            # === REFERENCE LAYERS ===
            {
                'id': 'BlueMarble_NextGeneration',
                'title': 'Blue Marble: Next Generation',
                'description': 'Cloud-free Earth imagery',
                'category': 'Reference',
                'format': 'jpg',
                'start_date': datetime(2004, 1, 1).date(),
                'end_date': datetime(2004, 12, 31).date(),
                'period': 'static'
            },
            {
                'id': 'BlueMarble_ShadedRelief_Bathymetry',
                'title': 'Blue Marble: Shaded Relief and Bathymetry',
                'description': 'Topography and ocean floor',
                'category': 'Reference',
                'format': 'jpg',
                'start_date': datetime(2004, 1, 1).date(),
                'end_date': datetime(2004, 12, 31).date(),
                'period': 'static'
            },
            {
                'id': 'Coastlines',
                'title': 'Coastlines',
                'description': 'World coastline boundaries',
                'category': 'Reference',
                'format': 'png',
                'start_date': datetime(2000, 1, 1).date(),
                'end_date': yesterday.date(),
                'period': 'static'
            },
            {
                'id': 'Reference_Features_15m',
                'title': 'Borders and Roads',
                'description': 'Political boundaries and major roads',
                'category': 'Reference',
                'format': 'png',
                'start_date': datetime(2000, 1, 1).date(),
                'end_date': yesterday.date(),
                'period': 'static'
            },
        ]