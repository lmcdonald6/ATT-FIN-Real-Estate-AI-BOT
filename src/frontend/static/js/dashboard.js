// Dashboard initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadInitialData();
});

// Initialize dashboard components
function initializeDashboard() {
    // Add event listeners to search form
    const searchButton = document.querySelector('button');
    searchButton.addEventListener('click', searchProperties);

    // Initialize property type filters
    const propertyType = document.getElementById('property-type');
    propertyType.addEventListener('change', updateFilters);

    // Initialize price range filters
    const priceRange = document.getElementById('price-range');
    priceRange.addEventListener('change', updateFilters);
}

// Load initial data
async function loadInitialData() {
    try {
        // Get user's location (you might want to use a geolocation service here)
        const defaultZipCode = '90210'; // Default to Beverly Hills for demo
        
        // Load market trends
        const trends = await getMarketTrends(defaultZipCode);
        updateMarketCharts(trends);
        
        // Load initial property search
        await searchProperties();
    } catch (error) {
        console.error('Error loading initial data:', error);
        showError('Failed to load initial data. Please try again.');
    }
}

// Search for properties
async function searchProperties() {
    showLoading('search-results');
    
    const location = document.getElementById('location').value;
    const propertyType = document.getElementById('property-type').value;
    const priceRange = document.getElementById('price-range').value;
    
    // Parse price range
    let [priceMin, priceMax] = parsePriceRange(priceRange);

    try {
        const response = await fetch('/api/properties/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: location,
                property_type: propertyType,
                price_min: priceMin,
                price_max: priceMax
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            updatePropertyList(data.properties);
            if (location) {
                updateMarketAnalysis(location);
            }
        } else {
            showError(data.message || 'Failed to search properties');
        }
    } catch (error) {
        console.error('Error searching properties:', error);
        showError('Failed to search properties. Please try again.');
    } finally {
        hideLoading('search-results');
    }
}

// Update market analysis
async function updateMarketAnalysis(location) {
    showLoading('market-analysis');
    
    try {
        const trends = await getMarketTrends(location);
        updateMarketCharts(trends);
    } catch (error) {
        console.error('Error updating market analysis:', error);
        showError('Failed to update market analysis');
    } finally {
        hideLoading('market-analysis');
    }
}

// Get market trends
async function getMarketTrends(zipCode) {
    const response = await fetch(`/api/market/trends?zip_code=${zipCode}`);
    const data = await response.json();
    if (data.status !== 'success') {
        throw new Error(data.message || 'Failed to get market trends');
    }
    return data.trends;
}

// Update property list
function updatePropertyList(properties) {
    const container = document.getElementById('property-list') || createPropertyList();
    container.innerHTML = '';

    if (!properties.length) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">No properties found matching your criteria.</p>';
        return;
    }

    properties.forEach(property => {
        const card = createPropertyCard(property);
        container.appendChild(card);
    });
}

// Create property card
function createPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'property-card bg-white rounded-lg shadow-md p-4 mb-4 hover:shadow-lg transition-shadow duration-200';
    
    const leadScoreClass = getLeadScoreClass(property.lead_score);
    
    card.innerHTML = `
        <div class="flex justify-between items-start">
            <div>
                <h3 class="text-lg font-semibold text-gray-900">${property.address}</h3>
                <p class="text-gray-600">${property.city}, ${property.state} ${property.zip_code}</p>
            </div>
            <div class="text-right">
                <p class="text-xl font-bold text-gray-900">$${formatPrice(property.price)}</p>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${leadScoreClass}">
                    Lead Score: ${property.lead_score}
                </span>
            </div>
        </div>
        <div class="mt-4 grid grid-cols-3 gap-4 text-sm text-gray-500">
            <div>
                <span class="block font-medium">Beds</span>
                ${property.beds}
            </div>
            <div>
                <span class="block font-medium">Baths</span>
                ${property.baths}
            </div>
            <div>
                <span class="block font-medium">Sq Ft</span>
                ${formatNumber(property.square_feet)}
            </div>
        </div>
        <div class="mt-4">
            <button onclick="analyzeProperty('${property.property_id}')" 
                    class="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                Analyze Property
            </button>
        </div>
    `;
    
    return card;
}

