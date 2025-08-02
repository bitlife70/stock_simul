#!/usr/bin/env python3
"""
Start the enhanced Korean Stock API server in background
"""
import subprocess
import sys
import time
import requests

def start_server():
    print("Starting Enhanced Korean Stock API Server...")
    
    # Start the server in background
    process = subprocess.Popen([
        sys.executable, "api_server_updated.py"
    ], cwd=".")
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Enhanced API Server is running successfully!")
            print("📊 Enhanced Stock Data: http://localhost:8002/api/v1/stocks")
            print("📈 Real Stock Prices: http://localhost:8002/api/v1/stocks/005930/data")
            print("🔍 Stock Search: http://localhost:8002/api/v1/stocks/search?q=삼성")
            print("📋 API Documentation: http://localhost:8002/docs")
            return process
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        return None

if __name__ == "__main__":
    process = start_server()
    if process:
        print("\n🎉 Enhanced API server is ready for Week 2 Data Integration!")
        print("Press Ctrl+C to stop the server...")
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()