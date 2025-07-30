#!/usr/bin/env python3
"""
Comprehensive Travel Assistant - Agent-Based Architecture
Uses specialized agents for data fetching, route optimization, deal hunting, and UI building
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, render_template, request, jsonify
import logging

# Import our agent coordinator
from agents.agent_coordinator import AgentCoordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the agent coordinator
coordinator = AgentCoordinator()

# Travel type configurations for the UI
TRAVEL_TYPES = {
    'flights': {
        'name': 'Flights',
        'apis': ['Skyscanner', 'Google Flights', 'Kayak', 'Expedia'],
        'icon': '✈️'
    },
    'hotels': {
        'name': 'Hotels & Accommodations', 
        'apis': ['Booking.com', 'Hotels.com', 'Airbnb', 'Agoda'],
        'icon': '🏨'
    },
    'car_rental': {
        'name': 'Car Rentals',
        'apis': ['Enterprise', 'Hertz', 'Budget', 'Avis'],
        'icon': '🚗'
    },
    'trains': {
        'name': 'Train Travel',
        'apis': ['Amtrak', 'Eurail', 'Trainline', 'Rail Europe'],
        'icon': '🚂'
    },
    'buses': {
        'name': 'Bus Travel',
        'apis': ['Greyhound', 'Megabus', 'FlixBus', 'BoltBus'],
        'icon': '🚌'
    },
    'cruises': {
        'name': 'Cruises',
        'apis': ['Royal Caribbean', 'Carnival', 'Norwegian', 'Celebrity'],
        'icon': '🚢'
    },
    'tours': {
        'name': 'Tours & Activities',
        'apis': ['Viator', 'GetYourGuide', 'Klook', 'TripAdvisor'],
        'icon': '🎯'
    },
    'rideshare': {
        'name': 'Rideshare & Taxis',
        'apis': ['Uber', 'Lyft', 'Local Taxis'],
        'icon': '🚕'
    },
    'flights_private': {
        'name': 'Private Jets',
        'apis': ['NetJets', 'Flexjet', 'JetSuite'],
        'icon': '🛩️'
    },
    'rv_camping': {
        'name': 'RV & Camping',
        'apis': ['RVshare', 'Outdoorsy', 'KOA', 'Hipcamp'],
        'icon': '🏕️'
    }
}

# Helper function to run async functions in Flask
def run_async(func):
    """Run async function in Flask context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(func)
    finally:
        loop.close()

# Flask Routes

