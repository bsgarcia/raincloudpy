# Contributing to raincloudpy

Thank you for your interest in contributing to raincloudpy! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/bsgarcia/raincloudpy.git
   cd raincloudpy
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure tests pass:
   ```bash
   pytest
   ```

3. Format your code:
   ```bash
   black raincloudpy tests
   flake8 raincloudpy tests
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. Push to your fork and submit a pull request

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 88)
- Add type hints where appropriate
- Write docstrings for all public functions and classes

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

Run tests with:
```bash
pytest --cov=raincloudpy
```

## Documentation

- Update README.md if adding new features
- Add docstrings following NumPy style
- Include examples for new functionality

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the version number following Semantic Versioning
3. The PR will be merged once you have the sign-off of a maintainer

## Reporting Bugs

Use GitHub Issues to report bugs. Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and dependencies

## Feature Requests

Feature requests are welcome! Please provide:
- Clear description of the feature
- Use case and motivation
- Example of how it would work

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

Thank you for contributing! 🎉
