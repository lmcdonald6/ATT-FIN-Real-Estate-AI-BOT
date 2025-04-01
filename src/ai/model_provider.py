from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import os
import openai
from anthropic import Anthropic
import google.generativeai as genai
from ..config.env_manager import EnvManager
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

logger = logging.getLogger(__name__)

class ModelResponse:
    """Standardized response format across providers"""
    def __init__(self, 
                 content: str,
                 model: str,
                 provider: str,
                 usage: Optional[Dict[str, int]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.model = model
        self.provider = provider
        self.usage = usage or {}
        self.metadata = metadata or {}
        self.timestamp = time.time()

class ModelProvider(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.env_manager = EnvManager()
        self.api_key = api_key or self.env_manager.get_api_key(self._get_provider_name())
        if not self.api_key:
            raise ValueError(f"{self._get_provider_name()} API key not found")
            
    @abstractmethod
    def _get_provider_name(self) -> str:
        pass
        
    @abstractmethod
    def analyze_intent(self, message: str) -> ModelResponse:
        pass
        
    @abstractmethod
    def generate_response(self, message: str, context: Dict) -> ModelResponse:
        pass
        
    def _handle_error(self, e: Exception, fallback_message: str) -> ModelResponse:
        logger.error(f"Error in {self._get_provider_name()}: {str(e)}")
        return ModelResponse(
            content=fallback_message,
            model=f"{self._get_provider_name()}_error",
            provider=self._get_provider_name(),
            metadata={'error': str(e)}
        )

class OpenAIProvider(ModelProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        openai.api_key = self.api_key
        self.models = {
            'chat': 'gpt-4',
            'analysis': 'gpt-4-1106-preview',
            'embedding': 'text-embedding-3-small'
        }
        
    def _get_provider_name(self) -> str:
        return 'openai'
        
    def analyze_intent(self, message: str) -> ModelResponse:
        try:
            response = openai.ChatCompletion.create(
                model=self.models['chat'],
                messages=[
                    {"role": "system", "content": "You are a real estate AI assistant. Classify the user's intent."},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=50
            )
            return ModelResponse(
                content=response.choices[0].message.content,
                model=self.models['chat'],
                provider=self._get_provider_name(),
                usage=response.usage
            )
        except Exception as e:
            return self._handle_error(e, "general_query")
            
    def generate_response(self, message: str, context: Dict) -> ModelResponse:
        try:
            conversation = [
                {"role": "system", "content": "You are a real estate AI assistant. Provide helpful and actionable advice."},
                {"role": "user", "content": message}
            ]
            
            if context:
                conversation.append({
                    "role": "system",
                    "content": f"Context: {str(context)}"
                })
                
            response = openai.ChatCompletion.create(
                model=self.models['chat'],
                messages=conversation,
                temperature=0.7,
                max_tokens=200
            )
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model=self.models['chat'],
                provider=self._get_provider_name(),
                usage=response.usage
            )
        except Exception as e:
            return self._handle_error(e, "I apologize, but I encountered an error. Please try again.")
            
    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding for semantic search"""
        try:
            response = openai.Embedding.create(
                model=self.models['embedding'],
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return []

class AnthropicProvider(ModelProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client = Anthropic(api_key=self.api_key)
        self.models = {
            'chat': 'claude-3-opus-20240229',
            'analysis': 'claude-3-opus-20240229'
        }
        
    def _get_provider_name(self) -> str:
        return 'anthropic'
        
    def analyze_intent(self, message: str) -> ModelResponse:
        try:
            response = self.client.messages.create(
                model=self.models['chat'],
                max_tokens=50,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": f"Classify the intent of this message: {message}"
                }]
            )
            return ModelResponse(
                content=response.content[0].text,
                model=self.models['chat'],
                provider=self._get_provider_name()
            )
        except Exception as e:
            return self._handle_error(e, "general_query")
            
    def generate_response(self, message: str, context: Dict) -> ModelResponse:
        try:
            system_prompt = "You are a real estate AI assistant. Provide helpful and actionable advice."
            if context:
                system_prompt += f"\nContext: {str(context)}"
                
            response = self.client.messages.create(
                model=self.models['chat'],
                max_tokens=200,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": f"{system_prompt}\n\nUser message: {message}"
                }]
            )
            
            return ModelResponse(
                content=response.content[0].text,
                model=self.models['chat'],
                provider=self._get_provider_name()
            )
        except Exception as e:
            return self._handle_error(e, "I apologize, but I encountered an error. Please try again.")

class GeminiProvider(ModelProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def _get_provider_name(self) -> str:
        return 'google'
        
    def analyze_intent(self, message: str) -> ModelResponse:
        try:
            response = self.model.generate_content(
                f"Classify the intent of this message: {message}",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=50
                )
            )
            return ModelResponse(
                content=response.text,
                model='gemini-pro',
                provider=self._get_provider_name()
            )
        except Exception as e:
            return self._handle_error(e, "general_query")
            
    def generate_response(self, message: str, context: Dict) -> ModelResponse:
        try:
            prompt = "You are a real estate AI assistant. Provide helpful and actionable advice.\n\n"
            if context:
                prompt += f"Context: {str(context)}\n\n"
            prompt += f"User message: {message}"
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200
                )
            )
            
            return ModelResponse(
                content=response.text,
                model='gemini-pro',
                provider=self._get_provider_name()
            )
        except Exception as e:
            return self._handle_error(e, "I apologize, but I encountered an error. Please try again.")

class FallbackProvider:
    """Provider that attempts multiple providers in sequence"""
    
    def __init__(self, providers: Optional[List[str]] = None):
        self.env_manager = EnvManager()
        self.providers = providers or ['openai', 'anthropic', 'google']
        self._initialize_providers()
        
    def _initialize_providers(self) -> None:
        """Initialize available providers"""
        self.active_providers = []
        provider_classes = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'google': GeminiProvider
        }
        
        for provider_name in self.providers:
            try:
                if self.env_manager.get_api_key(provider_name):
                    provider = provider_classes[provider_name]()
                    self.active_providers.append(provider)
            except Exception as e:
                logger.warning(f"Failed to initialize {provider_name}: {str(e)}")
                
    def _try_providers(self, method: str, *args, **kwargs) -> ModelResponse:
        """Try each provider in sequence until one succeeds"""
        last_error = None
        for provider in self.active_providers:
            try:
                return getattr(provider, method)(*args, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider._get_provider_name()} failed: {str(e)}")
                continue
                
        # If all providers failed, return error response
        return ModelResponse(
            content="All providers failed. Please try again later.",
            model="fallback_error",
            provider="fallback",
            metadata={'error': str(last_error)}
        )
        
    def analyze_intent(self, message: str) -> ModelResponse:
        return self._try_providers('analyze_intent', message)
        
    def generate_response(self, message: str, context: Dict) -> ModelResponse:
        return self._try_providers('generate_response', message, context)

class ModelProviderFactory:
    PROVIDERS = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'google': GeminiProvider,
        'fallback': FallbackProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: Optional[str] = None) -> ModelProvider:
        """Create a model provider instance"""
        if not provider_name:
            raise ValueError("Provider name is required")
            
        provider_name = provider_name.lower()
        if provider_name not in cls.PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider_name}")
            
        provider_class = cls.PROVIDERS[provider_name]
        
        if api_key:
            # Validate API key format
            if provider_name == 'openai' and not api_key.startswith('sk-'):
                raise ValueError("Invalid OpenAI API key format")
            elif provider_name == 'anthropic' and not api_key.startswith('sk-ant-'):
                raise ValueError("Invalid Anthropic API key format")
            elif provider_name == 'google' and len(api_key) < 20:
                raise ValueError("Invalid Google API key format")
                
        return provider_class(api_key)
        
    @classmethod
    def get_available_providers(cls) -> List[str]:
        return ['openai', 'anthropic', 'google', 'fallback']
