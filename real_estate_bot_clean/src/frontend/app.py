from flask import Flask, render_template, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Sample data generation for 3D demo
def generate_market_data():
    dates = [(datetime.now() - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30, 0, -1)]
    return {
        "trends": {
            "dates": dates,
            "prices": [random.uniform(150, 200) for _ in dates],
            "inventory": [random.randint(100, 150) for _ in dates]
        },
        "deals": [
            {
                "id": i,
                "price": random.uniform(200000, 800000),
                "score": random.uniform(50, 100),
                "x": random.uniform(-2, 2),  # 3D coordinates
                "y": random.uniform(-2, 2),
                "z": random.uniform(-2, 2)
            } for i in range(20)
        ],
        "properties": [
            {
                "id": i,
                "address": f"{random.randint(100, 999)} Main St",
                "price": random.uniform(200000, 800000),
                "beds": random.randint(2, 5),
                "baths": random.randint(2, 4),
                "sqft": random.randint(1200, 3000),
                "score": random.uniform(50, 100),
                "image": f"https://picsum.photos/seed/{i}/300/200",
                "model3d": f"https://prod.spline.design/property-{i}"  # 3D model URL
            } for i in range(6)
        ],
        "heatmap": [
            {
                "lat": random.uniform(35, 40),
                "lng": random.uniform(-100, -90),
                "weight": random.uniform(0, 1),
                "elevation": random.uniform(0, 100)  # 3D elevation
            } for _ in range(50)
        ]
    }

@app.route('/')
def dashboard():
    return render_template('dashboard_3d.html')

@app.route('/api/market/analysis', methods=['GET'])
def market_analysis():
    return jsonify(generate_market_data())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
