#!/bin/bash

# PACT Semantic Intent Matching - Setup Script
# This script sets up the environment and runs basic validation

set -e  # Exit on any error

echo "🚀 Setting up PACT Semantic Intent Matching..."
echo "================================================"

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not found"
    exit 1
}

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate || {
    echo "⚠️  Could not activate virtual environment, continuing without it..."
}

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"

# Run basic validation
echo "🧪 Running basic validation..."
python -c "
try:
    import sentence_transformers
    import numpy
    import scipy
    import pandas
    print('✅ All core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Run tests if pytest is available
echo "🧪 Running tests..."
if python -c "import pytest" 2>/dev/null; then
    python -m pytest test_matcher.py -v --tb=short || {
        echo "⚠️  Some tests failed, but setup continues..."
    }
else
    echo "⚠️  Pytest not available, skipping tests"
fi

# Run basic example
echo "🎯 Testing basic functionality..."
python -c "
import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute()))

try:
    from pact_semantic_matcher import PACTSemanticMatcher, PACTIntent
    
    # Quick test
    matcher = PACTSemanticMatcher()
    test_intent = PACTIntent(
        name='test',
        protocol_action='test.action',
        description='Test intent',
        examples=['hello test']
    )
    matcher.add_intent(test_intent)
    
    result = matcher.execute_pact_action('hello test')
    if result['status'] == 'success':
        print('✅ Basic functionality test passed!')
    else:
        print('⚠️  Basic functionality test did not match as expected')
        
except Exception as e:
    print(f'❌ Basic functionality test failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo "================================================"
echo ""
echo "📖 Next steps:"
echo "   1. Run basic example:     python example_usage.py"
echo "   2. Run advanced example:  python advanced_example.py"
echo "   3. Run tests:            pytest test_matcher.py -v"
echo "   4. Check the README.md for detailed documentation"
echo ""
echo "🚀 Happy matching with PACT!"
