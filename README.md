# Travel Assistant 🌍

A comprehensive, **agent-based** travel planning assistant with real-time traffic integration, interactive maps, and comprehensive search across all travel types.

## 🚀 **STATUS: PHASES 1-3 COMPLETE** ✅

### ✅ **Current Features**
- **🔍 Comprehensive Search**: Flights, hotels, car rentals, trains, buses, cruises, tours & activities
- **🤖 Agent Architecture**: 5 specialized autonomous agents working in parallel  
- **🗺️ Interactive Maps**: Google Maps integration with route visualization
- **🚦 Real-Time Traffic**: Phase 3 traffic integration with delay predictions and smart re-routing
- **💻 Web Interface**: Responsive frontend with booking integration
- **📊 14 API Endpoints**: Complete REST API for all travel operations

### 🏗️ **Next Phases** (Ready for Development)
- **Phase 4**: Advanced deal hunting algorithms + price prediction
- **Phase 5**: Smart AI recommendations engine  
- **Phase 6**: Real-time notifications + collaborative planning

## Quick Start

```bash
# Clone the repository  
git clone https://github.com/falafael/travel-assistant.git
cd travel-assistant

# Install dependencies
pip install -r requirements.txt

# Set up Google Maps API key (for map features)
# 1. Go to https://console.cloud.google.com/
# 2. Create a new project or select existing
# 3. Enable Maps JavaScript API and Places API
# 4. Create credentials (API key)
# 5. Replace YOUR_GOOGLE_MAPS_API_KEY in templates/index.html

# Run the agent-based application
python src/app_agents.py
```

## Configuration

### Google Maps API Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API  
   - Directions API
   - Geocoding API
4. Create an API key in Credentials
5. Replace `YOUR_GOOGLE_MAPS_API_KEY` in `templates/index.html`

### Optional: Restrict API Key
For security, restrict your API key to:
- HTTP referrers (websites): `localhost:5000/*`, `yourdomain.com/*`
- APIs: Maps JavaScript API, Places API, Directions API, Geocoding API

## Project Structure

```
travel-assistant/
├── src/           # Source code
├── templates/     # HTML templates
├── static/        # CSS, JS, images
├── tests/         # Test files
├── docs/          # Documentation
├── context/       # Development context files
└── CLAUDE.md      # Development log
```

## Development

See `CLAUDE.md` for detailed development progress and `context/` folder for development guidelines.

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML/CSS/JavaScript
- **APIs**: Real-time travel data sources
- **Maps**: Interactive mapping integration
- **Database**: SQLite (dev), PostgreSQL (prod)

## Security

This project follows defensive security practices:
- No payment processing or sensitive data handling
- Secure API key management
- Input validation and sanitization
- HTTPS for all external communications

## Contributing

1. Check `CLAUDE.md` for current development status
2. Review `context/development_guidelines.md` for code standards
3. Follow the established project structure
4. Add tests for new functionality

## License

MIT License - see LICENSE file for details