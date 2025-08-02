#!/usr/bin/env python3
"""
Professional Korean Stock Backtesting API Server Startup Script
Ensures all dependencies are available and starts the enhanced server
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    try:
        logger.info("Checking and installing required packages...")
        
        # Core packages that should be available
        required_packages = [
            'fastapi>=0.104.0',
            'uvicorn[standard]>=0.24.0',
            'pandas>=2.0.0',
            'numpy>=1.24.0',
            'scipy>=1.10.0',
            'pytz>=2023.3'
        ]
        
        # Korean market data packages (may need special handling)
        korean_packages = [
            'FinanceDataReader>=0.9.31',
            'pykrx>=1.3.1'
        ]
        
        # Install core packages
        for package in required_packages:
            logger.info(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Install Korean market packages with error handling
        for package in korean_packages:
            try:
                logger.info(f"Installing {package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install {package}: {e}")
                logger.warning("The system will work with fallback data generation")
        
        logger.info("Package installation completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to install requirements: {e}")
        return False

def check_import_dependencies():
    """Check if all critical dependencies can be imported"""
    try:
        logger.info("Checking import dependencies...")
        
        # Critical imports
        import fastapi
        import uvicorn
        import pandas
        import numpy
        logger.info("✅ Core dependencies available")
        
        # Korean market data (optional)
        try:
            import FinanceDataReader
            import pykrx
            logger.info("✅ Korean market data libraries available")
        except ImportError:
            logger.warning("⚠️  Korean market data libraries not available - using fallback data")
        
        return True
        
    except ImportError as e:
        logger.error(f"Critical dependency missing: {e}")
        return False

def create_backup_config():
    """Create backup configuration files if they don't exist"""
    try:
        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Create basic config if needed
        config_content = '''
# Korean Stock Backtesting Configuration
LOG_LEVEL=INFO
API_PORT=8001
DEFAULT_SYMBOL=005930
DEFAULT_CAPITAL=10000000
ENABLE_REAL_DATA=true
FALLBACK_MODE=false
'''
        
        config_file = Path('config.env')
        if not config_file.exists():
            with open(config_file, 'w') as f:
                f.write(config_content)
            logger.info("Created default configuration file")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create backup config: {e}")
        return False

def run_system_check():
    """Run comprehensive system check before starting server"""
    logger.info("=" * 60)
    logger.info("Korean Stock Backtesting System Check")
    logger.info("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Installation", install_requirements),
        ("Import Dependencies", check_import_dependencies),
        ("Backup Configuration", create_backup_config)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        logger.info(f"\nRunning check: {check_name}")
        try:
            result = check_func()
            if result:
                logger.info(f"✅ {check_name}: PASSED")
            else:
                logger.error(f"❌ {check_name}: FAILED")
                all_passed = False
        except Exception as e:
            logger.error(f"❌ {check_name}: ERROR - {e}")
            all_passed = False
    
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("🎉 All system checks passed! Ready to start server.")
    else:
        logger.warning("⚠️  Some checks failed. Server may run with limited functionality.")
    
    return all_passed

def start_api_server():
    """Start the professional API server"""
    try:
        logger.info("Starting Professional Korean Stock Backtesting API Server...")
        logger.info("Server will be available at: http://localhost:8001")
        logger.info("API Documentation: http://localhost:8001/docs")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        
        # Import and run the API server
        from api_server import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            reload=False,  # Disable reload for production-like startup
            access_log=True,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"Failed to import API server: {e}")
        logger.error("Make sure api_server.py and backtesting_engine.py are in the current directory")
        return False
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return False

def main():
    """Main startup routine"""
    try:
        logger.info("Korean Stock Backtesting Professional API Startup")
        logger.info("=" * 60)
        
        # Run system check
        system_ready = run_system_check()
        
        if not system_ready:
            logger.warning("System check failed, but attempting to start anyway...")
        
        # Start the server
        start_api_server()
        
    except KeyboardInterrupt:
        logger.info("\nServer shutdown requested by user")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        sys.exit(1)
    
    logger.info("Server shutdown complete")

if __name__ == "__main__":
    main()