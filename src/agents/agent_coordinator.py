#!/usr/bin/env python3
"""
Agent Coordinator
Central coordinator that manages and orchestrates all specialized travel agents
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .data_fetcher_agent import DataFetcherAgent
from .route_optimizer_agent import RouteOptimizerAgent
from .deal_hunter_agent import DealHunterAgent
from .ui_builder_agent import UIBuilderAgent

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Central coordinator that orchestrates multiple specialized agents
    Manages task distribution, inter-agent communication, and result aggregation
    """
    
    def __init__(self):
        # Initialize all specialized agents
        self.data_fetcher = DataFetcherAgent()
        self.route_optimizer = RouteOptimizerAgent()
        self.deal_hunter = DealHunterAgent()
        self.ui_builder = UIBuilderAgent()
        
        # Agent status tracking
        self.agent_status = {
            'data_fetcher': {'active': True, 'last_used': None, 'task_count': 0},
            'route_optimizer': {'active': True, 'last_used': None, 'task_count': 0},
            'deal_hunter': {'active': True, 'last_used': None, 'task_count': 0},
            'ui_builder': {'active': True, 'last_used': None, 'task_count': 0}
        }
        
        # Task queue for managing agent workload
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}

    async def coordinate_comprehensive_search(self, search_params: Dict) -> Dict:
        """
        Coordinate a comprehensive travel search using all relevant agents
        """
        try:
            logger.info("Agent Coordinator: Starting comprehensive search coordination")
            
            # Phase 1: Data Fetching (DataFetcherAgent)
            logger.info("Phase 1: Fetching travel data")
            data_fetch_task = asyncio.create_task(
                self._execute_agent_task('data_fetcher', 'comprehensive_fetch', search_params)
            )
            
            # Phase 2: Deal Hunting (DealHunterAgent) - Can run in parallel with data fetching
            logger.info("Phase 2: Hunting for deals")
            deal_hunt_task = asyncio.create_task(
                self._execute_agent_task('deal_hunter', 'hunt_deals', search_params)
            )
            
            # Wait for initial data and deals
            data_results, deal_results = await asyncio.gather(
                data_fetch_task, deal_hunt_task, return_exceptions=True
            )
            
            # Phase 3: Route Optimization (RouteOptimizerAgent) - if multi-city trip
            route_results = None
            if self._is_multi_city_request(search_params):
                logger.info("Phase 3: Optimizing multi-city route")
                cities = search_params.get('cities', [])
                if cities:
                    route_task = asyncio.create_task(
                        self._execute_agent_task('route_optimizer', 'optimize_multi_city_route', {
                            'cities': cities,
                            'start_city': search_params.get('origin'),
                            'preferences': search_params.get('route_preferences', {})
                        })
                    )
                    route_results = await route_task
            
            # Phase 4: UI Building (UIBuilderAgent)
            logger.info("Phase 4: Building dynamic interface")
            ui_config = {
                'type': 'search_results',
                'data': {
                    'results': data_results.get('results', {}) if isinstance(data_results, dict) else {},
                    'deals': deal_results.get('deals', {}) if isinstance(deal_results, dict) else {},
                    'route_optimization': route_results,
                    'total_results': self._count_total_results(data_results),
                    'search_time': '2.1'
                },
                'theme': search_params.get('ui_theme', 'default')
            }
            
            ui_task = asyncio.create_task(
                self._execute_agent_task('ui_builder', 'build_dynamic_interface', ui_config)
            )
            ui_results = await ui_task
            
            # Extract travel data results for frontend compatibility
            travel_data = data_results if isinstance(data_results, dict) else {'status': 'error', 'message': str(data_results)}
            
            # Aggregate all results in frontend-expected format
            comprehensive_results = {
                'status': 'success',
                'coordination_type': 'comprehensive_search',
                'timestamp': datetime.now().isoformat(),
                'search_params': search_params,
                'results': travel_data.get('results', travel_data),  # Extract nested results for frontend compatibility
                'deals': deal_results if isinstance(deal_results, dict) else {'status': 'error', 'message': str(deal_results)},
                'route_optimization': route_results,
                'ui_components': ui_results if isinstance(ui_results, dict) else {'status': 'error', 'message': str(ui_results)},
                'agent_performance': self._get_agent_performance_summary(),
                'coordinator': 'AgentCoordinator'
            }
            
            logger.info("Agent Coordinator: Comprehensive search completed successfully")
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Agent Coordinator: Comprehensive search coordination error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Search coordination failed: {str(e)}',
                'coordinator': 'AgentCoordinator'
            }

    async def coordinate_deal_tracking(self, tracking_params: Dict) -> Dict:
        """
        Coordinate deal tracking and price monitoring
        """
        try:
            logger.info("Agent Coordinator: Starting deal tracking coordination")
            
            # Set up price tracking with DealHunterAgent
            price_tracking_task = asyncio.create_task(
                self._execute_agent_task('deal_hunter', 'track_prices', tracking_params)
            )
            
            # Analyze price trends
            trend_analysis_task = asyncio.create_task(
                self._execute_agent_task('deal_hunter', 'analyze_price_trends', {
                    'route_params': tracking_params,
                    'lookback_days': 30
                })
            )
            
            # Get route optimization suggestions for alternatives
            route_alternatives_task = None
            if tracking_params.get('origin') and tracking_params.get('destination'):
                route_alternatives_task = asyncio.create_task(
                    self._execute_agent_task('route_optimizer', 'optimize_transport_mix', {
                        'origin': tracking_params['origin'],
                        'destination': tracking_params['destination'],
                        'departure_date': tracking_params.get('departure_date', '2025-08-01'),
                        'preferences': {'optimize_for': 'cost'}
                    })
                )
            
            # Wait for all tasks to complete
            tasks = [price_tracking_task, trend_analysis_task]
            if route_alternatives_task:
                tasks.append(route_alternatives_task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Build price tracker UI
            ui_data = {
                'type': 'price_tracker',
                'data': {
                    'tracking_setup': results[0] if isinstance(results[0], dict) else {},
                    'trend_analysis': results[1] if isinstance(results[1], dict) else {},
                    'route_alternatives': results[2] if len(results) > 2 and isinstance(results[2], dict) else {},
                    'active_tracks': 1,
                    'alerts_triggered': 0
                },
                'theme': tracking_params.get('ui_theme', 'default')
            }
            
            ui_task = asyncio.create_task(
                self._execute_agent_task('ui_builder', 'build_dynamic_interface', ui_data)
            )
            ui_results = await ui_task
            
            coordination_results = {
                'status': 'success',
                'coordination_type': 'deal_tracking',
                'timestamp': datetime.now().isoformat(),
                'tracking_params': tracking_params,
                'results': {
                    'price_tracking': results[0] if isinstance(results[0], dict) else {'status': 'error', 'message': str(results[0])},
                    'trend_analysis': results[1] if isinstance(results[1], dict) else {'status': 'error', 'message': str(results[1])},
                    'route_alternatives': results[2] if len(results) > 2 and isinstance(results[2], dict) else None,
                    'ui_components': ui_results if isinstance(ui_results, dict) else {'status': 'error', 'message': str(ui_results)}
                },
                'agent_performance': self._get_agent_performance_summary(),
                'coordinator': 'AgentCoordinator'
            }
            
            return coordination_results
            
        except Exception as e:
            logger.error(f"Agent Coordinator: Deal tracking coordination error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Deal tracking coordination failed: {str(e)}',
                'coordinator': 'AgentCoordinator'
            }

    async def coordinate_route_planning(self, planning_params: Dict) -> Dict:
        """
        Coordinate complex route planning with optimization and data fetching
        """
        try:
            logger.info("Agent Coordinator: Starting route planning coordination")
            
            # Phase 1: Multi-city route optimization
            route_optimization_task = asyncio.create_task(
                self._execute_agent_task('route_optimizer', 'optimize_multi_city_route', {
                    'cities': planning_params.get('cities', []),
                    'start_city': planning_params.get('start_city'),
                    'end_city': planning_params.get('end_city'),
                    'preferences': planning_params.get('preferences', {})
                })
            )
            
            # Phase 2: Get detailed data for each leg (in parallel with optimization)
            data_fetch_tasks = []
            cities = planning_params.get('cities', [])
            start_city = planning_params.get('start_city')
            
            if start_city and cities:
                # Fetch data for each city pair
                for i in range(len(cities)):
                    origin = start_city if i == 0 else cities[i-1]
                    destination = cities[i]
                    
                    fetch_params = {
                        'origin': origin,
                        'destination': destination,
                        'departure_date': planning_params.get('departure_date', '2025-08-01'),
                        'include_flights': True,
                        'include_ground_transport': True
                    }
                    
                    task = asyncio.create_task(
                        self._execute_agent_task('data_fetcher', 'comprehensive_fetch', fetch_params)
                    )
                    data_fetch_tasks.append(task)
            
            # Wait for route optimization
            route_results = await route_optimization_task
            
            # Wait for all data fetching tasks
            if data_fetch_tasks:
                leg_data_results = await asyncio.gather(*data_fetch_tasks, return_exceptions=True)
            else:
                leg_data_results = []
            
            # Phase 3: Hunt for deals on the optimized route
            if isinstance(route_results, dict) and route_results.get('status') == 'success':
                deal_hunt_params = planning_params.copy()
                deal_hunt_params['route_data'] = route_results
                
                deal_hunt_task = asyncio.create_task(
                    self._execute_agent_task('deal_hunter', 'hunt_deals', deal_hunt_params)
                )
                deal_results = await deal_hunt_task
            else:
                deal_results = {'status': 'error', 'message': 'Route optimization failed'}
            
            # Phase 4: Build route planner UI
            ui_data = {
                'type': 'route_planner',
                'data': {
                    'route_optimization': route_results,
                    'leg_details': leg_data_results,
                    'deals': deal_results,
                    'total_distance': self._calculate_total_distance(route_results),
                    'total_cost': self._calculate_total_cost(route_results),
                    'total_time': self._calculate_total_time(route_results)
                },
                'theme': planning_params.get('ui_theme', 'default')
            }
            
            ui_task = asyncio.create_task(
                self._execute_agent_task('ui_builder', 'build_dynamic_interface', ui_data)
            )
            ui_results = await ui_task
            
            coordination_results = {
                'status': 'success',
                'coordination_type': 'route_planning',
                'timestamp': datetime.now().isoformat(),
                'planning_params': planning_params,
                'results': {
                    'route_optimization': route_results,
                    'leg_details': [result if isinstance(result, dict) else {'status': 'error', 'message': str(result)} for result in leg_data_results],
                    'deals': deal_results if isinstance(deal_results, dict) else {'status': 'error', 'message': str(deal_results)},
                    'ui_components': ui_results if isinstance(ui_results, dict) else {'status': 'error', 'message': str(ui_results)}
                },
                'agent_performance': self._get_agent_performance_summary(),
                'coordinator': 'AgentCoordinator'
            }
            
            return coordination_results
            
        except Exception as e:
            logger.error(f"Agent Coordinator: Route planning coordination error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Route planning coordination failed: {str(e)}',
                'coordinator': 'AgentCoordinator'
            }

    async def _execute_agent_task(self, agent_name: str, method_name: str, params: Dict) -> Any:
        """
        Execute a task on a specific agent with error handling and performance tracking
        """
        try:
            start_time = datetime.now()
            
            # Update agent status
            self.agent_status[agent_name]['last_used'] = start_time.isoformat()
            self.agent_status[agent_name]['task_count'] += 1
            
            # Get the agent instance
            agent = getattr(self, agent_name)
            
            # Get the method
            method = getattr(agent, method_name)
            
            # Execute the method
            if asyncio.iscoroutinefunction(method):
                result = await method(params)
            else:
                result = method(params)
            
            # Track execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Agent {agent_name}.{method_name} completed in {execution_time:.2f}s")
            
            return result
            
        except AttributeError as e:
            logger.error(f"Agent {agent_name} does not have method {method_name}: {str(e)}")
            return {'status': 'error', 'message': f'Method {method_name} not found on agent {agent_name}'}
        except Exception as e:
            logger.error(f"Agent {agent_name}.{method_name} execution error: {str(e)}")
            return {'status': 'error', 'message': f'Agent task execution failed: {str(e)}'}

    def _is_multi_city_request(self, search_params: Dict) -> bool:
        """Check if the request involves multiple cities"""
        cities = search_params.get('cities', [])
        return len(cities) > 1

    def _count_total_results(self, data_results: Any) -> int:
        """Count total results from data fetching"""
        if not isinstance(data_results, dict) or data_results.get('status') != 'success':
            return 0
        
        total = 0
        results = data_results.get('results', {})
        
        for category, category_results in results.items():
            if isinstance(category_results, dict):
                category_data = category_results.get('results', [])
                if isinstance(category_data, list):
                    total += len(category_data)
        
        return total

    def _get_agent_performance_summary(self) -> Dict:
        """Get performance summary for all agents"""
        performance = {}
        
        for agent_name, status in self.agent_status.items():
            performance[agent_name] = {
                'active': status['active'],
                'tasks_completed': status['task_count'],
                'last_used': status['last_used'],
                'health_status': 'healthy' if status['active'] else 'inactive'
            }
        
        return performance

    def _calculate_total_distance(self, route_results: Any) -> float:
        """Calculate total distance from route optimization results"""
        if not isinstance(route_results, dict) or route_results.get('status') != 'success':
            return 0.0
        
        routes = route_results.get('routes', [])
        if routes:
            # Get the first (best) route
            best_route = routes[0]
            legs = best_route.get('legs', [])
            
            total_distance = 0.0
            for leg in legs:
                # Extract distance from leg data (this would depend on the actual data structure)
                distance = leg.get('distance_km', 0)
                total_distance += distance
            
            return total_distance
        
        return 0.0

    def _calculate_total_cost(self, route_results: Any) -> float:
        """Calculate total cost from route optimization results"""
        if not isinstance(route_results, dict) or route_results.get('status') != 'success':
            return 0.0
        
        routes = route_results.get('routes', [])
        if routes:
            best_route = routes[0]
            total_cost_str = best_route.get('total_cost', '$0')
            
            # Extract numeric value from cost string
            try:
                return float(total_cost_str.replace('$', '').replace(',', ''))
            except (ValueError, AttributeError):
                return 0.0
        
        return 0.0

    def _calculate_total_time(self, route_results: Any) -> str:
        """Calculate total time from route optimization results"""
        if not isinstance(route_results, dict) or route_results.get('status') != 'success':
            return '0h'
        
        routes = route_results.get('routes', [])
        if routes:
            best_route = routes[0]
            return best_route.get('total_duration', '0h')
        
        return '0h'

    async def get_agent_status(self) -> Dict:
        """Get current status of all agents"""
        return {
            'coordinator_status': 'active',
            'agents': self.agent_status,
            'active_tasks': len(self.active_tasks),
            'queue_size': self.task_queue.qsize(),
            'timestamp': datetime.now().isoformat()
        }

    async def restart_agent(self, agent_name: str) -> Dict:
        """Restart a specific agent"""
        try:
            if agent_name in ['data_fetcher', 'route_optimizer', 'deal_hunter', 'ui_builder']:
                # Reinitialize the agent
                if agent_name == 'data_fetcher':
                    self.data_fetcher = DataFetcherAgent()
                elif agent_name == 'route_optimizer':
                    self.route_optimizer = RouteOptimizerAgent()
                elif agent_name == 'deal_hunter':
                    self.deal_hunter = DealHunterAgent()
                elif agent_name == 'ui_builder':
                    self.ui_builder = UIBuilderAgent()
                
                # Reset status
                self.agent_status[agent_name] = {
                    'active': True,
                    'last_used': None,
                    'task_count': 0
                }
                
                return {
                    'status': 'success',
                    'message': f'Agent {agent_name} restarted successfully',
                    'agent': agent_name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown agent: {agent_name}'
                }
                
        except Exception as e:
            logger.error(f"Agent restart error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Agent restart failed: {str(e)}'
            }