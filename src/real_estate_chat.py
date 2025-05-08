"""Real Estate AI Chat Interface"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .data.extractors import AttomDataExtractor
from .data.manager import DataManager
from .utils.visualizer import DataVisualizer
from .utils.formatter import ResponseFormatter
from .controller import RealEstateController

logger = logging.getLogger(__name__)

class RealEstateChat:
    """Interactive chat interface for real estate queries with comprehensive analysis"""
    
    def __init__(self):
        self.controller = RealEstateController()
        self.extractor = AttomDataExtractor()
        self.data_manager = DataManager()
        self.visualizer = DataVisualizer(theme='plotly_white')
        self.formatter = ResponseFormatter()
        self.current_property = None
        
        # Query patterns for natural language processing
        self.query_patterns = {
            'property_analysis': [
                'analyze property', 'property details', 'tell me about',
                'what do you know about', 'look up property'
            ],
            'value_analysis': [
                'market value', 'worth', 'price', 'value', 'estimate',
                'comps', 'comparables', 'arv'
            ],
            'owner_info': [
                'owner', 'seller', 'who owns', 'ownership', 'landlord',
                'contact info', 'mailing address'
            ],
            'distressed': [
                'foreclosure', 'pre-foreclosure', 'reo', 'bank owned',
                'distressed', 'motivated', 'liens', 'vacant'
            ],
            'market_trends': [
                'market', 'trends', 'appreciation', 'growth',
                'sales', 'inventory', 'days on market'
            ],
            'investment': [
                'investment', 'roi', 'cash flow', 'rental',
                'repairs', 'rehab', 'mao', 'offer'
            ],
            'lead_score': [
                'lead score', 'motivation', 'seller score',
                'priority', 'ranking', 'hot lead'
            ]
        }
    
    async def chat(self):
        """Start the interactive chat interface"""
        print("\nWelcome to Real Estate AI Chat!")
        self._print_capabilities()
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                
                response = await self.process_query(user_input)
                print("\nAI:", response)
                
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print("\nAI: I encountered an error. Please try again.")
    
    async def process_query(self, query: str) -> str:
        """Process user query and generate structured response"""
        try:
            # Extract address and query type
            query_type, address, zipcode = self._parse_query(query)
            
            if not query_type and not self.current_property:
                return self._get_help_message()
            
            # Get or update property data
            if address and zipcode:
                self.current_property = await self.controller.analyze_property(address, zipcode)
            
            if not self.current_property:
                return "Please provide a valid property address and zip code."
            
            # Generate appropriate response based on query type
            response = await self._generate_response(query_type)
            
            # Create relevant visualizations
            await self._create_visualizations(query_type)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I had trouble processing that request. Please try again."
    
    def _parse_query(self, query: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse query to extract type and property information"""
        query = query.lower()
        
        # Determine query type
        query_type = None
        for qtype, patterns in self.query_patterns.items():
            if any(pattern in query for pattern in patterns):
                query_type = qtype
                break
        
        # Extract address and zipcode if present
        address = None
        zipcode = None
        
        if 'at' in query and 'in' in query:
            try:
                address_part = query.split('at')[1].split('in')[0].strip()
                zip_part = query.split('in')[-1].strip()
                if zip_part.isdigit() and len(zip_part) == 5:
                    address = address_part
                    zipcode = zip_part
            except:
                pass
        
        return query_type, address, zipcode
    
    async def _generate_response(self, query_type: str) -> str:
        """Generate structured response based on query type"""
        if not query_type:
            return self._analyze_property_summary()
        
        response_methods = {
            'property_analysis': self._analyze_property_summary,
            'value_analysis': self._analyze_market_value,
            'owner_info': self._analyze_owner_info,
            'distressed': self._analyze_distressed_status,
            'market_trends': self._analyze_market_trends,
            'investment': self._analyze_investment_potential,
            'lead_score': self._analyze_lead_score
        }
        
        method = response_methods.get(query_type, self._analyze_property_summary)
        return await method()
    
    async def _create_visualizations(self, query_type: str) -> None:
        """Create relevant visualizations based on query type"""
        try:
            if not self.current_property:
                return
            
            if query_type in ['value_analysis', 'property_analysis']:
                value_chart = self.visualizer.create_property_value_chart(self.current_property)
                self.visualizer.save_chart(value_chart, 'property_value.html')
            
            elif query_type == 'market_trends':
                market_chart = self.visualizer.create_market_trends_chart(self.current_property)
                self.visualizer.save_chart(market_chart, 'market_trends.html')
            
            elif query_type == 'investment':
                investment_chart = self.visualizer.create_investment_analysis_chart(self.current_property)
                self.visualizer.save_chart(investment_chart, 'investment_analysis.html')
                
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
    
    async def _analyze_property_summary(self) -> str:
        """Generate comprehensive property summary"""
        if not self.current_property:
            return "No property is currently being analyzed."
        
        details = self.current_property.get('property_details', {})
        return self.formatter.format_property_analysis(details)
    
    async def _analyze_market_value(self) -> str:
        """Analyze property's market value and comps"""
        if not self.current_property:
            return "Please analyze a property first."
        
        value_data = self.current_property.get('valuation', {})
        return self.formatter.format_value_analysis(value_data)
    
    async def _analyze_owner_info(self) -> str:
        """Analyze owner information and motivation"""
        if not self.current_property:
            return "Please analyze a property first."
        
        owner_data = self.current_property.get('owner_info', {})
        return self.formatter.format_owner_analysis(owner_data)
    
    async def _analyze_distressed_status(self) -> str:
        """Analyze property's distressed status"""
        if not self.current_property:
            return "Please analyze a property first."
        
        distressed_data = self.current_property.get('distressed', {})
        return self.formatter.format_distressed_analysis(distressed_data)
    
    async def _analyze_market_trends(self) -> str:
        """Analyze market trends and metrics"""
        if not self.current_property:
            return "Please analyze a property first."
        
        market_data = self.current_property.get('market_data', {})
        return self.formatter.format_market_analysis(market_data)
    
    async def _analyze_investment_potential(self) -> str:
        """Analyze investment potential and strategy"""
        if not self.current_property:
            return "Please analyze a property first."
        
        investment_data = self.current_property.get('investment_metrics', {})
        return self.formatter.format_investment_analysis(investment_data)
    
    async def _analyze_lead_score(self) -> str:
        """Analyze lead score and motivation"""
        if not self.current_property:
            return "Please analyze a property first."
        
        lead_data = self.current_property.get('lead_score', {})
        return self.formatter.format_lead_analysis(lead_data)
    
    def _print_capabilities(self) -> None:
        """Print AI capabilities"""
        print("\nI can help you with:")
        print("1. Property Analysis & Valuation")
        print("   - Market value estimates")
        print("   - Property details and features")
        print("   - Tax and assessment info")
        print("\n2. Seller & Ownership Insights")
        print("   - Owner information and history")
        print("   - Contact details and motivation")
        print("\n3. Distressed Property Analysis")
        print("   - Foreclosure and REO status")
        print("   - Vacancy and distress indicators")
        print("\n4. Market & Investment Analysis")
        print("   - Local market trends")
        print("   - Investment metrics (ARV, MAO, ROI)")
        print("\nExample: 'analyze property at 123 Main St in 12345'")
    
    def _get_help_message(self) -> str:
        """Get help message with example commands"""
        return (
            "I can help you analyze properties! Try these commands:\n"
            "• analyze property at [address] in [zipcode]\n"
            "• what's the market value?\n"
            "• tell me about the owner\n"
            "• what's the investment potential?\n"
            "• show me market trends\n"
            "• what's the lead score?"
        )

async def main():
    """Run the chat interface"""
    chat = RealEstateChat()
    await chat.chat()

if __name__ == "__main__":
    asyncio.run(main())
