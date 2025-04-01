from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.mock.data_generator import MockDataGenerator
from src.ai.agent import RealEstateAIAgent
import asyncio
import os
from datetime import datetime
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Flask app with correct static folder path
app = Flask(__name__, 
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
)
CORS(app)

# Initialize mock data generator
mock_data = MockDataGenerator()

# Initialize AI agent with test API key for demo
TEST_API_KEY = "sk-test-123"  # Replace with actual API key in production
ai_agent = RealEstateAIAgent(api_key=TEST_API_KEY)

@app.route('/')
def index():
    """Render the main dashboard"""
    return render_template('index.html')

@app.route('/api/properties/search', methods=['POST'])
def search_properties():
    """Search for properties based on criteria"""
    try:
        data = request.json
        properties = mock_data.search_properties(
            location=data.get('location'),
            price_range=data.get('price_range'),
            property_type=data.get('property_type')
        )
        return jsonify({
            "status": "success",
            "properties": properties
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/properties/analyze', methods=['POST'])
def analyze_property():
    """Analyze a specific property"""
    try:
        data = request.json
        analysis = mock_data.analyze_property(data.get('property_id'))
        return jsonify({
            "status": "success",
            "analysis": analysis
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/market/trends', methods=['GET'])
def get_market_trends():
    """Get market trends for an area"""
    try:
        zip_code = request.args.get('zip_code')
        trends = mock_data.get_market_trends(zip_code)
        return jsonify({
            "status": "success",
            "trends": trends
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/leads/score', methods=['POST'])
def score_lead():
    """Score a potential lead"""
    data = request.json
    # TODO: Integrate with your existing lead scoring logic
    return jsonify({
        "status": "success",
        "score": 0
    })

@app.route('/api/chat', methods=['POST'])
async def chat():
    data = request.json
    response = await ai_agent.process_input(
        user_input=data.get('message'),
        user_context=data.get('context')
    )
    return jsonify(response)

if __name__ == '__main__':
    print(f"Static folder: {app.static_folder}")
    print(f"Template folder: {app.template_folder}")
    app.run(debug=True, port=5000)
