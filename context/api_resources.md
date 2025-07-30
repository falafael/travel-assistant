# API Resources - Travel Assistant

## Flight APIs
- **Skyscanner API**: Flight search and booking links
- **Amadeus API**: Flight data and pricing
- **Google Flights API**: Flight search integration
- **Kayak API**: Price comparison and tracking

## Hotel APIs  
- **Booking.com API**: Hotel search and availability
- **Hotels.com API**: Hotel pricing and reviews
- **Expedia API**: Comprehensive travel booking
- **Airbnb API**: Alternative accommodations

## Travel Information APIs
- **OpenWeatherMap**: Weather forecasts and conditions
- **REST Countries**: Country information and requirements
- **ExchangeRate-API**: Real-time currency conversion
- **Travel Advisory APIs**: Government travel warnings

## Maps and Location APIs
- **Google Maps API**: Interactive maps and directions
- **Mapbox API**: Custom map styling and routing
- **OpenStreetMap**: Open-source mapping data
- **Google Places API**: Points of interest and reviews

## Additional APIs
- **Wikipedia API**: Destination information
- **Unsplash API**: High-quality travel photos
- **TimeZone API**: Local time information
- **Visa Requirements API**: Entry requirements

## API Key Management
- Store all keys in environment variables
- Use different keys for development and production
- Implement rate limiting to stay within quotas
- Monitor API usage and costs
- Have backup APIs for critical functionality

## Rate Limiting Strategy
- Implement exponential backoff for retries
- Cache responses where appropriate
- Batch requests when possible
- Monitor and respect API rate limits
- Graceful degradation when limits exceeded