@app.route('/')
def index():
    """Main page with search interface"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """
    Comprehensive search endpoint using agent coordination
    """
    try:
        data = request.get_json()
        logger.info(f"Search request received: {data}")
        
        # Use agent coordinator for comprehensive search
        results = run_async(coordinator.coordinate_comprehensive_search(data))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Search endpoint error: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': f'Search failed: {str(e)}',
            'coordinator': 'AgentCoordinator'
        }), 500

@app.route('/deals', methods=['POST'])
def hunt_deals():
    """
    Deal hunting endpoint using DealHunterAgent
    """
    try:
        data = request.get_json()
        logger.info(f"Deal hunting request: {data}")
        
        # Use deal hunter agent through coordinator
        results = run_async(coordinator.deal_hunter.hunt_deals(data))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Deal hunting error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Deal hunting failed: {str(e)}',
            'agent': 'DealHunterAgent'
        }), 500

@app.route('/track-prices', methods=['POST'])
def track_prices():
    """
    Price tracking endpoint
    """
    try:
        data = request.get_json()
        logger.info(f"Price tracking request: {data}")
        
        # Use coordinator for deal tracking
        results = run_async(coordinator.coordinate_deal_tracking(data))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Price tracking error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Price tracking failed: {str(e)}',
            'coordinator': 'AgentCoordinator'
        }), 500

@app.route('/optimize-route', methods=['POST'])
def optimize_route():
    """
    Route optimization endpoint using RouteOptimizerAgent
    """
    try:
        data = request.get_json()
        logger.info(f"Route optimization request: {data}")
        
        # Use coordinator for route planning
        results = run_async(coordinator.coordinate_route_planning(data))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Route optimization error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Route optimization failed: {str(e)}',
            'coordinator': 'AgentCoordinator'
        }), 500

@app.route('/multi-city-route', methods=['POST'])
def multi_city_route():
    """
    Multi-city route planning endpoint
    """
    try:
        data = request.get_json()
        logger.info(f"Multi-city route request: {data}")
        
        cities = data.get('cities', [])
        start_city = data.get('start_city')
        preferences = data.get('preferences', {})
        
        # Use route optimizer agent directly
        results = run_async(coordinator.route_optimizer.optimize_multi_city_route(
            cities=cities,
            start_city=start_city,
            preferences=preferences
        ))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Multi-city route error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Multi-city route optimization failed: {str(e)}',
            'agent': 'RouteOptimizerAgent'
        }), 500

@app.route('/price-trends', methods=['POST'])
def analyze_price_trends():
    """
    Price trend analysis endpoint
    """
    try:
        data = request.get_json()
        logger.info(f"Price trend analysis request: {data}")
        
        route_params = data.get('route_params', {})
        lookback_days = data.get('lookback_days', 30)
        
        # Use deal hunter agent directly
        results = run_async(coordinator.deal_hunter.analyze_price_trends(
            route_params=route_params,
            lookback_days=lookback_days
        ))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Price trend analysis error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Price trend analysis failed: {str(e)}',
            'agent': 'DealHunterAgent'
        }), 500

@app.route('/build-ui', methods=['POST'])
def build_dynamic_ui():
    """
    Dynamic UI building endpoint
    """
    try:
        data = request.get_json()
        logger.info(f"UI building request: {data}")
        
        # Use UI builder agent directly
        results = run_async(coordinator.ui_builder.build_dynamic_interface(data))
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"UI building error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'UI building failed: {str(e)}',
            'agent': 'UIBuilderAgent'
        }), 500

@app.route('/agent-status')
def get_agent_status():
    """
    Get status of all agents
    """
    try:
        status = run_async(coordinator.get_agent_status())
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Agent status error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Agent status check failed: {str(e)}'
        }), 500

@app.route('/restart-agent/<agent_name>', methods=['POST'])
def restart_agent(agent_name):
    """
    Restart a specific agent
    """
    try:
        results = run_async(coordinator.restart_agent(agent_name))
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Agent restart error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Agent restart failed: {str(e)}'
        }), 500

@app.route('/travel-types')
def travel_types():
    """
    Get available travel types
    """
    return jsonify(TRAVEL_TYPES)

# Health check endpoint
@app.route('/health')
def health_check():
    """
    Health check endpoint
    """
    try:
        agent_status = run_async(coordinator.get_agent_status())
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0-agents',
            'architecture': 'agent-based',
            'agents': agent_status
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': [
            '/search', '/deals', '/track-prices', '/optimize-route',
            '/multi-city-route', '/price-trends', '/build-ui',
            '/agent-status', '/travel-types', '/health'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("Comprehensive Travel Assistant - Agent-Based Architecture")
    print("=" * 65)
    print("AGENTS ACTIVE:")
    print("  DataFetcherAgent: Handles all API calls and data retrieval")
    print("  RouteOptimizerAgent: Optimizes routes and multi-city planning")
    print("  DealHunterAgent: Finds deals and tracks prices")
    print("  UIBuilderAgent: Builds dynamic user interfaces")
    print("  AgentCoordinator: Orchestrates all agent interactions")
    print("=" * 65)
    print("ENDPOINTS:")
    print("  POST /search - Comprehensive travel search")
    print("  POST /deals - Hunt for travel deals")
    print("  POST /track-prices - Set up price tracking")
    print("  POST /optimize-route - Route optimization")
    print("  POST /multi-city-route - Multi-city planning")
    print("  POST /price-trends - Price trend analysis")
    print("  POST /build-ui - Dynamic UI generation")
    print("  GET  /agent-status - Agent health status")
    print("  GET  /travel-types - Available travel types")
    print("  GET  /health - System health check")
    print("=" * 65)
    print("Web interface: http://localhost:5000")
    print("Agent coordination ready!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)