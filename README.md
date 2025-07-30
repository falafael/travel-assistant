# Travel Assistant 🌍

A comprehensive travel planning assistant that fetches real-time data from travel websites and APIs to help users plan trips, find deals, and get recommendations.

## Features

### Phase 1: Core Functionality ⏳
- Real-time flight and hotel search
- Live pricing and availability data
- Basic web interface
- Travel information and recommendations

### Phase 2: Enhanced Features (Planned)
- Multi-city route optimization
- Deal hunting and price tracking
- Interactive maps integration
- Advanced search filters

### Phase 3: Advanced Features (Planned)
- AI-powered recommendations
- Real-time notifications
- Mobile-responsive design
- User accounts and trip saving

### Phase 4: Premium Features (Planned)
- Visa and vaccination requirements
- Travel insurance comparison
- Trip sharing and collaboration
- Comprehensive analytics

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd travel-assistant

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py
```

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