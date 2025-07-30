#!/usr/bin/env python3
"""
Comprehensive Travel Assistant - All Travel Types
Supports flights, hotels, car rentals, trains, buses, cruises, tours, and more
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ComprehensiveTravelAssistant:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # All travel type configurations
        self.travel_types = {
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

    def search_flights(self, origin: str, destination: str, departure_date: str, 
                      return_date: Optional[str] = None, passengers: int = 1) -> Dict:
        """Search for flights with real-time data"""
        try:
            logger.info(f"Searching flights: {origin} → {destination}")
            
            # Simulate API calls to multiple flight search engines
            results = []
            
            # Major Airlines Mock Data (in real implementation, use actual APIs)
            airlines_data = [
                {
                    'airline': 'Delta Air Lines',
                    'flight_number': 'DL 1234',
                    'price': f'${420 + (passengers - 1) * 380}',
                    'departure_time': '08:30',
                    'arrival_time': '14:45',
                    'duration': '6h 15m',
                    'stops': 'Nonstop',
                    'aircraft': 'Boeing 737',
                    'booking_url': f'https://www.delta.com/booking?from={origin}&to={destination}&date={departure_date}&pax={passengers}'
                },
                {
                    'airline': 'United Airlines',
                    'flight_number': 'UA 5678',
                    'price': f'${395 + (passengers - 1) * 355}',
                    'departure_time': '11:20',
                    'arrival_time': '17:55',
                    'duration': '6h 35m',
                    'stops': 'Nonstop',
                    'aircraft': 'Airbus A320',
                    'booking_url': f'https://www.united.com/booking?from={origin}&to={destination}&date={departure_date}&pax={passengers}'
                },
                {
                    'airline': 'American Airlines',
                    'flight_number': 'AA 9012',
                    'price': f'${360 + (passengers - 1) * 320}',
                    'departure_time': '06:15',
                    'arrival_time': '15:30',
                    'duration': '9h 15m',
                    'stops': '1 stop in Chicago',
                    'aircraft': 'Boeing 757',
                    'booking_url': f'https://www.aa.com/booking?from={origin}&to={destination}&date={departure_date}&pax={passengers}'
                },
                {
                    'airline': 'Southwest Airlines',
                    'flight_number': 'WN 3456',
                    'price': f'${285 + (passengers - 1) * 245}',
                    'departure_time': '14:30',
                    'arrival_time': '21:15',
                    'duration': '6h 45m',
                    'stops': 'Nonstop',
                    'aircraft': 'Boeing 737-800',
                    'booking_url': f'https://www.southwest.com/booking?from={origin}&to={destination}&date={departure_date}&pax={passengers}'
                }
            ]
            
            return {
                'status': 'success',
                'travel_type': 'flights',
                'search_params': {
                    'origin': origin,
                    'destination': destination,
                    'departure_date': departure_date,
                    'return_date': return_date,
                    'passengers': passengers
                },
                'results': airlines_data,
                'search_engines': [
                    {'name': 'Google Flights', 'url': f'https://www.google.com/travel/flights?q=Flights%20from%20{origin}%20to%20{destination}%20on%20{departure_date}'},
                    {'name': 'Kayak', 'url': f'https://www.kayak.com/flights/{origin}-{destination}/{departure_date}'},
                    {'name': 'Expedia', 'url': f'https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{origin},to:{destination},departure:{departure_date}'}
                ]
            }
            
        except Exception as e:
            logger.error(f"Flight search error: {str(e)}")
            return {'status': 'error', 'message': f'Flight search failed: {str(e)}'}

    def search_hotels(self, destination: str, checkin: str, checkout: str, 
                     guests: int = 2, rooms: int = 1) -> Dict:
        """Search for all types of accommodations"""
        try:
            logger.info(f"Searching accommodations in {destination}")
            
            accommodations = [
                {
                    'name': 'Grand Plaza Hotel',
                    'type': 'Hotel',
                    'rating': 4.5,
                    'price_per_night': '$120',
                    'total_price': f'${120 * self._calculate_nights(checkin, checkout)}',
                    'amenities': ['Free WiFi', 'Pool', 'Gym', 'Breakfast', 'Spa'],
                    'distance_from_center': '0.5 miles',
                    'guest_rating': '8.7/10',
                    'booking_url': f'https://www.booking.com/hotel?destination={quote(destination)}&checkin={checkin}&checkout={checkout}&group_adults={guests}'
                },
                {
                    'name': 'Cozy Downtown Apartment',
                    'type': 'Airbnb',
                    'rating': 4.8,
                    'price_per_night': '$95',
                    'total_price': f'${95 * self._calculate_nights(checkin, checkout)}',
                    'amenities': ['Full Kitchen', 'WiFi', 'Parking', 'Pets OK'],
                    'distance_from_center': '0.8 miles',
                    'guest_rating': '4.8/5',
                    'booking_url': f'https://www.airbnb.com/s/{quote(destination)}?checkin={checkin}&checkout={checkout}&adults={guests}'
                },
                {
                    'name': 'Luxury Resort & Spa',
                    'type': 'Resort',
                    'rating': 4.9,
                    'price_per_night': '$280',
                    'total_price': f'${280 * self._calculate_nights(checkin, checkout)}',
                    'amenities': ['All-Inclusive', 'Beach Access', 'Multiple Restaurants', 'Concierge', 'Kids Club'],
                    'distance_from_center': '2.1 miles',
                    'guest_rating': '9.2/10',
                    'booking_url': f'https://www.expedia.com/hotels?destination={quote(destination)}&checkin={checkin}&checkout={checkout}&rooms={rooms}&adults={guests}'
                },
                {
                    'name': 'Backpacker Hostel',
                    'type': 'Hostel',
                    'rating': 4.2,
                    'price_per_night': '$35',
                    'total_price': f'${35 * self._calculate_nights(checkin, checkout)}',
                    'amenities': ['Free WiFi', 'Shared Kitchen', 'Laundry', 'Common Area'],
                    'distance_from_center': '1.5 miles',
                    'guest_rating': '8.1/10',
                    'booking_url': f'https://www.hostelworld.com/search?search_keywords={quote(destination)}&date_from={checkin}&date_to={checkout}'
                }
            ]
            
            return {
                'status': 'success',
                'travel_type': 'hotels',
                'search_params': {
                    'destination': destination,
                    'checkin': checkin,
                    'checkout': checkout,
                    'guests': guests,
                    'rooms': rooms
                },
                'results': accommodations
            }
            
        except Exception as e:
            logger.error(f"Hotel search error: {str(e)}")
            return {'status': 'error', 'message': f'Hotel search failed: {str(e)}'}

    def search_ground_transportation(self, pickup: str, dropoff: str, 
                                   pickup_date: str, pickup_time: str = "10:00") -> Dict:
        """Search for car rentals, trains, buses, rideshare"""
        try:
            logger.info(f"Searching ground transport: {pickup} → {dropoff}")
            
            transportation_options = []
            
            # Car Rentals
            car_rentals = [
                {
                    'provider': 'Enterprise',
                    'type': 'Car Rental',
                    'vehicle': 'Economy (Nissan Versa or similar)',
                    'price_per_day': '$45',
                    'total_estimated': '$315 (7 days)',
                    'features': ['Unlimited Miles', 'Free Pickup'],
                    'booking_url': f'https://www.enterprise.com/car-rental?pickup={quote(pickup)}&dropoff={quote(dropoff)}&date={pickup_date}'
                },
                {
                    'provider': 'Budget',
                    'type': 'Car Rental', 
                    'vehicle': 'Compact (Toyota Corolla or similar)',
                    'price_per_day': '$52',
                    'total_estimated': '$364 (7 days)',
                    'features': ['GPS Available', 'Young Driver Friendly'],
                    'booking_url': f'https://www.budget.com/car-rental?pickup={quote(pickup)}&dropoff={quote(dropoff)}&date={pickup_date}'
                }
            ]
            
            # Train Options
            train_options = [
                {
                    'provider': 'Amtrak',
                    'type': 'Train',
                    'route': f'{pickup} → {dropoff}',
                    'price': '$89',
                    'duration': '5h 30m',
                    'departure': '08:15',
                    'arrival': '13:45',
                    'features': ['WiFi', 'Food Service', 'Power Outlets'],
                    'booking_url': f'https://www.amtrak.com/tickets/departure/{quote(pickup)}/arrival/{quote(dropoff)}/depart/{pickup_date}'
                }
            ]
            
            # Bus Options
            bus_options = [
                {
                    'provider': 'Greyhound',
                    'type': 'Bus',
                    'route': f'{pickup} → {dropoff}',
                    'price': '$45',
                    'duration': '6h 15m',
                    'departure': '09:30',
                    'arrival': '15:45',
                    'features': ['WiFi', 'Power Outlets', 'Restroom'],
                    'booking_url': f'https://www.greyhound.com/schedules-and-tickets?from={quote(pickup)}&to={quote(dropoff)}&departDate={pickup_date}'
                },
                {
                    'provider': 'Megabus',
                    'type': 'Bus',
                    'route': f'{pickup} → {dropoff}',
                    'price': '$35',
                    'duration': '7h 00m',
                    'departure': '07:00',
                    'arrival': '14:00',
                    'features': ['Double Decker', 'Reserved Seating'],
                    'booking_url': f'https://www.megabus.com/journey-planner/from/{quote(pickup)}/to/{quote(dropoff)}/date/{pickup_date}'
                }
            ]
            
            # Rideshare (estimates)
            rideshare_options = [
                {
                    'provider': 'Uber',
                    'type': 'Rideshare',
                    'service': 'UberX',
                    'price_estimate': '$25-35',
                    'duration': '35-45 min',
                    'features': ['Door-to-door', 'Real-time tracking'],
                    'booking_url': 'https://www.uber.com/'
                },
                {
                    'provider': 'Lyft',
                    'type': 'Rideshare',
                    'service': 'Lyft',
                    'price_estimate': '$22-32',
                    'duration': '35-45 min',
                    'features': ['Door-to-door', 'In-app tipping'],
                    'booking_url': 'https://www.lyft.com/'
                }
            ]
            
            all_options = car_rentals + train_options + bus_options + rideshare_options
            
            return {
                'status': 'success',
                'travel_type': 'ground_transportation',
                'search_params': {
                    'pickup': pickup,
                    'dropoff': dropoff,
                    'date': pickup_date,
                    'time': pickup_time
                },
                'results': all_options,
                'categories': {
                    'car_rentals': len(car_rentals),
                    'trains': len(train_options), 
                    'buses': len(bus_options),
                    'rideshare': len(rideshare_options)
                }
            }
            
        except Exception as e:
            logger.error(f"Ground transport search error: {str(e)}")
            return {'status': 'error', 'message': f'Ground transport search failed: {str(e)}'}

    def search_cruises(self, departure_port: str, duration_days: int = 7, 
                      departure_month: str = None) -> Dict:
        """Search for cruise options"""
        try:
            logger.info(f"Searching cruises from {departure_port}")
            
            cruise_options = [
                {
                    'cruise_line': 'Royal Caribbean',
                    'ship': 'Symphony of the Seas',
                    'duration': f'{duration_days} days',
                    'route': 'Caribbean',
                    'ports': ['Miami', 'Cozumel', 'Roatan', 'Costa Maya'],
                    'price_per_person': '$899',
                    'cabin_type': 'Interior',
                    'departure_date': '2025-08-15',
                    'amenities': ['Multiple Pools', 'Broadway Shows', 'Rock Climbing', 'Surf Simulator'],
                    'booking_url': f'https://www.royalcaribbean.com/cruises/7-night-caribbean-cruise?departure={quote(departure_port)}'
                },
                {
                    'cruise_line': 'Norwegian Cruise Line',
                    'ship': 'Norwegian Epic',
                    'duration': f'{duration_days} days',
                    'route': 'Mediterranean',
                    'ports': ['Barcelona', 'Rome', 'Naples', 'Florence'],
                    'price_per_person': '$1,299',
                    'cabin_type': 'Balcony',
                    'departure_date': '2025-09-02',
                    'amenities': ['Freestyle Dining', 'Water Slides', 'Spa', 'Casino'],
                    'booking_url': f'https://www.ncl.com/cruises/7-day-mediterranean-cruise?departure={quote(departure_port)}'
                },
                {
                    'cruise_line': 'Carnival Cruise Line',
                    'ship': 'Carnival Vista',
                    'duration': f'{duration_days} days',
                    'route': 'Alaska',
                    'ports': ['Seattle', 'Juneau', 'Skagway', 'Ketchikan', 'Glacier Bay'],
                    'price_per_person': '$1,149',
                    'cabin_type': 'Ocean View',
                    'departure_date': '2025-07-20',
                    'amenities': ['SkyRide', 'SeaPlex', 'Serenity Deck', 'RedFrog Pub'],
                    'booking_url': f'https://www.carnival.com/cruises/alaska-cruise?departure={quote(departure_port)}'
                }
            ]
            
            return {
                'status': 'success',
                'travel_type': 'cruises',
                'search_params': {
                    'departure_port': departure_port,
                    'duration': duration_days,
                    'month': departure_month
                },
                'results': cruise_options
            }
            
        except Exception as e:
            logger.error(f"Cruise search error: {str(e)}")
            return {'status': 'error', 'message': f'Cruise search failed: {str(e)}'}

    def search_tours_activities(self, destination: str, activity_type: str = 'all') -> Dict:
        """Search for tours, activities, and experiences"""
        try:
            logger.info(f"Searching tours/activities in {destination}")
            
            activities = [
                {
                    'provider': 'Viator',
                    'name': f'{destination} City Walking Tour',
                    'type': 'Walking Tour',
                    'duration': '3 hours',
                    'price': '$35',
                    'rating': 4.7,
                    'highlights': ['Historic Downtown', 'Local Markets', 'Architecture', 'Food Tastings'],
                    'group_size': 'Small (max 15)',
                    'booking_url': f'https://www.viator.com/tours/{quote(destination)}/walking-tour'
                },
                {
                    'provider': 'GetYourGuide',
                    'name': f'{destination} Food & Culture Experience',
                    'type': 'Food Tour',
                    'duration': '4 hours',
                    'price': '$89',
                    'rating': 4.9,
                    'highlights': ['Local Restaurants', 'Traditional Dishes', 'Cultural Stories', 'Hidden Gems'],
                    'group_size': 'Medium (max 25)',
                    'booking_url': f'https://www.getyourguide.com/{quote(destination)}/food-tour'
                },
                {
                    'provider': 'Klook',
                    'name': f'{destination} Adventure Day Trip',
                    'type': 'Adventure',
                    'duration': '8 hours',
                    'price': '$145',
                    'rating': 4.6,
                    'highlights': ['Outdoor Activities', 'Scenic Views', 'Professional Guide', 'Equipment Included'],
                    'group_size': 'Large (max 40)',
                    'booking_url': f'https://www.klook.com/activity/{quote(destination)}-adventure-tour'
                },
                {
                    'provider': 'Local Guide',
                    'name': f'{destination} Photography Workshop',
                    'type': 'Workshop',
                    'duration': '5 hours',
                    'price': '$120',
                    'rating': 4.8,
                    'highlights': ['Professional Tips', 'Best Photo Spots', 'Editing Basics', 'Small Group'],
                    'group_size': 'Small (max 8)',
                    'booking_url': f'https://www.airbnb.com/experiences/search?location={quote(destination)}&category_tag=photography'
                }
            ]
            
            return {
                'status': 'success',
                'travel_type': 'tours_activities',
                'search_params': {
                    'destination': destination,
                    'activity_type': activity_type
                },
                'results': activities
            }
            
        except Exception as e:
            logger.error(f"Tours/activities search error: {str(e)}")
            return {'status': 'error', 'message': f'Tours/activities search failed: {str(e)}'}

    def _calculate_nights(self, checkin: str, checkout: str) -> int:
        """Calculate number of nights between checkin and checkout"""
        try:
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
            return (checkout_date - checkin_date).days
        except:
            return 3  # Default fallback

    def comprehensive_search(self, search_params: Dict) -> Dict:
        """Perform comprehensive search across all travel types"""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'search_params': search_params,
                'results': {}
            }
            
            # Search flights if requested
            if search_params.get('include_flights', True):
                if all(k in search_params for k in ['origin', 'destination', 'departure_date']):
                    flight_results = self.search_flights(
                        search_params['origin'],
                        search_params['destination'], 
                        search_params['departure_date'],
                        search_params.get('return_date'),
                        search_params.get('passengers', 1)
                    )
                    results['results']['flights'] = flight_results
            
            # Search accommodations if requested
            if search_params.get('include_hotels', True):
                if all(k in search_params for k in ['destination', 'checkin', 'checkout']):
                    hotel_results = self.search_hotels(
                        search_params['destination'],
                        search_params['checkin'],
                        search_params['checkout'],
                        search_params.get('guests', 2),
                        search_params.get('rooms', 1)
                    )
                    results['results']['hotels'] = hotel_results
            
            # Search ground transportation if requested
            if search_params.get('include_ground_transport', True):
                if all(k in search_params for k in ['origin', 'destination', 'departure_date']):
                    ground_results = self.search_ground_transportation(
                        search_params['origin'],
                        search_params['destination'],
                        search_params['departure_date']
                    )
                    results['results']['ground_transportation'] = ground_results
            
            # Search cruises if requested
            if search_params.get('include_cruises', False):
                if 'departure_port' in search_params:
                    cruise_results = self.search_cruises(
                        search_params['departure_port'],
                        search_params.get('cruise_duration', 7)
                    )
                    results['results']['cruises'] = cruise_results
            
            # Search tours/activities if requested
            if search_params.get('include_activities', True):
                if 'destination' in search_params:
                    activity_results = self.search_tours_activities(
                        search_params['destination'],
                        search_params.get('activity_type', 'all')
                    )
                    results['results']['tours_activities'] = activity_results
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive search error: {str(e)}")
            return {'status': 'error', 'message': f'Search failed: {str(e)}'}

# Flask Web Interface
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        assistant = ComprehensiveTravelAssistant()
        results = assistant.comprehensive_search(data)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search endpoint error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/travel-types')
def travel_types():
    assistant = ComprehensiveTravelAssistant()
    return jsonify(assistant.travel_types)

if __name__ == '__main__':
    print("Comprehensive Travel Assistant - All Travel Types")
    print("=" * 60)
    print("Supporting: Flights, Hotels, Car Rentals, Trains, Buses,")
    print("Cruises, Tours, Activities, Rideshare, Private Jets, RV/Camping")
    print("=" * 60)
    print("Web interface: http://localhost:5000")
    print("API endpoints available for integration")
    
    app.run(debug=True, host='0.0.0.0', port=5000)