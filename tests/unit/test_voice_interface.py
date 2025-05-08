"""Unit tests for voice interface."""
import pytest
from unittest.mock import Mock, patch
import speech_recognition as sr
from src.interface.voice_interface import VoiceInterface

@pytest.fixture
def voice_interface():
    """Create voice interface instance with mocked dependencies."""
    with patch('speech_recognition.Recognizer') as mock_recognizer, \
         patch('pyttsx3.init') as mock_tts, \
         patch('transformers.pipeline') as mock_nlp:
        
        # Configure speech recognition mock
        mock_recognizer.return_value.recognize_google.return_value = "test query"
        mock_recognizer.return_value.listen.return_value = "audio"
        
        # Configure TTS mock
        mock_engine = Mock()
        mock_tts.return_value = mock_engine
        
        # Configure NLP pipeline mock
        mock_nlp.return_value = lambda x: [{'label': 'property_analysis', 'score': 0.95}]
        
        interface = VoiceInterface({'testing': True})
        interface.engine = mock_engine
        return interface

@pytest.mark.asyncio
async def test_process_query_property_analysis(voice_interface):
    """Test processing property analysis query."""
    query = "analyze property at 123 Main St"
    response = await voice_interface.process_query(query)
    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_process_query_market_insights(voice_interface):
    """Test processing market insights query."""
    with patch.object(voice_interface, '_classify_intent') as mock_classify:
        mock_classify.return_value = {'intent': 'market_insights', 'confidence': 0.9}
        
        query = "how is the market in 12345"
        response = await voice_interface.process_query(query)
        assert isinstance(response, str)
        assert len(response) > 0

def test_listen_success(voice_interface):
    """Test successful voice input recognition."""
    text = voice_interface.listen()
    assert text == "test query"

def test_listen_unknown_value(voice_interface):
    """Test handling unknown voice input."""
    voice_interface.recognizer.recognize_google.side_effect = sr.UnknownValueError()
    text = voice_interface.listen()
    assert text is None

def test_speak(voice_interface):
    """Test text-to-speech output."""
    test_text = "Hello, this is a test"
    voice_interface.speak(test_text)
    voice_interface.engine.say.assert_called_once_with(test_text)
    voice_interface.engine.runAndWait.assert_called_once()

def test_context_update(voice_interface):
    """Test conversation context updates."""
    intent = {'intent': 'property_analysis', 'confidence': 0.9}
    entities = {
        'property': '123 Main St',
        'location': '12345'
    }
    
    voice_interface._update_context(intent, entities)
    assert voice_interface.context['current_property'] == '123 Main St'
    assert voice_interface.context['current_location'] == '12345'

def test_generate_follow_ups(voice_interface):
    """Test follow-up question generation."""
    voice_interface.context['last_analysis'] = {'some': 'data'}
    voice_interface.context['current_location'] = '12345'
    
    voice_interface._generate_follow_ups()
    
    assert len(voice_interface.context['follow_up_questions']) > 0
    assert any('neighborhood' in q.lower() for q in voice_interface.context['follow_up_questions'])

def test_format_property_analysis(voice_interface):
    """Test property analysis formatting."""
    analysis = {
        'summary': {
            'market_strength': 'strong',
            'neighborhood_quality': 'excellent',
            'growth_potential': 'high',
            'investment_recommendation': 'Consider investing now'
        }
    }
    
    response = voice_interface._format_property_analysis(analysis)
    assert 'strong' in response
    assert 'excellent' in response
    assert 'high' in response
    assert 'Consider investing now' in response

def test_format_market_insights(voice_interface):
    """Test market insights formatting."""
    insights = {
        'summary': {
            'market_strength': 'moderate',
            'growth_potential': 'high',
            'investment_recommendation': 'Good time to invest'
        }
    }
    
    response = voice_interface._format_market_insights(insights)
    assert 'moderate' in response
    assert 'high' in response
    assert 'Good time to invest' in response

def test_format_property_search(voice_interface):
    """Test property search results formatting."""
    properties = [{
        'property_type': 'Single Family Home',
        'price': '$300,000',
        'score': 0.85
    }]
    
    response = voice_interface._format_property_search(properties)
    assert 'Single Family Home' in response
    assert '$300,000' in response
    assert '85%' in response
