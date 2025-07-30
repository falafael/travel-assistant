#!/usr/bin/env python3
"""
Route Optimizer Agent
Specialized agent for calculating optimal travel routes, multi-city itineraries, and travel logistics
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import math
import itertools
from dataclasses import dataclass
import asyncio

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
    
@dataclass 
class OptimizedRoute:
    """Represents an optimized travel route"""
    legs: List[TravelLeg]
    total_cost: float
    total_duration_hours: float
    total_carbon_footprint: float
    efficiency_score: float
    
class RouteOptimizerAgent:
    """
    Autonomous agent responsible for route optimization and travel logistics
    Handles multi-city planning, transport mode selection, and itinerary optimization
    """
    
    def __init__(self):
        # Transport type configurations with typical speeds and costs
        self.transport_configs = {
            'flight': {
                'avg_speed_kmh': 800,
                'cost_per_km': 0.15,
                'carbon_per_km': 0.255,  # kg CO2 per km
                'setup_time_hours': 3,  # Airport time
                'availability': 'global'
            },
            'train': {
                'avg_speed_kmh': 120,
                'cost_per_km': 0.08,
                'carbon_per_km': 0.041,
                'setup_time_hours': 1,
                'availability': 'regional'
            },
            'bus': {
                'avg_speed_kmh': 80,
                'cost_per_km': 0.05,
                'carbon_per_km': 0.089,
                'setup_time_hours': 0.5,
                'availability': 'regional'
            },
            'car_rental': {
                'avg_speed_kmh': 90,
                'cost_per_km': 0.12,
                'carbon_per_km': 0.171,
                'setup_time_hours': 0.5,
                'availability': 'global'
            }
        }
        
        # City coordinates (simplified - in production would use geocoding API)
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

    async def optimize_multi_city_route(self, cities: List[str], start_city: str, 
                                       end_city: str = None, preferences: Dict = None) -> Dict:
        """
        Optimize route for multiple cities
        Uses traveling salesman problem (TSP) algorithms for optimization
        """
        try:
            logger.info(f"Route Optimizer Agent: Optimizing route for {len(cities)} cities")
            
            preferences = preferences or {}
            optimization_criteria = preferences.get('optimize_for', 'cost')  # cost, time, carbon, balanced
            transport_preferences = preferences.get('transport_types', ['flight', 'train', 'bus', 'car_rental'])
            
            if end_city is None:
                end_city = start_city
            
            # Generate all possible routes
            intermediate_cities = [city for city in cities if city not in [start_city, end_city]]
            
            if len(intermediate_cities) > 8:
                # Use heuristic for large numbers of cities
                optimized_routes = await self._optimize_large_route(start_city, intermediate_cities, end_city, preferences)
            else:
                # Brute force for smaller routes
                optimized_routes = await self._optimize_small_route(start_city, intermediate_cities, end_city, preferences)
            
            # Rank routes by optimization criteria
            ranked_routes = self._rank_routes(optimized_routes, optimization_criteria)
            
            result = {
                'status': 'success',
                'optimization_type': 'multi_city_route',
                'criteria': optimization_criteria,
                'total_cities': len(cities),
                'routes': ranked_routes[:5],  # Top 5 routes
                'agent': 'RouteOptimizerAgent'
            }
            
            logger.info(f"Route Optimizer Agent: Generated {len(ranked_routes)} optimized routes")
            return result
            
        except Exception as e:
            logger.error(f"Route Optimizer Agent: Multi-city optimization error: {str(e)}")
            return {'status': 'error', 'message': f'Route optimization failed: {str(e)}'}

    async def optimize_transport_mix(self, origin: str, destination: str, 
                                   departure_date: str, preferences: Dict = None) -> Dict:
        """
        Find optimal mix of transport types for a single journey
        """
        try:
            logger.info(f"Route Optimizer Agent: Optimizing transport mix {origin} → {destination}")
            
            preferences = preferences or {}
            distance_km = self._calculate_distance(origin, destination)
            
            if distance_km == 0:
                return {'status': 'error', 'message': 'Cannot calculate distance between cities'}
            
            # Generate transport options
            transport_options = []
            
            for transport_type, config in self.transport_configs.items():
                if self._is_transport_viable(transport_type, distance_km, origin, destination):
                    option = self._calculate_transport_option(
                        transport_type, origin, destination, distance_km, departure_date, config
                    )
                    transport_options.append(option)
            
            # Consider multi-modal options for long distances
            if distance_km > 500:
                multi_modal_options = await self._generate_multi_modal_options(
                    origin, destination, distance_km, departure_date
                )
                transport_options.extend(multi_modal_options)
            
            # Rank options
            ranked_options = self._rank_transport_options(
                transport_options, preferences.get('optimize_for', 'balanced')
            )
            
            result = {
                'status': 'success',
                'optimization_type': 'transport_mix',
                'origin': origin,
                'destination': destination,
                'distance_km': distance_km,
                'options': ranked_options,
                'agent': 'RouteOptimizerAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Route Optimizer Agent: Transport mix optimization error: {str(e)}")
            return {'status': 'error', 'message': f'Transport optimization failed: {str(e)}'}

    async def calculate_itinerary_timing(self, route_legs: List[Dict], 
                                       preferences: Dict = None) -> Dict:
        """
        Calculate optimal timing for multi-leg itineraries
        """
        try:
            logger.info("Route Optimizer Agent: Calculating itinerary timing")
            
            preferences = preferences or {}
            min_layover_hours = preferences.get('min_layover_hours', 2)
            max_daily_travel_hours = preferences.get('max_daily_travel_hours', 12)
            preferred_departure_time = preferences.get('preferred_departure_time', '09:00')
            
            optimized_legs = []
            current_datetime = datetime.strptime(f"{route_legs[0].get('date', '2025-08-01')} {preferred_departure_time}", '%Y-%m-%d %H:%M')
            
            for i, leg in enumerate(route_legs):
                # Calculate departure and arrival times
                travel_time_hours = leg.get('duration_hours', 2)
                setup_time_hours = self.transport_configs.get(leg.get('transport_type', 'flight'), {}).get('setup_time_hours', 1)
                
                departure_time = current_datetime
                arrival_time = departure_time + timedelta(hours=travel_time_hours + setup_time_hours)
                
                optimized_leg = {
                    'leg_number': i + 1,
                    'origin': leg.get('origin'),
                    'destination': leg.get('destination'),
                    'transport_type': leg.get('transport_type'),
                    'departure_datetime': departure_time.isoformat(),
                    'arrival_datetime': arrival_time.isoformat(),
                    'duration_hours': travel_time_hours,
                    'layover_time_hours': leg.get('layover_hours', min_layover_hours) if i < len(route_legs) - 1 else 0
                }
                
                optimized_legs.append(optimized_leg)
                
                # Set next departure time (arrival + layover)
                if i < len(route_legs) - 1:
                    layover_hours = max(min_layover_hours, leg.get('layover_hours', min_layover_hours))
                    current_datetime = arrival_time + timedelta(hours=layover_hours)
            
            # Calculate total itinerary stats
            total_travel_time = sum(leg['duration_hours'] for leg in optimized_legs)
            total_layover_time = sum(leg['layover_time_hours'] for leg in optimized_legs)
            total_trip_time = total_travel_time + total_layover_time
            
            result = {
                'status': 'success',
                'optimization_type': 'itinerary_timing',
                'legs': optimized_legs,
                'summary': {
                    'total_legs': len(optimized_legs),
                    'total_travel_hours': round(total_travel_time, 2),
                    'total_layover_hours': round(total_layover_time, 2),
                    'total_trip_hours': round(total_trip_time, 2),
                    'departure_datetime': optimized_legs[0]['departure_datetime'],
                    'arrival_datetime': optimized_legs[-1]['arrival_datetime']
                },
                'agent': 'RouteOptimizerAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Route Optimizer Agent: Itinerary timing error: {str(e)}")
            return {'status': 'error', 'message': f'Itinerary timing failed: {str(e)}'}

    async def _optimize_small_route(self, start_city: str, intermediate_cities: List[str], 
                                   end_city: str, preferences: Dict) -> List[OptimizedRoute]:
        """Optimize route for small number of cities using brute force"""
        all_routes = []
        
        # Generate all permutations of intermediate cities
        for perm in itertools.permutations(intermediate_cities):
            route_cities = [start_city] + list(perm) + [end_city] if end_city != start_city else [start_city] + list(perm)
            
            # Calculate route metrics
            legs = []
            total_cost = 0
            total_duration = 0
            total_carbon = 0
            
            for i in range(len(route_cities) - 1):
                origin, destination = route_cities[i], route_cities[i + 1]
                distance_km = self._calculate_distance(origin, destination)
                
                # Choose best transport for this leg
                best_transport = self._select_best_transport(origin, destination, distance_km, preferences)
                
                leg = TravelLeg(
                    origin=origin,
                    destination=destination,
                    transport_type=best_transport['type'],
                    departure_date='2025-08-01',  # Placeholder
                    arrival_date='2025-08-01',
                    cost=best_transport['cost'],
                    duration_hours=best_transport['duration_hours'],
                    carbon_footprint=best_transport['carbon_footprint']
                )
                
                legs.append(leg)
                total_cost += best_transport['cost']
                total_duration += best_transport['duration_hours']
                total_carbon += best_transport['carbon_footprint']
            
            efficiency_score = self._calculate_efficiency_score(total_cost, total_duration, total_carbon)
            
            route = OptimizedRoute(
                legs=legs,
                total_cost=total_cost,
                total_duration_hours=total_duration,
                total_carbon_footprint=total_carbon,
                efficiency_score=efficiency_score
            )
            
            all_routes.append(route)
        
        return all_routes

    async def _optimize_large_route(self, start_city: str, intermediate_cities: List[str], 
                                   end_city: str, preferences: Dict) -> List[OptimizedRoute]:
        """Optimize route for large number of cities using heuristics"""
        # Use nearest neighbor heuristic
        current_city = start_city
        remaining_cities = intermediate_cities.copy()
        route_cities = [start_city]
        
        while remaining_cities:
            # Find nearest unvisited city
            nearest_city = min(remaining_cities, 
                             key=lambda city: self._calculate_distance(current_city, city))
            route_cities.append(nearest_city)
            remaining_cities.remove(nearest_city)
            current_city = nearest_city
        
        if end_city != start_city:
            route_cities.append(end_city)
        
        # Convert to OptimizedRoute format
        legs = []
        total_cost = 0
        total_duration = 0
        total_carbon = 0
        
        for i in range(len(route_cities) - 1):
            origin, destination = route_cities[i], route_cities[i + 1]
            distance_km = self._calculate_distance(origin, destination)
            best_transport = self._select_best_transport(origin, destination, distance_km, preferences)
            
            leg = TravelLeg(
                origin=origin,
                destination=destination,
                transport_type=best_transport['type'],
                departure_date='2025-08-01',
                arrival_date='2025-08-01',
                cost=best_transport['cost'],
                duration_hours=best_transport['duration_hours'],
                carbon_footprint=best_transport['carbon_footprint']
            )
            
            legs.append(leg)
            total_cost += best_transport['cost']
            total_duration += best_transport['duration_hours']
            total_carbon += best_transport['carbon_footprint']
        
        efficiency_score = self._calculate_efficiency_score(total_cost, total_duration, total_carbon)
        
        route = OptimizedRoute(
            legs=legs,
            total_cost=total_cost,
            total_duration_hours=total_duration,
            total_carbon_footprint=total_carbon,
            efficiency_score=efficiency_score
        )
        
        return [route]  # Return single heuristic solution

    def _calculate_distance(self, city1: str, city2: str) -> float:
        """Calculate distance between two cities using coordinates"""
        try:
            coord1 = self.city_coordinates.get(city1.lower())
            coord2 = self.city_coordinates.get(city2.lower())
            
            if not coord1 or not coord2:
                # Fallback: estimate based on city names
                return 500.0  # Default distance
            
            # Haversine formula
            lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
            lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth's radius in km
            r = 6371
            
            return c * r
            
        except Exception:
            return 500.0  # Fallback distance

    def _select_best_transport(self, origin: str, destination: str, distance_km: float, 
                              preferences: Dict) -> Dict:
        """Select best transport type for a leg based on distance and preferences"""
        options = []
        
        for transport_type, config in self.transport_configs.items():
            if self._is_transport_viable(transport_type, distance_km, origin, destination):
                option = self._calculate_transport_option(
                    transport_type, origin, destination, distance_km, '2025-08-01', config
                )
                options.append(option)
        
        if not options:
            # Fallback to flight
            return self._calculate_transport_option(
                'flight', origin, destination, distance_km, '2025-08-01', 
                self.transport_configs['flight']
            )
        
        # Select based on optimization criteria
        optimize_for = preferences.get('optimize_for', 'cost')
        
        if optimize_for == 'cost':
            return min(options, key=lambda x: x['cost'])
        elif optimize_for == 'time':
            return min(options, key=lambda x: x['duration_hours'])
        elif optimize_for == 'carbon':
            return min(options, key=lambda x: x['carbon_footprint'])
        else:  # balanced
            return min(options, key=lambda x: x['cost'] + x['duration_hours'] * 10 + x['carbon_footprint'] * 100)

    def _is_transport_viable(self, transport_type: str, distance_km: float, 
                           origin: str, destination: str) -> bool:
        """Check if transport type is viable for the route"""
        if transport_type == 'flight':
            return distance_km > 100  # Flights for longer distances
        elif transport_type == 'train':
            return distance_km < 1000 and distance_km > 50  # Regional train service
        elif transport_type == 'bus':
            return distance_km < 800  # Bus service range
        elif transport_type == 'car_rental':
            return distance_km < 1200  # Reasonable driving distance
        
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

    async def _generate_multi_modal_options(self, origin: str, destination: str, 
                                          distance_km: float, date: str) -> List[Dict]:
        """Generate multi-modal transport combinations"""
        # For long distances, consider combinations like:
        # Flight + local transport, Train + bus, etc.
        options = []
        
        # Example: Flight to major hub + local transport
        if distance_km > 1000:
            # Simplified multi-modal option
            flight_portion = distance_km * 0.8
            local_portion = distance_km * 0.2
            
            flight_config = self.transport_configs['flight']
            bus_config = self.transport_configs['bus']
            
            total_cost = (flight_portion * flight_config['cost_per_km'] + 
                         local_portion * bus_config['cost_per_km'])
            total_duration = (flight_portion / flight_config['avg_speed_kmh'] + 
                            local_portion / bus_config['avg_speed_kmh'] + 
                            flight_config['setup_time_hours'] + bus_config['setup_time_hours'])
            total_carbon = (flight_portion * flight_config['carbon_per_km'] + 
                          local_portion * bus_config['carbon_per_km'])
            
            options.append({
                'type': 'multi_modal_flight_bus',
                'origin': origin,
                'destination': destination,
                'distance_km': distance_km,
                'cost': round(total_cost, 2),
                'duration_hours': round(total_duration, 2),
                'carbon_footprint': round(total_carbon, 2),
                'modes': ['flight', 'bus'],
                'date': date
            })
        
        return options

    def _rank_routes(self, routes: List[OptimizedRoute], criteria: str) -> List[Dict]:
        """Rank routes based on optimization criteria"""
        if criteria == 'cost':
            routes.sort(key=lambda r: r.total_cost)
        elif criteria == 'time':
            routes.sort(key=lambda r: r.total_duration_hours)
        elif criteria == 'carbon':
            routes.sort(key=lambda r: r.total_carbon_footprint)
        else:  # balanced
            routes.sort(key=lambda r: r.efficiency_score, reverse=True)
        
        # Convert to serializable format
        ranked = []
        for i, route in enumerate(routes):
            route_dict = {
                'rank': i + 1,
                'total_cost': f"${route.total_cost:.2f}",
                'total_duration': f"{route.total_duration_hours:.1f} hours",
                'total_carbon': f"{route.total_carbon_footprint:.2f} kg CO₂",
                'efficiency_score': round(route.efficiency_score, 2),
                'legs': [
                    {
                        'origin': leg.origin,
                        'destination': leg.destination,
                        'transport_type': leg.transport_type,
                        'cost': f"${leg.cost:.2f}",
                        'duration': f"{leg.duration_hours:.1f}h",
                        'carbon': f"{leg.carbon_footprint:.2f} kg"
                    }
                    for leg in route.legs
                ]
            }
            ranked.append(route_dict)
        
        return ranked

    def _rank_transport_options(self, options: List[Dict], criteria: str) -> List[Dict]:
        """Rank transport options based on criteria"""
        if criteria == 'cost':
            options.sort(key=lambda o: o['cost'])
        elif criteria == 'time':
            options.sort(key=lambda o: o['duration_hours'])
        elif criteria == 'carbon':
            options.sort(key=lambda o: o['carbon_footprint'])
        else:  # balanced
            options.sort(key=lambda o: o['cost'] + o['duration_hours'] * 10 + o['carbon_footprint'] * 100)
        
        # Add rankings and format
        for i, option in enumerate(options):
            option['rank'] = i + 1
            option['cost_formatted'] = f"${option['cost']:.2f}"
            option['duration_formatted'] = f"{option['duration_hours']:.1f} hours"
            option['carbon_formatted'] = f"{option['carbon_footprint']:.2f} kg CO₂"
        
        return options

    def _calculate_efficiency_score(self, cost: float, duration_hours: float, carbon: float) -> float:
        """Calculate overall efficiency score (higher is better)"""
        # Normalize and weight different factors
        # Lower cost/time/carbon = higher score
        cost_score = max(0, 1000 - cost) / 1000  # Normalize cost
        time_score = max(0, 48 - duration_hours) / 48  # Normalize time (up to 48 hours)
        carbon_score = max(0, 1000 - carbon) / 1000  # Normalize carbon
        
        # Weighted average (adjust weights based on preferences)
        efficiency = (cost_score * 0.4 + time_score * 0.4 + carbon_score * 0.2) * 100
        
        return efficiency

    async def analyze_route_alternatives(self, base_route: Dict, preferences: Dict = None) -> Dict:
        """
        Analyze alternative routes and provide recommendations
        """
        try:
            logger.info("Route Optimizer Agent: Analyzing route alternatives")
            
            # Extract route information
            legs = base_route.get('legs', [])
            if not legs:
                return {'status': 'error', 'message': 'No route legs provided'}
            
            alternatives = {
                'status': 'success',
                'base_route': base_route,
                'alternatives': [],
                'recommendations': [],
                'agent': 'RouteOptimizerAgent'
            }
            
            # Generate alternative suggestions
            for i, leg in enumerate(legs):
                origin = leg.get('origin')
                destination = leg.get('destination')
                current_transport = leg.get('transport_type')
                
                # Find alternative transport modes
                distance_km = self._calculate_distance(origin, destination)
                transport_alternatives = []
                
                for transport_type, config in self.transport_configs.items():
                    if (transport_type != current_transport and 
                        self._is_transport_viable(transport_type, distance_km, origin, destination)):
                        
                        alt_option = self._calculate_transport_option(
                            transport_type, origin, destination, distance_km, 
                            leg.get('date', '2025-08-01'), config
                        )
                        transport_alternatives.append(alt_option)
                
                if transport_alternatives:
                    leg_alternatives = {
                        'leg_number': i + 1,
                        'current': leg,
                        'alternatives': transport_alternatives[:3]  # Top 3 alternatives
                    }
                    alternatives['alternatives'].append(leg_alternatives)
            
            # Generate recommendations
            recommendations = []
            
            # Cost optimization recommendation
            total_savings = 0
            for alt in alternatives['alternatives']:
                if alt['alternatives']:
                    cheapest = min(alt['alternatives'], key=lambda x: x['cost'])
                    current_cost = float(alt['current'].get('cost', '0').replace('$', ''))
                    savings = current_cost - cheapest['cost']
                    if savings > 0:
                        total_savings += savings
                        recommendations.append({
                            'type': 'cost_optimization',
                            'leg': alt['leg_number'],
                            'suggestion': f"Switch from {alt['current']['transport_type']} to {cheapest['type']}",
                            'savings': f"${savings:.2f}",
                            'trade_off': f"Additional {cheapest['duration_hours'] - float(alt['current'].get('duration', '0h').replace('h', '')):.1f} hours"
                        })
            
            if total_savings > 0:
                recommendations.insert(0, {
                    'type': 'overall_savings',
                    'suggestion': f"Total potential savings: ${total_savings:.2f}",
                    'priority': 'high'
                })
            
            alternatives['recommendations'] = recommendations
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Route Optimizer Agent: Route analysis error: {str(e)}")
            return {'status': 'error', 'message': f'Route analysis failed: {str(e)}'}