#!/usr/bin/env python3
"""
Route Optimizer Agent - Clean Version with Traffic Integration
Enhanced Phase 3 version with real-time traffic features
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import math
import itertools
from dataclasses import dataclass
import asyncio
import time
import json

logger = logging.getLogger(__name__)

@dataclass
class TravelLeg:
    """Represents a single leg of travel"""
    origin: str
    destination: str
    transport_type: str
    departure_date: str
    arrival_date: str
    cost: float
    duration_hours: float
    carbon_footprint: float = 0.0
    traffic_delay_minutes: int = 0
    real_time_duration: float = 0.0
    traffic_conditions: str = "normal"

@dataclass 
class OptimizedRoute:
    """Represents an optimized travel route"""
    legs: List[TravelLeg]
    total_cost: float
    total_duration_hours: float
    total_carbon_footprint: float
    efficiency_score: float
    real_time_duration: float = 0.0
    traffic_impact: Dict = None
    last_updated: str = ""

class RouteOptimizerAgent:
    """
    Enhanced Route Optimizer Agent with Phase 3 real-time traffic integration
    """
    
    def __init__(self):
        # Traffic data cache for real-time optimization
        self.traffic_cache = {}
        self.cache_expiry_minutes = 15
        
        # Real-time traffic simulation data
        self.traffic_conditions = {
            'peak_hours': [7, 8, 17, 18, 19],  # Rush hours
            'congestion_multipliers': {
                'light': 1.1,
                'moderate': 1.3,
                'heavy': 1.8,
                'severe': 2.5
            },
            'weather_impact': {
                'clear': 1.0,
                'rain': 1.2,
                'snow': 1.5,
                'storm': 2.0
            }
        }
        
        # Transport configurations
        self.transport_configs = {
            'flight': {
                'avg_speed_kmh': 800,
                'cost_per_km': 0.15,
                'carbon_per_km': 0.255,
                'setup_time_hours': 3,
                'availability': 'global',
                'traffic_sensitive': False
            },
            'train': {
                'avg_speed_kmh': 120,
                'cost_per_km': 0.08,
                'carbon_per_km': 0.041,
                'setup_time_hours': 1,
                'availability': 'regional',
                'traffic_sensitive': False
            },
            'bus': {
                'avg_speed_kmh': 80,
                'cost_per_km': 0.05,
                'carbon_per_km': 0.089,
                'setup_time_hours': 0.5,
                'availability': 'regional',
                'traffic_sensitive': True
            },
            'car_rental': {
                'avg_speed_kmh': 90,
                'cost_per_km': 0.12,
                'carbon_per_km': 0.171,
                'setup_time_hours': 0.5,
                'availability': 'global',
                'traffic_sensitive': True
            }
        }
        
        # City coordinates
        self.city_coordinates = {
            'new york': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'miami': (25.7617, -80.1918),
            'seattle': (47.6062, -122.3321),
            'denver': (39.7392, -104.9903),
            'atlanta': (33.7490, -84.3880),
            'boston': (42.3601, -71.0589),
            'san francisco': (37.7749, -122.4194),
            'washington dc': (38.9072, -77.0369),
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522),
            'rome': (41.9028, 12.4964),
            'tokyo': (35.6762, 139.6503),
            'sydney': (-33.8688, 151.2093)
        }

    # Phase 3 Enhanced Traffic Methods
    
    async def get_real_time_traffic_data(self, origin: str, destination: str, 
                                       transport_type: str = 'car_rental') -> Dict:
        """
        Fetch real-time traffic data for route optimization
        Enhanced Phase 3 feature with traffic integration
        """
        try:
            logger.info(f"Route Optimizer Agent: Fetching real-time traffic data {origin} → {destination}")
            
            # Check if transport is traffic-sensitive
            if not self.transport_configs.get(transport_type, {}).get('traffic_sensitive', False):
                return {
                    'status': 'success',
                    'traffic_impact': 'none',
                    'delay_minutes': 0,
                    'conditions': 'not_applicable',
                    'transport_type': transport_type
                }
            
            # Check cache first
            cache_key = f"{origin}_{destination}_{transport_type}"
            cached_data = self._get_cached_traffic_data(cache_key)
            if cached_data:
                logger.info("Using cached traffic data")
                return cached_data
            
            # Simulate real-time traffic data
            traffic_data = await self._simulate_traffic_conditions(origin, destination, transport_type)
            
            # Cache the result
            self._cache_traffic_data(cache_key, traffic_data)
            
            logger.info(f"Traffic data retrieved: {traffic_data['conditions']} conditions, {traffic_data['delay_minutes']}min delay")
            return traffic_data
            
        except Exception as e:
            logger.error(f"Route Optimizer Agent: Traffic data fetch error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Traffic data fetch failed: {str(e)}',
                'fallback_conditions': 'normal'
            }

    async def optimize_route_with_traffic(self, origin: str, destination: str, 
                                        departure_time: str = None, preferences: Dict = None) -> Dict:
        """
        Enhanced route optimization with real-time traffic integration
        Phase 3 core feature
        """
        try:
            logger.info(f"Route Optimizer Agent: Optimizing route with traffic {origin} → {destination}")
            
            preferences = preferences or {}
            departure_time = departure_time or datetime.now().strftime('%H:%M')
            
            # Get all transport options
            distance_km = self._calculate_distance(origin, destination)
            transport_options = []
            
            for transport_type, config in self.transport_configs.items():
                if self._is_transport_viable(transport_type, distance_km, origin, destination):
                    # Get traffic data
                    traffic_data = await self.get_real_time_traffic_data(origin, destination, transport_type)
                    
                    # Calculate base option
                    base_option = self._calculate_transport_option(
                        transport_type, origin, destination, distance_km, 
                        datetime.now().strftime('%Y-%m-%d'), config
                    )
                    
                    # Apply traffic impact
                    enhanced_option = await self._apply_traffic_to_option(base_option, traffic_data, departure_time)
                    transport_options.append(enhanced_option)
            
            # Rank options with traffic considerations
            enhanced_options = self._rank_traffic_enhanced_options(transport_options, preferences.get('optimize_for', 'balanced'))
            
            result = {
                'status': 'success',
                'optimization_type': 'traffic_enhanced_route',
                'origin': origin,
                'destination': destination,
                'departure_time': departure_time,
                'traffic_considered': True,
                'options': enhanced_options,
                'traffic_summary': self._generate_traffic_summary(enhanced_options),
                'last_updated': datetime.now().isoformat(),
                'agent': 'RouteOptimizerAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Route Optimizer Agent: Traffic-enhanced optimization error: {str(e)}")
            return {'status': 'error', 'message': f'Traffic optimization failed: {str(e)}'}

    # Helper methods for traffic integration
    
    def _get_cached_traffic_data(self, cache_key: str) -> Optional[Dict]:
        """Get cached traffic data if still valid"""
        if cache_key in self.traffic_cache:
            cached_item = self.traffic_cache[cache_key]
            cache_time = cached_item.get('timestamp', 0)
            
            if time.time() - cache_time < (self.cache_expiry_minutes * 60):
                return cached_item.get('data')
        
        return None
    
    def _cache_traffic_data(self, cache_key: str, data: Dict) -> None:
        """Cache traffic data with timestamp"""
        self.traffic_cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    async def _simulate_traffic_conditions(self, origin: str, destination: str, 
                                         transport_type: str) -> Dict:
        """Simulate real-time traffic conditions"""
        current_hour = datetime.now().hour
        distance_km = self._calculate_distance(origin, destination)
        
        # Determine base conditions
        conditions = 'normal'
        delay_multiplier = 1.0
        
        # Peak hour analysis
        if current_hour in self.traffic_conditions['peak_hours']:
            conditions = 'moderate'
            delay_multiplier = self.traffic_conditions['congestion_multipliers']['moderate']
            
            # Random chance for heavy traffic during peak hours
            import random
            if random.random() < 0.3:  # 30% chance
                conditions = 'heavy'
                delay_multiplier = self.traffic_conditions['congestion_multipliers']['heavy']
        
        # Distance-based adjustments
        if distance_km > 200:  # Long distance routes
            delay_multiplier *= 1.1
        
        # Calculate delays
        base_duration_hours = distance_km / self.transport_configs[transport_type]['avg_speed_kmh']
        delay_minutes = max(0, int((delay_multiplier - 1.0) * base_duration_hours * 60))
        
        # Simulate weather impact
        import random
        weather_conditions = ['clear', 'rain', 'snow']
        weather = random.choice(weather_conditions)
        weather_multiplier = self.traffic_conditions['weather_impact'][weather]
        
        if weather != 'clear':
            delay_minutes = int(delay_minutes * weather_multiplier)
            conditions = f"{conditions}_{weather}"
        
        return {
            'status': 'success',
            'conditions': conditions,
            'delay_minutes': delay_minutes,
            'weather': weather,
            'congestion_level': delay_multiplier,
            'distance_km': distance_km,
            'base_duration_hours': base_duration_hours,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _apply_traffic_to_option(self, base_option: Dict, traffic_data: Dict, 
                                     departure_time: str) -> Dict:
        """Apply traffic conditions to a transport option"""
        enhanced_option = base_option.copy()
        
        if traffic_data.get('status') == 'success':
            delay_minutes = traffic_data.get('delay_minutes', 0)
            delay_hours = delay_minutes / 60.0
            
            # Update duration
            original_duration = enhanced_option['duration_hours']
            enhanced_option['real_time_duration_hours'] = original_duration + delay_hours
            enhanced_option['traffic_delay_minutes'] = delay_minutes
            enhanced_option['traffic_conditions'] = traffic_data.get('conditions', 'normal')
            
            # Adjust cost for delays
            if delay_minutes > 30:
                cost_increase = enhanced_option['cost'] * 0.1
                enhanced_option['traffic_adjusted_cost'] = enhanced_option['cost'] + cost_increase
            else:
                enhanced_option['traffic_adjusted_cost'] = enhanced_option['cost']
            
            # Update carbon footprint for longer travel time
            if enhanced_option['type'] == 'car_rental':
                extra_carbon = (delay_hours * 2.5)
                enhanced_option['traffic_adjusted_carbon'] = enhanced_option['carbon_footprint'] + extra_carbon
            else:
                enhanced_option['traffic_adjusted_carbon'] = enhanced_option['carbon_footprint']
        
        return enhanced_option
    
    def _rank_traffic_enhanced_options(self, options: List[Dict], criteria: str) -> List[Dict]:
        """Rank transport options considering traffic impact"""
        for option in options:
            # Use traffic-adjusted values for ranking
            option['_ranking_duration'] = option.get('real_time_duration_hours', option['duration_hours'])
            option['_ranking_cost'] = option.get('traffic_adjusted_cost', option['cost'])
            option['_ranking_carbon'] = option.get('traffic_adjusted_carbon', option['carbon_footprint'])
        
        if criteria == 'cost':
            options.sort(key=lambda o: o['_ranking_cost'])
        elif criteria == 'time':
            options.sort(key=lambda o: o['_ranking_duration'])
        elif criteria == 'carbon':
            options.sort(key=lambda o: o['_ranking_carbon'])
        else:  # balanced
            options.sort(key=lambda o: (
                o['_ranking_cost'] + 
                o['_ranking_duration'] * 10 + 
                o['_ranking_carbon'] * 100
            ))
        
        # Add rankings and format with traffic info
        for i, option in enumerate(options):
            option['rank'] = i + 1
            option['cost_formatted'] = f"${option['_ranking_cost']:.2f}"
            option['duration_formatted'] = f"{option['_ranking_duration']:.1f} hours"
            option['carbon_formatted'] = f"{option['_ranking_carbon']:.2f} kg CO₂"
            
            # Add traffic impact summary
            if option.get('traffic_delay_minutes', 0) > 0:
                option['traffic_impact'] = f"+{option['traffic_delay_minutes']} min delay ({option.get('traffic_conditions', 'unknown')})"
            else:
                option['traffic_impact'] = "No significant impact"
        
        return options
    
    def _generate_traffic_summary(self, options: List[Dict]) -> Dict:
        """Generate overall traffic impact summary"""
        total_delays = sum(opt.get('traffic_delay_minutes', 0) for opt in options)
        affected_routes = len([opt for opt in options if opt.get('traffic_delay_minutes', 0) > 0])
        
        return {
            'total_routes_checked': len(options),
            'routes_with_delays': affected_routes,
            'average_delay_minutes': round(total_delays / len(options), 1) if options else 0,
            'max_delay_minutes': max((opt.get('traffic_delay_minutes', 0) for opt in options), default=0),
            'traffic_status': 'heavy' if total_delays > 120 else 'moderate' if total_delays > 60 else 'light'
        }

    # Utility methods
    
    def _calculate_distance(self, city1: str, city2: str) -> float:
        """Calculate distance between two cities using coordinates"""
        try:
            coord1 = self.city_coordinates.get(city1.lower())
            coord2 = self.city_coordinates.get(city2.lower())
            
            if not coord1 or not coord2:
                return 500.0  # Default distance
            
            # Haversine formula
            lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
            lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            return c * 6371  # Earth's radius in km
            
        except Exception:
            return 500.0
    
    def _is_transport_viable(self, transport_type: str, distance_km: float, 
                           origin: str, destination: str) -> bool:
        """Check if transport type is viable for the route"""
        if transport_type == 'flight':
            return distance_km > 100
        elif transport_type == 'train':
            return distance_km < 1000 and distance_km > 50
        elif transport_type == 'bus':
            return distance_km < 800
        elif transport_type == 'car_rental':
            return distance_km < 1200
        
        return True
    
    def _calculate_transport_option(self, transport_type: str, origin: str, destination: str,
                                  distance_km: float, date: str, config: Dict) -> Dict:
        """Calculate cost, time, and carbon for a transport option"""
        base_cost = distance_km * config['cost_per_km']
        base_duration = distance_km / config['avg_speed_kmh'] + config['setup_time_hours']
        carbon_footprint = distance_km * config['carbon_per_km']
        
        return {
            'type': transport_type,
            'origin': origin,
            'destination': destination,
            'distance_km': distance_km,
            'cost': round(base_cost, 2),
            'duration_hours': round(base_duration, 2),
            'carbon_footprint': round(carbon_footprint, 2),
            'date': date
        }