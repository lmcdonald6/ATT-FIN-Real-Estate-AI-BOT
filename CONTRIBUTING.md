# Contributing to ATT-FIN Real Estate AI BOT

Thank you for your interest in contributing to the ATT-FIN Real Estate AI BOT! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Microservice Architecture](#microservice-architecture)

## Code of Conduct

This project adheres to a Code of Conduct that establishes expected behavior in our community. We expect all contributors to read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR-USERNAME/ATT-FIN-Real-Estate-AI-BOT.git
   cd ATT-FIN-Real-Estate-AI-BOT
   ```
3. **Set up the development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```
4. **Create a branch** for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. **Choose an issue** to work on from the GitHub issue tracker or create a new one
2. **Implement your changes** following our coding standards
3. **Write tests** for your changes
4. **Update documentation** as needed
5. **Run the test suite** to ensure all tests pass
   ```bash
   pytest
   ```
6. **Commit your changes** with a descriptive commit message
   ```bash
   git commit -m "Add feature: your feature description"
   ```
7. **Push your changes** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request** from your fork to the main repository

## Pull Request Process

1. Ensure your PR includes appropriate tests and documentation
2. Update the README.md or relevant documentation with details of changes if applicable
3. The PR should work for all supported Python versions
4. Your PR will be reviewed by at least one maintainer
5. Address any requested changes from the code review
6. Once approved, a maintainer will merge your PR

## Coding Standards

We follow PEP 8 style guidelines for Python code. Additionally:

- Use descriptive variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions focused on a single responsibility
- Use type hints where appropriate
- Format your code with `black` and check with `flake8`
  ```bash
  black .
  flake8 .
  ```

## Testing Guidelines

- Write unit tests for all new functionality
- Aim for high test coverage (>80%)
- Structure tests using pytest fixtures and parametrization where appropriate
- Include both positive and negative test cases
- For microservices, include integration tests that verify service boundaries

### Test Structure

```python
# Example test structure
def test_function_name_scenario_being_tested():
    # Arrange
    input_data = {...}
    expected_output = {...}
    
    # Act
    actual_output = function_being_tested(input_data)
    
    # Assert
    assert actual_output == expected_output
```

## Documentation Guidelines

- Keep README.md up to date with setup instructions and usage examples
- Document all public APIs with docstrings
- Include examples in docstrings for complex functions
- Update CHANGELOG.md for significant changes
- For microservices, include service-specific README files

## Microservice Architecture

This project follows a microservice architecture. When contributing to a specific microservice:

1. Respect service boundaries and responsibilities
2. Maintain independent deployability of each service
3. Follow the single responsibility principle
4. Update service-specific documentation
5. Include service-specific tests

### Microservice Structure

Each microservice should maintain its own:
- Configuration
- Dependencies (in a service-specific requirements.txt)
- Tests
- Documentation
- API contracts

## Questions?

If you have any questions or need help, please open an issue or reach out to the maintainers.

Thank you for contributing to ATT-FIN Real Estate AI BOT!
