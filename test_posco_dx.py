#!/usr/bin/env python3
"""Test script to check if 포스코DX is available in the database"""

from stock_data_manager import stock_manager

def test_posco_dx():
    print("=== 포스코DX 테스트 ===")
    
    # Check total stocks
    all_stocks = stock_manager.get_all_stocks()
    print(f"Total stocks in database: {len(all_stocks)}")
    
    # Search for 포스코DX
    search_results = stock_manager.search_stocks("포스코DX")
    print(f"Search results for '포스코DX': {len(search_results)}")
    
    if search_results:
        for stock in search_results:
            print(f"Found: {stock['symbol']} - {stock['name_kr']} ({stock['market']})")
    
    # Search by symbol
    symbol_results = stock_manager.search_stocks("022100")
    print(f"Search results for '022100': {len(symbol_results)}")
    
    if symbol_results:
        for stock in symbol_results:
            print(f"Found: {stock['symbol']} - {stock['name_kr']} ({stock['market']})")
    
    # General search for POSCO related stocks
    posco_results = stock_manager.search_stocks("포스코")
    print(f"Search results for '포스코': {len(posco_results)}")
    
    for stock in posco_results:
        print(f"  - {stock['symbol']}: {stock['name_kr']} ({stock['market']})")

if __name__ == "__main__":
    test_posco_dx()