# Real Estate AI System

A robust real estate AI system that leverages multiple AI providers (OpenAI, Anthropic, Google) for intelligent property analysis and recommendations.

## Features

- Multi-provider AI system with fallback support
- Secure API key management using keyring
- Standardized responses across different AI providers
- Comprehensive error handling and logging
- Environment variable management with .env support

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys:
```bash
python scripts/setup_env.py
```

3. Run the demo:
```bash
python examples/ai_provider_demo.py
```

## Project Structure

```
src/
├── ai/
│   ├── agent.py           # Main AI agent implementation
│   └── model_provider.py  # AI model providers and factory
├── config/
│   └── env_manager.py     # Environment and API key management
└── mock/
    └── data_generator.py  # Mock data generation for testing

tests/
├── test_env.py           # Environment manager tests
└── test_providers.py     # AI provider tests

examples/
└── ai_provider_demo.py   # Demo script
```

## Environment Variables

Required API keys (at least one):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

## Security

API keys are stored securely using the keyring library, which integrates with your system's secure credential storage.

## Testing

Run tests:
```bash
python -m unittest discover tests
```

## Error Handling

The system includes comprehensive error handling:
- Validates API key formats
- Provides fallback mechanisms
- Logs errors for debugging
- Returns standardized error responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request