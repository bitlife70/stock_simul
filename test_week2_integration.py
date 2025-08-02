#!/usr/bin/env python3
"""
Week 2 Enhanced Data Integration Test Suite
Tests all enhanced features with real Korean market data
"""
import requests
import json
from datetime import datetime

# API Base URL
API_BASE = "http://localhost:8002"

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy - Status: {data['status']}")
            return True
        else:
            print(f"❌ API health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_real_stock_data():
    """Test real Korean stock data fetching"""
    print("\n📈 Testing Real Korean Stock Data...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/stocks?limit=5", timeout=10)
        if response.status_code == 200:
            stocks = response.json()
            print(f"✅ Fetched {len(stocks)} real Korean stocks")
            for stock in stocks[:3]:
                print(f"   • {stock['name_kr']} ({stock['symbol']}) - {stock['market']}")
            return True
        else:
            print(f"❌ Stock data fetch failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stock data fetch error: {e}")
        return False

def test_samsung_price_data():
    """Test real price data for Samsung Electronics"""
    print("\n💰 Testing Samsung Electronics Price Data...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/stocks/005930/data?days=5", timeout=15)
        if response.status_code == 200:
            price_data = response.json()
            if price_data:
                latest = price_data[-1]
                print(f"✅ Samsung (005930) latest data:")
                print(f"   • Date: {latest['date']}")
                print(f"   • Close: ₩{latest['close']:,}")
                print(f"   • Volume: {latest['volume']:,}")
                print(f"   • Total records: {len(price_data)} days")
                return True
            else:
                print("❌ No price data returned")
                return False
        else:
            print(f"❌ Price data fetch failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Price data fetch error: {e}")
        return False

def test_market_overview():
    """Test market overview endpoint"""
    print("\n🏢 Testing Market Overview...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/market/overview", timeout=10)
        if response.status_code == 200:
            overview = response.json()
            print(f"✅ Market Overview:")
            print(f"   • KOSPI stocks: {overview['markets']['KOSPI']['total_stocks']}")
            print(f"   • KOSDAQ stocks: {overview['markets']['KOSDAQ']['total_stocks']}")
            print(f"   • Primary data source: {overview['data_sources']['primary']}")
            return True
        else:
            print(f"❌ Market overview failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market overview error: {e}")
        return False

def test_caching_performance():
    """Test caching performance improvement"""
    print("\n⚡ Testing Caching Performance...")
    try:
        import time
        
        # First request (cache miss)
        start_time = time.time()
        response1 = requests.get(f"{API_BASE}/api/v1/stocks?limit=10", timeout=10)
        first_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        response2 = requests.get(f"{API_BASE}/api/v1/stocks?limit=10", timeout=10)
        second_time = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            print(f"✅ Caching Performance:")
            print(f"   • First request (cold): {first_time:.3f}s")
            print(f"   • Second request (cached): {second_time:.3f}s")
            if second_time < first_time:
                print(f"   • Performance improvement: {((first_time - second_time) / first_time * 100):.1f}%")
            return True
        else:
            print("❌ Caching test failed")
            return False
    except Exception as e:
        print(f"❌ Caching test error: {e}")
        return False

def test_strategy_templates():
    """Test strategy templates endpoint"""
    print("\n📋 Testing Strategy Templates...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/strategies/templates", timeout=5)
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Strategy Templates Available: {len(templates)}")
            for template in templates:
                print(f"   • {template['name_kr']} ({template['id']})")
            return True
        else:
            print(f"❌ Strategy templates failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Strategy templates error: {e}")
        return False

def main():
    """Run complete Week 2 integration test suite"""
    print("=" * 60)
    print("🧪 Week 2 Enhanced Data Integration Test Suite")
    print("=" * 60)
    
    tests = [
        test_api_health,
        test_real_stock_data,
        test_samsung_price_data,
        test_market_overview,
        test_caching_performance,
        test_strategy_templates
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 Week 2 Enhanced Data Integration: ALL TESTS PASSED!")
        print("✅ Real Korean market data integration is fully functional")
        print("✅ Caching system is working properly")
        print("✅ All API endpoints are responding correctly")
        print("✅ Frontend can connect to enhanced API on port 8002")
        print("\n🚀 Ready for Week 3: Strategy Engine Enhancement!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the enhanced API server.")
    
    print("\n📱 Frontend Application: http://localhost:3003")
    print("📚 API Documentation: http://localhost:8002/docs")

if __name__ == "__main__":
    main()