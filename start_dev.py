#!/usr/bin/env python3
"""
Automated development environment startup script
자동으로 백엔드와 프론트엔드를 시작하고 테스트합니다.
"""

import subprocess
import sys
import os
import time
import requests
import threading
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color):
    """색상 출력 (Windows에서는 색상 없이)"""
    try:
        print(f"{color}{message}{Colors.END}")
    except UnicodeEncodeError:
        print(message)

def check_dependencies():
    """필수 의존성 확인"""
    print_colored("=== 의존성 확인 ===", Colors.BLUE)
    
    # Python 확인
    try:
        python_version = sys.version.split()[0]
        print_colored(f"✓ Python {python_version}", Colors.GREEN)
    except:
        print_colored("✗ Python not found", Colors.RED)
        return False
    
    # Node.js 확인
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print_colored(f"✓ Node.js {result.stdout.strip()}", Colors.GREEN)
        else:
            print_colored("✗ Node.js not found", Colors.RED)
            return False
    except:
        print_colored("✗ Node.js not found", Colors.RED)
        return False
    
    # npm 확인
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print_colored(f"✓ npm {result.stdout.strip()}", Colors.GREEN)
        else:
            print_colored("✗ npm not found", Colors.RED)
            return False
    except:
        print_colored("✗ npm not found", Colors.RED)
        return False
    
    return True

def install_python_deps():
    """Python 의존성 설치"""
    print_colored("=== Python 의존성 설치 ===", Colors.BLUE)
    
    required_packages = ['fastapi', 'uvicorn', 'requests']
    
    for package in required_packages:
        try:
            print_colored(f"Installing {package}...", Colors.YELLOW)
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_colored(f"✓ {package} installed", Colors.GREEN)
            else:
                print_colored(f"✗ Failed to install {package}", Colors.RED)
        except Exception as e:
            print_colored(f"✗ Error installing {package}: {e}", Colors.RED)

def install_frontend_deps():
    """프론트엔드 의존성 설치"""
    print_colored("=== 프론트엔드 의존성 확인 ===", Colors.BLUE)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_colored("✗ Frontend directory not found", Colors.RED)
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print_colored("Installing frontend dependencies...", Colors.YELLOW)
        os.chdir(frontend_dir)
        result = subprocess.run(['npm', 'install'], shell=True)
        os.chdir('..')
        
        if result.returncode == 0:
            print_colored("✓ Frontend dependencies installed", Colors.GREEN)
        else:
            print_colored("✗ Failed to install frontend dependencies", Colors.RED)
            return False
    else:
        print_colored("✓ Frontend dependencies already installed", Colors.GREEN)
    
    return True

def start_backend():
    """백엔드 서버 시작"""
    print_colored("=== 백엔드 서버 시작 ===", Colors.BLUE)
    
    try:
        # 백그라운드에서 API 서버 실행
        process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 서버 시작 대기
        time.sleep(3)
        
        # Health check
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    print_colored("✓ Backend server is running at http://localhost:8000", Colors.GREEN)
                    return process
            except:
                time.sleep(1)
                continue
        
        print_colored("✗ Backend server failed to start", Colors.RED)
        return None
        
    except Exception as e:
        print_colored(f"✗ Error starting backend: {e}", Colors.RED)
        return None

def start_frontend():
    """프론트엔드 서버 시작"""
    print_colored("=== 프론트엔드 서버 시작 ===", Colors.BLUE)
    
    try:
        frontend_dir = Path("frontend")
        os.chdir(frontend_dir)
        
        # 프론트엔드 서버 시작
        process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        os.chdir('..')
        
        # 프론트엔드 시작 대기
        time.sleep(5)
        
        print_colored("✓ Frontend server starting at http://localhost:3000", Colors.GREEN)
        return process
        
    except Exception as e:
        print_colored(f"✗ Error starting frontend: {e}", Colors.RED)
        return None

def run_api_tests():
    """API 테스트 실행"""
    print_colored("=== API 테스트 ===", Colors.BLUE)
    
    tests = [
        {
            'name': 'Health Check',
            'url': 'http://localhost:8000/health',
            'expected_status': 200
        },
        {
            'name': 'Root Endpoint',
            'url': 'http://localhost:8000/',
            'expected_status': 200
        },
        {
            'name': 'Stock List',
            'url': 'http://localhost:8000/api/v1/stocks',
            'expected_status': 200
        },
        {
            'name': 'Strategy Templates',
            'url': 'http://localhost:8000/api/v1/strategies/templates',
            'expected_status': 200
        },
        {
            'name': 'Market Overview',
            'url': 'http://localhost:8000/api/v1/market-overview',
            'expected_status': 200
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            response = requests.get(test['url'], timeout=10)
            if response.status_code == test['expected_status']:
                print_colored(f"✓ {test['name']}: PASS", Colors.GREEN)
                passed += 1
            else:
                print_colored(f"✗ {test['name']}: FAIL (Status: {response.status_code})", Colors.RED)
        except Exception as e:
            print_colored(f"✗ {test['name']}: ERROR ({e})", Colors.RED)
    
    print_colored(f"테스트 결과: {passed}/{total} 통과", Colors.BLUE)
    return passed == total

def show_status():
    """현재 상태 표시"""
    print_colored("=== 개발 환경 상태 ===", Colors.BLUE)
    print_colored("✓ Backend API: http://localhost:8000", Colors.GREEN)
    print_colored("✓ API Documentation: http://localhost:8000/docs", Colors.GREEN)
    print_colored("✓ Frontend Web: http://localhost:3000", Colors.GREEN)
    print_colored("✓ Sample Stock Data: http://localhost:8000/api/v1/stocks", Colors.GREEN)
    print_colored("✓ Strategy Templates: http://localhost:8000/api/v1/strategies/templates", Colors.GREEN)
    print("")
    print_colored("Press Ctrl+C to stop all servers", Colors.YELLOW)

def main():
    """메인 실행 함수"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Korean Stock Backtesting App - Auto Start", Colors.BOLD)
    print_colored("=" * 60, Colors.BLUE)
    
    # 1. 의존성 확인
    if not check_dependencies():
        print_colored("의존성 확인에 실패했습니다.", Colors.RED)
        return
    
    # 2. Python 패키지 설치
    install_python_deps()
    
    # 3. 프론트엔드 의존성 설치
    if not install_frontend_deps():
        print_colored("프론트엔드 설정에 실패했습니다.", Colors.RED)
        return
    
    # 4. 백엔드 시작
    backend_process = start_backend()
    if not backend_process:
        print_colored("백엔드 시작에 실패했습니다.", Colors.RED)
        return
    
    # 5. API 테스트
    time.sleep(2)
    if not run_api_tests():
        print_colored("일부 API 테스트가 실패했지만 계속 진행합니다.", Colors.YELLOW)
    
    # 6. 프론트엔드 시작
    frontend_process = start_frontend()
    
    # 7. 상태 표시
    show_status()
    
    try:
        # 서버들이 실행되는 동안 대기
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_colored("\\n=== 서버 종료 중 ===", Colors.YELLOW)
        
        # 프로세스 종료
        if backend_process:
            backend_process.terminate()
            print_colored("✓ Backend server stopped", Colors.GREEN)
        
        if frontend_process:
            frontend_process.terminate()
            print_colored("✓ Frontend server stopped", Colors.GREEN)
        
        print_colored("모든 서버가 종료되었습니다.", Colors.GREEN)

if __name__ == "__main__":
    main()