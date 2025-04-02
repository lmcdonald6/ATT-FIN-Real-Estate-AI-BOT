# Plugin Development Guide

This guide explains how to create custom plugins for the Real Estate AI System.

## Table of Contents
- [Overview](#overview)
- [Plugin Types](#plugin-types)
- [Creating a Plugin](#creating-a-plugin)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The plugin system allows you to extend the AI system's capabilities with custom:
- Data sources
- ML models
- Data processors
- Analysis tools

Each plugin is a self-contained module with its own:
- Metadata
- Configuration
- Dependencies
- Business logic

## Plugin Types

### 1. Data Source Plugin
For integrating external data sources:
```python
from src.core.plugin_system import DataSourcePlugin

class MyDataSource(DataSourcePlugin):
    async def fetch_data(self, query: Dict) -> Dict:
        # Implement data fetching logic
        pass

    def validate_data(self, data: Dict) -> bool:
        # Implement validation logic
        pass
```

### 2. Model Plugin
For implementing ML models:
```python
from src.core.plugin_system import ModelPlugin

class MyModel(ModelPlugin):
    async def predict(self, data: Dict) -> Dict:
        # Implement prediction logic
        pass

    def get_model_info(self) -> Dict:
        # Return model information
        pass
```

### 3. Processor Plugin
For custom data processing:
```python
from src.core.plugin_system import ProcessorPlugin

class MyProcessor(ProcessorPlugin):
    async def process_data(self, data: Dict) -> Dict:
        # Implement processing logic
        pass
```

## Creating a Plugin

1. Create plugin directory:
```bash
mkdir plugins/my_plugin
```

2. Create metadata file (`metadata.yaml`):
```yaml
name: my_plugin
version: "1.0.0"
description: "Plugin description"
author: "Your Name"
dependencies:
  - package>=version
capabilities:
  - capability1
  - capability2
config_schema:
  type: object
  properties:
    setting1:
      type: string
    setting2:
      type: integer
```

3. Create plugin implementation (`plugin.py`):
```python
from src.core.plugin_system import Plugin

class MyPlugin(Plugin):
    def initialize(self, config: Dict) -> bool:
        # Initialize plugin
        pass

    def get_capabilities(self) -> List[str]:
        # Return capabilities
        pass

    def process(self, data: Dict) -> Dict:
        # Process data
        pass
```

## Configuration

Plugins can be configured using JSON or YAML:

```json
{
    "setting1": "value1",
    "setting2": 42,
    "feature_flags": {
        "enable_feature": true
    }
}
```

Configuration is managed by the `ConfigManager`:
```python
from src.core.config_manager import ConfigManager

config_manager = ConfigManager()
config = config_manager.get_config('my_plugin')
```

## Best Practices

1. **Error Handling**
   - Always handle exceptions gracefully
   - Log errors with appropriate detail
   - Return sensible defaults on failure

```python
try:
    result = process_data(data)
except Exception as e:
    logger.error(f"Error processing data: {str(e)}")
    return default_value
```

2. **Validation**
   - Validate all input data
   - Check configuration values
   - Verify external API responses

3. **Performance**
   - Use caching when appropriate
   - Implement rate limiting for APIs
   - Process data in batches when possible

4. **Testing**
   - Write unit tests for your plugin
   - Test edge cases and error conditions
   - Mock external dependencies

## Examples

### Data Source Plugin
See [zillow_data_source](../plugins/zillow_data_source) for a complete example of:
- API integration
- Data validation
- Error handling
- Rate limiting
- Caching

### ML Model Plugin
See [property_valuation_model](../plugins/property_valuation_model) for a complete example of:
- Model creation
- Feature engineering
- Prediction logic
- Confidence scoring

### Processor Plugin
See [property_recommender](../plugins/property_recommender) for a complete example of:
- Data processing
- Recommendation generation
- Similarity scoring
- Investment analysis

## Support

For questions or issues:
1. Check the [FAQ](faq.md)
2. Open an issue on GitHub
3. Contact support@yourcompany.com
