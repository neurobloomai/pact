#!/usr/bin/env python3
# scripts/create_test_data.py - Create test data for development

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List

import asyncpg
import aioredis
from faker import Faker

fake = Faker()

async def create_test_portfolios():
    """Create test portfolio data"""
    portfolios = []
    
    for i in range(10):
        # Generate random positions
        positions = []
        for j in range(random.randint(50, 200)):
            position = {
                'id': f'pos_{i}_{j}',
                'name': fake.company(),
                'type': random.choice(['equity', 'bond', 'derivative', 'commodity']),
                'market_value': random.uniform(100000, 5000000),
                'quantity': random.randint(100, 10000),
                'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
                'sector': random.choice(['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer']),
                'country': random.choice(['US', 'UK', 'DE', 'JP', 'FR']),
                'sensitivities': {
                    'equity_us': random.uniform(-0.5, 1.5),
                    'equity_eu': random.uniform(-0.3, 1.2),
                    'interest_rate_usd': random.uniform(-0.2, 0.2),
                    'credit_spread': random.uniform(-0.1, 0.3),
                    'usd_eur': random.uniform(-0.4, 0.4),
                }
            }
            
            # Add derivative-specific fields
            if position['type'] == 'derivative':
                position.update({
                    'option_type': random.choice(['call', 'put']),
                    'underlying_price': random.uniform(50, 200),
                    'strike_price': random.uniform(50, 200),
                    'time_to_expiry': random.uniform(0.1, 2.0),
                    'volatility': random.uniform(0.1, 0.5),
                    'risk_free_rate': 0.05
                })
            
            positions.append(position)
        
        # Generate risk factors
        risk_factors = [
            {'name': 'equity_us', 'volatility': 0.16, 'current_value': 4500},
            {'name': 'equity_eu', 'volatility': 0.18, 'current_value': 3800},
            {'name': 'equity_asia', 'volatility': 0.20, 'current_value': 2900},
            {'name': 'bonds_us', 'volatility': 0.05, 'current_value': 102.5},
            {'name': 'bonds_eu', 'volatility': 0.04, 'current_value': 101.8},
            {'name': 'credit_spread', 'volatility': 0.15, 'current_value': 0.025},
            {'name': 'usd_eur', 'volatility': 0.12, 'current_value': 1.08},
            {'name': 'usd_jpy', 'volatility': 0.14, 'current_value': 150.0},
            {'name': 'oil_price', 'volatility': 0.30, 'current_value': 80.0},
            {'name': 'gold_price', 'volatility': 0.18, 'current_value': 2000.0}
        ]
        
        portfolio = {
            'id': f'portfolio_{i}',
            'name': f'Test Portfolio {i+1}',
            'description': f'Test portfolio for {fake.company()}',
            'total_value': sum(pos['market_value'] for pos in positions),
            'currency': 'USD',
            'positions': positions,
            'risk_factors': risk_factors,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        portfolios.append(portfolio)
    
    return portfolios

async def create_test_market_data():
    """Create test market data"""
    market_data = {
        'equity_indices': {
            'SPX': {'price': 4500, 'change': 0.012, 'volatility': 0.16},
            'STOXX': {'price': 3800, 'change': -0.008, 'volatility': 0.18},
            'NIKKEI': {'price': 32000, 'change': 0.005, 'volatility': 0.20}
        },
        'fx_rates': {
            'USDEUR': {'rate': 1.08, 'change': -0.002, 'volatility': 0.12},
            'USDJPY': {'rate': 150.0, 'change': 0.001, 'volatility': 0.14},
            'GBPUSD': {'rate': 1.25, 'change': 0.003, 'volatility': 0.13}
        },
        'commodities': {
            'CRUDE_OIL': {'price': 80.0, 'change': 0.025, 'volatility': 0.30},
            'GOLD': {'price': 2000.0, 'change': -0.005, 'volatility': 0.18},
            'SILVER': {'price': 25.0, 'change': 0.015, 'volatility': 0.25}
        },
        'interest_rates': {
            'USD_3M': {'rate': 0.052, 'change': 0.0002},
            'EUR_3M': {'rate': 0.038, 'change': 0.0001},
            'GBP_3M': {'rate': 0.048, 'change': 0.0003}
        },
        'credit_spreads': {
            'IG_CORPORATE': {'spread': 0.025, 'change': 0.0001},
            'HY_CORPORATE': {'spread': 0.045, 'change': 0.0005},
            'SOVEREIGN': {'spread': 0.015, 'change': 0.0000}
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return market_data

async def store_test_data():
    """Store test data in database and Redis"""
    try:
        # Create test portfolios
        portfolios = await create_test_portfolios()
        market_data = await create_test_market_data()
        
        # Connect to PostgreSQL
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/pact_risk')
        
        try:
            # Create portfolios table if not exists
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Insert test portfolios
            for portfolio in portfolios:
                await conn.execute('''
                    INSERT INTO portfolios (id, name, description, data)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (id) DO UPDATE SET
                        data = $4,
                        updated_at = NOW()
                ''', portfolio['id'], portfolio['name'], portfolio['description'], json.dumps(portfolio))
            
            print(f"✅ Created {len(portfolios)} test portfolios in database")
            
        finally:
            await conn.close()
        
        # Connect to Redis and store market data
        redis = aioredis.from_url('redis://localhost:6379/0')
        
        try:
            await redis.set('market_data:latest', json.dumps(market_data))
            await redis.expire('market_data:latest', 300)  # 5 minute expiry
            
            print("✅ Stored market data in Redis")
            
        finally:
            await redis.close()
        
        print("🎉 Test data creation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(store_test_data())
