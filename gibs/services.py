import requests
from datetime import datetime, timedelta
from django.conf import settings
import xml.etree.ElementTree as ET


class GIBSService:
    """Service to interact with NASA GIBS API"""
    
    GIBS_CAPABILITIES_URL = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml'
    GIBS_TILE_URL = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer}/default/{date}/{tilematrixset}/{z}/{y}/{x}.{format}'
    
    WORLDVIEW_API = 'https://worldview.earthdata.nasa.gov/config/wv.json'
    
    @staticmethod
    def get_tile_url(layer_id, date, z, x, y, projection='EPSG:4326', format_type='jpg'):
        """
        Generate GIBS tile URL
        
        Args:
            layer_id: Layer identifier
            date: Date string in format YYYY-MM-DD
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            projection: Map projection (default: EPSG:4326)
            format_type: Image format (jpg or png)
        
        Returns:
            Complete tile URL
        """
        tilematrixset = '250m' if projection == 'EPSG:4326' else '31.25m'
        
        return GIBSService.GIBS_TILE_URL.format(
            layer=layer_id,
            date=date,
            tilematrixset=tilematrixset,
            z=z,
            y=y,
            x=x,
            format=format_type
        )
    
    @staticmethod
    def fetch_capabilities():
        """
        Fetch and parse WMTS capabilities document
        
        Returns:
            Dictionary of available layers
        """
        try:
            response = requests.get(GIBSService.GIBS_CAPABILITIES_URL, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            # Parse XML namespace
            ns = {
                'wmts': 'http://www.opengis.net/wmts/1.0',
                'ows': 'http://www.opengis.net/ows/1.1',
            }
            
            layers = []
            
            for layer_elem in root.findall('.//wmts:Layer', ns):
                identifier = layer_elem.find('ows:Identifier', ns)
                title = layer_elem.find('ows:Title', ns)
                
                if identifier is not None and title is not None:
                    layer_data = {
                        'identifier': identifier.text,
                        'title': title.text,
                    }
                    
                    # Get format
                    format_elem = layer_elem.find('.//wmts:Format', ns)
                    if format_elem is not None:
                        layer_data['format'] = format_elem.text
                    
                    layers.append(layer_data)
            
            return layers
            
        except Exception as e:
            print(f"Error fetching GIBS capabilities: {e}")
            return []
    
    @staticmethod
    def get_worldview_config():
        """
        Fetch Worldview configuration for layers metadata
        
        Returns:
            Dictionary with layer configurations
        """
        try:
            response = requests.get(GIBSService.WORLDVIEW_API, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Worldview config: {e}")
            return {}
    
    @staticmethod
    def get_available_dates(layer_id, start_date=None, end_date=None):
        """
        Get available dates for a specific layer
        
        Args:
            layer_id: Layer identifier
            start_date: Start date (datetime object)
            end_date: End date (datetime object)
        
        Returns:
            List of available dates
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
        
        # This is a simplified version
        # In production, you'd query the GIBS API for actual available dates
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
        """
        Build WMTS GetTile request URL
        
        Args:
            layer_id: Layer identifier
            date: Date in YYYY-MM-DD format
            tile_matrix: Tile matrix set
            tile_row: Tile row
            tile_col: Tile column
            tile_matrix_level: Zoom level
            format_type: Image format
        
        Returns:
            WMTS GetTile URL
        """
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