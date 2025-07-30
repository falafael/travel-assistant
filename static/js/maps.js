/**
 * Interactive Maps Module for Travel Assistant
 * Handles route visualization, destination mapping, and interactive features
 */

class TravelMaps {
    constructor() {
        this.map = null;
        this.markers = [];
        this.routePolylines = [];
        this.infoWindows = [];
        this.currentRoute = null;
        
        // Map styles for different themes
        this.mapStyles = {
            default: [],
            dark: [
                {
                    "elementType": "geometry",
                    "stylers": [{"color": "#212121"}]
                },
                {
                    "elementType": "labels.icon",
                    "stylers": [{"visibility": "off"}]
                },
                {
                    "elementType": "labels.text.fill",
                    "stylers": [{"color": "#757575"}]
                },
                {
                    "elementType": "labels.text.stroke",
                    "stylers": [{"color": "#212121"}]
                }
            ],
            travel: [
                {
                    "featureType": "water",
                    "elementType": "geometry",
                    "stylers": [{"color": "#193341"}]
                },
                {
                    "featureType": "landscape",
                    "elementType": "geometry",
                    "stylers": [{"color": "#2c5234"}]
                }
            ]
        };
    }

    /**
     * Initialize the map with given container and options
     */
    async initializeMap(containerId, options = {}) {
        try {
            const defaultOptions = {
                center: { lat: 40.7128, lng: -74.0060 }, // NYC default
                zoom: 4,
                mapTypeId: 'roadmap',
                styles: this.mapStyles.travel
            };

            const mapOptions = { ...defaultOptions, ...options };
            
            this.map = new google.maps.Map(
                document.getElementById(containerId),
                mapOptions
            );

            // Add map controls
            this.addMapControls();
            
            console.log('Travel map initialized successfully');
            return this.map;
            
        } catch (error) {
            console.error('Map initialization failed:', error);
            throw error;
        }
    }

