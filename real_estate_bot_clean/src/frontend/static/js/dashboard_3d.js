// Modern 3D dashboard implementation with Spline integration
class RealEstateDashboard3D {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.charts = {};
        this.filters = {};
        this.selectedMarket = null;
        this.splineViewers = {};
        this.initializeComponents();
    }

    async initializeComponents() {
        // Initialize Three.js scene for 3D visualizations
        this.initThreeJS();
        
        // Initialize Spline components
        await this.initSpline();
        
        // Initialize Chart.js with 3D effects
        this.initCharts();
        
        // Setup interactive 3D filters
        this.setupFilters();
        
        // Initialize 3D property cards
        this.propertyContainer = new PropertyCardContainer3D();
        
        // Initialize 3D analysis tools
        this.dealCalculator = new DealCalculator3D();
        this.rehabEstimator = new RehabEstimator3D();
        this.profitProjector = new ProfitProjector3D();
        
        // Load initial data with 3D animations
        await this.refreshData();
        
        // Start animation loop
        this.animate();
    }

    initThreeJS() {
        // Setup Three.js scene
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        
        // Add ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);
        
        // Add directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);
        
        // Position camera
        this.camera.position.z = 5;
    }

    async initSpline() {
        // Initialize Spline viewers for different components
        this.splineViewers = {
            background: document.querySelector('.spline-bg'),
            propertyCards: document.querySelector('.property-cards-3d'),
            logo: document.querySelector('.logo-3d')
        };
        
        // Configure Spline interactions
        for (const [key, viewer] of Object.entries(this.splineViewers)) {
            viewer.addEventListener('mousedown', (e) => this.handleSplineInteraction(e, key));
            viewer.addEventListener('mousemove', (e) => this.handleSplineHover(e, key));
        }
    }

    initCharts() {
        // Market Trends with 3D effects
        this.charts.marketTrends = new Chart('marketTrends', {
            type: 'line',
            plugins: [this.create3DChartPlugin()],
            data: {
                labels: [],
                datasets: [{
                    label: 'Price/sqft Trend',
                    borderColor: '#4CAF50',
                    data: [],
                    tension: 0.4
                }, {
                    label: 'Inventory Level',
                    borderColor: '#2196F3',
                    data: [],
                    tension: 0.4
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
                            label: (context) => this.format3DChartLabel(context)
                        }
                    }
                }
            }
        });

        // Initialize 3D Deal Scores visualization
        this.initializeDealScores3D();
    }

    create3DChartPlugin() {
        return {
            id: '3dEffect',
            beforeDraw: (chart) => {
                const ctx = chart.ctx;
                const width = chart.width;
                const height = chart.height;
                
                // Add 3D shadow effect
                const gradient = ctx.createLinearGradient(0, 0, 0, height);
                gradient.addColorStop(0, 'rgba(33, 150, 243, 0.1)');
                gradient.addColorStop(1, 'rgba(33, 150, 243, 0)');
                
                ctx.save();
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, width, height);
                ctx.restore();
            }
        };
    }

    initializeDealScores3D() {
        const container = document.getElementById('dealScores3D');
        
        // Create 3D scatter plot
        const geometry = new THREE.SphereGeometry(0.1, 32, 32);
        const material = new THREE.MeshPhongMaterial({
            color: 0x2196F3,
            shininess: 100
        });
        
        this.dealScoresPoints = [];
        
        // Add points to scene
        for (let i = 0; i < 50; i++) {
            const point = new THREE.Mesh(geometry, material.clone());
            this.dealScoresPoints.push(point);
            this.scene.add(point);
        }
    }

    setupFilters() {
        // Initialize 3D range sliders
        this.filters = {
            priceRange: new RangeSlider3D('priceFilter', {
                min: 0,
                max: 1000000,
                step: 10000,
                onChange: () => this.refreshData()
            }),
            dealScore: new RangeSlider3D('scoreFilter', {
                min: 0,
                max: 100,
                step: 5,
                onChange: () => this.refreshData()
            }),
            propertyType: new MultiSelect3D('propertyType', {
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
            
            // Update visualizations with 3D animations
            await Promise.all([
                this.updateCharts(data),
                this.updatePropertyCards3D(data.properties),
                this.updateAnalysisTools3D(data)
            ]);
            
        } catch (error) {
            console.error('Failed to refresh 3D dashboard:', error);
            this.showError('Unable to update dashboard. Please try again later.');
        }
    }

    async updateCharts(data) {
        // Animate market trends
        await this.animateChartUpdate(this.charts.marketTrends, {
            labels: data.trends.dates,
            datasets: [{
                data: data.trends.prices
            }, {
                data: data.trends.inventory
            }]
        });

        // Update 3D deal scores
        this.updateDealScores3D(data.deals);
    }

    async animateChartUpdate(chart, newData) {
        return new Promise((resolve) => {
            gsap.to(chart.data.datasets[0].data, {
                endArray: newData.datasets[0].data,
                duration: 1,
                ease: "power2.out",
                onUpdate: () => chart.update('none'),
                onComplete: resolve
            });
        });
    }

    updateDealScores3D(deals) {
        deals.forEach((deal, i) => {
            if (this.dealScoresPoints[i]) {
                gsap.to(this.dealScoresPoints[i].position, {
                    x: (deal.price / 1000000) - 2.5,
                    y: (deal.score / 100) - 0.5,
                    z: Math.random() * 2 - 1,
                    duration: 1,
                    ease: "power2.out"
                });
                
                // Update color based on score
                const hue = deal.score * 1.2; // 0-120 range for red to green
                this.dealScoresPoints[i].material.color.setHSL(hue/360, 1, 0.5);
            }
        });
    }

    async updatePropertyCards3D(properties) {
        await this.propertyContainer.updateCards(properties);
    }

    updateAnalysisTools3D(data) {
        this.dealCalculator.update3D(data.market);
        this.rehabEstimator.update3D(data.costs);
        this.profitProjector.update3D(data.projections);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Rotate deal scores visualization
        this.scene.rotation.y += 0.001;
        
        // Update 3D effects
        this.renderer.render(this.scene, this.camera);
    }

    handleSplineInteraction(event, viewerKey) {
        // Handle Spline object interactions
        const viewer = this.splineViewers[viewerKey];
        if (viewer) {
            // Implement custom interaction logic
        }
    }

    handleSplineHover(event, viewerKey) {
        // Handle hover effects on Spline objects
        const viewer = this.splineViewers[viewerKey];
        if (viewer) {
            // Implement hover effects
        }
    }

    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        
        gsap.to(errorContainer, {
            opacity: 0,
            y: -20,
            duration: 0.5,
            delay: 4.5,
            onComplete: () => {
                errorContainer.style.display = 'none';
                gsap.set(errorContainer, { opacity: 1, y: 0 });
            }
        });
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new RealEstateDashboard3D();
});
