'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';
import type { Stock } from '@/types';

interface StockSearchProps {
  onStockSelect: (stock: Stock) => void;
  selectedStock?: Stock | null;  
  placeholder?: string;
}

export default function StockSearchSimple({ 
  onStockSelect, 
  selectedStock, 
  placeholder = "종목 검색 (예: 삼성전자, 005930)" 
}: StockSearchProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [filteredStocks, setFilteredStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load all stocks once on component mount
  useEffect(() => {
    fetchAllStocks();
  }, []);

  const fetchAllStocks = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8003/api/v1/stocks?limit=100');
      const data = await response.json();
      setStocks(data);
    } catch (error) {
      console.error('주식 데이터를 가져오는데 실패했습니다:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fast client-side search
  useEffect(() => {
    if (query.length > 0) {
      const searchStart = performance.now();
      
      const filtered = stocks.filter(stock => 
        stock.name_kr.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase()) ||
        stock.symbol.includes(query.toUpperCase()) ||
        stock.sector.toLowerCase().includes(query.toLowerCase())
      );
      
      // Sort by relevance (exact matches first, then market cap)
      filtered.sort((a, b) => {
        const aExact = a.name_kr.toLowerCase() === query.toLowerCase() || a.symbol === query.toUpperCase();
        const bExact = b.name_kr.toLowerCase() === query.toLowerCase() || b.symbol === query.toUpperCase();
        
        if (aExact && !bExact) return -1;
        if (!aExact && bExact) return 1;
        
        // Sort by current price as proxy for market cap
        return (b.current_price || 0) - (a.current_price || 0);
      });
      
      setFilteredStocks(filtered.slice(0, 10));
      setSelectedIndex(-1);
      
      const searchTime = performance.now() - searchStart;
      console.log(`Search completed in ${searchTime.toFixed(2)}ms`);
    } else {
      setFilteredStocks([]);
    }
  }, [query, stocks]);

  // Click outside handler
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setIsOpen(value.length > 0);
  };

  const handleStockSelect = (stock: Stock) => {
    onStockSelect(stock);
    setQuery(`${stock.name_kr} (${stock.symbol})`);
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || filteredStocks.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < filteredStocks.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleStockSelect(filteredStocks[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const clearSearch = () => {
    setQuery('');
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  return (
    <div className="relative w-full max-w-md" ref={searchRef}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          className="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length > 0 && setIsOpen(true)}
        />
        {query && (
          <button
            onClick={clearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <X className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Search Results */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none">
          {loading ? (
            <div className="px-4 py-2 text-sm text-gray-500">검색 중...</div>
          ) : filteredStocks.length > 0 ? (
            <>
              <div className="px-3 py-1 text-xs text-gray-500 bg-gray-50 border-b">
                {filteredStocks.length}개 결과 | {stocks.length}개 종목 검색 가능
              </div>
              {filteredStocks.map((stock, index) => (
                <button
                  key={stock.symbol}
                  className={`w-full text-left px-4 py-2 hover:bg-gray-100 ${
                    index === selectedIndex ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleStockSelect(stock)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-gray-900 flex items-center gap-2">
                        {stock.name_kr}
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          stock.market === 'KOSPI' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {stock.market}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {stock.symbol} | {stock.sector}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">
                        ₩{stock.current_price?.toLocaleString()}
                      </div>
                      <div className={`text-sm ${
                        (stock.change || 0) >= 0 ? 'text-red-600' : 'text-blue-600'
                      }`}>
                        {(stock.change || 0) >= 0 ? '+' : ''}{stock.change}%
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </>
          ) : query ? (
            <div className="px-4 py-2 text-sm text-gray-500">
              "{query}"에 대한 검색 결과가 없습니다.
            </div>
          ) : null}
        </div>
      )}

      {/* Selected Stock Display */}
      {selectedStock && (
        <div className="mt-2 p-2 bg-blue-50 rounded-md">
          <div className="text-sm text-blue-800">
            선택된 종목: <strong>{selectedStock.name_kr}</strong> ({selectedStock.symbol})
          </div>
        </div>
      )}
    </div>
  );
}