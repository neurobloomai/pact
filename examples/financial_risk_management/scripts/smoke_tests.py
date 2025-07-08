#!/usr/bin/env python3
# scripts/smoke_tests.py - Smoke tests for deployment validation

import asyncio
import aiohttp
import json
import argparse
from typing import Dict, Any

class SmokeTests:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_endpoint(self) -> bool:
        """Test health check endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'healthy':
                        print("✅ Health check passed")
                        return True
                    else:
                        print(f"❌ Health check failed: {data}")
                        return False
                else:
                    print(f"❌ Health endpoint returned {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_metrics_endpoint(self) -> bool:
        """Test Prometheus metrics endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    content = await response.text()
                    if 'pact_' in content:
                        print("✅ Metrics endpoint working")
                        return True
                    else:
                        print("❌ Metrics endpoint missing PACT metrics")
                        return False
                else:
                    print(f"❌ Metrics endpoint returned {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Metrics endpoint error: {e}")
            return False
    
    async def test_api_docs(self) -> bool:
        """Test API documentation endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/docs") as response:
                if response.status in [200, 404]:  # 404 is OK in production
                    print("✅ API docs endpoint accessible")
                    return True
                else:
                    print(f"❌ API docs returned {response.status}")
                    return False
        except Exception as e:
            print(f"❌ API docs error: {e}")
            return False
    
    async def test_risk_assessment_api(self) -> bool:
        """Test risk assessment API with sample data"""
        try:
            # Sample portfolio data
            test_portfolio = {
                "portfolio_data": {
                    "total_value": 10000000,
                    "positions": [
                        {
                            "id": "test_pos_1",
                            "name": "Test Position 1",
                            "type": "equity",
                            "market_value": 5000000,
                            "sensitivities": {
                                "equity_us": 1.0,
                                "interest_rate_usd": -0.1
                            }
                        },
                        {
                            "id": "test_pos_2", 
                            "name": "Test Position 2",
                            "type": "bond",
                            "market_value": 5000000,
                            "sensitivities": {
                                "interest_rate_usd": -0.5,
                                "credit_spread": 0.3
                            }
                        }
                    ],
                    "risk_factors": [
                        {"name": "equity_us", "volatility": 0.16},
                        {"name": "interest_rate_usd", "volatility": 0.02},
                        {"name": "credit_spread", "volatility": 0.15}
                    ]
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/risk/assess",
                json=test_portfolio,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'risk_score' in data:
                        print("✅ Risk assessment API working")
                        return True
                    else:
                        print(f"❌ Risk assessment API invalid response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Risk assessment API returned {response.status}: {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Risk assessment API error: {e}")
            return False
    
    async def test_agent_status(self) -> bool:
        """Test agent status endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/monitoring/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        active_agents = [agent for agent in data if agent.get('status') == 'active']
                        if len(active_agents) >= 3:  # Expect at least 3 agents
                            print(f"✅ {len(active_agents)} agents active")
                            return True
                        else:
                            print(f"❌ Only {len(active_agents)} agents active, expected >= 3")
                            return False
                    else:
                        print("❌ No agents found")
                        return False
                else:
                    print(f"❌ Agent status endpoint returned {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Agent status error: {e}")
            return False

async def run_smoke_tests(environment: str):
    """Run all smoke tests"""
    
    # Determine base URL based on environment
    if environment == "production":
        base_url = "https://api.pact-risk.neurobloom.ai"
    elif environment == "staging":
        base_url = "https://staging-api.pact-risk.neurobloom.ai"
    else:
        base_url = "http://localhost:8000"
    
    print(f"🧪 Running smoke tests against {base_url}")
    
    async with SmokeTests(base_url) as tests:
        test_results = []
        
        # Run all tests
        test_results.append(await tests.test_health_endpoint())
        test_results.append(await tests.test_metrics_endpoint())
        test_results.append(await tests.test_api_docs())
        test_results.append(await tests.test_risk_assessment_api())
        test_results.append(await tests.test_agent_status())
        
        # Summary
        passed = sum(test_results)
        total = len(test_results)
        
        print(f"\n📊 Smoke test results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All smoke tests passed!")
            return True
        else:
            print("❌ Some smoke tests failed!")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run smoke tests")
    parser.add_argument("--environment", choices=["development", "staging", "production"], 
                       default="development", help="Target environment")
    
    args = parser.parse_args()
    
    success = asyncio.run(run_smoke_tests(args.environment))
    exit(0 if success else 1)
