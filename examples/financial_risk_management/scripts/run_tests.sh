#!/bin/bash
# scripts/run_tests.sh - Test execution script

set -e

echo "🧪 Running PACT Financial Risk Management test suite..."

# Activate virtual environment
source venv/bin/activate

# Start test infrastructure
echo "🐳 Starting test infrastructure..."
docker-compose -f docker-compose.test.yml up -d

# Wait for services
sleep 5

# Run linting
echo "🔍 Running code quality checks..."
echo "Running flake8..."
flake8 pact_risk/ tests/

echo "Running black..."
black --check pact_risk/ tests/

echo "Running mypy..."
mypy pact_risk/

# Run tests with coverage
echo "🏃 Running tests with coverage..."
pytest tests/ \
    --cov=pact_risk \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v

# Performance tests
echo "⚡ Running performance tests..."
pytest tests/performance/ -v

# Integration tests
echo "🔗 Running integration tests..."
pytest tests/integration/ -v

# Cleanup
echo "🧹 Cleaning up test infrastructure..."
docker-compose -f docker-compose.test.yml down

echo "✅ All tests passed!"
