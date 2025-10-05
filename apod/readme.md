# NASA APOD Explorer - Project Setup

## Project Structure

```
apod_project/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── apod/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── tasks.py
│   ├── management/
│   │   └── commands/
│   │       ├── fetch_apod.py
│   │       └── populate_coordinates.py
│   └── templates/
│       └── apod/
│           ├── home.html
│           ├── archive.html
│           └── coordinates.html
├── templates/
│   ├── base.html
│   ├── header.html
│   └── footer.html
├── static/
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── main.js
├── media/
├── .env
├── requirements.txt
├── manage.py
└── README.md
```

## Installation Steps

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` file in project root:

```env
NASA_API_KEY=es9aMGyrIKae9wcgTKkUwLAqJo974s9krl8qzaG8
DEBUG=True
SECRET_KEY=your-django-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Populate Initial Data

```bash
# Fetch today's APOD
python manage.py fetch_apod

# Backfill 30 days of historical data
python manage.py fetch_apod --backfill --days 30

# Populate celestial coordinates
python manage.py populate_coordinates
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Setting Up Celery for Scheduled Tasks

### Install Redis (Required for Celery)

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download from https://github.com/microsoftarchive/redis/releases

### Run Celery Worker

Open a new terminal:

```bash
celery -A config worker -l info
```

### Run Celery Beat (Scheduler)

Open another terminal:

```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Celery Schedule Configuration

The following tasks are automatically scheduled:

- **Fetch Latest APOD**: Runs daily at 00:05 (midnight)
- **Check NASA Update**: Runs every 5 minutes
- **Cleanup Old Logs**: Runs weekly on Sunday at 2 AM

## Management Commands

### Fetch APOD

```bash
# Fetch today's APOD
python manage.py fetch_apod

# Fetch specific date
python manage.py fetch_apod --date 2024-01-15

# Backfill multiple days
python manage.py fetch_apod --backfill --days 90
```

### Populate Coordinates

```bash
python manage.py populate_coordinates
```

## Features

### 1. Landing Page with Gradient Blur Effect
- Beautiful gradient background with blurred APOD image
- Click to view fullscreen with zoom capability
- Coordinate search integration

### 2. Archive Calendar View
- Circular thumbnails in grid layout
- Lazy loading for performance
- Hover effects with glassmorphism
- Click to view detailed modal

### 3. Coordinate Search
- Search celestial objects
- View coordinates on images
- Integrated with APOD images

### 4. Desktop Terminal Monitor
- Fixed footer terminal (desktop only)
- Real-time system logs
- Color-coded indicators (green/orange/red)
- Collapsible interface

### 5. Responsive Navigation
- Vertical glassmorphism sidebar (desktop)
- Hamburger menu (mobile/tablet)
- Smooth animations

## API Endpoints

- `GET /apod/api/archive/` - Paginated archive data
- `GET /apod/api/image/<id>/` - Single image details
- `GET /apod/api/coordinates/?q=<query>` - Search coordinates
- `GET /apod/api/logs/` - Recent system logs

## Design Principles

- Clean, NASA-inspired color scheme (blue, yellow, black)
- Soft gradients and glassmorphism effects
- Memory-efficient tile loading for large images
- Mobile-first responsive design
- No emojis, professional interface
- Terminal-style system monitoring

## Production Deployment

### Using Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/your/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Issue: APOD not fetching
- Check NASA API key in .env
- Verify internet connection
- Check system logs in admin panel

### Issue: Images not loading
- Run `python manage.py collectstatic`
- Check MEDIA_ROOT and STATIC_ROOT settings
- Verify file permissions

### Issue: Celery tasks not running
- Ensure Redis is running
- Check Celery worker logs
- Verify CELERY_BROKER_URL in settings

## Future Enhancements

- Add more celestial coordinate databases
- Implement image tile server for large images
- Add user favorites and collections
- Social sharing features
- Mobile app integration
- 3D visualization of celestial coordinates

## License

This project uses NASA's public API and follows their usage guidelines.

## Support

For issues related to NASA API: https://api.nasa.gov/
For Django issues: https://docs.djangoproject.com/