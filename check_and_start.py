#!/usr/bin/env python3
"""
Korean Stock Backtesting Platform - Server Check and Start Script
"""

import subprocess
import requests
import time
import os
import sys

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get('http://localhost:8001/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server"""
    print("Starting API server on port 8001...")
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start API server
    subprocess.Popen([sys.executable, "api_server.py"])
    
    # Wait for server to start
    for i in range(10):
        time.sleep(1)
        if check_api_server():
            print("✅ API server started successfully!")
            return True
        print(f"Waiting for API server to start... {i+1}/10")
    
    print("❌ Failed to start API server")
    return False

def main():
    print("=" * 60)
    print("Korean Stock Backtesting Platform - Server Status Check")
    print("=" * 60)
    
    # Check if API server is running
    if check_api_server():
        print("✅ API server is already running on port 8001")
        print("   API Documentation: http://localhost:8001/docs")
        print("   Health Check: http://localhost:8001/health")
    else:
        print("⚠️  API server is not running")
        if start_api_server():
            print("\n🚀 API Server Ready!")
            print("   API Documentation: http://localhost:8001/docs")
            print("   Stock Data: http://localhost:8001/api/v1/stocks")
            print("   Strategy Templates: http://localhost:8001/api/v1/strategies/templates")
        else:
            print("\n❌ Failed to start API server. Please check the logs.")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Frontend should be running at: http://localhost:3000")
    print("If not, run: cd frontend && npm run dev")
    print("=" * 60)

if __name__ == "__main__":
    main()