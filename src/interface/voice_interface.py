"""Voice-enabled natural language interface.

Provides conversational AI interface for real estate analysis using:
- Speech recognition
- Natural language understanding
- Text-to-speech synthesis
- Context management
"""

import logging
from typing import Dict, List, Optional, Tuple
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
import json
import asyncio

from ..real_estate_ai_agent import RealEstateAIAgent

logger = logging.getLogger(__name__)

class VoiceInterface:
    """Voice interface for real estate analysis."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 175)  # Speed of speech
        self.engine.setProperty('volume', 0.9)
        
        # Initialize NLP pipeline
        self.nlp = pipeline("text-classification", 
                          model="real-estate/intent-classifier",
                          tokenizer="real-estate/intent-classifier")
        
        # Initialize AI agent
        self.agent = RealEstateAIAgent()
        
        # Conversation context
        self.context = {
            'current_property': None,
            'current_location': None,
            'last_analysis': None,
            'follow_up_questions': []
        }
    
    async def start_conversation(self):
        """Start voice conversation loop."""
        self.speak("Hello! I'm your real estate analysis assistant. How can I help you today?")
        
        while True:
            try:
                # Listen for user input
                query = self.listen()
                if not query:
                    continue
                
                # Process the query
                response = await self.process_query(query)
                
                # Speak the response
                self.speak(response)
                
                # Generate follow-up questions
                self._generate_follow_ups()
                
            except Exception as e:
                logger.error(f"Error in conversation: {str(e)}")
                self.speak("I'm sorry, I encountered an error. Could you please repeat that?")
    
    def listen(self) -> Optional[str]:
        """Listen for voice input and convert to text."""
        try:
            with sr.Microphone() as source:
                logger.debug("Listening for input...")
                audio = self.recognizer.listen(source)
                
                text = self.recognizer.recognize_google(audio)
                logger.debug(f"Recognized: {text}")
                return text
                
        except sr.UnknownValueError:
            self.speak("I'm sorry, I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {str(e)}")
            self.speak("I'm having trouble with speech recognition. Please try again.")
            return None
    
    def speak(self, text: str):
        """Convert text to speech."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
    
    async def process_query(self, query: str) -> str:
        """Process natural language query and generate response."""
        try:
            # Classify intent
            intent = self._classify_intent(query)
            
            # Extract entities
            entities = self._extract_entities(query)
            
            # Update context
            self._update_context(intent, entities)
            
            # Handle intent
            response = await self._handle_intent(intent, entities)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I'm sorry, I couldn't process your request. Could you rephrase that?"
    
    def _classify_intent(self, query: str) -> Dict:
        """Classify user intent from query."""
        result = self.nlp(query)[0]
        return {
            'intent': result['label'],
            'confidence': result['score']
        }
    
    def _extract_entities(self, query: str) -> Dict:
        """Extract relevant entities from query."""
        # TODO: Implement entity extraction
        return {}
    
    def _update_context(self, intent: Dict, entities: Dict):
        """Update conversation context."""
        if entities.get('property'):
            self.context['current_property'] = entities['property']
        if entities.get('location'):
            self.context['current_location'] = entities['location']
    
    async def _handle_intent(self, intent: Dict, entities: Dict) -> str:
        """Handle classified intent and generate response."""
        intent_type = intent['intent']
        
        if intent_type == 'property_analysis':
            return await self._handle_property_analysis(entities)
        elif intent_type == 'market_insights':
            return await self._handle_market_insights(entities)
        elif intent_type == 'property_search':
            return await self._handle_property_search(entities)
        elif intent_type == 'clarification':
            return self._handle_clarification()
        else:
            return "I'm not sure how to help with that. Could you be more specific?"
    
    async def _handle_property_analysis(self, entities: Dict) -> str:
        """Handle property analysis request."""
        address = entities.get('address') or self.context.get('current_property')
        if not address:
            return "Could you specify the property address you'd like to analyze?"
        
        zipcode = entities.get('zipcode')
        if not zipcode:
            return "I'll need the ZIP code for that property as well."
        
        analysis = await self.agent.analyze_property(address, zipcode)
        self.context['last_analysis'] = analysis
        
        return self._format_property_analysis(analysis)
    
    async def _handle_market_insights(self, entities: Dict) -> str:
        """Handle market insights request."""
        zipcode = entities.get('zipcode') or self.context.get('current_location')
        if not zipcode:
            return "Which area would you like insights for? Please provide a ZIP code."
        
        insights = await self.agent.get_market_insights(zipcode)
        return self._format_market_insights(insights)
    
    async def _handle_property_search(self, entities: Dict) -> str:
        """Handle property search request."""
        if not entities.get('city') or not entities.get('state'):
            return "Could you specify the city and state you're interested in?"
        
        properties = await self.agent.search_properties(
            entities['city'],
            entities['state'],
            entities.get('zipcode', '')
        )
        
        return self._format_property_search(properties)
    
    def _handle_clarification(self) -> str:
        """Handle clarification request."""
        if not self.context['follow_up_questions']:
            return "What would you like me to clarify?"
        
        return self.context['follow_up_questions'][0]
    
    def _generate_follow_ups(self):
        """Generate relevant follow-up questions based on context."""
        follow_ups = []
        
        if self.context.get('last_analysis'):
            follow_ups.append("Would you like to know more about the neighborhood trends?")
            follow_ups.append("Should I analyze similar properties in the area?")
        
        if self.context.get('current_location'):
            follow_ups.append("Would you like to see investment opportunities in this area?")
        
        self.context['follow_up_questions'] = follow_ups
    
    def _format_property_analysis(self, analysis: Dict) -> str:
        """Format property analysis for speech."""
        if 'error' in analysis:
            return f"I encountered an error analyzing the property: {analysis['error']}"
        
        summary = analysis.get('summary', {})
        return (
            f"Here's what I found about the property. "
            f"The current market strength is {summary.get('market_strength', 'unknown')}. "
            f"The neighborhood quality is {summary.get('neighborhood_quality', 'unknown')} "
            f"and growth potential is {summary.get('growth_potential', 'unknown')}. "
            f"{summary.get('investment_recommendation', '')}"
        )
    
    def _format_market_insights(self, insights: Dict) -> str:
        """Format market insights for speech."""
        if 'error' in insights:
            return f"I encountered an error getting market insights: {insights['error']}"
        
        summary = insights.get('summary', {})
        return (
            f"Here are the market insights. "
            f"The market is currently showing {summary.get('market_strength', 'moderate')} strength. "
            f"Growth potential is {summary.get('growth_potential', 'unknown')}. "
            f"{summary.get('investment_recommendation', '')}"
        )
    
    def _format_property_search(self, properties: List[Dict]) -> str:
        """Format property search results for speech."""
        if not properties:
            return "I couldn't find any properties matching your criteria."
        
        count = len(properties)
        top_property = properties[0]
        
        return (
            f"I found {count} properties. "
            f"The top match is a {top_property.get('property_type', 'property')} "
            f"priced at {top_property.get('price', 'unknown')} "
            f"with a match score of {top_property.get('score', 0):.0%}. "
            "Would you like to hear more details about this property?"
        )
