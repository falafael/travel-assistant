#!/usr/bin/env python3
"""
Data Fetcher Agent
Specialized agent for handling all API calls, web scraping, and data retrieval
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import quote
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class DataFetcherAgent:
    """
    Autonomous agent responsible for fetching travel data from various sources
    Handles API calls, web scraping, rate limiting, and data normalization
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # API configurations and rate limits
        self.api_configs = {
            'flights': {
                'primary': 'skyscanner',
                'fallbacks': ['google_flights', 'kayak', 'expedia'],
                'rate_limit': 10,  # requests per minute
                'timeout': 30
            },
            'hotels': {
                'primary': 'booking',
                'fallbacks': ['hotels_com', 'airbnb', 'agoda'],
                'rate_limit': 15,
                'timeout': 25
            },
            'ground_transport': {
                'primary': 'multiple',
                'fallbacks': [],
                'rate_limit': 20,
                'timeout': 20
            },
            'activities': {
                'primary': 'viator',
                'fallbacks': ['getyourguide', 'klook'],
                'rate_limit': 12,
                'timeout': 25
            }
        }
        
        # Cache for reducing API calls
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Executor for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def fetch_flight_data(self, search_params: Dict) -> Dict:
        """
        Fetch flight data from multiple sources in parallel
        """
        try:
            logger.info(f"Data Fetcher Agent: Starting flight search for {search_params.get('origin')} → {search_params.get('destination')}")
            
            # Check cache first
            cache_key = f"flights:{search_params.get('origin')}:{search_params.get('destination')}:{search_params.get('departure_date')}"
            if self._is_cached(cache_key):
                logger.info("Data Fetcher Agent: Returning cached flight data")
                return self.cache[cache_key]['data']
            
            # Parallel API calls to multiple flight sources
            flight_sources = [
                self._fetch_from_source('skyscanner', 'flights', search_params),
                self._fetch_from_source('google_flights', 'flights', search_params),
                self._fetch_from_source('kayak', 'flights', search_params),
                self._fetch_from_source('expedia', 'flights', search_params)
            ]
            
            # Execute parallel requests
            results = await asyncio.gather(*flight_sources, return_exceptions=True)
            
            # Process and normalize results
            normalized_results = self._normalize_flight_results(results, search_params)
            
            # Cache results
            self._cache_result(cache_key, normalized_results)
            
            logger.info(f"Data Fetcher Agent: Successfully fetched {len(normalized_results.get('results', []))} flight options")
            return normalized_results
            
        except Exception as e:
            logger.error(f"Data Fetcher Agent: Flight fetch error: {str(e)}")
            return self._error_response(f"Flight data fetch failed: {str(e)}")

    async def fetch_hotel_data(self, search_params: Dict) -> Dict:
        """
        Fetch accommodation data from multiple sources
        """
        try:
            logger.info(f"Data Fetcher Agent: Starting hotel search for {search_params.get('destination')}")
            
            cache_key = f"hotels:{search_params.get('destination')}:{search_params.get('checkin')}:{search_params.get('checkout')}"
            if self._is_cached(cache_key):
                logger.info("Data Fetcher Agent: Returning cached hotel data")
                return self.cache[cache_key]['data']
            
            # Parallel API calls
            hotel_sources = [
                self._fetch_from_source('booking', 'hotels', search_params),
                self._fetch_from_source('hotels_com', 'hotels', search_params),
                self._fetch_from_source('airbnb', 'hotels', search_params),
                self._fetch_from_source('agoda', 'hotels', search_params)
            ]
            
            results = await asyncio.gather(*hotel_sources, return_exceptions=True)
            normalized_results = self._normalize_hotel_results(results, search_params)
            
            self._cache_result(cache_key, normalized_results)
            
            logger.info(f"Data Fetcher Agent: Successfully fetched {len(normalized_results.get('results', []))} accommodation options")
            return normalized_results
            
        except Exception as e:
            logger.error(f"Data Fetcher Agent: Hotel fetch error: {str(e)}")
            return self._error_response(f"Hotel data fetch failed: {str(e)}")

    async def fetch_ground_transport_data(self, search_params: Dict) -> Dict:
        """
        Fetch ground transportation options
        """
        try:
            logger.info(f"Data Fetcher Agent: Starting ground transport search")
            
            cache_key = f"ground:{search_params.get('pickup')}:{search_params.get('dropoff')}:{search_params.get('pickup_date')}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            # Fetch different transport types in parallel
            transport_sources = [
                self._fetch_car_rentals(search_params),
                self._fetch_train_options(search_params),
                self._fetch_bus_options(search_params),
                self._fetch_rideshare_estimates(search_params)
            ]
            
            results = await asyncio.gather(*transport_sources, return_exceptions=True)
            normalized_results = self._normalize_transport_results(results, search_params)
            
            self._cache_result(cache_key, normalized_results)
            
            return normalized_results
            
        except Exception as e:
            logger.error(f"Data Fetcher Agent: Ground transport fetch error: {str(e)}")
            return self._error_response(f"Ground transport data fetch failed: {str(e)}")

    async def fetch_activity_data(self, search_params: Dict) -> Dict:
        """
        Fetch tours and activities data
        """
        try:
            logger.info(f"Data Fetcher Agent: Starting activity search for {search_params.get('destination')}")
            
            cache_key = f"activities:{search_params.get('destination')}:{search_params.get('activity_type', 'all')}"
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            activity_sources = [
                self._fetch_from_source('viator', 'activities', search_params),
                self._fetch_from_source('getyourguide', 'activities', search_params),
                self._fetch_from_source('klook', 'activities', search_params),
                self._fetch_from_source('airbnb_experiences', 'activities', search_params)
            ]
            
            results = await asyncio.gather(*activity_sources, return_exceptions=True)
            normalized_results = self._normalize_activity_results(results, search_params)
            
            self._cache_result(cache_key, normalized_results)
            
            return normalized_results
            
        except Exception as e:
            logger.error(f"Data Fetcher Agent: Activity fetch error: {str(e)}")
            return self._error_response(f"Activity data fetch failed: {str(e)}")

    async def _fetch_from_source(self, source: str, data_type: str, params: Dict) -> Dict:
        """
        Generic method to fetch data from a specific source
        In production, this would make actual API calls
        """
        try:
            # Simulate API call delay
            await asyncio.sleep(0.5)  # Real APIs would have actual network delay
            
            # This is where real API integration would happen
            if source == 'skyscanner' and data_type == 'flights':
                return self._mock_skyscanner_flights(params)
            elif source == 'booking' and data_type == 'hotels':
                return self._mock_booking_hotels(params)
            elif source == 'viator' and data_type == 'activities':
                return self._mock_viator_activities(params)
            else:
                return self._mock_generic_response(source, data_type, params)
                
        except Exception as e:
            logger.error(f"Data Fetcher Agent: Error fetching from {source}: {str(e)}")
            return {'status': 'error', 'source': source, 'message': str(e)}

    def _mock_skyscanner_flights(self, params: Dict) -> Dict:
        """Mock Skyscanner API response"""
        return {
            'status': 'success',
            'source': 'skyscanner',
            'results': [
                {
                    'airline': 'Delta Air Lines',
                    'flight_number': 'DL 1234',
                    'price': 420,
                    'currency': 'USD',
                    'departure_time': '08:30',
                    'arrival_time': '14:45',
                    'duration_minutes': 375,
                    'stops': 0,
                    'aircraft': 'Boeing 737',
                    'booking_url': f"https://www.skyscanner.com/transport/flights/{params.get('origin')}/{params.get('destination')}/{params.get('departure_date')}"
                }
            ]
        }

    def _mock_booking_hotels(self, params: Dict) -> Dict:
        """Mock Booking.com API response"""
        return {
            'status': 'success',
            'source': 'booking',
            'results': [
                {
                    'name': 'Grand Plaza Hotel',
                    'type': 'Hotel',
                    'rating': 4.5,
                    'price_per_night': 120,
                    'currency': 'USD',
                    'amenities': ['WiFi', 'Pool', 'Gym', 'Breakfast'],
                    'distance_km': 0.8,
                    'guest_rating': 8.7,
                    'booking_url': f"https://www.booking.com/hotel?destination={quote(params.get('destination', ''))}"
                }
            ]
        }

    def _mock_viator_activities(self, params: Dict) -> Dict:
        """Mock Viator API response"""
        return {
            'status': 'success',
            'source': 'viator',
            'results': [
                {
                    'name': f"{params.get('destination', 'City')} Walking Tour",
                    'type': 'Walking Tour',
                    'duration_hours': 3,
                    'price': 35,
                    'currency': 'USD',
                    'rating': 4.7,
                    'highlights': ['Historic Downtown', 'Local Markets', 'Architecture'],
                    'group_size_max': 15,
                    'booking_url': f"https://www.viator.com/tours/{quote(params.get('destination', ''))}"
                }
            ]
        }

    def _mock_generic_response(self, source: str, data_type: str, params: Dict) -> Dict:
        """Generic mock response for other sources"""
        return {
            'status': 'success',
            'source': source,
            'results': [],
            'message': f'Mock data from {source} for {data_type}'
        }

    async def _fetch_car_rentals(self, params: Dict) -> Dict:
        """Fetch car rental options"""
        await asyncio.sleep(0.3)
        return {
            'status': 'success',
            'type': 'car_rentals',
            'results': [
                {
                    'provider': 'Enterprise',
                    'vehicle_class': 'Economy',
                    'vehicle_model': 'Nissan Versa or similar',
                    'price_per_day': 45,
                    'total_estimated': 315,
                    'features': ['Unlimited Miles', 'Free Pickup'],
                    'booking_url': f"https://www.enterprise.com/car-rental?pickup={quote(params.get('pickup', ''))}"
                }
            ]
        }

    async def _fetch_train_options(self, params: Dict) -> Dict:
        """Fetch train travel options"""
        await asyncio.sleep(0.4)
        return {
            'status': 'success',
            'type': 'trains',
            'results': [
                {
                    'provider': 'Amtrak',
                    'route': f"{params.get('pickup', '')} → {params.get('dropoff', '')}",
                    'price': 89,
                    'duration_minutes': 330,
                    'departure_time': '08:15',
                    'arrival_time': '13:45',
                    'features': ['WiFi', 'Food Service', 'Power Outlets'],
                    'booking_url': f"https://www.amtrak.com/tickets/departure/{quote(params.get('pickup', ''))}"
                }
            ]
        }

    async def _fetch_bus_options(self, params: Dict) -> Dict:
        """Fetch bus travel options"""
        await asyncio.sleep(0.3)
        return {
            'status': 'success',
            'type': 'buses',
            'results': [
                {
                    'provider': 'Greyhound',
                    'route': f"{params.get('pickup', '')} → {params.get('dropoff', '')}",
                    'price': 45,
                    'duration_minutes': 375,
                    'departure_time': '09:30',
                    'arrival_time': '15:45',
                    'features': ['WiFi', 'Power Outlets', 'Restroom'],
                    'booking_url': f"https://www.greyhound.com/schedules-and-tickets"
                }
            ]
        }

    async def _fetch_rideshare_estimates(self, params: Dict) -> Dict:
        """Fetch rideshare price estimates"""
        await asyncio.sleep(0.2)
        return {
            'status': 'success',
            'type': 'rideshare',
            'results': [
                {
                    'provider': 'Uber',
                    'service': 'UberX',
                    'price_min': 25,
                    'price_max': 35,
                    'duration_minutes': 40,
                    'features': ['Door-to-door', 'Real-time tracking'],
                    'booking_url': 'https://www.uber.com/'
                }
            ]
        }

    def _normalize_flight_results(self, results: List[Any], params: Dict) -> Dict:
        """Normalize flight results from multiple sources"""
        normalized = {
            'status': 'success',
            'travel_type': 'flights',
            'search_params': params,
            'results': [],
            'sources_used': []
        }
        
        for result in results:
            if isinstance(result, dict) and result.get('status') == 'success':
                normalized['sources_used'].append(result.get('source', 'unknown'))
                for flight in result.get('results', []):
                    normalized_flight = {
                        'airline': flight.get('airline'),
                        'flight_number': flight.get('flight_number'),
                        'price': f"${flight.get('price', 0)}",
                        'departure_time': flight.get('departure_time'),
                        'arrival_time': flight.get('arrival_time'),
                        'duration': self._format_duration(flight.get('duration_minutes', 0)),
                        'stops': 'Nonstop' if flight.get('stops', 0) == 0 else f"{flight.get('stops')} stop(s)",
                        'aircraft': flight.get('aircraft'),
                        'booking_url': flight.get('booking_url'),
                        'source': result.get('source')
                    }
                    normalized['results'].append(normalized_flight)
        
        return normalized

    def _normalize_hotel_results(self, results: List[Any], params: Dict) -> Dict:
        """Normalize hotel results from multiple sources"""
        normalized = {
            'status': 'success',
            'travel_type': 'hotels',
            'search_params': params,
            'results': [],
            'sources_used': []
        }
        
        nights = self._calculate_nights(params.get('checkin', ''), params.get('checkout', ''))
        
        for result in results:
            if isinstance(result, dict) and result.get('status') == 'success':
                normalized['sources_used'].append(result.get('source', 'unknown'))
                for hotel in result.get('results', []):
                    normalized_hotel = {
                        'name': hotel.get('name'),
                        'type': hotel.get('type', 'Hotel'),
                        'rating': hotel.get('rating'),
                        'price_per_night': f"${hotel.get('price_per_night', 0)}",
                        'total_price': f"${hotel.get('price_per_night', 0) * nights}",
                        'amenities': hotel.get('amenities', []),
                        'distance_from_center': f"{hotel.get('distance_km', 0)} km",
                        'guest_rating': f"{hotel.get('guest_rating', 0)}/10",
                        'booking_url': hotel.get('booking_url'),
                        'source': result.get('source')
                    }
                    normalized['results'].append(normalized_hotel)
        
        return normalized

    def _normalize_transport_results(self, results: List[Any], params: Dict) -> Dict:
        """Normalize ground transportation results"""
        normalized = {
            'status': 'success',
            'travel_type': 'ground_transportation',
            'search_params': params,
            'results': [],
            'categories': {'car_rentals': 0, 'trains': 0, 'buses': 0, 'rideshare': 0}
        }
        
        for result in results:
            if isinstance(result, dict) and result.get('status') == 'success':
                transport_type = result.get('type')
                if transport_type in normalized['categories']:
                    normalized['categories'][transport_type] += len(result.get('results', []))
                
                for transport in result.get('results', []):
                    normalized_transport = {
                        'provider': transport.get('provider'),
                        'type': transport_type.replace('_', ' ').title(),
                        'vehicle': transport.get('vehicle_model') or transport.get('service'),
                        'price': f"${transport.get('price', transport.get('price_per_day', 0))}",
                        'price_estimate': f"${transport.get('price_min', 0)}-{transport.get('price_max', 0)}" if 'price_min' in transport else None,
                        'duration': self._format_duration(transport.get('duration_minutes', 0)),
                        'departure': transport.get('departure_time'),
                        'features': transport.get('features', []),
                        'booking_url': transport.get('booking_url')
                    }
                    normalized['results'].append(normalized_transport)
        
        return normalized

    def _normalize_activity_results(self, results: List[Any], params: Dict) -> Dict:
        """Normalize tours and activities results"""
        normalized = {
            'status': 'success',
            'travel_type': 'tours_activities',
            'search_params': params,
            'results': [],
            'sources_used': []
        }
        
        for result in results:
            if isinstance(result, dict) and result.get('status') == 'success':
                normalized['sources_used'].append(result.get('source', 'unknown'))
                for activity in result.get('results', []):
                    normalized_activity = {
                        'provider': result.get('source', 'Unknown').title(),
                        'name': activity.get('name'),
                        'type': activity.get('type'),
                        'duration': f"{activity.get('duration_hours', 0)} hours",
                        'price': f"${activity.get('price', 0)}",
                        'rating': activity.get('rating'),
                        'highlights': activity.get('highlights', []),
                        'group_size': f"Small (max {activity.get('group_size_max', 0)})",
                        'booking_url': activity.get('booking_url')
                    }
                    normalized['results'].append(normalized_activity)
        
        return normalized

    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (datetime.now().timestamp() - cache_time) < self.cache_ttl

    def _cache_result(self, cache_key: str, data: Dict) -> None:
        """Cache result with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }

    def _format_duration(self, minutes: int) -> str:
        """Format duration from minutes to hours and minutes"""
        if minutes == 0:
            return "Unknown"
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
        return f"{mins}m"

    def _calculate_nights(self, checkin: str, checkout: str) -> int:
        """Calculate number of nights between dates"""
        try:
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
            return max(1, (checkout_date - checkin_date).days)
        except:
            return 3  # Default fallback

    def _error_response(self, message: str) -> Dict:
        """Standard error response format"""
        return {
            'status': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

    async def comprehensive_fetch(self, search_params: Dict) -> Dict:
        """
        Main method to fetch all requested travel data types
        Coordinates parallel fetching across multiple data types
        """
        logger.info("Data Fetcher Agent: Starting comprehensive data fetch")
        
        fetch_tasks = []
        
        # Add tasks based on requested data types
        if search_params.get('include_flights', False):
            fetch_tasks.append(('flights', self.fetch_flight_data(search_params)))
        
        if search_params.get('include_hotels', False):
            fetch_tasks.append(('hotels', self.fetch_hotel_data(search_params)))
        
        if search_params.get('include_ground_transport', False):
            ground_params = {
                'pickup': search_params.get('origin'),
                'dropoff': search_params.get('destination'),
                'pickup_date': search_params.get('departure_date')
            }
            fetch_tasks.append(('ground_transportation', self.fetch_ground_transport_data(ground_params)))
        
        if search_params.get('include_activities', False):
            activity_params = {
                'destination': search_params.get('destination'),
                'activity_type': search_params.get('activity_type', 'all')
            }
            fetch_tasks.append(('tours_activities', self.fetch_activity_data(activity_params)))
        
        if not fetch_tasks:
            return self._error_response("No data types requested")
        
        # Execute all fetch tasks in parallel
        task_names, tasks = zip(*fetch_tasks)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        compiled_results = {
            'timestamp': datetime.now().isoformat(),
            'search_params': search_params,
            'results': {},
            'agent': 'DataFetcherAgent'
        }
        
        for task_name, result in zip(task_names, results):
            if isinstance(result, dict):
                compiled_results['results'][task_name] = result
            else:
                compiled_results['results'][task_name] = self._error_response(f"Task {task_name} failed: {str(result)}")
        
        logger.info(f"Data Fetcher Agent: Completed comprehensive fetch with {len(compiled_results['results'])} data types")
        return compiled_results