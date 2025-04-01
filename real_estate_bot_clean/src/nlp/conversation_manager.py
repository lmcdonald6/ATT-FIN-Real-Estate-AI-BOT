"""
Advanced Conversation Management for Real Estate AI Bot
Handles context tracking, intent recognition, and dynamic responses
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConversationContext:
    """Tracks conversation state and context"""
    last_property: Optional[str] = None
    last_query_type: Optional[str] = None
    last_response: Optional[Dict] = None
    conversation_history: List[Dict] = None
    user_preferences: Dict = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.user_preferences is None:
            self.user_preferences = {}

class ConversationManager:
    """Manages advanced conversation features"""
    
    def __init__(self):
        self.context = ConversationContext()
        
        # Intent patterns for better query understanding
        self.intent_patterns = {
            'value_analysis': [
                'worth', 'value', 'price', 'estimate', 'appraisal',
                'how much', 'market value', 'arv', 'comps', 'valuation',
                'what would it sell for', 'what could i get', 'fair market',
                'current price', 'list price', 'asking price', 'sale price'
            ],
            'property_details': [
                'details', 'info', 'about', 'tell me about', 'what do you know',
                'features', 'specs', 'characteristics', 'description',
                'what kind of', 'what type of', 'condition', 'status',
                'square feet', 'sqft', 'beds', 'baths', 'year built',
                'lot size', 'garage', 'pool', 'renovations', 'updates'
            ],
            'owner_info': [
                'owner', 'who owns', 'seller', 'landlord', 'homeowner',
                'owned by', 'belongs to', 'property owner', 'current owner',
                'previous owner', 'how long owned', 'who lives', 'resident',
                'owner history', 'seller motivation', 'why selling',
                'contact info', 'phone number', 'email', 'reach out'
            ],
            'occupancy': [
                'vacant', 'occupied', 'empty', 'lives there', 'living in',
                'tenant', 'rental', 'anyone home', 'abandoned', 'move out',
                'utilities on', 'power on', 'water on', 'gas on',
                'mail delivery', 'last seen', 'activity', 'occupant'
            ],
            'distressed': [
                'distressed', 'foreclosure', 'pre-foreclosure', 'reo',
                'behind', 'delinquent', 'tax sale', 'auction', 'bank owned',
                'motivated', 'must sell', 'quick sale', 'short sale',
                'underwater', 'upside down', 'back taxes', 'tax liens',
                'code violations', 'probate', 'divorce', 'estate sale'
            ],
            'market_analysis': [
                'market', 'trend', 'stats', 'statistics', 'data',
                'appreciation', 'growth', 'sales data', 'average price',
                'median price', 'days on market', 'inventory', 'supply',
                'demand', 'buyer interest', 'seller market', 'buyer market',
                'neighborhood', 'area', 'zip code', 'school district'
            ],
            'investment': [
                'roi', 'return', 'profit', 'cash flow', 'cap rate',
                'investment', 'offer', 'deal', 'wholesale', 'flip',
                'rehab', 'renovation cost', 'repair estimate', 'arv',
                'max offer', 'mao', 'rental', 'cash on cash', 'equity',
                'down payment', 'financing', 'hard money', 'private money'
            ]
        }
        
        # Response templates for more natural conversation
        self.response_templates = {
            'greeting': [
                "Hi! I'm your real estate analysis assistant. How can I help you today?",
                "Hello! Ready to analyze some properties. What would you like to know?",
                "Welcome! I can help you find and analyze real estate opportunities.",
                "Hi there! Let's find some great real estate deals together.",
                "Hello! I'm here to help with property analysis and lead scoring."
            ],
            'clarification': [
                "Could you provide the property address for that?",
                "I'll help with that. Which property are you interested in?",
                "Sure, let me know the address you're looking at.",
                "I can analyze that for you. What's the property address?",
                "To give you accurate information, I need the property address."
            ],
            'transition': [
                "Let me analyze that for you...",
                "I'll look into that right away...",
                "Gathering the latest data for you...",
                "Analyzing the property details now...",
                "Let me check the latest market data..."
            ],
            'follow_up': [
                "Would you like to know more about {}?",
                "I can also tell you about {}. Interested?",
                "Should I analyze {} as well?",
                "Would you like me to look into {}?",
                "I can provide more details about {}."
            ],
            'property_context': [
                "Based on my analysis of {} in {}:",
                "Looking at {} in the {} area:",
                "Here's what I found for {} in {}:",
                "Analyzing {} in the {} market:",
                "For {} in {}, here's what I see:"
            ],
            'high_score_lead': [
                "This looks like a hot lead! Here's why:",
                "This property shows strong potential. Let me explain:",
                "I've found some promising indicators here:",
                "This could be a great opportunity. Here's the analysis:",
                "You might want to act quickly on this one. Here's why:"
            ],
            'medium_score_lead': [
                "This property shows some potential. Here's the breakdown:",
                "There are some interesting factors to consider:",
                "This could be worth exploring. Here's what I found:",
                "Here's why this property might be worth pursuing:",
                "Let me show you the opportunities and challenges here:"
            ],
            'low_score_lead': [
                "This property might not be the best fit. Here's why:",
                "You might want to consider other options. Here's the analysis:",
                "There are some concerns to be aware of:",
                "Let me show you why this might not be ideal:",
                "Here are the factors that make this less attractive:"
            ],
            'error_handling': [
                "I couldn't find that information. Could you try rephrasing?",
                "I'm having trouble understanding. Could you be more specific?",
                "I want to help, but I need more details about what you're looking for.",
                "Could you provide more context about what you need?",
                "I'm not sure about that. Could you ask in a different way?"
            ],
            'success_confirmation': [
                "I've found what you're looking for. Here's the analysis:",
                "Great news! I have the information you need:",
                "I've completed the analysis. Here's what I found:",
                "Here's your comprehensive property report:",
                "I've gathered all the relevant data. Take a look:"
            ]
        }
        
        # Contextual suggestions based on query type
        self.contextual_suggestions = {
            'value_analysis': [
                'recent comparable sales',
                'market appreciation trends',
                'investment potential analysis',
                'rental market comparison',
                'price per square foot analysis',
                'historical price trends',
                'equity position calculation'
            ],
            'property_details': [
                'ownership history',
                'tax assessment records',
                'improvement history',
                'permit records',
                'zoning restrictions',
                'insurance claims history',
                'utility consumption patterns'
            ],
            'owner_info': [
                'contact strategy recommendations',
                'other properties in portfolio',
                'motivation analysis',
                'financial position assessment',
                'timeline expectations',
                'decision-making factors',
                'negotiation leverage points'
            ],
            'occupancy': [
                'utility status verification',
                'neighbor interviews',
                'mail accumulation check',
                'property maintenance status',
                'recent activity patterns',
                'security concerns',
                'access possibilities'
            ],
            'distressed': [
                'current tax status',
                'lien positions',
                'repair cost estimates',
                'timeline to auction',
                'redemption period details',
                'bankruptcy status',
                'code violation history'
            ],
            'market_analysis': [
                'price trends by property type',
                'inventory levels',
                'days on market analysis',
                'buyer demand metrics',
                'new construction impact',
                'rental market dynamics',
                'neighborhood development plans'
            ],
            'investment': [
                'detailed ROI calculation',
                'repair cost breakdown',
                'exit strategy analysis',
                'financing options',
                'cash flow projections',
                'risk assessment',
                'timeline to completion'
            ]
        }

    def analyze_intent(self, query: str) -> str:
        """Determine query intent using advanced pattern matching"""
        query = query.lower()
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in query for pattern in patterns):
                return intent
                
        return 'unknown'

    def update_context(self, query: str, intent: str, response: Dict):
        """Update conversation context with latest interaction"""
        # Extract property address if present
        address = self._extract_address(query)
        if address:
            self.context.last_property = address
            
        # Update context
        self.context.last_query_type = intent
        self.context.last_response = response
        
        # Add to history
        self.context.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'intent': intent,
            'property': address,
            'response': response
        })

    def get_follow_up_suggestions(self) -> List[str]:
        """Generate contextual follow-up suggestions"""
        if not self.context.last_query_type:
            return []
            
        suggestions = self.contextual_suggestions.get(
            self.context.last_query_type, []
        )[:3]  # Get top 3 suggestions
        
        if self.context.last_property:
            suggestions = [
                f"{s} for {self.context.last_property}"
                for s in suggestions
            ]
            
        return suggestions

    def generate_response_text(self, data: Dict, intent: str) -> str:
        """Generate natural language response"""
        if not data or data.get('status') == 'error':
            return self._get_random_template('error_handling')
            
        # Get base response
        response = data.get('response', [])
        if not response:
            return self._get_random_template('error_handling')
            
        # Add context-aware intro
        intro = self._get_contextual_intro(intent)
        
        # Add property context if available
        if self.context.last_property:
            intro = intro.replace(
                'that property',
                f'{self.context.last_property}'
            )
            
        # Add lead score context if available
        if 'lead_score' in data:
            score = data['lead_score']
            if score >= 80:
                intro = self._get_random_template('high_score_lead')
            elif score >= 60:
                intro = self._get_random_template('medium_score_lead')
            else:
                intro = self._get_random_template('low_score_lead')
            
        # Combine everything
        full_response = [intro] + response
        
        # Add follow-up suggestions
        suggestions = self.get_follow_up_suggestions()
        if suggestions:
            full_response.append("")
            full_response.append("You might also want to know:")
            for suggestion in suggestions:
                full_response.append(f"- {suggestion}")
                
        return "\n".join(full_response)

    def _get_random_template(self, template_type: str) -> str:
        """Get a random response template of the specified type"""
        import random
        templates = self.response_templates.get(template_type, [])
        return random.choice(templates) if templates else ""

    def _get_contextual_intro(self, intent: str) -> str:
        """Get context-aware introduction"""
        intros = {
            'value_analysis': "Based on my analysis of that property:",
            'property_details': "Here are the key details I found:",
            'owner_info': "Here's what I know about the owner:",
            'occupancy': "Regarding the occupancy status:",
            'distressed': "I've analyzed the distress indicators:",
            'market_analysis': "Here's my market analysis:",
            'investment': "Here's my investment analysis:"
        }
        return intros.get(intent, "Here's what I found:")

    def _extract_address(self, query: str) -> Optional[str]:
        """Extract property address from query"""
        # TODO: Implement more sophisticated address extraction
        # For now, just look for common patterns
        words = query.split()
        for i, word in enumerate(words):
            if word.isdigit() and i < len(words) - 1:
                # Found a number followed by text
                # Basic address extraction
                address_parts = []
                for j in range(i, min(i + 5, len(words))):
                    if words[j].lower() in ['in', 'at', 'near', 'about']:
                        break
                    address_parts.append(words[j])
                if address_parts:
                    return " ".join(address_parts)
        return None