// Update market charts
function updateMarketCharts(trends) {
    if (!trends) return;

    // Price Trends Chart
    const priceTrendsData = {
        x: trends.dates || [],
        y: trends.prices || [],
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: 'rgb(79, 70, 229)',
            width: 2
        }
    };

    const priceTrendsLayout = {
        title: 'Average Property Prices',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 30, r: 20, b: 30, l: 40 },
        xaxis: {
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)'
        },
        yaxis: {
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)',
            tickformat: '$,.0f'
        }
    };

    Plotly.newPlot('price-trends', [priceTrendsData], priceTrendsLayout);

    // Market Stats Chart
    if (trends.market_stats) {
        const marketStatsData = {
            values: [
                trends.market_stats.high_potential || 0,
                trends.market_stats.medium_potential || 0,
                trends.market_stats.low_potential || 0
            ],
            labels: ['High Potential', 'Medium Potential', 'Low Potential'],
            type: 'pie',
            marker: {
                colors: ['rgb(79, 70, 229)', 'rgb(147, 197, 253)', 'rgb(219, 234, 254)']
            }
        };

        const marketStatsLayout = {
            title: 'Market Opportunity Distribution',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { t: 30, r: 20, b: 30, l: 20 }
        };

        Plotly.newPlot('market-stats', [marketStatsData], marketStatsLayout);
    }
}

// Analyze property
async function analyzeProperty(propertyId) {
    showLoading('property-analysis');
    
    try {
        const response = await fetch('/api/properties/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                property_id: propertyId
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            showPropertyAnalysis(data.analysis);
        } else {
            showError(data.message || 'Failed to analyze property');
        }
    } catch (error) {
        console.error('Error analyzing property:', error);
        showError('Failed to analyze property. Please try again.');
    } finally {
        hideLoading('property-analysis');
    }
}

