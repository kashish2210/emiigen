# NASA GIBS Explorer App

This Django app integrates NASA's Global Imagery Browse Services (GIBS) to provide an interactive platform for exploring satellite imagery.

## Features

- **Interactive Map Viewer**: Explore NASA satellite imagery with zoom and pan capabilities
- **Multiple Layers**: Access over 1,000 visualization products from various satellites
- **Date Selection**: View imagery from different dates
- **Worldview Image of the Week**: Browse weekly featured satellite images in calendar format
- **Layer Catalog**: Search and filter available GIBS layers
- **User Configurations**: Save and restore your viewing preferences

## Installation

### 1. Add to INSTALLED_APPS

In your `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'gibs',
]
```

### 2. Include URLs

In your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('gibs/', include('gibs.urls')),
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations gibs
python manage.py migrate
```

### 4. Create Directory Structure

Create the following directory structure:

```
gibs/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── services.py
├── urls.py
├── views.py
├── templates/
│   └── gibs/
│       ├── explorer.html
│       ├── image_of_week.html
│       └── image_detail.html
└── management/
    └── commands/
        └── fetch_gibs_layers.py
```

### 5. Fetch GIBS Layers

Run the management command to populate the database with available GIBS layers:

```bash
python manage.py fetch_gibs_layers
```

To force update existing layers:

```bash
python manage.py fetch_gibs_layers --force
```

## Usage

### Main Explorer View

Access the main GIBS explorer at `/gibs/`

Features:
- Interactive map with NASA satellite imagery
- Date picker to select imagery date
- Layer selection panel
- Coordinate display
- Save/load configurations

### Image of the Week

Access the weekly image archive at `/gibs/image-of-week/`

Features:
- Calendar navigation by month/year
- Grid view of featured images
- Click to view full details

### API Endpoints

- `GET /gibs/api/layer/<layer_id>/` - Get layer information
- `GET /gibs/api/search/?q=<query>` - Search layers
- `POST /gibs/api/config/save/` - Save user configuration
- `GET /gibs/api/config/get/` - Retrieve saved configuration

## Terminal Integration

The app logs activities to the footer terminal:

```javascript
logToTerminal('info', 'Layer loaded successfully');
logToTerminal('success', 'Configuration saved');
logToTerminal('warning', 'No data available for this date');
logToTerminal('error', 'Failed to load layer');
```

## GIBS Layer Examples

Popular layers included:

- **VIIRS_SNPP_CorrectedReflectance_TrueColor**: True color imagery from Suomi NPP
- **MODIS_Terra_CorrectedReflectance_TrueColor**: MODIS Terra true color
- **MODIS_Aqua_CorrectedReflectance_TrueColor**: MODIS Aqua true color
- **VIIRS_NOAA20_CorrectedReflectance_TrueColor**: NOAA-20 VIIRS imagery
- **BlueMarble_NextGeneration**: Blue Marble reference layer

## Data Sources

- **GIBS API**: https://gibs.earthdata.nasa.gov/
- **Worldview Config**: https://worldview.earthdata.nasa.gov/
- **Documentation**: https://nasa-gibs.github.io/gibs-api-docs/

## Requirements

- Django 3.2+
- Python 3.8+
- Leaflet.js (included via CDN)
- requests library

## Configuration

No additional configuration needed. The app uses NASA's public GIBS endpoints which don't require API keys.

## Memory Efficiency

The app implements tile-based loading:
- Only visible tiles are loaded
- Tiles are cached by the browser
- Zoom levels determine detail level
- Date-based imagery served on-demand

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (responsive design)

## Future Enhancements

Planned features:
- AI-powered search for features in imagery
- Time-lapse animation generation
- Comparison view for different dates
- Export functionality for high-resolution images
- User annotations and bookmarks

## License

This app integrates with NASA's public APIs. NASA imagery is generally in the public domain.

## Support

For issues related to:
- GIBS API: https://nasa-gibs.github.io/gibs-api-docs/
- Worldview: https://worldview.earthdata.nasa.gov/

## Credits

Built using NASA's Global Imagery Browse Services (GIBS) and Worldview platform.