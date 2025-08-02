#!/usr/bin/env python3
"""
API 테스트 스크립트
백엔드 API의 모든 엔드포인트를 테스트합니다.
"""

import requests
import json
import time
import sys

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
    
    def test_endpoint(self, name, endpoint, method="GET", expected_status=200, data=None):
        """개별 엔드포인트 테스트"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.request(method, url, json=data, timeout=10)
            
            if response.status_code == expected_status:
                print(f"[PASS] {name}")
                print(f"  Status: {response.status_code}")
                
                # JSON 응답이면 예쁘게 출력
                try:
                    json_data = response.json()
                    if isinstance(json_data, list) and len(json_data) > 0:
                        print(f"  Data: {len(json_data)} items")
                        if len(json_data) <= 3:
                            print(f"  Sample: {json.dumps(json_data[0], ensure_ascii=False, indent=2)}")
                    elif isinstance(json_data, dict):
                        print(f"  Keys: {list(json_data.keys())}")
                except:
                    print(f"  Response: {response.text[:100]}...")
                
                print()
                self.passed += 1
                return True
            else:
                print(f"[FAIL] {name}")
                print(f"  Expected: {expected_status}, Got: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                print()
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"[ERROR] {name}")
            print(f"  Error: {e}")
            print()
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("Korean Stock Backtesting API - 전체 테스트")
        print("=" * 60)
        print()
        
        # 기본 엔드포인트
        print("=== 기본 엔드포인트 ===")
        self.test_endpoint("Health Check", "/health")
        self.test_endpoint("Root Endpoint", "/")
        
        # 주식 데이터 엔드포인트
        print("=== 주식 데이터 ===")
        self.test_endpoint("Stock List", "/api/v1/stocks")
        self.test_endpoint("Market Overview", "/api/v1/market-overview")
        self.test_endpoint("Stock Detail (Samsung)", "/api/v1/stocks/005930")
        self.test_endpoint("Stock Detail (Not Found)", "/api/v1/stocks/999999")
        
        # 전략 엔드포인트
        print("=== 전략 관리 ===")
        self.test_endpoint("Strategy Templates", "/api/v1/strategies/templates")
        
        # 결과 출력
        print("=" * 60)
        print(f"테스트 결과: {self.passed}개 통과, {self.failed}개 실패")
        print("=" * 60)
        
        if self.failed == 0:
            print("SUCCESS: All tests passed!")
            return True
        else:
            print(f"WARNING: {self.failed} tests failed.")
            return False

def check_server_status():
    """서버 상태 확인"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def main():
    """메인 함수"""
    print("API 서버 상태 확인 중...")
    
    if not check_server_status():
        print("ERROR: API server is not running.")
        print("Please start the server first:")
        print("  python api_server.py")
        print("Or:")
        print("  python start_dev.py")
        return False
    
    print("SUCCESS: API server is running.")
    print()
    
    # 테스트 실행
    tester = APITester()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)