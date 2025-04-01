// Modern dashboard implementation with interactive components
class RealEstateDashboard {
    constructor() {
        this.charts = {};
        this.filters = {};
        this.selectedMarket = null;
        this.initializeComponents();
    }

    async initializeComponents() {
        // Initialize Chart.js components
        this.charts.marketTrends = this.createMarketTrendsChart();
        this.charts.dealScores = this.createDealScoresChart();
        this.charts.propertyHeatmap = this.createPropertyHeatmap();
        
        // Initialize interactive filters
        this.setupFilters();
        
        // Setup property cards container
        this.propertyContainer = new PropertyCardContainer();
        
        // Initialize analysis tools
        this.dealCalculator = new DealCalculator();
        this.rehabEstimator = new RehabEstimator();
        this.profitProjector = new ProfitProjector();
        
        // Load initial data
        await this.refreshData();
    }

    createMarketTrendsChart() {
        return new Chart('marketTrends', {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Price/sqft Trend',
                    borderColor: '#4CAF50',
                    data: []
                }, {
                    label: 'Inventory Level',
                    borderColor: '#2196F3',
                    data: []
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                return this.formatChartLabel(context);
                            }
                        }
                    }
                }
            }
        });
    }

    createDealScoresChart() {
        return new Chart('dealScores', {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Deal Opportunities',
                    data: [],
                    backgroundColor: (context) => {
                        const score = context.raw?.y || 0;
                        return this.getDealScoreColor(score);
                    }
                }]
            },
            options: {
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Deal Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Price Range'
                        }
                    }
                }
            }
        });
    }

    createPropertyHeatmap() {
        return new mapboxgl.Map({
            container: 'propertyHeatmap',
            style: 'mapbox://styles/mapbox/light-v10',
            center: [-96, 37.8],
            zoom: 3
        });
    }

    setupFilters() {
        this.filters = {
            priceRange: new RangeSlider('priceFilter', {
                min: 0,
                max: 1000000,
                step: 10000,
                onChange: () => this.refreshData()
            }),
            dealScore: new RangeSlider('scoreFilter', {
                min: 0,
                max: 100,
                step: 5,
                onChange: () => this.refreshData()
            }),
            propertyType: new MultiSelect('propertyType', {
                options: ['Single Family', 'Multi Family', 'Commercial'],
                onChange: () => this.refreshData()
            })
        };
    }

    async refreshData() {
        try {
            const response = await fetch('/api/market/analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.getFilters())
            });
            
            const data = await response.json();
            this.updateCharts(data);
            this.updatePropertyCards(data.properties);
            this.updateAnalysisTools(data);
            
        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
            // Show user-friendly error message
            this.showError('Unable to update dashboard. Please try again later.');
        }
    }

    updateCharts(data) {
        // Update market trends
        this.charts.marketTrends.data.labels = data.trends.dates;
        this.charts.marketTrends.data.datasets[0].data = data.trends.prices;
        this.charts.marketTrends.data.datasets[1].data = data.trends.inventory;
        this.charts.marketTrends.update();

        // Update deal scores
        this.charts.dealScores.data.datasets[0].data = data.deals.map(d => ({
            x: d.price,
            y: d.score,
            propertyId: d.id
        }));
        this.charts.dealScores.update();

        // Update heatmap
        this.updateHeatmap(data.heatmap);
    }

    updatePropertyCards(properties) {
        this.propertyContainer.clear();
        properties.forEach(property => {
            const card = new PropertyCard(property);
            this.propertyContainer.addCard(card);
        });
    }

    updateAnalysisTools(data) {
        this.dealCalculator.update(data.market);
        this.rehabEstimator.update(data.costs);
        this.profitProjector.update(data.projections);
    }

    getFilters() {
        return {
            priceRange: this.filters.priceRange.getValue(),
            dealScore: this.filters.dealScore.getValue(),
            propertyType: this.filters.propertyType.getSelected(),
            market: this.selectedMarket
        };
    }

    showError(message) {
        // Implement user-friendly error display
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new RealEstateDashboard();
});
