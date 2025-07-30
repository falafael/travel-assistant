#!/usr/bin/env python3
"""
Deal Hunter Agent
Specialized agent for finding travel deals, tracking prices, and identifying savings opportunities
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
import asyncio
import json
from dataclasses import dataclass
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PriceAlert:
    """Represents a price tracking alert"""
    search_id: str
    travel_type: str
    route: str
    target_price: float
    current_price: float
    created_date: datetime
    alert_threshold: float

@dataclass
class Deal:
    """Represents a travel deal"""
    id: str
    title: str
    description: str
    original_price: float
    deal_price: float
    savings_amount: float
    savings_percentage: float
    valid_until: datetime
    travel_type: str
    destination: str
    deal_source: str
    booking_url: str

class DealHunterAgent:
    """
    Autonomous agent for finding deals, tracking prices, and optimizing savings
    Monitors price trends, identifies error fares, and provides deal recommendations
    """
    
    def __init__(self):
        # Price tracking storage (in production, would use database)
        self.price_history = {}
        self.active_alerts = {}
        self.deal_cache = {}
        
        # Deal source configurations
        self.deal_sources = {
            'airlines': [
                'delta', 'united', 'american', 'southwest', 'jetblue',
                'alaska', 'frontier', 'spirit'
            ],
            'hotels': [
                'booking', 'expedia', 'hotels_com', 'marriott', 'hilton',
                'hyatt', 'ihg', 'airbnb'
            ],
            'aggregators': [
                'kayak', 'priceline', 'orbitz', 'travelocity', 'momondo',
                'skyscanner', 'google_flights'
            ],
            'flash_deal_sites': [
                'secret_flying', 'scott_cheap_flights', 'travel_zoo',
                'groupon_getaways', 'living_social_escapes'
            ]
        }
        
        # Price thresholds for different travel types
        self.deal_thresholds = {
            'domestic_flights': {'excellent': 200, 'good': 300, 'fair': 400},
            'international_flights': {'excellent': 400, 'good': 600, 'fair': 800},
            'hotels': {'excellent': 80, 'good': 120, 'fair': 160},
            'car_rentals': {'excellent': 25, 'good': 40, 'fair': 60},
            'cruises': {'excellent': 500, 'good': 800, 'fair': 1200}
        }

    async def hunt_deals(self, search_params: Dict) -> Dict:
        """
        Main deal hunting method - finds current deals based on search parameters
        """
        try:
            logger.info("Deal Hunter Agent: Starting deal hunt")
            
            # Hunt for deals across different travel types
            deal_tasks = []
            
            if search_params.get('include_flights', False):
                deal_tasks.append(self._hunt_flight_deals(search_params))
            
            if search_params.get('include_hotels', False):
                deal_tasks.append(self._hunt_hotel_deals(search_params))
            
            if search_params.get('include_ground_transport', False):
                deal_tasks.append(self._hunt_transport_deals(search_params))
            
            # Add general destination deals
            if search_params.get('destination'):
                deal_tasks.append(self._hunt_destination_deals(search_params))
            
            # Execute deal hunting in parallel
            deal_results = await asyncio.gather(*deal_tasks, return_exceptions=True)
            
            # Compile and rank deals
            all_deals = []
            for result in deal_results:
                if isinstance(result, dict) and result.get('status') == 'success':
                    all_deals.extend(result.get('deals', []))
            
            # Rank deals by savings percentage
            ranked_deals = sorted(all_deals, key=lambda d: d.get('savings_percentage', 0), reverse=True)
            
            # Categorize deals
            categorized_deals = self._categorize_deals(ranked_deals)
            
            result = {
                'status': 'success',
                'hunt_type': 'comprehensive',
                'total_deals_found': len(all_deals),
                'search_params': search_params,
                'deals': {
                    'top_deals': ranked_deals[:10],
                    'by_category': categorized_deals,
                    'flash_deals': [d for d in ranked_deals if d.get('is_flash_deal', False)],
                    'error_fares': [d for d in ranked_deals if d.get('is_error_fare', False)]
                },
                'recommendations': self._generate_deal_recommendations(ranked_deals, search_params),
                'agent': 'DealHunterAgent'
            }
            
            logger.info(f"Deal Hunter Agent: Found {len(all_deals)} deals")
            return result
            
        except Exception as e:
            logger.error(f"Deal Hunter Agent: Deal hunting error: {str(e)}")
            return {'status': 'error', 'message': f'Deal hunting failed: {str(e)}'}

    async def track_prices(self, tracking_params: Dict) -> Dict:
        """
        Set up price tracking for specified routes and dates
        """
        try:
            logger.info("Deal Hunter Agent: Setting up price tracking")
            
            tracking_id = f"track_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create price tracking entry
            price_track = {
                'id': tracking_id,
                'params': tracking_params,
                'created': datetime.now().isoformat(),
                'alerts': [],
                'price_history': [],
                'current_price': None,
                'lowest_price': None,
                'highest_price': None,
                'price_trend': 'unknown'
            }
            
            # Get initial price
            current_prices = await self._get_current_prices(tracking_params)
            if current_prices:
                avg_price = statistics.mean([p['price'] for p in current_prices])
                price_track['current_price'] = avg_price
                price_track['lowest_price'] = avg_price
                price_track['highest_price'] = avg_price
                price_track['price_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'price': avg_price,
                    'source': 'initial_check'
                })
            
            # Set up alerts
            target_price = tracking_params.get('target_price')
            if target_price:
                alert = PriceAlert(
                    search_id=tracking_id,
                    travel_type=tracking_params.get('travel_type', 'flight'),
                    route=f"{tracking_params.get('origin', '')} → {tracking_params.get('destination', '')}",
                    target_price=target_price,
                    current_price=price_track['current_price'] or 0,
                    created_date=datetime.now(),
                    alert_threshold=tracking_params.get('alert_threshold', 0.1)  # 10% change
                )
                self.active_alerts[tracking_id] = alert
            
            # Store tracking
            self.price_history[tracking_id] = price_track
            
            result = {
                'status': 'success',
                'tracking_id': tracking_id,
                'tracking_setup': price_track,
                'monitoring': {
                    'frequency': 'every_6_hours',
                    'alert_conditions': [
                        f"Price drops below ${target_price}" if target_price else "Price drops by 10%",
                        "Price increases by 20%",
                        "Significant price volatility detected"
                    ]
                },
                'agent': 'DealHunterAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Deal Hunter Agent: Price tracking error: {str(e)}")
            return {'status': 'error', 'message': f'Price tracking setup failed: {str(e)}'}

    async def analyze_price_trends(self, route_params: Dict, lookback_days: int = 30) -> Dict:
        """
        Analyze historical price trends for a route
        """
        try:
            logger.info("Deal Hunter Agent: Analyzing price trends")
            
            # Simulate historical price data (in production, would query real data)
            historical_data = await self._simulate_historical_prices(route_params, lookback_days)
            
            # Calculate trend metrics
            prices = [p['price'] for p in historical_data]
            if not prices:
                return {'status': 'error', 'message': 'No price data available'}
            
            avg_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            min_price = min(prices)
            max_price = max(prices)
            current_price = prices[-1] if prices else 0
            
            # Calculate price trend
            if len(prices) >= 7:
                recent_avg = statistics.mean(prices[-7:])  # Last week
                older_avg = statistics.mean(prices[:-7])    # Before last week
                
                if recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
                elif recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            # Price volatility
            price_std = statistics.stdev(prices) if len(prices) > 1 else 0
            volatility_ratio = price_std / avg_price if avg_price > 0 else 0
            
            # Recommendations based on trends
            recommendations = []
            
            if current_price <= min_price * 1.1:
                recommendations.append({
                    'type': 'buy_now',
                    'reason': 'Price is near historical low',
                    'confidence': 'high'
                })
            elif current_price >= max_price * 0.9:
                recommendations.append({
                    'type': 'wait',
                    'reason': 'Price is near historical high',
                    'confidence': 'medium'
                })
            elif trend == 'decreasing':
                recommendations.append({
                    'type': 'wait',
                    'reason': 'Price trend is decreasing',
                    'confidence': 'medium'
                })
            else:
                recommendations.append({
                    'type': 'monitor',
                    'reason': 'No clear trend detected',
                    'confidence': 'low'
                })
            
            # Best booking windows
            best_days = self._identify_best_booking_days(historical_data)
            
            result = {
                'status': 'success',
                'route': f"{route_params.get('origin', '')} → {route_params.get('destination', '')}",
                'analysis_period': f"{lookback_days} days",
                'price_statistics': {
                    'current_price': f"${current_price:.2f}",
                    'average_price': f"${avg_price:.2f}",
                    'median_price': f"${median_price:.2f}",
                    'lowest_price': f"${min_price:.2f}",
                    'highest_price': f"${max_price:.2f}",
                    'price_range': f"${max_price - min_price:.2f}",
                    'volatility': f"{volatility_ratio:.2%}"
                },
                'trend_analysis': {
                    'current_trend': trend,
                    'trend_strength': 'strong' if volatility_ratio > 0.3 else 'moderate' if volatility_ratio > 0.15 else 'weak',
                    'price_momentum': 'upward' if current_price > avg_price else 'downward'
                },
                'recommendations': recommendations,
                'best_booking_windows': best_days,
                'historical_data': historical_data[-14:],  # Last 2 weeks
                'agent': 'DealHunterAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Deal Hunter Agent: Price trend analysis error: {str(e)}")
            return {'status': 'error', 'message': f'Price trend analysis failed: {str(e)}'}

    async def _hunt_flight_deals(self, params: Dict) -> Dict:
        """Hunt for flight deals"""
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Mock flight deals
        deals = [
            {
                'id': 'flight_deal_1',
                'title': f"Flash Sale: {params.get('origin', 'NYC')} to {params.get('destination', 'LAX')}",
                'description': f"Limited time offer on {params.get('origin', 'NYC')} to {params.get('destination', 'LAX')} flights",
                'original_price': 450.0,
                'deal_price': 289.0,
                'savings_amount': 161.0,
                'savings_percentage': 35.8,
                'valid_until': (datetime.now() + timedelta(days=3)).isoformat(),
                'travel_type': 'flight',
                'destination': params.get('destination', 'LAX'),
                'deal_source': 'airline_direct',
                'booking_url': f"https://deals.airline.com/flash-sale?from={params.get('origin', '')}&to={params.get('destination', '')}",
                'is_flash_deal': True,
                'deal_quality': 'excellent'
            },
            {
                'id': 'flight_deal_2',
                'title': 'Error Fare Alert',
                'description': 'Pricing error detected - book immediately',
                'original_price': 1200.0,
                'deal_price': 340.0,
                'savings_amount': 860.0,
                'savings_percentage': 71.7,
                'valid_until': (datetime.now() + timedelta(hours=6)).isoformat(),
                'travel_type': 'flight',
                'destination': params.get('destination', ''),
                'deal_source': 'aggregator',
                'booking_url': f"https://errorfare.example.com/book",
                'is_error_fare': True,
                'deal_quality': 'exceptional',
                'risk_level': 'high'
            }
        ]
        
        return {'status': 'success', 'deals': deals}

    async def _hunt_hotel_deals(self, params: Dict) -> Dict:
        """Hunt for hotel deals"""
        await asyncio.sleep(0.4)
        
        deals = [
            {
                'id': 'hotel_deal_1',
                'title': f"Weekend Special in {params.get('destination', 'Downtown')}",
                'description': 'Book 2 nights, get 1 free + breakfast included',
                'original_price': 180.0,
                'deal_price': 120.0,
                'savings_amount': 60.0,
                'savings_percentage': 33.3,
                'valid_until': (datetime.now() + timedelta(days=7)).isoformat(),
                'travel_type': 'hotel',
                'destination': params.get('destination', ''),
                'deal_source': 'hotel_direct',
                'booking_url': f"https://hotel.com/weekend-special",
                'deal_quality': 'good',
                'additional_perks': ['Free breakfast', 'Late checkout', 'Wi-Fi']
            }
        ]
        
        return {'status': 'success', 'deals': deals}

    async def _hunt_transport_deals(self, params: Dict) -> Dict:
        """Hunt for transportation deals"""
        await asyncio.sleep(0.3)
        
        deals = [
            {
                'id': 'transport_deal_1',
                'title': 'Car Rental Flash Sale',
                'description': '50% off economy cars for bookings this week',
                'original_price': 280.0,
                'deal_price': 140.0,
                'savings_amount': 140.0,
                'savings_percentage': 50.0,
                'valid_until': (datetime.now() + timedelta(days=5)).isoformat(),
                'travel_type': 'car_rental',
                'destination': params.get('destination', ''),
                'deal_source': 'rental_company',
                'booking_url': 'https://carrental.com/flash-sale',
                'deal_quality': 'excellent'
            }
        ]
        
        return {'status': 'success', 'deals': deals}

    async def _hunt_destination_deals(self, params: Dict) -> Dict:
        """Hunt for destination-specific deals"""
        await asyncio.sleep(0.6)
        
        deals = [
            {
                'id': 'destination_deal_1',
                'title': f"Complete {params.get('destination', 'City')} Package",
                'description': 'Flight + Hotel + Activities bundle',
                'original_price': 899.0,
                'deal_price': 599.0,
                'savings_amount': 300.0,
                'savings_percentage': 33.4,
                'valid_until': (datetime.now() + timedelta(days=14)).isoformat(),
                'travel_type': 'package',
                'destination': params.get('destination', ''),
                'deal_source': 'travel_agency',
                'booking_url': f"https://travelagency.com/packages/{params.get('destination', '').lower()}",
                'deal_quality': 'good',
                'includes': ['Round-trip flights', '3 nights hotel', 'City tour', 'Airport transfers']
            }
        ]
        
        return {'status': 'success', 'deals': deals}

    async def _get_current_prices(self, params: Dict) -> List[Dict]:
        """Get current prices from multiple sources"""
        # Simulate price fetching
        await asyncio.sleep(0.5)
        
        return [
            {'source': 'source1', 'price': 350.0},
            {'source': 'source2', 'price': 375.0},
            {'source': 'source3', 'price': 340.0}
        ]

    async def _simulate_historical_prices(self, params: Dict, days: int) -> List[Dict]:
        """Simulate historical price data"""
        import random
        
        base_price = 400
        historical_data = []
        
        for i in range(days):
            date_obj = datetime.now() - timedelta(days=i)
            # Add some randomness to simulate price fluctuations
            daily_change = random.uniform(-0.15, 0.15)
            price = base_price * (1 + daily_change)
            
            historical_data.append({
                'date': date_obj.strftime('%Y-%m-%d'),
                'price': round(price, 2),
                'day_of_week': date_obj.strftime('%A').lower()
            })
        
        return list(reversed(historical_data))  # Chronological order

    def _categorize_deals(self, deals: List[Dict]) -> Dict:
        """Categorize deals by type and quality"""
        categories = {
            'flights': [],
            'hotels': [],
            'transport': [],
            'packages': [],
            'flash_deals': [],
            'error_fares': []
        }
        
        for deal in deals:
            travel_type = deal.get('travel_type', 'other')
            if travel_type in categories:
                categories[travel_type].append(deal)
            
            if deal.get('is_flash_deal'):
                categories['flash_deals'].append(deal)
            if deal.get('is_error_fare'):
                categories['error_fares'].append(deal)
        
        return categories

    def _generate_deal_recommendations(self, deals: List[Dict], search_params: Dict) -> List[Dict]:
        """Generate personalized deal recommendations"""
        recommendations = []
        
        if not deals:
            return [{
                'type': 'no_deals',
                'message': 'No deals found for your search. Try adjusting dates or destinations.',
                'priority': 'info'
            }]
        
        # Best overall deal
        best_deal = max(deals, key=lambda d: d.get('savings_percentage', 0))
        recommendations.append({
            'type': 'best_deal',
            'message': f"Best Deal: Save {best_deal.get('savings_percentage', 0):.1f}% on {best_deal.get('title', 'travel')}",
            'deal_id': best_deal.get('id'),
            'priority': 'high'
        })
        
        # Flash deals expiring soon
        flash_deals = [d for d in deals if d.get('is_flash_deal')]
        if flash_deals:
            recommendations.append({
                'type': 'urgency',
                'message': f"{len(flash_deals)} flash deals expiring soon - book immediately!",
                'priority': 'urgent'
            })
        
        # Error fares
        error_fares = [d for d in deals if d.get('is_error_fare')]
        if error_fares:
            recommendations.append({
                'type': 'error_fare',
                'message': 'Error fare detected! Book now but be prepared for possible cancellation.',
                'priority': 'urgent',
                'warning': 'High risk - airline may cancel booking'
            })
        
        # Budget recommendation
        budget_deals = [d for d in deals if d.get('deal_price', 0) < 300]
        if budget_deals and search_params.get('budget') == 'low':
            recommendations.append({
                'type': 'budget_friendly',
                'message': f"Found {len(budget_deals)} deals under $300 perfect for your budget",
                'priority': 'medium'
            })
        
        return recommendations

    def _identify_best_booking_days(self, historical_data: List[Dict]) -> Dict:
        """Identify best days of week to book based on historical data"""
        day_prices = {}
        
        for entry in historical_data:
            day = entry.get('day_of_week', 'unknown')
            price = entry.get('price', 0)
            
            if day not in day_prices:
                day_prices[day] = []
            day_prices[day].append(price)
        
        # Calculate average prices by day
        day_averages = {}
        for day, prices in day_prices.items():
            if prices:
                day_averages[day] = statistics.mean(prices)
        
        if not day_averages:
            return {'best_days': [], 'worst_days': []}
        
        # Sort days by average price
        sorted_days = sorted(day_averages.items(), key=lambda x: x[1])
        
        return {
            'best_days': [day for day, price in sorted_days[:3]],
            'worst_days': [day for day, price in sorted_days[-2:]],
            'price_by_day': {day: f"${price:.2f}" for day, price in day_averages.items()}
        }

    async def check_price_alerts(self) -> Dict:
        """Check all active price alerts and trigger notifications"""
        try:
            logger.info("Deal Hunter Agent: Checking price alerts")
            
            triggered_alerts = []
            
            for tracking_id, alert in self.active_alerts.items():
                # Get current price
                if tracking_id in self.price_history:
                    track_data = self.price_history[tracking_id]
                    current_prices = await self._get_current_prices(track_data['params'])
                    
                    if current_prices:
                        avg_current_price = statistics.mean([p['price'] for p in current_prices])
                        
                        # Check if alert conditions are met
                        if avg_current_price <= alert.target_price:
                            triggered_alerts.append({
                                'alert_id': tracking_id,
                                'type': 'target_price_reached',
                                'message': f"Price dropped to ${avg_current_price:.2f} (target: ${alert.target_price:.2f})",
                                'current_price': avg_current_price,
                                'target_price': alert.target_price,
                                'route': alert.route
                            })
            
            return {
                'status': 'success',
                'alerts_checked': len(self.active_alerts),
                'triggered_alerts': triggered_alerts,
                'agent': 'DealHunterAgent'
            }
            
        except Exception as e:
            logger.error(f"Deal Hunter Agent: Alert checking error: {str(e)}")
            return {'status': 'error', 'message': f'Alert checking failed: {str(e)}'}