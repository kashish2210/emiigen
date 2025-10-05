from django.core.management.base import BaseCommand
from gibs.models import WorldviewImageOfWeek
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seed sample Worldview Images of the Week for demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding sample images...'))
        
        # Sample image data based on actual NASA Worldview images
        sample_images = [
            {
                'title': 'Typhoon Ragasa',
                'description': 'Image captured by the VIIRS instrument aboard the joint NASA/NOAA NOAA-21 platform, showing Typhoon Ragasa over the Pacific Ocean.',
                'location': 'Pacific Ocean',
                'satellite': 'NOAA-21',
                'instrument': 'VIIRS',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-09-24&LAYERS=VIIRS_SNPP_CorrectedReflectance_TrueColor',
                'layers_used': ['VIIRS_SNPP_CorrectedReflectance_TrueColor'],
                'coordinates': {'lat': 15.0, 'lon': 140.0},
            },
            {
                'title': 'Smoke From Fires in Washington State and British Columbia',
                'description': 'Image captured by the VIIRS instrument showing smoke plumes from wildfires spreading across the Pacific Northwest.',
                'location': 'Washington State, USA',
                'satellite': 'Suomi NPP',
                'instrument': 'VIIRS',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-09-17&LAYERS=VIIRS_SNPP_CorrectedReflectance_TrueColor',
                'layers_used': ['VIIRS_SNPP_CorrectedReflectance_TrueColor', 'VIIRS_SNPP_Fires_375m_Day'],
                'coordinates': {'lat': 48.5, 'lon': -120.0},
            },
            {
                'title': 'Flooding in Pakistan',
                'description': 'Harmonized Landsat Sentinel-2 imagery showing extensive flooding across Pakistan\'s agricultural regions.',
                'location': 'Pakistan',
                'satellite': 'Landsat 8',
                'instrument': 'OLI',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-09-11&LAYERS=HLS_S30_Nadir_BRDF_Adjusted_Reflectance',
                'layers_used': ['HLS_S30_Nadir_BRDF_Adjusted_Reflectance'],
                'coordinates': {'lat': 28.0, 'lon': 70.0},
            },
            {
                'title': 'Dam Removal on the Klamath River, USA',
                'description': 'Harmonized Landsat Sentinel-2 image showing the landscape transformation after dam removal on the Klamath River.',
                'location': 'California, USA',
                'satellite': 'Landsat 8',
                'instrument': 'OLI',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-09-04&LAYERS=HLS_L30_Nadir_BRDF_Adjusted_Reflectance',
                'layers_used': ['HLS_L30_Nadir_BRDF_Adjusted_Reflectance'],
                'coordinates': {'lat': 42.0, 'lon': -122.5},
            },
            {
                'title': 'Phytoplankton Bloom in the Barents Sea',
                'description': 'MODIS Terra captured vibrant phytoplankton blooms swirling in the cold waters of the Barents Sea.',
                'location': 'Barents Sea',
                'satellite': 'Terra',
                'instrument': 'MODIS',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-08-28&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor',
                'layers_used': ['MODIS_Terra_CorrectedReflectance_TrueColor'],
                'coordinates': {'lat': 75.0, 'lon': 40.0},
            },
            {
                'title': 'Hurricane forming in Atlantic',
                'description': 'GOES-16 satellite imagery showing the development of a tropical cyclone in the Atlantic Ocean.',
                'location': 'Atlantic Ocean',
                'satellite': 'GOES-16',
                'instrument': 'ABI',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-08-21&LAYERS=VIIRS_NOAA20_CorrectedReflectance_TrueColor',
                'layers_used': ['VIIRS_NOAA20_CorrectedReflectance_TrueColor'],
                'coordinates': {'lat': 15.0, 'lon': -45.0},
            },
            {
                'title': 'Glacial Lakes in Patagonia',
                'description': 'Stunning turquoise glacial lakes visible in this Landsat image of Patagonia\'s Torres del Paine region.',
                'location': 'Patagonia, Chile',
                'satellite': 'Landsat 8',
                'instrument': 'OLI',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-08-14&LAYERS=HLS_L30_Nadir_BRDF_Adjusted_Reflectance',
                'layers_used': ['HLS_L30_Nadir_BRDF_Adjusted_Reflectance'],
                'coordinates': {'lat': -51.0, 'lon': -73.0},
            },
            {
                'title': 'Sand Dunes in Sahara Desert',
                'description': 'Spectacular patterns of sand dunes in the Sahara Desert captured by Landsat 8.',
                'location': 'Sahara Desert, Algeria',
                'satellite': 'Landsat 8',
                'instrument': 'OLI',
                'image_url': 'https://worldview.earthdata.nasa.gov/image-download?REQUEST=GetSnapshot&TIME=2025-08-07&LAYERS=HLS_L30_Nadir_BRDF_Adjusted_Reflectance',
                'layers_used': ['HLS_L30_Nadir_BRDF_Adjusted_Reflectance'],
                'coordinates': {'lat': 25.0, 'lon': 2.0},
            },
        ]
        
        created_count = 0
        base_date = datetime.now() - timedelta(days=60)
        
        for idx, image_data in enumerate(sample_images):
            # Spread images across different weeks
            published_date = base_date + timedelta(weeks=idx)
            capture_date = published_date - timedelta(days=random.randint(1, 3))
            
            image, created = WorldviewImageOfWeek.objects.get_or_create(
                title=image_data['title'],
                defaults={
                    'description': image_data['description'],
                    'image_url': image_data['image_url'],
                    'thumbnail_url': image_data['image_url'],
                    'published_date': published_date.date(),
                    'capture_date': capture_date.date(),
                    'location': image_data['location'],
                    'coordinates': image_data['coordinates'],
                    'layers_used': image_data['layers_used'],
                    'satellite': image_data['satellite'],
                    'instrument': image_data['instrument'],
                    'featured': idx < 3,  # Feature first 3 images
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created: {image.title}')
            else:
                self.stdout.write(f'Already exists: {image.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully seeded {created_count} new images'
            )
        )