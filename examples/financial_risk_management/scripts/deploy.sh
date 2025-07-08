#!/bin/bash
# scripts/deploy.sh - Production deployment script

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Deploying PACT Financial Risk Management to $ENVIRONMENT..."

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "❌ Environment must be 'staging' or 'production'"
    exit 1
fi

# Test API endpoint
API_URL="https://api.pact-risk-$ENVIRONMENT.neurobloom.ai"
if [ "$ENVIRONMENT" = "staging" ]; then
    API_URL="https://staging-api.pact-risk.neurobloom.ai"
fi

echo "🌐 Testing API endpoint: $API_URL"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed (HTTP $HTTP_STATUS)"
    exit 1
fi

# Run smoke tests
echo "💨 Running smoke tests..."
python scripts/smoke_tests.py --environment=$ENVIRONMENT

echo "🎉 Deployment to $ENVIRONMENT completed successfully!"
echo "📊 Monitor at: https://grafana.neurobloom.ai"
