#!/usr/bin/env python3
"""
Test script for the Professional Korean Stock Backtesting Engine
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_golden_cross_strategy():
    """Test Golden Cross strategy"""
    try:
        from backtesting_engine import run_professional_backtest
        
        logger.info("Testing Golden Cross Strategy...")
        
        config = {
            'symbol': '005930',  # Samsung Electronics
            'strategy_id': 'golden_cross',
            'start_date': '2023-01-01',
            'end_date': '2024-01-01',
            'initial_capital': 10000000,  # 10M KRW
            'strategy_parameters': {
                'short_period': 5,
                'long_period': 20,
                'stop_loss': 0.05
            }
        }
        
        results = await run_professional_backtest(config)
        
        logger.info("Golden Cross Results:")
        logger.info(f"Total Return: {results['total_return']:.2%}")
        logger.info(f"Win Rate: {results['win_rate']:.2%}")
        logger.info(f"Total Trades: {results['total_trades']}")
        logger.info(f"Max Drawdown: {results['max_drawdown']:.2%}")
        logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"Final Capital: ₩{results['final_capital']:,}")
        
        return results
        
    except Exception as e:
        logger.error(f"Golden Cross test failed: {e}")
        return None

async def test_rsi_reversal_strategy():
    """Test RSI Reversal strategy"""
    try:
        from backtesting_engine import run_professional_backtest
        
        logger.info("Testing RSI Reversal Strategy...")
        
        config = {
            'symbol': '000660',  # SK Hynix
            'strategy_id': 'rsi_reversal',
            'start_date': '2023-01-01',
            'end_date': '2024-01-01',
            'initial_capital': 10000000,
            'strategy_parameters': {
                'rsi_period': 14,
                'oversold_level': 30,
                'overbought_level': 70
            }
        }
        
        results = await run_professional_backtest(config)
        
        logger.info("RSI Reversal Results:")
        logger.info(f"Total Return: {results['total_return']:.2%}")
        logger.info(f"Win Rate: {results['win_rate']:.2%}")
        logger.info(f"Total Trades: {results['total_trades']}")
        logger.info(f"Max Drawdown: {results['max_drawdown']:.2%}")
        logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"Final Capital: ₩{results['final_capital']:,}")
        
        return results
        
    except Exception as e:
        logger.error(f"RSI Reversal test failed: {e}")
        return None

async def test_bollinger_breakout_strategy():
    """Test Bollinger Band Breakout strategy"""
    try:
        from backtesting_engine import run_professional_backtest
        
        logger.info("Testing Bollinger Band Breakout Strategy...")
        
        config = {
            'symbol': '035420',  # NAVER
            'strategy_id': 'bollinger_squeeze',
            'start_date': '2023-01-01',
            'end_date': '2024-01-01', 
            'initial_capital': 10000000,
            'strategy_parameters': {
                'bb_period': 20,
                'bb_std': 2.0,
                'volume_confirm': True
            }
        }
        
        results = await run_professional_backtest(config)
        
        logger.info("Bollinger Breakout Results:")
        logger.info(f"Total Return: {results['total_return']:.2%}")
        logger.info(f"Win Rate: {results['win_rate']:.2%}")
        logger.info(f"Total Trades: {results['total_trades']}")
        logger.info(f"Max Drawdown: {results['max_drawdown']:.2%}")
        logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"Final Capital: ₩{results['final_capital']:,}")
        
        return results
        
    except Exception as e:
        logger.error(f"Bollinger Breakout test failed: {e}")
        return None

async def test_api_integration():
    """Test API integration with backtesting engine"""
    try:
        import requests
        import time
        
        logger.info("Testing API Integration...")
        
        # Start the API server in the background (if not already running)
        api_url = "http://localhost:8001/api/v1/backtest/run"
        
        test_request = {
            "symbol": "005930",
            "strategy": "golden_cross",
            "start_date": "2023-06-01",
            "end_date": "2023-12-31",
            "initial_capital": 5000000,
            "short_period": 5,
            "long_period": 20,
            "stop_loss": 0.05
        }
        
        # Make API request
        response = requests.post(api_url, json=test_request, timeout=30)
        
        if response.status_code == 200:
            results = response.json()
            logger.info("API Integration Results:")
            logger.info(f"Total Return: {results.get('total_return', 0):.2%}")
            logger.info(f"Win Rate: {results.get('win_rate', 0):.2%}")
            logger.info(f"Total Trades: {results.get('total_trades', 0)}")
            
            return results
        else:
            logger.error(f"API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"API integration test failed: {e}")
        logger.info("Make sure the API server is running: python api_server.py")
        return None

async def run_comprehensive_test():
    """Run comprehensive backtesting engine tests"""
    logger.info("=" * 60)
    logger.info("Korean Stock Backtesting Engine - Comprehensive Test")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test 1: Golden Cross Strategy
    logger.info("\n" + "=" * 40)
    logger.info("TEST 1: Golden Cross Strategy")
    logger.info("=" * 40)
    test_results['golden_cross'] = await test_golden_cross_strategy()
    
    # Test 2: RSI Reversal Strategy
    logger.info("\n" + "=" * 40)
    logger.info("TEST 2: RSI Reversal Strategy") 
    logger.info("=" * 40)
    test_results['rsi_reversal'] = await test_rsi_reversal_strategy()
    
    # Test 3: Bollinger Band Breakout Strategy
    logger.info("\n" + "=" * 40)
    logger.info("TEST 3: Bollinger Band Breakout Strategy")
    logger.info("=" * 40)
    test_results['bollinger_breakout'] = await test_bollinger_breakout_strategy()
    
    # Test 4: API Integration (optional)
    logger.info("\n" + "=" * 40)
    logger.info("TEST 4: API Integration")
    logger.info("=" * 40)
    test_results['api_integration'] = await test_api_integration()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed_tests = 0
    total_tests = 0
    
    for test_name, result in test_results.items():
        total_tests += 1
        if result:
            passed_tests += 1
            logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
        else:
            logger.info(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
    
    logger.info(f"\nTests Passed: {passed_tests}/{total_tests}")
    logger.info(f"Success Rate: {passed_tests/total_tests:.1%}")
    
    if passed_tests >= 3:  # At least 3 out of 4 tests should pass
        logger.info("\n🎉 Professional Backtesting Engine is ready for production!")
    else:
        logger.warning("\n⚠️  Some tests failed. Please check the implementation.")
    
    return test_results

def save_test_results(results):
    """Save test results to JSON file"""
    try:
        filename = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert any non-serializable objects
        serializable_results = {}
        for key, value in results.items():
            if value and isinstance(value, dict):
                serializable_results[key] = {
                    k: str(v) if hasattr(v, '__str__') else v 
                    for k, v in value.items()
                }
            else:
                serializable_results[key] = value
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test results saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to save test results: {e}")

if __name__ == "__main__":
    # Run the comprehensive test
    try:
        results = asyncio.run(run_comprehensive_test())
        save_test_results(results)
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
    
    logger.info("\nTest execution completed!")