// Show property analysis
function showPropertyAnalysis(analysis) {
    // Create modal with analysis details
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full';
    modal.id = 'analysis-modal';
    
    modal.innerHTML = `
        <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
            <div class="flex justify-between items-start">
                <h3 class="text-lg font-semibold text-gray-900">Property Analysis</h3>
                <button onclick="closeModal('analysis-modal')" class="text-gray-400 hover:text-gray-500">
                    <span class="sr-only">Close</span>
                    <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            
            <div class="mt-4">
                <h4 class="font-medium text-gray-900">Property Details</h4>
                <div class="mt-2 grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-500">Address</p>
                        <p class="font-medium">${analysis.property_details.address}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500">Price</p>
                        <p class="font-medium">$${formatPrice(analysis.property_details.price)}</p>
                    </div>
                </div>
            </div>
            
            <div class="mt-6">
                <h4 class="font-medium text-gray-900">ROI Analysis</h4>
                <div class="mt-2 grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-500">Potential Profit</p>
                        <p class="font-medium text-green-600">$${formatPrice(analysis.roi_analysis.potential_profit)}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500">ROI Percentage</p>
                        <p class="font-medium text-green-600">${analysis.roi_analysis.roi_percentage.toFixed(2)}%</p>
                    </div>
                </div>
                
                <div class="mt-4 grid grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-500">Total Costs</p>
                        <p class="font-medium">$${formatPrice(analysis.roi_analysis.total_costs)}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500">After Repair Value (ARV)</p>
                        <p class="font-medium">$${formatPrice(analysis.roi_analysis.arv)}</p>
                    </div>
                </div>
            </div>
            
            <div class="mt-6">
                <h4 class="font-medium text-gray-900">Market Analysis</h4>
                <div class="mt-2">
                    <div id="market-analysis-chart" class="h-64"></div>
                </div>
            </div>
            
            <div class="mt-6">
                <button onclick="exportAnalysis(${JSON.stringify(analysis)})" 
                        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Export Analysis
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Create market analysis chart
    createMarketAnalysisChart(analysis.market_analysis);
}

// Helper functions
function parsePriceRange(range) {
    if (range === 'Any') return [0, null];
    
    const matches = range.match(/\$([0-9,]+)/g);
    if (!matches || matches.length !== 2) return [0, null];
    
    return matches.map(price => parseInt(price.replace(/[$,]/g, '')));
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-US').format(price);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function getLeadScoreClass(score) {
    if (score >= 8) return 'bg-green-100 text-green-800';
    if (score >= 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
}

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('loading');
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('loading');
    }
}

function showError(message) {
    // TODO: Implement error notification system
    console.error(message);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

function createPropertyList() {
    const container = document.createElement('div');
    container.id = 'property-list';
    container.className = 'mt-6';
    
    const searchResults = document.querySelector('.search-results');
    if (searchResults) {
        searchResults.appendChild(container);
    } else {
        document.querySelector('main').appendChild(container);
    }
    
    return container;
}

// Export analysis to PDF or Excel
function exportAnalysis(analysis) {
    // TODO: Implement export functionality
    console.log('Exporting analysis:', analysis);
}

// Update filters
function updateFilters() {
    // Trigger new search when filters change
    searchProperties();
}

// Create sample charts for demonstration
function createSampleCharts() {
    // Price Trends Chart
    const priceTrendsData = {
        x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        y: [200000, 205000, 215000, 218000, 225000, 230000],
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: 'rgb(79, 70, 229)',
            width: 2
        }
    };

    const priceTrendsLayout = {
        title: 'Average Property Prices',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 30, r: 20, b: 30, l: 40 },
        xaxis: {
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)'
        },
        yaxis: {
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)',
            tickformat: '$,.0f'
        }
    };

    Plotly.newPlot('price-trends', [priceTrendsData], priceTrendsLayout);

    // Market Stats Chart
    const marketStatsData = {
        values: [30, 25, 45],
        labels: ['High Potential', 'Medium Potential', 'Low Potential'],
        type: 'pie',
        marker: {
            colors: ['rgb(79, 70, 229)', 'rgb(147, 197, 253)', 'rgb(219, 234, 254)']
        }
    };

    const marketStatsLayout = {
        title: 'Lead Distribution',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 30, r: 20, b: 30, l: 20 }
    };

    Plotly.newPlot('market-stats', [marketStatsData], marketStatsLayout);
}

// Create market analysis chart
function createMarketAnalysisChart(analysis) {
    const chartData = {
        x: analysis.dates || [],
        y: analysis.prices || [],
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: 'rgb(79, 70, 229)',
            width: 2
        }
    };

    const chartLayout = {
        title: 'Market Analysis',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 30, r: 20, b: 30, l: 40 },
        xaxis: {
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)'
        },
        yaxis: {
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)',
            tickformat: '$,.0f'
        }
    };

    Plotly.newPlot('market-analysis-chart', [chartData], chartLayout);
}

// Initialize Price Trends Chart
function initializePriceTrendsChart() {
    const trace = {
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Price Trend',
        line: {
            color: 'rgb(79, 70, 229)',
            width: 2
        }
    };

    const layout = {
        margin: { t: 20, r: 20, l: 40, b: 40 },
        xaxis: {
            showgrid: false,
            zeroline: false
        },
        yaxis: {
            tickformat: '$,.0f',
            showgrid: true,
            gridcolor: 'rgb(243, 244, 246)'
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('price-trends', [trace], layout);
}

// Initialize Market Stats Chart
function initializeMarketStatsChart() {
    const data = [{
        values: [30, 45, 25],
        labels: ['High Potential', 'Medium Potential', 'Low Potential'],
        type: 'pie',
        marker: {
            colors: ['rgb(59, 130, 246)', 'rgb(139, 92, 246)', 'rgb(236, 72, 153)']
        }
    }];

    const layout = {
        margin: { t: 20, r: 20, l: 20, b: 20 },
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };

    Plotly.newPlot('market-stats', data, layout);
}

// Update Market Analysis
async function updateMarketAnalysis(location) {
    try {
        const response = await fetch(`/api/market/trends?zip_code=${location}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            updatePriceTrendsChart(data.trends);
            updateMarketStatsChart(data.trends.market_stats);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Update Price Trends Chart
function updatePriceTrendsChart(trends) {
    const trace = {
        x: trends.dates,
        y: trends.prices,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Price Trend',
        line: {
            color: 'rgb(79, 70, 229)',
            width: 2
        }
    };

    Plotly.react('price-trends', [trace]);
}

// Update Market Stats Chart
function updateMarketStatsChart(stats) {
    const data = [{
        values: [stats.high_potential, stats.medium_potential, stats.low_potential],
        labels: ['High Potential', 'Medium Potential', 'Low Potential'],
        type: 'pie',
        marker: {
            colors: ['rgb(59, 130, 246)', 'rgb(139, 92, 246)', 'rgb(236, 72, 153)']
        }
    }];

    Plotly.react('market-stats', data);
}

// Search Properties
async function searchProperties() {
    const location = document.getElementById('location').value;
    const priceRange = document.getElementById('price-range').value;
    const propertyType = document.getElementById('property-type').value;

    try {
        const response = await fetch('/api/properties/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: location,
                price_range: priceRange,
                property_type: propertyType
            }),
        });

        const data = await response.json();
        if (data.status === 'success') {
            displayProperties(data.properties);
            if (location) {
                updateMarketAnalysis(location);
            }
        } else {
            console.error('Error:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Display Properties
function displayProperties(properties) {
    const container = document.createElement('div');
    container.className = 'grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-6';

    properties.forEach(property => {
        const card = createPropertyCard(property);
        container.appendChild(card);
    });

    // Find and replace existing properties container if it exists
    const existingContainer = document.querySelector('.properties-container');
    if (existingContainer) {
        existingContainer.replaceWith(container);
    } else {
        // Insert after the search section
        const searchSection = document.querySelector('.bg-white.rounded-lg.shadow');
        searchSection.parentNode.insertBefore(container, searchSection.nextSibling);
    }
    container.classList.add('properties-container');
}

// Create Property Card
function createPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow overflow-hidden';
    card.innerHTML = `
        <div class="p-6">
            <h3 class="text-lg font-medium text-gray-900">${property.address}</h3>
            <p class="mt-1 text-sm text-gray-500">${property.city}, ${property.state} ${property.zip_code}</p>
            <div class="mt-4">
                <div class="flex items-center justify-between">
                    <span class="text-2xl font-bold text-gray-900">$${property.price.toLocaleString()}</span>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        property.lead_score >= 8 ? 'bg-green-100 text-green-800' :
                        property.lead_score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                    }">
                        Lead Score: ${property.lead_score}
                    </span>
                </div>
                <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
                    <span>${property.beds} beds</span>
                    <span>${property.baths} baths</span>
                    <span>${property.square_feet.toLocaleString()} sqft</span>
                </div>
                ${property.features ? `
                <div class="mt-4">
                    <div class="flex flex-wrap gap-2">
                        ${property.features.map(feature => `
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                ${feature}
                            </span>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                <div class="mt-4">
                    <button onclick="analyzeProperty('${property.property_id}')" 
                            class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                        Analyze Property
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Analyze Property
async function analyzeProperty(propertyId) {
    try {
        const response = await fetch('/api/properties/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ property_id: propertyId }),
        });

        const data = await response.json();
        if (data.status === 'success') {
            displayPropertyAnalysis(data.analysis);
        } else {
            console.error('Error:', data.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Display Property Analysis
function displayPropertyAnalysis(analysis) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 overflow-y-auto';
    modal.innerHTML = `
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div class="fixed inset-0 transition-opacity" aria-hidden="true">
                <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <div class="sm:flex sm:items-start">
                        <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                                Property Analysis: ${analysis.property_details.address}
                            </h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <!-- ROI Analysis -->
                                <div class="bg-gray-50 rounded-lg p-4">
                                    <h4 class="text-md font-medium text-gray-900 mb-3">ROI Analysis</h4>
                                    <div class="space-y-2">
                                        <div class="flex justify-between">
                                            <span>Purchase Price:</span>
                                            <span>$${analysis.roi_analysis.purchase_price.toLocaleString()}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>Repair Cost:</span>
                                            <span>$${analysis.roi_analysis.repair_cost.toLocaleString()}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>ARV:</span>
                                            <span>$${analysis.roi_analysis.arv.toLocaleString()}</span>
                                        </div>
                                        <div class="flex justify-between font-bold text-indigo-600">
                                            <span>Potential Profit:</span>
                                            <span>$${analysis.roi_analysis.potential_profit.toLocaleString()}</span>
                                        </div>
                                        <div class="flex justify-between font-bold text-green-600">
                                            <span>ROI:</span>
                                            <span>${analysis.roi_analysis.roi_percentage}%</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Market Analysis -->
                                <div class="bg-gray-50 rounded-lg p-4">
                                    <h4 class="text-md font-medium text-gray-900 mb-3">Market Analysis</h4>
                                    <div class="space-y-2">
                                        <div class="flex justify-between">
                                            <span>Days on Market:</span>
                                            <span>${analysis.property_details.days_on_market} days</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>Property Condition:</span>
                                            <span>${analysis.property_details.condition}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>Year Built:</span>
                                            <span>${analysis.property_details.year_built}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>Zoning:</span>
                                            <span>${analysis.property_details.zoning}</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Rehab Details -->
                                <div class="bg-gray-50 rounded-lg p-4">
                                    <h4 class="text-md font-medium text-gray-900 mb-3">Rehabilitation Details</h4>
                                    <div class="space-y-2">
                                        ${Object.entries(analysis.roi_analysis.rehab_details.breakdown).map(([key, value]) => `
                                            <div class="flex justify-between">
                                                <span>${key.charAt(0).toUpperCase() + key.slice(1)}:</span>
                                                <span>$${value.toLocaleString()}</span>
                                            </div>
                                        `).join('')}
                                        <div class="flex justify-between font-bold text-indigo-600 pt-2 border-t">
                                            <span>Total Rehab Cost:</span>
                                            <span>$${analysis.roi_analysis.rehab_details.total.toLocaleString()}</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Deal Analysis -->
                                <div class="bg-gray-50 rounded-lg p-4">
                                    <h4 class="text-md font-medium text-gray-900 mb-3">Deal Analysis</h4>
                                    <div class="space-y-4">
                                        <div>
                                            <h5 class="text-sm font-medium text-gray-700 mb-2">Recommended Strategies</h5>
                                            <div class="space-y-2">
                                                ${analysis.deal_analysis.recommended_strategies.map(strategy => `
                                                    <div class="flex justify-between items-center">
                                                        <span>${strategy.type}</span>
                                                        <span class="text-sm text-gray-500">${Math.round(strategy.confidence * 100)}% confidence</span>
                                                    </div>
                                                `).join('')}
                                            </div>
                                        </div>
                                        <div>
                                            <h5 class="text-sm font-medium text-gray-700 mb-2">Timeline</h5>
                                            <div class="space-y-2">
                                                <div class="flex justify-between">
                                                    <span>Acquisition:</span>
                                                    <span>${analysis.deal_analysis.timeline.acquisition} days</span>
                                                </div>
                                                <div class="flex justify-between">
                                                    <span>Renovation:</span>
                                                    <span>${analysis.deal_analysis.timeline.renovation} days</span>
                                                </div>
                                                <div class="flex justify-between">
                                                    <span>Sale:</span>
                                                    <span>${analysis.deal_analysis.timeline.sale} days</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                    <button type="button" onclick="this.closest('.fixed').remove()" 
                            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm">
                        Close
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Helper Functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function getLeadScoreClass(score) {
    if (score >= 8) return 'lead-score-high';
    if (score >= 5) return 'lead-score-medium';
    return 'lead-score-low';
}

function estimateMonthlyRent(propertyValue) {
    // Simple estimation using 1% rule
    return propertyValue * 0.01;
}

function calculateCapRate(annualIncome, totalInvestment) {
    return (annualIncome / totalInvestment) * 100;
}

function displayROIResults(results) {
    const roiResult = document.getElementById('roi-result');
    roiResult.innerHTML = `
        <div class="space-y-2">
            <p><strong>Total Investment:</strong> ${formatPrice(results.totalInvestment)}</p>
            <p><strong>Potential Profit:</strong> ${formatPrice(results.potentialProfit)}</p>
            <p><strong>ROI:</strong> ${results.roi.toFixed(2)}%</p>
            <p><strong>Est. Monthly Rent:</strong> ${formatPrice(results.monthlyRent)}</p>
            <p><strong>Cap Rate:</strong> ${results.capRate.toFixed(2)}%</p>
        </div>
    `;
    roiResult.classList.remove('hidden');
}

function displayStrategyRecommendations(strategies) {
    const container = document.getElementById('strategy-recommendations');
    container.innerHTML = strategies.map(strategy => `
        <div class="bg-white p-3 rounded-md shadow-sm">
            <div class="flex justify-between items-center mb-2">
                <h4 class="font-medium">${strategy.type}</h4>
                <span class="text-sm text-gray-500">${strategy.confidence}% confidence</span>
            </div>
            <p class="text-sm text-gray-600">${strategy.reasoning}</p>
        </div>
    `).join('');
}

function displayRiskAnalysis(risks) {
    const container = document.getElementById('risk-analysis');
    container.innerHTML = risks.map(risk => `
        <div class="bg-white p-3 rounded-md shadow-sm">
            <div class="flex justify-between items-center mb-2">
                <h4 class="font-medium">${risk.type}</h4>
                <span class="text-sm ${getRiskLevelClass(risk.level)}">${risk.level}</span>
            </div>
            <p class="text-sm text-gray-600">${risk.description}</p>
        </div>
    `).join('');
}

function getRiskLevelClass(level) {
    const classes = {
        'High': 'text-red-600',
        'Medium': 'text-yellow-600',
        'Low': 'text-green-600'
    };
    return classes[level] || 'text-gray-600';
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function updateChartsTheme(isDark) {
    const layout = {
        paper_bgcolor: isDark ? '#1F2937' : '#FFFFFF',
        plot_bgcolor: isDark ? '#1F2937' : '#FFFFFF',
        font: {
            color: isDark ? '#FFFFFF' : '#000000'
        }
    };

    Plotly.relayout('price-trends', layout);
    Plotly.relayout('market-stats', layout);
}
