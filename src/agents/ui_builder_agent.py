#!/usr/bin/env python3
"""
UI Builder Agent
Specialized agent for building and updating user interfaces dynamically
"""

import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class UIBuilderAgent:
    """
    Autonomous agent responsible for building dynamic user interfaces,
    updating components, and managing frontend interactions
    """
    
    def __init__(self):
        # UI component templates
        self.component_templates = {
            'search_form': self._get_search_form_template(),
            'result_card': self._get_result_card_template(),
            'deal_banner': self._get_deal_banner_template(),
            'price_chart': self._get_price_chart_template(),
            'route_map': self._get_route_map_template(),
            'filter_panel': self._get_filter_panel_template()
        }
        
        # CSS and styling configurations
        self.style_themes = {
            'default': {
                'primary_color': '#667eea',
                'secondary_color': '#764ba2',
                'success_color': '#28a745',
                'warning_color': '#ffc107',
                'danger_color': '#dc3545',
                'background_gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            },
            'dark': {
                'primary_color': '#4a5568',
                'secondary_color': '#2d3748',
                'success_color': '#38a169',
                'warning_color': '#d69e2e',
                'danger_color': '#e53e3e',
                'background_gradient': 'linear-gradient(135deg, #2d3748 0%, #4a5568 100%)'
            }
        }

    async def build_dynamic_interface(self, interface_config: Dict) -> Dict:
        """
        Build a dynamic interface based on configuration
        """
        try:
            logger.info("UI Builder Agent: Building dynamic interface")
            
            interface_type = interface_config.get('type', 'search_results')
            data = interface_config.get('data', {})
            theme = interface_config.get('theme', 'default')
            
            if interface_type == 'search_results':
                ui_components = await self._build_search_results_interface(data, theme)
            elif interface_type == 'deal_dashboard':
                ui_components = await self._build_deal_dashboard(data, theme)
            elif interface_type == 'route_planner':
                ui_components = await self._build_route_planner_interface(data, theme)
            elif interface_type == 'price_tracker':
                ui_components = await self._build_price_tracker_interface(data, theme)
            else:
                ui_components = await self._build_generic_interface(data, theme)
            
            result = {
                'status': 'success',
                'interface_type': interface_type,
                'theme': theme,
                'components': ui_components,
                'styles': self._generate_custom_styles(theme),
                'scripts': self._generate_javascript_handlers(),
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'component_count': len(ui_components),
                    'responsive': True
                },
                'agent': 'UIBuilderAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"UI Builder Agent: Interface building error: {str(e)}")
            return {'status': 'error', 'message': f'Interface building failed: {str(e)}'}

    async def update_component(self, component_id: str, update_data: Dict, 
                             animation: str = 'fade') -> Dict:
        """
        Update a specific UI component with new data
        """
        try:
            logger.info(f"UI Builder Agent: Updating component {component_id}")
            
            component_type = update_data.get('type', 'generic')
            new_content = update_data.get('content', {})
            
            # Generate updated component HTML
            if component_type == 'result_card':
                updated_html = self._generate_result_card(new_content)
            elif component_type == 'deal_banner':
                updated_html = self._generate_deal_banner(new_content)
            elif component_type == 'price_chart':
                updated_html = self._generate_price_chart(new_content)
            else:
                updated_html = self._generate_generic_component(new_content)
            
            # Generate update instructions
            update_instructions = {
                'component_id': component_id,
                'action': 'replace_content',
                'html': updated_html,
                'animation': animation,
                'animation_duration': '300ms',
                'callback': f'onComponentUpdated_{component_id}'
            }
            
            result = {
                'status': 'success',
                'component_id': component_id,
                'update_type': component_type,
                'update_instructions': update_instructions,
                'javascript': self._generate_update_script(update_instructions),
                'agent': 'UIBuilderAgent'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"UI Builder Agent: Component update error: {str(e)}")
            return {'status': 'error', 'message': f'Component update failed: {str(e)}'}

    async def _build_search_results_interface(self, data: Dict, theme: str) -> List[Dict]:
        """Build search results interface components"""
        components = []
        
        # Header component
        components.append({
            'id': 'search_header',
            'type': 'header',
            'html': f'''
            <div class="search-header">
                <h2>🌍 Travel Search Results</h2>
                <p>Found {data.get('total_results', 0)} options for your trip</p>
                <div class="search-meta">
                    <span>Search completed in {data.get('search_time', '1.2')}s</span>
                    <span>•</span>
                    <span>Last updated: {datetime.now().strftime('%H:%M')}</span>
                </div>
            </div>
            ''',
            'css_classes': ['search-header', f'theme-{theme}']
        })
        
        # Filters component
        components.append({
            'id': 'result_filters',
            'type': 'filters',
            'html': self._generate_filter_panel(data.get('filters', {})),
            'css_classes': ['filter-panel']
        })
        
        # Results grid
        if 'results' in data:
            for category, results in data['results'].items():
                if results and results.get('status') == 'success':
                    components.append({
                        'id': f'results_{category}',
                        'type': 'result_section',
                        'html': self._generate_result_section(category, results.get('results', [])),
                        'css_classes': ['result-section', f'category-{category}']
                    })
        
        return components

    async def _build_deal_dashboard(self, data: Dict, theme: str) -> List[Dict]:
        """Build deal dashboard interface"""
        components = []
        
        # Deal summary header
        components.append({
            'id': 'deal_summary',
            'type': 'summary',
            'html': f'''
            <div class="deal-summary">
                <h2>💰 Active Deals & Savings</h2>
                <div class="deal-stats">
                    <div class="stat-item">
                        <span class="stat-number">{data.get('total_deals', 0)}</span>
                        <span class="stat-label">Active Deals</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${data.get('total_savings', 0):,.0f}</span>
                        <span class="stat-label">Total Savings</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{data.get('flash_deals', 0)}</span>
                        <span class="stat-label">Flash Deals</span>
                    </div>
                </div>
            </div>
            ''',
            'css_classes': ['deal-summary']
        })
        
        # Top deals carousel
        if 'top_deals' in data:
            components.append({
                'id': 'top_deals_carousel',
                'type': 'carousel',
                'html': self._generate_deals_carousel(data['top_deals']),
                'css_classes': ['deals-carousel']
            })
        
        # Deal categories
        if 'deals_by_category' in data:
            for category, deals in data['deals_by_category'].items():
                if deals:
                    components.append({
                        'id': f'deals_{category}',
                        'type': 'deal_category',
                        'html': self._generate_deal_category(category, deals),
                        'css_classes': ['deal-category', f'category-{category}']
                    })
        
        return components

    async def _build_route_planner_interface(self, data: Dict, theme: str) -> List[Dict]:
        """Build route planner interface"""
        components = []
        
        # Route overview
        components.append({
            'id': 'route_overview',
            'type': 'overview',
            'html': f'''
            <div class="route-overview">
                <h2>🗺️ Route Optimization Results</h2>
                <div class="route-summary">
                    <div class="route-stat">
                        <span class="label">Total Distance:</span>
                        <span class="value">{data.get('total_distance', 0):,.0f} km</span>
                    </div>
                    <div class="route-stat">
                        <span class="label">Total Cost:</span>
                        <span class="value">${data.get('total_cost', 0):,.2f}</span>
                    </div>
                    <div class="route-stat">
                        <span class="label">Travel Time:</span>
                        <span class="value">{data.get('total_time', '0h')}</span>
                    </div>
                </div>
            </div>
            ''',
            'css_classes': ['route-overview']
        })
        
        # Interactive map
        components.append({
            'id': 'route_map',
            'type': 'map',
            'html': self._generate_route_map(data.get('route_data', {})),
            'css_classes': ['route-map']
        })
        
        # Route alternatives
        if 'alternatives' in data:
            components.append({
                'id': 'route_alternatives',
                'type': 'alternatives',
                'html': self._generate_route_alternatives(data['alternatives']),
                'css_classes': ['route-alternatives']
            })
        
        return components

    async def _build_price_tracker_interface(self, data: Dict, theme: str) -> List[Dict]:
        """Build price tracker interface"""
        components = []
        
        # Price tracker header
        components.append({
            'id': 'tracker_header',
            'type': 'header',
            'html': f'''
            <div class="tracker-header">
                <h2>📈 Price Tracking Dashboard</h2>
                <div class="tracking-stats">
                    <span>Tracking {data.get('active_tracks', 0)} routes</span>
                    <span>•</span>
                    <span>{data.get('alerts_triggered', 0)} alerts triggered</span>
                </div>
            </div>
            ''',
            'css_classes': ['tracker-header']
        })
        
        # Price charts
        if 'price_data' in data:
            components.append({
                'id': 'price_charts',
                'type': 'charts',
                'html': self._generate_price_charts(data['price_data']),
                'css_classes': ['price-charts']
            })
        
        # Active alerts
        if 'active_alerts' in data:
            components.append({
                'id': 'active_alerts',
                'type': 'alerts',
                'html': self._generate_alerts_panel(data['active_alerts']),
                'css_classes': ['alerts-panel']
            })
        
        return components

    async def _build_generic_interface(self, data: Dict, theme: str) -> List[Dict]:
        """Build generic interface components"""
        return [{
            'id': 'generic_content',
            'type': 'content',
            'html': f'''
            <div class="generic-content">
                <h2>Travel Assistant</h2>
                <p>Interface ready for customization</p>
                <pre>{json.dumps(data, indent=2)}</pre>
            </div>
            ''',
            'css_classes': ['generic-content']
        }]

    def _generate_result_section(self, category: str, results: List[Dict]) -> str:
        """Generate HTML for a result section"""
        category_icons = {
            'flights': '✈️',
            'hotels': '🏨',
            'ground_transportation': '🚗',
            'cruises': '🚢',
            'tours_activities': '🎯'
        }
        
        icon = category_icons.get(category, '📍')
        title = category.replace('_', ' ').title()
        
        html = f'''
        <div class="result-section" id="section-{category}">
            <h3 class="section-title">{icon} {title} ({len(results)} options)</h3>
            <div class="results-grid">
        '''
        
        for result in results[:5]:  # Show top 5 results
            html += self._generate_result_card(result)
        
        html += '''
            </div>
            <button class="show-more-btn" onclick="showMoreResults('{}')">Show More Results</button>
        </div>
        '''.format(category)
        
        return html

    def _generate_result_card(self, result: Dict) -> str:
        """Generate HTML for a single result card"""
        return f'''
        <div class="result-card" data-result-id="{result.get('id', '')}">
            <div class="result-header">
                <h4 class="result-title">{result.get('name', result.get('airline', 'Travel Option'))}</h4>
                <div class="result-price">{result.get('price', result.get('total_price', 'N/A'))}</div>
            </div>
            <div class="result-details">
                {self._generate_result_details(result)}
            </div>
            <div class="result-actions">
                <button class="btn btn-primary" onclick="bookNow('{result.get('booking_url', '#')}')">
                    Book Now
                </button>
                <button class="btn btn-secondary" onclick="saveResult('{result.get('id', '')}')">
                    Save
                </button>
            </div>
        </div>
        '''

    def _generate_result_details(self, result: Dict) -> str:
        """Generate detail items for a result"""
        details_html = ""
        
        # Common detail mappings
        detail_mappings = {
            'departure_time': 'Departure',
            'arrival_time': 'Arrival',
            'duration': 'Duration',
            'rating': 'Rating',
            'distance_from_center': 'Distance',
            'amenities': 'Amenities'
        }
        
        for key, label in detail_mappings.items():
            if key in result:
                value = result[key]
                if isinstance(value, list):
                    value = ', '.join(value[:3])  # Show first 3 items
                details_html += f'''
                <div class="detail-item">
                    <span class="detail-label">{label}:</span>
                    <span class="detail-value">{value}</span>
                </div>
                '''
        
        return details_html

    def _generate_filter_panel(self, filters: Dict) -> str:
        """Generate filter panel HTML"""
        return '''
        <div class="filter-panel">
            <h4>Filter Results</h4>
            <div class="filter-groups">
                <div class="filter-group">
                    <label>Price Range</label>
                    <input type="range" id="priceRange" min="0" max="2000" value="1000">
                    <span id="priceValue">$1000</span>
                </div>
                <div class="filter-group">
                    <label>Travel Type</label>
                    <select id="travelTypeFilter">
                        <option value="">All Types</option>
                        <option value="flights">Flights</option>
                        <option value="hotels">Hotels</option>
                        <option value="transport">Transport</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Sort By</label>
                    <select id="sortBy">
                        <option value="price">Price</option>
                        <option value="duration">Duration</option>
                        <option value="rating">Rating</option>
                    </select>
                </div>
            </div>
            <button class="apply-filters-btn" onclick="applyFilters()">Apply Filters</button>
        </div>
        '''

    def _generate_deals_carousel(self, deals: List[Dict]) -> str:
        """Generate deals carousel HTML"""
        carousel_items = ""
        
        for i, deal in enumerate(deals[:5]):
            active_class = "active" if i == 0 else ""
            carousel_items += f'''
            <div class="carousel-item {active_class}">
                <div class="deal-card featured">
                    <div class="deal-badge">{deal.get('savings_percentage', 0):.0f}% OFF</div>
                    <h4>{deal.get('title', 'Great Deal')}</h4>
                    <p>{deal.get('description', 'Limited time offer')}</p>
                    <div class="deal-prices">
                        <span class="original-price">${deal.get('original_price', 0):.0f}</span>
                        <span class="deal-price">${deal.get('deal_price', 0):.0f}</span>
                    </div>
                    <button class="book-deal-btn" onclick="bookDeal('{deal.get('id', '')}')">
                        Book This Deal
                    </button>
                </div>
            </div>
            '''
        
        return f'''
        <div class="deals-carousel">
            <div class="carousel-container">
                {carousel_items}
            </div>
            <div class="carousel-controls">
                <button class="carousel-prev" onclick="prevDeal()">‹</button>
                <button class="carousel-next" onclick="nextDeal()">›</button>
            </div>
        </div>
        '''

    def _generate_deal_category(self, category: str, deals: List[Dict]) -> str:
        """Generate deal category section"""
        category_titles = {
            'flights': 'Flight Deals',
            'hotels': 'Hotel Deals', 
            'transport': 'Transport Deals',
            'packages': 'Package Deals'
        }
        
        title = category_titles.get(category, category.title())
        
        deals_html = ""
        for deal in deals[:3]:
            deals_html += f'''
            <div class="deal-item">
                <div class="deal-info">
                    <h5>{deal.get('title', 'Deal')}</h5>
                    <p>{deal.get('description', 'Great savings opportunity')}</p>
                </div>
                <div class="deal-savings">
                    <span class="savings-amount">${deal.get('savings_amount', 0):.0f} saved</span>
                    <span class="deal-price">${deal.get('deal_price', 0):.0f}</span>
                </div>
            </div>
            '''
        
        return f'''
        <div class="deal-category">
            <h4>{title}</h4>
            <div class="deals-list">
                {deals_html}
            </div>
        </div>
        '''

    def _generate_custom_styles(self, theme: str) -> str:
        """Generate custom CSS styles"""
        theme_colors = self.style_themes.get(theme, self.style_themes['default'])
        
        return f'''
        <style>
            :root {{
                --primary-color: {theme_colors['primary_color']};
                --secondary-color: {theme_colors['secondary_color']};
                --success-color: {theme_colors['success_color']};
                --warning-color: {theme_colors['warning_color']};
                --danger-color: {theme_colors['danger_color']};
                --background-gradient: {theme_colors['background_gradient']};
            }}
            
            .result-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            
            .result-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            
            .result-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
            }}
            
            .result-price {{
                font-size: 1.5rem;
                font-weight: bold;
                color: var(--primary-color);
            }}
            
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: background-color 0.2s ease;
            }}
            
            .btn-primary {{
                background: var(--primary-color);
                color: white;
            }}
            
            .btn-primary:hover {{
                background: var(--secondary-color);
            }}
            
            .deals-carousel {{
                position: relative;
                overflow: hidden;
                border-radius: 15px;
                margin-bottom: 30px;
            }}
            
            .carousel-item {{
                display: none;
            }}
            
            .carousel-item.active {{
                display: block;
            }}
            
            .deal-card.featured {{
                background: var(--background-gradient);
                color: white;
                text-align: center;
                padding: 40px;
            }}
            
            .deal-badge {{
                background: var(--warning-color);
                color: #333;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 16px;
            }}
            
            @media (max-width: 768px) {{
                .result-card {{
                    padding: 16px;
                }}
                
                .result-header {{
                    flex-direction: column;
                    align-items: flex-start;
                }}
                
                .result-price {{
                    margin-top: 8px;
                }}
            }}
        </style>
        '''

    def _generate_javascript_handlers(self) -> str:
        """Generate JavaScript event handlers"""
        return '''
        <script>
            // Result card interactions
            function bookNow(url) {
                if (url && url !== '#') {
                    window.open(url, '_blank');
                } else {
                    alert('Booking URL not available');
                }
            }
            
            function saveResult(resultId) {
                // Save result to local storage or send to backend
                localStorage.setItem('saved_' + resultId, JSON.stringify({
                    id: resultId,
                    savedAt: new Date().toISOString()
                }));
                showNotification('Result saved!', 'success');
            }
            
            // Deal carousel
            let currentDealIndex = 0;
            const dealItems = document.querySelectorAll('.carousel-item');
            
            function showDeal(index) {
                dealItems.forEach(item => item.classList.remove('active'));
                if (dealItems[index]) {
                    dealItems[index].classList.add('active');
                }
            }
            
            function nextDeal() {
                currentDealIndex = (currentDealIndex + 1) % dealItems.length;
                showDeal(currentDealIndex);
            }
            
            function prevDeal() {
                currentDealIndex = (currentDealIndex - 1 + dealItems.length) % dealItems.length;
                showDeal(currentDealIndex);
            }
            
            function bookDeal(dealId) {
                // Handle deal booking
                console.log('Booking deal:', dealId);
                showNotification('Redirecting to booking...', 'info');
            }
            
            // Filters
            function applyFilters() {
                const priceRange = document.getElementById('priceRange').value;
                const travelType = document.getElementById('travelTypeFilter').value;
                const sortBy = document.getElementById('sortBy').value;
                
                // Apply filters logic
                filterResults({ priceRange, travelType, sortBy });
            }
            
            function filterResults(filters) {
                // Implementation would filter visible results
                console.log('Applying filters:', filters);
                showNotification('Filters applied', 'success');
            }
            
            // Utility functions
            function showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.textContent = message;
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 600;
                    z-index: 10000;
                    background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
                `;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.remove();
                }, 3000);
            }
            
            function showMoreResults(category) {
                // Load more results for category
                console.log('Loading more results for:', category);
                showNotification('Loading more results...', 'info');
            }
        </script>
        '''

    def _generate_update_script(self, instructions: Dict) -> str:
        """Generate JavaScript for component updates"""
        return f'''
        <script>
            function updateComponent_{instructions['component_id']}() {{
                const element = document.getElementById('{instructions['component_id']}');
                if (element) {{
                    element.style.transition = 'opacity {instructions['animation_duration']}';
                    element.style.opacity = '0';
                    
                    setTimeout(() => {{
                        element.innerHTML = `{instructions['html']}`;
                        element.style.opacity = '1';
                    }}, {int(instructions['animation_duration'].replace('ms', ''))});
                }}
            }}
            
            // Auto-execute update
            updateComponent_{instructions['component_id']}();
        </script>
        '''

    def _get_search_form_template(self) -> str:
        """Get search form template"""
        return "<!-- Search form template -->"

    def _get_result_card_template(self) -> str:
        """Get result card template"""
        return "<!-- Result card template -->"

    def _get_deal_banner_template(self) -> str:
        """Get deal banner template"""
        return "<!-- Deal banner template -->"

    def _get_price_chart_template(self) -> str:
        """Get price chart template"""
        return "<!-- Price chart template -->"

    def _get_route_map_template(self) -> str:
        """Get route map template"""
        return "<!-- Route map template -->"

    def _get_filter_panel_template(self) -> str:
        """Get filter panel template"""
        return "<!-- Filter panel template -->"

    def _generate_deal_banner(self, content: Dict) -> str:
        """Generate deal banner HTML"""
        return f"<!-- Deal banner for {content.get('title', 'Deal')} -->"

    def _generate_price_chart(self, content: Dict) -> str:
        """Generate price chart HTML"""
        return f"<!-- Price chart for {content.get('route', 'Route')} -->"

    def _generate_generic_component(self, content: Dict) -> str:
        """Generate generic component HTML"""
        return f"<!-- Generic component: {json.dumps(content)} -->"

    def _generate_route_map(self, route_data: Dict) -> str:
        """Generate route map HTML"""
        return "<!-- Interactive route map -->"

    def _generate_route_alternatives(self, alternatives: List[Dict]) -> str:
        """Generate route alternatives HTML"""
        return "<!-- Route alternatives -->"

    def _generate_price_charts(self, price_data: Dict) -> str:
        """Generate price charts HTML"""
        return "<!-- Price tracking charts -->"

    def _generate_alerts_panel(self, alerts: List[Dict]) -> str:
        """Generate alerts panel HTML"""
        return "<!-- Active alerts panel -->"