// static/js/main.js

// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            
            const event = new CustomEvent('apod:log', {
                detail: { 
                    level: 'info', 
                    message: mobileMenu.classList.contains('active') ? 'Menu opened' : 'Menu closed'
                }
            });
            window.dispatchEvent(event);
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (hamburger && mobileMenu) {
            if (!hamburger.contains(event.target) && !mobileMenu.contains(event.target)) {
                hamburger.classList.remove('active');
                mobileMenu.classList.remove('active');
            }
        }
    });
    
    // Log page load
    const event = new CustomEvent('apod:log', {
        detail: { 
            level: 'success', 
            message: `Page loaded: ${document.title}`
        }
    });
    window.dispatchEvent(event);
});

// Image Loading with Progress
function loadImageWithProgress(imgElement, onProgress) {
    const src = imgElement.dataset.src || imgElement.src;
    
    const xhr = new XMLHttpRequest();
    xhr.open('GET', src, true);
    xhr.responseType = 'blob';
    
    xhr.onprogress = function(e) {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            if (onProgress) onProgress(percentComplete);
        }
    };
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            const blob = xhr.response;
            imgElement.src = URL.createObjectURL(blob);
            
            const event = new CustomEvent('apod:log', {
                detail: { 
                    level: 'success', 
                    message: 'Image loaded successfully'
                }
            });
            window.dispatchEvent(event);
        }
    };
    
    xhr.onerror = function() {
        const event = new CustomEvent('apod:log', {
            detail: { 
                level: 'error', 
                message: 'Failed to load image'
            }
        });
        window.dispatchEvent(event);
    };
    
    xhr.send();
}

// Tile-based Image Loading for Zoom
class TileImageLoader {
    constructor(imageUrl, tileSize = 256) {
        this.imageUrl = imageUrl;
        this.tileSize = tileSize;
        this.loadedTiles = new Set();
    }
    
    getTileCoordinates(x, y, zoom) {
        const tileX = Math.floor(x / this.tileSize);
        const tileY = Math.floor(y / this.tileSize);
        return { tileX, tileY, zoom };
    }
    
    loadTile(tileX, tileY, zoom, callback) {
        const tileId = `${zoom}-${tileX}-${tileY}`;
        
        if (this.loadedTiles.has(tileId)) {
            return;
        }
        
        // In production, you would request specific tile from server
        // For now, we'll simulate tile loading
        const event = new CustomEvent('apod:log', {
            detail: { 
                level: 'info', 
                message: `Loading tile: ${tileId}`
            }
        });
        window.dispatchEvent(event);
        
        this.loadedTiles.add(tileId);
        
        if (callback) callback(tileId);
    }
    
    getVisibleTiles(viewport) {
        const tiles = [];
        const startX = Math.floor(viewport.x / this.tileSize);
        const startY = Math.floor(viewport.y / this.tileSize);
        const endX = Math.ceil((viewport.x + viewport.width) / this.tileSize);
        const endY = Math.ceil((viewport.y + viewport.height) / this.tileSize);
        
        for (let x = startX; x <= endX; x++) {
            for (let y = startY; y <= endY; y++) {
                tiles.push({ x, y, zoom: viewport.zoom });
            }
        }
        
        return tiles;
    }
}

// Lazy Loading Observer
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
                
                const event = new CustomEvent('apod:log', {
                    detail: { 
                        level: 'info', 
                        message: 'Lazy loaded image'
                    }
                });
                window.dispatchEvent(event);
            }
        }
    });
}, {
    rootMargin: '50px'
});

// Apply lazy loading to images
document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});

// Keyboard Navigation
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Close any open modals
        const modals = document.querySelectorAll('.modal, .fullscreen-modal');
        modals.forEach(modal => {
            if (modal.classList.contains('active')) {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }
});

// Performance Monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            
            const event = new CustomEvent('apod:log', {
                detail: { 
                    level: 'info', 
                    message: `Page load time: ${(pageLoadTime / 1000).toFixed(2)}s`
                }
            });
            window.dispatchEvent(event);
        }, 0);
    });
}

// Network Status Monitoring
window.addEventListener('online', function() {
    const event = new CustomEvent('apod:log', {
        detail: { 
            level: 'success', 
            message: 'Network connection restored'
        }
    });
    window.dispatchEvent(event);
});

window.addEventListener('offline', function() {
    const event = new CustomEvent('apod:log', {
        detail: { 
            level: 'error', 
            message: 'Network connection lost'
        }
    });
    window.dispatchEvent(event);
});

// Export utilities
window.APODUtils = {
    TileImageLoader,
    loadImageWithProgress,
    imageObserver
};