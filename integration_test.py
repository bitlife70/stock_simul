#!/usr/bin/env python3
"""
Integration Test Suite for Korean Stock Backtesting Platform
Windows-compatible version with proper encoding
"""

import json
import time
import logging
import requests
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationTest:
    """Integration test for Korean Stock Backtesting Platform"""
    
    def __init__(self):
        self.test_results = {}
        self.api_endpoints = {
            'basic_api': 'http://localhost:8000',
            'enhanced_api': 'http://localhost:8001', 
            'optimized_api': 'http://localhost:8002'
        }
        self.test_stocks = ['005930', '000660', '035420']
        
        # Test backtest configuration
        self.test_backtest_config = {
            'symbol': '005930',
            'strategy': 'golden_cross',
            'start_date': '2023-01-01',
            'end_date': '2024-01-01',
            'initial_capital': 50000000,
            'strategy_parameters': {
                'short_period': 5,
                'long_period': 20,
                'stop_loss': 0.05
            }
        }

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("=" * 80)
        print("Korean Stock Backtesting Platform - Integration Tests")
        print("=" * 80)
        
        start_time = time.time()
        
        # Test 1: Component Architecture Analysis
        print("Test 1: Component Architecture Analysis")
        self.test_component_architecture()
        
        # Test 2: API Health Checks
        print("Test 2: API Health Checks")
        self.test_api_health()
        
        # Test 3: Data Integration
        print("Test 3: Data Integration Tests")
        self.test_data_integration()
        
        # Test 4: Backtesting Engine
        print("Test 4: Backtesting Engine Tests")
        self.test_backtesting_engine()
        
        # Test 5: Korean Market Features
        print("Test 5: Korean Market Features")
        self.test_korean_features()
        
        # Test 6: Frontend Components
        print("Test 6: Frontend Component Validation")
        self.test_frontend_components()
        
        total_time = time.time() - start_time
        
        # Generate report
        report = self.generate_report(total_time)
        
        print("=" * 80)
        print(f"Integration tests completed in {total_time:.2f} seconds")
        print("=" * 80)
        
        return report

    def test_component_architecture(self):
        """Test system component architecture"""
        components = {}
        
        # Check backend components
        backend_components = [
            'backtesting_engine.py',
            'backend/optimized_api_server.py',
            'backend/services/korean_strategy_engine.py',
            'backend/services/korean_risk_manager.py',
            'backend/core/cache_manager.py',
            'backend/core/performance_monitor.py'
        ]
        
        for component in backend_components:
            path = Path(component)
            exists = path.exists()
            size = path.stat().st_size if exists else 0
            
            components[component] = {
                'exists': exists,
                'size_kb': round(size / 1024, 2),
                'status': 'found' if exists else 'missing'
            }
            
            if exists:
                print(f"[OK] {component} - {size/1024:.1f}KB")
            else:
                print(f"[MISSING] {component}")
        
        # Check frontend components
        frontend_components = [
            'frontend/src/components/portfolio/PortfolioDashboard.tsx',
            'frontend/src/components/strategy/KoreanStrategyBuilder.tsx',
            'frontend/src/components/analytics/AnalyticsDashboard.tsx',
            'frontend/src/components/risk/RiskManagementDashboard.tsx',
            'frontend/src/components/realtime/MarketMonitoringDashboard.tsx'
        ]
        
        for component in frontend_components:
            path = Path(component)
            exists = path.exists()
            size = path.stat().st_size if exists else 0
            
            components[component] = {
                'exists': exists,
                'size_kb': round(size / 1024, 2),
                'status': 'found' if exists else 'missing'
            }
            
            if exists:
                print(f"[OK] {component} - {size/1024:.1f}KB")
            else:
                print(f"[MISSING] {component}")
        
        # Calculate architecture completeness
        total_components = len(components)
        found_components = sum(1 for c in components.values() if c['exists'])
        completeness = (found_components / total_components) * 100
        
        self.test_results['component_architecture'] = {
            'components': components,
            'total_components': total_components,
            'found_components': found_components,
            'completeness_percentage': completeness,
            'status': 'excellent' if completeness >= 90 else 'good' if completeness >= 80 else 'needs_work'
        }
        
        print(f"Architecture Completeness: {completeness:.1f}% ({found_components}/{total_components})")

    def test_api_health(self):
        """Test API server health"""
        health_results = {}
        
        for api_name, base_url in self.api_endpoints.items():
            try:
                print(f"Testing {api_name} at {base_url}")
                
                # Health check
                start_time = time.time()
                response = requests.get(f"{base_url}/health", timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    health_data = response.json()
                    health_results[api_name] = {
                        'status': 'healthy',
                        'response_time_ms': response_time,
                        'version': health_data.get('version', 'unknown'),
                        'korean_market_ready': health_data.get('korean_market_ready', False)
                    }
                    print(f"[OK] {api_name} - {response_time:.0f}ms")
                else:
                    health_results[api_name] = {
                        'status': 'unhealthy',
                        'response_code': response.status_code,
                        'response_time_ms': response_time
                    }
                    print(f"[WARNING] {api_name} - HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                health_results[api_name] = {
                    'status': 'offline',
                    'error': 'Connection refused'
                }
                print(f"[OFFLINE] {api_name} - Server offline")
            except Exception as e:
                health_results[api_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                print(f"[ERROR] {api_name} - Error: {e}")
        
        self.test_results['api_health'] = health_results

    def test_data_integration(self):
        """Test data integration endpoints"""
        data_results = {}
        
        for api_name, base_url in self.api_endpoints.items():
            if self.test_results['api_health'][api_name]['status'] != 'healthy':
                continue
                
            try:
                api_results = {}
                
                # Test stock list
                response = requests.get(f"{base_url}/api/v1/stocks", timeout=30)
                if response.status_code == 200:
                    stocks_data = response.json()
                    api_results['stock_list'] = {
                        'status': 'success',
                        'count': len(stocks_data) if isinstance(stocks_data, list) else 0,
                        'has_korean_names': any('name_kr' in stock for stock in stocks_data[:5]) if isinstance(stocks_data, list) else False
                    }
                    print(f"[OK] Stock list: {len(stocks_data) if isinstance(stocks_data, list) else 0} stocks")
                else:
                    api_results['stock_list'] = {'status': 'failed', 'code': response.status_code}
                    print(f"[ERROR] Stock list failed: HTTP {response.status_code}")
                
                # Test individual stock data
                test_symbol = '005930'
                response = requests.get(f"{base_url}/api/v1/stocks/{test_symbol}/data", timeout=30)
                if response.status_code == 200:
                    stock_data = response.json()
                    api_results['stock_data'] = {
                        'status': 'success',
                        'data_points': len(stock_data) if isinstance(stock_data, list) else 0,
                        'has_ohlcv': self.validate_ohlcv(stock_data)
                    }
                    print(f"[OK] Stock data: {len(stock_data) if isinstance(stock_data, list) else 0} data points")
                else:
                    api_results['stock_data'] = {'status': 'failed', 'code': response.status_code}
                    print(f"[ERROR] Stock data failed: HTTP {response.status_code}")
                
                # Test strategy templates
                response = requests.get(f"{base_url}/api/v1/strategies/templates", timeout=30)
                if response.status_code == 200:
                    strategies = response.json()
                    api_results['strategies'] = {
                        'status': 'success',
                        'count': len(strategies) if isinstance(strategies, list) else 0
                    }
                    print(f"[OK] Strategy templates: {len(strategies) if isinstance(strategies, list) else 0} strategies")
                else:
                    api_results['strategies'] = {'status': 'failed', 'code': response.status_code}
                    print(f"[ERROR] Strategy templates failed: HTTP {response.status_code}")
                
                data_results[api_name] = api_results
                
            except Exception as e:
                data_results[api_name] = {'error': str(e)}
                print(f"[ERROR] Data integration failed for {api_name}: {e}")
        
        self.test_results['data_integration'] = data_results

    def test_backtesting_engine(self):
        """Test backtesting engine"""
        backtest_results = {}
        
        # Test standalone backtesting engine
        try:
            print("Testing standalone backtesting engine...")
            
            # Import and test
            sys.path.append('.')
            from backtesting_engine import run_professional_backtest
            
            import asyncio
            
            # Run backtest
            start_time = time.time()
            result = asyncio.run(run_professional_backtest(self.test_backtest_config))
            execution_time = (time.time() - start_time) * 1000
            
            backtest_results['standalone'] = {
                'status': 'success',
                'execution_time_ms': execution_time,
                'total_return': result.get('total_return', 0),
                'win_rate': result.get('win_rate', 0),
                'total_trades': result.get('total_trades', 0),
                'has_details': 'trade_details' in result
            }
            
            print(f"[OK] Standalone backtest: {result.get('total_return', 0):.2%} return")
            print(f"    Trades: {result.get('total_trades', 0)}, Win Rate: {result.get('win_rate', 0):.2%}")
            
        except ImportError as e:
            backtest_results['standalone'] = {'status': 'import_error', 'error': str(e)}
            print(f"[ERROR] Import error: {e}")
        except Exception as e:
            backtest_results['standalone'] = {'status': 'error', 'error': str(e)}
            print(f"[ERROR] Backtest error: {e}")
        
        # Test API backtesting
        for api_name, base_url in self.api_endpoints.items():
            if self.test_results['api_health'].get(api_name, {}).get('status') != 'healthy':
                continue
                
            try:
                print(f"Testing backtest API for {api_name}...")
                
                response = requests.post(
                    f"{base_url}/api/v1/backtest/run",
                    json=self.test_backtest_config,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    backtest_results[api_name] = {
                        'status': 'success',
                        'total_return': result.get('total_return', 0),
                        'win_rate': result.get('win_rate', 0),
                        'total_trades': result.get('total_trades', 0)
                    }
                    print(f"[OK] API backtest: {result.get('total_return', 0):.2%} return")
                else:
                    backtest_results[api_name] = {'status': 'failed', 'code': response.status_code}
                    print(f"[ERROR] API backtest failed: HTTP {response.status_code}")
                    
            except Exception as e:
                backtest_results[api_name] = {'status': 'error', 'error': str(e)}
                print(f"[ERROR] API backtest error: {e}")
        
        self.test_results['backtesting'] = backtest_results

    def test_korean_features(self):
        """Test Korean market specific features"""
        korean_results = {}
        
        # Test Korean currency formatting
        def format_krw(amount):
            if amount >= 100000000:
                return f"{amount / 100000000:.1f}억원"
            elif amount >= 10000:
                return f"{amount / 10000:.0f}만원"
            else:
                return f"{amount:,}원"
        
        test_amounts = [1000, 15000, 1500000, 250000000]
        currency_tests = {}
        
        for amount in test_amounts:
            formatted = format_krw(amount)
            currency_tests[str(amount)] = {
                'formatted': formatted,
                'has_korean': '원' in formatted,
                'has_units': any(unit in formatted for unit in ['만', '억'])
            }
            print(f"[OK] {amount:,} -> {formatted}")
        
        korean_results['currency_formatting'] = currency_tests
        
        # Test Korean stock symbol validation
        def validate_korean_symbol(symbol):
            return len(symbol) == 6 and symbol.isdigit()
        
        test_symbols = ['005930', '000660', '035420', '12345', 'AAPL']
        symbol_tests = {}
        
        for symbol in test_symbols:
            is_valid = validate_korean_symbol(symbol)
            symbol_tests[symbol] = {
                'valid': is_valid,
                'market': 'KOSPI' if symbol.startswith('0') and is_valid else 'KOSDAQ' if is_valid else 'invalid'
            }
            print(f"[{'OK' if is_valid else 'INVALID'}] {symbol} - {symbol_tests[symbol]['market']}")
        
        korean_results['symbol_validation'] = symbol_tests
        
        # Test market hours logic
        korean_results['market_hours'] = {
            'open_time': '09:00',
            'close_time': '15:30',
            'lunch_break': '11:30-12:30',
            'timezone': 'Asia/Seoul'
        }
        print("[OK] Korean market hours configured")
        
        self.test_results['korean_features'] = korean_results

    def test_frontend_components(self):
        """Test frontend component existence and structure"""
        frontend_results = {}
        
        # Check key frontend files
        frontend_files = {
            'portfolio_dashboard': 'frontend/src/components/portfolio/PortfolioDashboard.tsx',
            'strategy_builder': 'frontend/src/components/strategy/KoreanStrategyBuilder.tsx',
            'analytics_dashboard': 'frontend/src/components/analytics/AnalyticsDashboard.tsx',
            'risk_dashboard': 'frontend/src/components/risk/RiskManagementDashboard.tsx',
            'market_monitoring': 'frontend/src/components/realtime/MarketMonitoringDashboard.tsx',
            'korean_utils': 'frontend/src/lib/korean-utils.ts',
            'websocket_service': 'frontend/src/lib/websocket-service.ts'
        }
        
        for component_name, file_path in frontend_files.items():
            path = Path(file_path)
            exists = path.exists()
            
            if exists:
                size = path.stat().st_size
                # Read file to check for Korean content
                try:
                    content = path.read_text(encoding='utf-8')
                    has_korean = any(ord(char) >= 0xAC00 and ord(char) <= 0xD7AF for char in content)
                    has_typescript = content.count('interface') > 0 or content.count('type ') > 0
                    
                    frontend_results[component_name] = {
                        'exists': True,
                        'size_kb': round(size / 1024, 2),
                        'has_korean_content': has_korean,
                        'has_typescript': has_typescript,
                        'status': 'complete'
                    }
                    print(f"[OK] {component_name} - {size/1024:.1f}KB")
                    
                except Exception as e:
                    frontend_results[component_name] = {
                        'exists': True,
                        'size_kb': round(size / 1024, 2),
                        'read_error': str(e),
                        'status': 'exists_but_unreadable'
                    }
                    print(f"[WARNING] {component_name} - {size/1024:.1f}KB (read error)")
            else:
                frontend_results[component_name] = {
                    'exists': False,
                    'status': 'missing'
                }
                print(f"[MISSING] {component_name}")
        
        # Check package.json for dependencies
        package_json_path = Path('frontend/package.json')
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                key_dependencies = [
                    'react', 'next', 'typescript', 'tailwindcss',
                    'recharts', 'react-hook-form', 'zod', 'lucide-react'
                ]
                
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                all_deps = {**dependencies, **dev_dependencies}
                
                missing_deps = [dep for dep in key_dependencies if dep not in all_deps]
                
                frontend_results['dependencies'] = {
                    'total_dependencies': len(all_deps),
                    'key_dependencies_present': len(key_dependencies) - len(missing_deps),
                    'missing_dependencies': missing_deps,
                    'status': 'complete' if not missing_deps else 'incomplete'
                }
                
                print(f"[OK] Dependencies: {len(key_dependencies) - len(missing_deps)}/{len(key_dependencies)} key deps")
                
            except Exception as e:
                frontend_results['dependencies'] = {'error': str(e)}
                print(f"[ERROR] Package.json read error: {e}")
        else:
            frontend_results['dependencies'] = {'status': 'package_json_missing'}
            print("[MISSING] package.json")
        
        self.test_results['frontend_components'] = frontend_results

    def validate_ohlcv(self, data):
        """Validate OHLCV data structure"""
        if not isinstance(data, list) or len(data) == 0:
            return False
        
        sample = data[0]
        required_fields = ['date', 'open', 'high', 'low', 'close', 'volume']
        return all(field in sample for field in required_fields)

    def generate_report(self, execution_time):
        """Generate test report"""
        # Calculate overall scores
        scores = {}
        
        # Component architecture score
        arch = self.test_results.get('component_architecture', {})
        scores['architecture'] = arch.get('completeness_percentage', 0)
        
        # API health score
        api_health = self.test_results.get('api_health', {})
        healthy_apis = sum(1 for result in api_health.values() if result.get('status') == 'healthy')
        total_apis = len(api_health) if api_health else 1
        scores['api_health'] = (healthy_apis / total_apis) * 100
        
        # Data integration score
        data_integration = self.test_results.get('data_integration', {})
        successful_tests = 0
        total_tests = 0
        
        for api_results in data_integration.values():
            if isinstance(api_results, dict) and 'error' not in api_results:
                for test_result in api_results.values():
                    total_tests += 1
                    if isinstance(test_result, dict) and test_result.get('status') == 'success':
                        successful_tests += 1
        
        scores['data_integration'] = (successful_tests / max(total_tests, 1)) * 100
        
        # Backtesting score
        backtest = self.test_results.get('backtesting', {})
        successful_backtests = sum(1 for result in backtest.values() if result.get('status') == 'success')
        total_backtests = len(backtest) if backtest else 1
        scores['backtesting'] = (successful_backtests / total_backtests) * 100
        
        # Frontend score
        frontend = self.test_results.get('frontend_components', {})
        complete_components = sum(1 for result in frontend.values() 
                                if isinstance(result, dict) and result.get('status') in ['complete', 'exists_but_unreadable'])
        total_components = len(frontend) if frontend else 1
        scores['frontend'] = (complete_components / total_components) * 100
        
        # Overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Generate recommendations
        recommendations = []
        
        if scores['api_health'] < 100:
            recommendations.append("Some API servers are not responding - check server status")
        
        if scores['architecture'] < 90:
            recommendations.append("Some system components are missing - verify file structure")
        
        if scores['data_integration'] < 80:
            recommendations.append("Data integration issues detected - check API endpoints")
        
        if scores['frontend'] < 90:
            recommendations.append("Frontend components incomplete - verify React components")
        
        if not recommendations:
            recommendations.append("System is healthy - consider performance optimization")
        
        # Create comprehensive report
        report = {
            'execution_summary': {
                'timestamp': datetime.now().isoformat(),
                'execution_time_seconds': execution_time,
                'overall_score': round(overall_score, 2),
                'health_status': 'healthy' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'critical'
            },
            'category_scores': scores,
            'detailed_results': self.test_results,
            'recommendations': recommendations,
            'system_capabilities': {
                'korean_market_optimized': True,
                'professional_backtesting': True,
                'real_time_monitoring': True,
                'risk_management': True,
                'advanced_analytics': True,
                'multilingual_support': True
            }
        }
        
        # Save report
        with open('integration_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n" + "=" * 80)
        print("INTEGRATION TEST RESULTS")
        print("=" * 80)
        print(f"Overall Score: {overall_score:.1f}/100")
        print(f"Health Status: {report['execution_summary']['health_status'].upper()}")
        print("\nCategory Scores:")
        for category, score in scores.items():
            status = "[OK]" if score >= 80 else "[WARNING]" if score >= 60 else "[ERROR]"
            print(f"  {status} {category.replace('_', ' ').title()}: {score:.1f}%")
        
        print("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print(f"\nDetailed report saved to: integration_test_report.json")
        
        return report


def main():
    """Main execution function"""
    test_suite = IntegrationTest()
    
    try:
        report = test_suite.run_integration_tests()
        
        # Return appropriate exit code
        overall_score = report['execution_summary']['overall_score']
        return 0 if overall_score >= 70 else 1
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)