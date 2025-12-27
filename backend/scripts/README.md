# Deployment Scripts

This directory contains scripts for deploying and managing the FunctionGemma integration.

## Quick Start

### Complete Deployment

Run the complete deployment process:

```bash
cd backend/scripts
python deploy.py
```

This will:
1. Install all dependencies
2. Download the FunctionGemma model
3. Run tests
4. Start the service

### Individual Scripts

#### 1. Install Dependencies

Install all required packages:

```bash
python install_dependencies.py
```

Options:
- `--upgrade`: Upgrade existing packages
- `--dev`: Install development dependencies (testing, linting)

#### 2. Download Model

Download the FunctionGemma-270M model:

```bash
python download_model.py
```

Options:
- `--model-path PATH`: Custom path to save model
- `--force`: Force re-download even if model exists

#### 3. Run Tests

Run the test suite:

```bash
python run_tests.py
```

Options:
- `--type TYPE`: Test type (all, unit, property, integration)
- `--coverage`: Generate coverage report
- `--verbose`: Verbose output
- `--fast`: Skip slow tests

#### 4. Start Service

Start the FunctionGemma service:

```bash
python start_service.py
```

Options:
- `--mode MODE`: Run mode (dev, prod)
- `--port PORT`: Port to listen on (default: 5000)
- `--host HOST`: Host to bind to (default: 127.0.0.1)
- `--no-model`: Start without loading model

## Deployment Scenarios

### Development Deployment

For local development with hot-reload:

```bash
python deploy.py
```

### Production Deployment

For production with optimizations:

```bash
python deploy.py --production
```

### Quick Deployment (Skip Tests)

When you need to deploy quickly:

```bash
python deploy.py --skip-tests
```

### Deployment with Existing Model

If model is already downloaded:

```bash
python deploy.py --skip-model
```

## Script Details

### deploy.py

Orchestrates the complete deployment process.

**Steps:**
1. Install dependencies
2. Download model (optional)
3. Run tests (optional)
4. Start service

**Usage:**
```bash
python deploy.py [--skip-tests] [--skip-model] [--production]
```

### install_dependencies.py

Installs all required Python packages.

**Features:**
- Checks Python version (3.8+ required)
- Installs core dependencies
- Optionally installs dev dependencies
- Verifies installation

**Usage:**
```bash
python install_dependencies.py [--upgrade] [--dev]
```

### download_model.py

Downloads the FunctionGemma-270M model from Hugging Face.

**Features:**
- Downloads model and processor
- Saves for offline use
- Checks if model already exists
- Provides progress feedback

**Usage:**
```bash
python download_model.py [--model-path PATH] [--force]
```

### run_tests.py

Runs the test suite with various options.

**Features:**
- Run all tests or specific types
- Generate coverage reports
- Verbose or quiet output
- Fast mode (skip slow tests)

**Usage:**
```bash
python run_tests.py [--type TYPE] [--coverage] [--verbose] [--fast]
```

### start_service.py

Starts the FunctionGemma service.

**Features:**
- Initializes function registry
- Loads model (optional)
- Starts Flask server
- Provides health check endpoint

**Usage:**
```bash
python start_service.py [--mode MODE] [--port PORT] [--host HOST] [--no-model]
```

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for initial setup)
- At least 4GB RAM (2GB for model)
- Windows operating system

## Troubleshooting

### Dependency Installation Fails

**Problem:** Package installation fails

**Solutions:**
1. Check internet connection
2. Update pip: `python -m pip install --upgrade pip`
3. Try with `--upgrade` flag
4. Check Python version (3.8+ required)

### Model Download Fails

**Problem:** Model download fails or times out

**Solutions:**
1. Check internet connection
2. Verify Hugging Face access
3. Check disk space (model is ~500MB)
4. Try again with `--force` flag
5. Download manually from Hugging Face

### Tests Fail

**Problem:** Tests fail during deployment

**Solutions:**
1. Run with `--verbose` for details
2. Run specific test type to isolate issue
3. Check test output for specific failures
4. Use `--skip-tests` to deploy anyway (not recommended)

### Service Won't Start

**Problem:** Service fails to start

**Solutions:**
1. Check if port is already in use
2. Verify model is downloaded
3. Check dependencies are installed
4. Try with `--no-model` to test without model
5. Check logs for specific error

### Memory Issues

**Problem:** Out of memory errors

**Solutions:**
1. Close other applications
2. Increase system RAM
3. Use model auto-unload feature
4. Monitor memory with service.get_memory_usage()

## Environment Variables

You can set these environment variables to customize behavior:

- `FUNCTIONGEMMA_MODEL_PATH`: Default model path
- `FUNCTIONGEMMA_PORT`: Default service port
- `FUNCTIONGEMMA_HOST`: Default service host
- `FUNCTIONGEMMA_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

Example:
```bash
export FUNCTIONGEMMA_MODEL_PATH="./my_models/functiongemma"
export FUNCTIONGEMMA_PORT=8000
python start_service.py
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
python scripts/install_dependencies.py --dev

# Run tests with coverage
python scripts/run_tests.py --coverage

# Deploy (skip model download in CI)
python scripts/deploy.py --skip-model --skip-tests
```

## Monitoring

The service provides a health check endpoint:

```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "functions_registered": 25
}
```

## Support

For issues or questions:

1. Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
2. Review script output for specific errors
3. Run with `--verbose` for more details
4. Check logs in backend directory

## Version

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Status:** Production Ready