    /**
     * Add custom map controls
     */
    addMapControls() {
        // Route mode toggle
        const routeModeControl = document.createElement('div');
        routeModeControl.className = 'map-control route-mode';
        routeModeControl.innerHTML = `
            <button id="driving-mode" class="active">🚗 Driving</button>
            <button id="transit-mode">🚌 Transit</button>
            <button id="walking-mode">🚶 Walking</button>
            <button id="flying-mode">✈️ Flying</button>
        `;
        
        this.map.controls[google.maps.ControlPosition.TOP_CENTER].push(routeModeControl);
        
        // Add event listeners
        routeModeControl.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON') {
                this.setRouteMode(e.target.id.replace('-mode', ''));
                this.updateActiveButton(routeModeControl, e.target);
            }
        });

        // Map style toggle
        const styleControl = document.createElement('div');
        styleControl.className = 'map-control style-toggle';
        styleControl.innerHTML = `
            <button id="toggle-style">🌙 Dark Mode</button>
        `;
        
        this.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(styleControl);
        
        styleControl.addEventListener('click', () => {
            this.toggleMapStyle();
        });
    }

    /**
     * Update active button styling
     */
    updateActiveButton(container, activeButton) {
        container.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    }

    /**
     * Set route visualization mode
     */
    setRouteMode(mode) {
        this.currentRouteMode = mode;
        if (this.currentRoute) {
            this.visualizeRoute(this.currentRoute, mode);
        }
        console.log(`Route mode set to: ${mode}`);
    }

    /**
     * Toggle between map styles
     */
    toggleMapStyle() {
        const currentStyle = this.map.getMapTypeId();
        const button = document.getElementById('toggle-style');
        
        if (this.map.get('styles') === this.mapStyles.dark) {
            this.map.setOptions({ styles: this.mapStyles.travel });
            button.textContent = '🌙 Dark Mode';
        } else {
            this.map.setOptions({ styles: this.mapStyles.dark });
            button.textContent = '☀️ Light Mode';
        }
    }

    /**
     * Add a marker to the map with custom info
     */
    addMarker(location, info = {}) {
        const marker = new google.maps.Marker({
            position: location,
            map: this.map,
            title: info.title || 'Travel Location',
            icon: this.getMarkerIcon(info.type)
        });

        // Add info window if content provided
        if (info.content) {
            const infoWindow = new google.maps.InfoWindow({
                content: this.createInfoWindowContent(info)
            });

            marker.addListener('click', () => {
                // Close other info windows
                this.infoWindows.forEach(window => window.close());
                infoWindow.open(this.map, marker);
            });

            this.infoWindows.push(infoWindow);
        }

        this.markers.push(marker);
        return marker;
    }

    /**
     * Get custom marker icon based on type
     */
    getMarkerIcon(type) {
        const icons = {
            airport: {
                url: 'data:image/svg+xml;base64,' + btoa(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                        <circle cx="16" cy="16" r="14" fill="#4285f4" stroke="white" stroke-width="2"/>
                        <text x="16" y="22" text-anchor="middle" fill="white" font-size="16">✈</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(32, 32)
            },
            hotel: {
                url: 'data:image/svg+xml;base64,' + btoa(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                        <circle cx="16" cy="16" r="14" fill="#34a853" stroke="white" stroke-width="2"/>
                        <text x="16" y="22" text-anchor="middle" fill="white" font-size="16">🏨</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(32, 32)
            },
            attraction: {
                url: 'data:image/svg+xml;base64=' + btoa(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                        <circle cx="16" cy="16" r="14" fill="#fbbc04" stroke="white" stroke-width="2"/>
                        <text x="16" y="22" text-anchor="middle" fill="white" font-size="16">🎯</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(32, 32)
            },
            default: {
                url: 'data:image/svg+xml;base64=' + btoa(`
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
                        <circle cx="16" cy="16" r="14" fill="#ea4335" stroke="white" stroke-width="2"/>
                        <text x="16" y="22" text-anchor="middle" fill="white" font-size="16">📍</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(32, 32)
            }
        };

        return icons[type] || icons.default;
    }

    /**
     * Create rich info window content
     */
    createInfoWindowContent(info) {
        return `
            <div class="map-info-window">
                <div class="info-header">
                    <h3>${info.title || 'Location'}</h3>
                    ${info.rating ? `<div class="rating">⭐ ${info.rating}</div>` : ''}
                </div>
                ${info.address ? `<p class="address">📍 ${info.address}</p>` : ''}
                ${info.description ? `<p class="description">${info.description}</p>` : ''}
                ${info.price ? `<div class="price">💰 ${info.price}</div>` : ''}
                ${info.bookingUrl ? `<a href="${info.bookingUrl}" target="_blank" class="book-btn">Book Now</a>` : ''}
                ${info.website ? `<a href="${info.website}" target="_blank" class="website-link">Visit Website</a>` : ''}
            </div>
        `;
    }

    /**
     * Visualize a complete route with multiple waypoints
     */
    async visualizeRoute(routeData, mode = 'driving') {
        try {
            this.clearRoute();
            this.currentRoute = routeData;

            const legs = routeData.legs || [];
            if (legs.length === 0) return;

            // Add markers for all locations
            legs.forEach((leg, index) => {
                // Origin marker
                if (index === 0) {
                    this.addMarker(
                        this.geocodeLocation(leg.origin),
                        {
                            title: `Start: ${leg.origin}`,
                            type: 'default',
                            content: `Starting point of your journey`
                        }
                    );
                }

                // Destination marker
                this.addMarker(
                    this.geocodeLocation(leg.destination),
                    {
                        title: `${index === legs.length - 1 ? 'End' : 'Stop'}: ${leg.destination}`,
                        type: leg.transport_type === 'flight' ? 'airport' : 'default',
                        content: `${leg.transport_type} to ${leg.destination}<br>Cost: ${leg.cost}<br>Duration: ${leg.duration}`
                    }
                );
            });

            // Draw route lines based on transport type
            for (let i = 0; i < legs.length; i++) {
                const leg = legs[i];
                await this.drawRouteLeg(leg, mode);
            }

            // Fit map to show all markers
            this.fitMapToMarkers();

            console.log('Route visualized successfully');

        } catch (error) {
            console.error('Route visualization failed:', error);
        }
    }

    /**
     * Draw a single leg of the route
     */
    async drawRouteLeg(leg, mode) {
        const origin = this.geocodeLocation(leg.origin);
        const destination = this.geocodeLocation(leg.destination);

        if (leg.transport_type === 'flight') {
            // Draw flight path (great circle)
            this.drawFlightPath(origin, destination, leg);
        } else {
            // Use Google Directions for ground transport
            await this.drawGroundRoute(origin, destination, leg, mode);
        }
    }

    /**
     * Draw flight path between two points
     */
    drawFlightPath(origin, destination, legInfo) {
        const flightPath = new google.maps.Polyline({
            path: [origin, destination],
            geodesic: true,
            strokeColor: '#FF6B6B',
            strokeOpacity: 1.0,
            strokeWeight: 3,
            icons: [{
                icon: {
                    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                    scale: 4,
                    fillColor: '#FF6B6B',
                    fillOpacity: 1,
                    strokeWeight: 1,
                    strokeColor: '#ffffff'
                },
                offset: '50%'
            }]
        });

        flightPath.setMap(this.map);
        this.routePolylines.push(flightPath);

        // Add click listener for route info
        flightPath.addListener('click', (event) => {
            this.showRouteInfo(event.latLng, legInfo);
        });
    }

    /**
     * Draw ground route using Google Directions
     */
    async drawGroundRoute(origin, destination, legInfo, mode) {
        return new Promise((resolve, reject) => {
            const directionsService = new google.maps.DirectionsService();
            const directionsRenderer = new google.maps.DirectionsRenderer({
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: this.getRouteColor(legInfo.transport_type),
                    strokeWeight: 4,
                    strokeOpacity: 0.8
                }
            });

            const travelMode = this.getTravelMode(mode);

            directionsService.route({
                origin: origin,
                destination: destination,
                travelMode: travelMode
            }, (result, status) => {
                if (status === 'OK') {
                    directionsRenderer.setDirections(result);
                    directionsRenderer.setMap(this.map);
                    this.routePolylines.push(directionsRenderer);
                    resolve(result);
                } else {
                    console.warn('Directions request failed:', status);
                    // Fallback to straight line
                    this.drawStraightLine(origin, destination, legInfo);
                    resolve();
                }
            });
        });
    }

    /**
     * Get Google Maps travel mode
     */
    getTravelMode(mode) {
        const modes = {
            driving: google.maps.TravelMode.DRIVING,
            transit: google.maps.TravelMode.TRANSIT,
            walking: google.maps.TravelMode.WALKING,
            flying: google.maps.TravelMode.DRIVING // Fallback
        };
        return modes[mode] || google.maps.TravelMode.DRIVING;
    }

    /**
     * Get color for different transport types
     */
    getRouteColor(transportType) {
        const colors = {
            flight: '#FF6B6B',
            train: '#4ECDC4',
            bus: '#45B7D1',
            car_rental: '#96CEB4',
            rideshare: '#FFEAA7',
            default: '#6C5CE7'
        };
        return colors[transportType] || colors.default;
    }

    /**
     * Draw straight line fallback
     */
    drawStraightLine(origin, destination, legInfo) {
        const line = new google.maps.Polyline({
            path: [origin, destination],
            strokeColor: this.getRouteColor(legInfo.transport_type),
            strokeOpacity: 0.6,
            strokeWeight: 2,
            icons: [{
                icon: {
                    path: 'M 0,-1 0,1',
                    strokeOpacity: 1,
                    scale: 4
                },
                offset: '0',
                repeat: '20px'
            }]
        });

        line.setMap(this.map);
        this.routePolylines.push(line);
    }

    /**
     * Show route information popup
     */
    showRouteInfo(position, legInfo) {
        const infoWindow = new google.maps.InfoWindow({
            position: position,
            content: `
                <div class="route-info-popup">
                    <h4>${legInfo.origin} → ${legInfo.destination}</h4>
                    <p><strong>Transport:</strong> ${legInfo.transport_type}</p>
                    <p><strong>Cost:</strong> ${legInfo.cost}</p>
                    <p><strong>Duration:</strong> ${legInfo.duration}</p>
                    ${legInfo.carbon_footprint ? `<p><strong>Carbon:</strong> ${legInfo.carbon_footprint} kg CO₂</p>` : ''}
                </div>
            `
        });

        // Close other info windows
        this.infoWindows.forEach(window => window.close());
        infoWindow.open(this.map);
        this.infoWindows.push(infoWindow);
    }

    /**
     * Convert location name to coordinates (simplified geocoding)
     */
    geocodeLocation(locationName) {
        // Simplified coordinates mapping (in production, use Google Geocoding API)
        const coordinates = {
            'new york': { lat: 40.7128, lng: -74.0060 },
            'los angeles': { lat: 34.0522, lng: -118.2437 },
            'chicago': { lat: 41.8781, lng: -87.6298 },
            'miami': { lat: 25.7617, lng: -80.1918 },
            'seattle': { lat: 47.6062, lng: -122.3321 },
            'london': { lat: 51.5074, lng: -0.1278 },
            'paris': { lat: 48.8566, lng: 2.3522 },
            'tokyo': { lat: 35.6762, lng: 139.6503 },
            'sydney': { lat: -33.8688, lng: 151.2093 }
        };

        return coordinates[locationName.toLowerCase()] || { lat: 0, lng: 0 };
    }

    /**
     * Fit map to show all markers
     */
    fitMapToMarkers() {
        if (this.markers.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        this.markers.forEach(marker => {
            bounds.extend(marker.getPosition());
        });

        this.map.fitBounds(bounds);
        
        // Ensure minimum zoom level
        google.maps.event.addListenerOnce(this.map, 'bounds_changed', () => {
            if (this.map.getZoom() > 15) {
                this.map.setZoom(15);
            }
        });
    }

    /**
     * Clear all route visualizations
     */
    clearRoute() {
        // Clear polylines
        this.routePolylines.forEach(polyline => {
            if (polyline.setMap) {
                polyline.setMap(null);
            }
        });
        this.routePolylines = [];

        // Clear markers
        this.markers.forEach(marker => marker.setMap(null));
        this.markers = [];

        // Close info windows
        this.infoWindows.forEach(window => window.close());
        this.infoWindows = [];
    }

    /**
     * Add heatmap overlay for popular destinations
     */
    addDestinationHeatmap(destinationData) {
        const heatmapData = destinationData.map(dest => ({
            location: new google.maps.LatLng(dest.lat, dest.lng),
            weight: dest.popularity || 1
        }));

        const heatmap = new google.maps.visualization.HeatmapLayer({
            data: heatmapData,
            radius: 50,
            opacity: 0.6
        });

        heatmap.setMap(this.map);
        return heatmap;
    }

    /**
     * Enable drawing mode for custom routes
     */
    enableDrawingMode() {
        const drawingManager = new google.maps.drawing.DrawingManager({
            drawingMode: google.maps.drawing.OverlayType.POLYLINE,
            drawingControl: true,
            drawingControlOptions: {
                position: google.maps.ControlPosition.TOP_CENTER,
                drawingModes: [
                    google.maps.drawing.OverlayType.POLYLINE,
                    google.maps.drawing.OverlayType.POLYGON,
                    google.maps.drawing.OverlayType.CIRCLE,
                    google.maps.drawing.OverlayType.MARKER
                ]
            }
        });

        drawingManager.setMap(this.map);
        return drawingManager;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TravelMaps;
} else if (typeof window !== 'undefined') {
    window.TravelMaps = TravelMaps;
}