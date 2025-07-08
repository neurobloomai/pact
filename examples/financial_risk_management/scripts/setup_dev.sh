#!/bin/bash
# scripts/setup_dev.sh - Development environment setup

set -e

echo "🚀 Setting up PACT Financial Risk Management development environment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.11+ is required"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required"; exit 1; }

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Start infrastructure services
echo "🐳 Starting infrastructure with Docker Compose..."
docker-compose up -d postgres redis prometheus grafana

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Create test data
echo "🧪 Creating test data..."
python scripts/create_test_data.py

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python -m uvicorn pact_risk.main:app --reload"
echo "   4. Visit: http://localhost:8000/docs"
echo ""
echo "📊 Monitoring URLs:"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
