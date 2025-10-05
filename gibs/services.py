import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.conf import settings


class GIBSService:
    """Service to interact with NASA GIBS API"""
    
    GIBS_CAPABILITIES_URL = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml'
    GIBS_TILE_URL = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer}/default/{date}/{tilematrixset}/{z}/{y}/{x}.{format}'
    
    # Predefined layer categories from NASA Worldview
    LAYER_CATEGORIES = {
        'Corrected Reflectance': ['VIIRS_SNPP_CorrectedReflectance_TrueColor', 'MODIS_Terra_CorrectedReflectance_TrueColor', 
                                   'MODIS_Aqua_CorrectedReflectance_TrueColor', 'VIIRS_NOAA20_CorrectedReflectance_TrueColor'],
        'Fires': ['MODIS_Aqua_Thermal_Anomalies_All', 'MODIS_Terra_Thermal_Anomalies_All', 'VIIRS_SNPP_Thermal_Anomalies_375m_Day'],
        'Aerosols': ['MODIS_Combined_Value_Added_AOD', 'OMI_Aerosol_Index', 'MERRA2_Aerosol_Optical_Depth_550nm'],
        'Sea Ice': ['AMSR2_Sea_Ice_Concentration_12km', 'MODIS_Terra_Sea_Ice', 'VIIRS_SNPP_Sea_Ice'],
        'Snow Cover': ['MODIS_Terra_Snow_Cover', 'MODIS_Aqua_Snow_Cover', 'VIIRS_SNPP_DayNightBand_ENCC'],
        'Water Vapor': ['AIRS_L2_Water_Vapor_Volume_Mixing_Ratio', 'MODIS_Terra_Water_Vapor_5km'],
        'Land Surface': ['MODIS_Terra_Land_Surface_Temp_Day', 'MODIS_Aqua_Land_Surface_Temp_Day'],
        'Vegetation': ['MODIS_Terra_NDVI_8Day', 'VIIRS_SNPP_NDVI'],
        'Reference': ['BlueMarble_NextGeneration', 'BlueMarble_ShadedRelief_Bathymetry', 'Coastlines'],
    }
    
    @staticmethod
    def get_tile_url(layer_id, date, z, x, y, projection='EPSG:4326', format_type='jpg'):
        """Generate GIBS tile URL"""
        tilematrixset = '250m' if projection == 'EPSG:4326' else '31.25m'
        
        return f'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer_id}/default/{date}/{tilematrixset}/{z}/{y}/{x}.{format_type}'
    
    @staticmethod
    def fetch_capabilities():
        """Fetch and parse WMTS capabilities document"""
        try:
            response = requests.get(GIBSService.GIBS_CAPABILITIES_URL, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Define namespaces
            ns = {
                'wmts': 'http://www.opengis.net/wmts/1.0',
                'ows': 'http://www.opengis.net/ows/1.1',
                'gml': 'http://www.opengis.net/gml',
            }
            
            layers = []
            
            for layer_elem in root.findall('.//wmts:Layer', ns):
                identifier_elem = layer_elem.find('ows:Identifier', ns)
                title_elem = layer_elem.find('ows:Title', ns)
                abstract_elem = layer_elem.find('ows:Abstract', ns)
                
                if identifier_elem is not None and title_elem is not None:
                    layer_id = identifier_elem.text
                    
                    layer_data = {
                        'identifier': layer_id,
                        'title': title_elem.text,
                        'abstract': abstract_elem.text if abstract_elem is not None else '',
                    }
                    
                    # Get format
                    format_elem = layer_elem.find('.//wmts:Format', ns)
                    if format_elem is not None:
                        format_text = format_elem.text
                        layer_data['format'] = format_text.split('/')[-1] if '/' in format_text else format_text
                    else:
                        layer_data['format'] = 'jpg'
                    
                    # Get temporal dimension
                    dimension_elem = layer_elem.find('.//wmts:Dimension[@ows:Identifier="Time"]', ns)
                    if dimension_elem is not None:
                        default_elem = dimension_elem.find('wmts:Default', ns)
                        if default_elem is not None:
                            try:
                                layer_data['end_date'] = datetime.strptime(default_elem.text, '%Y-%m-%d').date()
                            except:
                                pass
                    
                    # Determine category
                    layer_data['category'] = GIBSService.get_layer_category(layer_id)
                    
                    layers.append(layer_data)
            
            print(f"Fetched {len(layers)} layers from GIBS WMTS")
            return layers
            
        except Exception as e:
            print(f"Error fetching GIBS capabilities: {e}")
            return []
    
    @staticmethod
    def get_layer_category(layer_id):
        """Determine category for a layer based on its ID"""
        for category, layer_ids in GIBSService.LAYER_CATEGORIES.items():
            for pattern in layer_ids:
                if pattern in layer_id:
                    return category
        
        # Categorize based on keywords in layer ID
        layer_lower = layer_id.lower()
        if 'reflectance' in layer_lower or 'corrected' in layer_lower:
            return 'Corrected Reflectance'
        elif 'fire' in layer_lower or 'thermal' in layer_lower or 'anomal' in layer_lower:
            return 'Fires'
        elif 'aerosol' in layer_lower or 'aod' in layer_lower:
            return 'Aerosols'
        elif 'ice' in layer_lower:
            return 'Sea Ice'
        elif 'snow' in layer_lower:
            return 'Snow Cover'
        elif 'vapor' in layer_lower or 'moisture' in layer_lower:
            return 'Water Vapor'
        elif 'temperature' in layer_lower or 'temp' in layer_lower:
            return 'Land Surface'
        elif 'ndvi' in layer_lower or 'vegetation' in layer_lower or 'biomass' in layer_lower:
            return 'Vegetation'
        elif 'cloud' in layer_lower:
            return 'Clouds'
        elif 'precipitation' in layer_lower or 'rain' in layer_lower:
            return 'Precipitation'
        elif 'blue' in layer_lower or 'marble' in layer_lower or 'coastline' in layer_lower:
            return 'Reference'
        else:
            return 'Other'
    
    @staticmethod
    def get_available_dates(layer_id, days_back=365):
        """Generate list of available dates (simplified version)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        dates = []
        current = start_date
        
        while current <= end_date:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return dates
    
    @staticmethod
    def build_wmts_url(layer_id, date, tile_matrix='EPSG4326_250m', 
                       tile_row=0, tile_col=0, tile_matrix_level=0, 
                       format_type='image/jpeg'):
        """Build WMTS GetTile request URL"""
        base_url = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi'
        
        params = {
            'SERVICE': 'WMTS',
            'REQUEST': 'GetTile',
            'VERSION': '1.0.0',
            'LAYER': layer_id,
            'STYLE': 'default',
            'TILEMATRIXSET': tile_matrix,
            'TILEMATRIX': tile_matrix_level,
            'TILEROW': tile_row,
            'TILECOL': tile_col,
            'FORMAT': format_type,
            'TIME': date,
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"