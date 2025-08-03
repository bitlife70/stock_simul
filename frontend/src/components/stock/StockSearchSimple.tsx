'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, X, TrendingUp } from 'lucide-react';
import type { Stock } from '@/types';
import { API_BASE_URL } from '@/lib/config';

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
  const [popularStocks, setPopularStocks] = useState<Stock[]>([]);
  const [showPopular, setShowPopular] = useState(false);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load sample stocks and popular stocks on component mount
  useEffect(() => {
    fetchSampleStocks();
    fetchPopularStocks();
  }, []);

  // Load a small set of sample stocks for reference
  const fetchSampleStocks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/stocks?limit=20`);
      const data = await response.json();
      setStocks(data);
    } catch (error) {
      console.error('주식 데이터를 가져오는데 실패했습니다:', error);
    }
  };

  // Load popular stocks for initial display
  const fetchPopularStocks = async () => {
    setLoading(true);
    try {
      // Fetch popular Korean stocks (could be enhanced with actual popular stocks endpoint)
      const response = await fetch(`${API_BASE_URL}/api/v1/stocks?limit=10`);
      const data = await response.json();
      setPopularStocks(data);
    } catch (error) {
      console.error('인기 종목 데이터를 가져오는데 실패했습니다:', error);
    } finally {
      setLoading(false);
    }
  };

  // Server-side search with debouncing
  useEffect(() => {
    if (query.length > 0) {
      const timeoutId = setTimeout(async () => {
        await performSearch(query);
      }, 300); // 300ms debounce

      return () => clearTimeout(timeoutId);
    } else {
      setFilteredStocks([]);
    }
  }, [query]);

  const performSearch = async (searchQuery: string) => {
    if (searchQuery.length < 1) {
      setFilteredStocks([]);
      return;
    }

    setLoading(true);
    try {
      const searchStart = performance.now();
      
      const url = `${API_BASE_URL}/api/v1/stocks/search?q=${encodeURIComponent(searchQuery)}&limit=15`;
      console.log('Searching with URL:', url);
      
      const response = await fetch(url);
      console.log('Response status:', response.status);
      
      const data = await response.json();
      console.log('Response data:', data);
      
      // API returns an object with results array
      if (data && data.results) {
        console.log(`Found ${data.results.length} results`);
        setFilteredStocks(data.results);
      } else {
        console.log('No results found or unexpected data structure');
        setFilteredStocks([]);
      }
      setSelectedIndex(-1);
      
      const searchTime = performance.now() - searchStart;
      console.log(`Database search completed in ${searchTime.toFixed(2)}ms for query: "${searchQuery}"`);
    } catch (error) {
      console.error('검색 중 오류가 발생했습니다:', error);
      console.error('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        query: searchQuery
      });
      setFilteredStocks([]);
    } finally {
      setLoading(false);
    }
  };

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
    setIsOpen(value.length > 0 || showPopular);
    if (value.length === 0) {
      setShowPopular(true);
    } else {
      setShowPopular(false);
    }
  };

  const handleSearchClick = () => {
    if (query.trim()) {
      performSearch(query.trim());
    }
  };

  const handleEnterSearch = () => {
    if (query.trim()) {
      performSearch(query.trim());
    } else if (showPopular && selectedIndex >= 0) {
      handleStockSelect(popularStocks[selectedIndex]);
    }
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
        if (query.trim() && filteredStocks.length === 0) {
          // Explicit search when no results
          handleEnterSearch();
        } else if (selectedIndex >= 0) {
          if (showPopular) {
            handleStockSelect(popularStocks[selectedIndex]);
          } else {
            handleStockSelect(filteredStocks[selectedIndex]);
          }
        } else if (query.trim()) {
          // Search when Enter is pressed without selection
          handleEnterSearch();
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
    setShowPopular(false);
  };

  const handleFocus = () => {
    if (query.length > 0) {
      setIsOpen(true);
      setShowPopular(false);
    } else {
      setIsOpen(true);
      setShowPopular(true);
    }
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
          className="block w-full pl-10 pr-20 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
        />
        <div className="absolute inset-y-0 right-0 flex items-center">
          {query && (
            <button
              onClick={clearSearch}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <button
            onClick={handleSearchClick}
            className="ml-1 mr-2 px-2 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
            title="검색"
          >
            <Search className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Search Results */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white dark:bg-gray-800 shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 dark:ring-gray-600 overflow-auto focus:outline-none">
          {loading ? (
            <div className="px-4 py-2 text-sm text-gray-500 dark:text-gray-400">검색 중...</div>
          ) : showPopular ? (
            <>
              <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 border-b dark:border-gray-600 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                인기 종목 ({popularStocks.length}개)
              </div>
              {popularStocks.map((stock, index) => (
                <button
                  key={stock.symbol}
                  className={`w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                    index === selectedIndex ? 'bg-blue-50 dark:bg-blue-900' : ''
                  }`}
                  onClick={() => handleStockSelect(stock)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                        {stock.name_kr}
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          stock.market === 'KOSPI' 
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200' 
                            : 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
                        }`}>
                          {stock.market}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {stock.symbol} | {stock.sector}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {stock.current_price ? `₩${stock.current_price.toLocaleString()}` : '-'}
                      </div>
                      {stock.change_rate !== undefined && (
                        <div className={`text-sm ${
                          stock.change_rate >= 0 ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'
                        }`}>
                          {stock.change_rate >= 0 ? '+' : ''}{(stock.change_rate * 100).toFixed(2)}%
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </>
          ) : filteredStocks.length > 0 ? (
            <>
              <div className="px-3 py-1 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700 border-b dark:border-gray-600">
                {filteredStocks.length}개 결과 | {stocks.length}개 종목 검색 가능
              </div>
              {filteredStocks.map((stock, index) => (
                <button
                  key={stock.symbol}
                  className={`w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                    index === selectedIndex ? 'bg-blue-50 dark:bg-blue-900' : ''
                  }`}
                  onClick={() => handleStockSelect(stock)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                        {stock.name_kr}
                        <span className={`px-2 py-0.5 text-xs rounded-full ${
                          stock.market === 'KOSPI' 
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-200' 
                            : 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-200'
                        }`}>
                          {stock.market}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {stock.symbol} | {stock.sector}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {stock.current_price ? `₩${stock.current_price.toLocaleString()}` : '-'}
                      </div>
                      {stock.change_rate !== undefined && (
                        <div className={`text-sm ${
                          stock.change_rate >= 0 ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'
                        }`}>
                          {stock.change_rate >= 0 ? '+' : ''}{(stock.change_rate * 100).toFixed(2)}%
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </>
          ) : query ? (
            <div className="px-4 py-8 text-center">
              <div className="text-gray-500 dark:text-gray-400 mb-2">
                "{query}"에 대한 검색 결과가 없습니다.
              </div>
              <div className="text-sm text-gray-400 dark:text-gray-500">
                • 종목명이나 종목코드를 정확히 입력해주세요<br />
                • 예시: 삼성전자, 005930, Samsung
              </div>
              <button
                onClick={() => {
                  setQuery('');
                  setShowPopular(true);
                }}
                className="mt-3 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm underline"
              >
                인기 종목 보기
              </button>
            </div>
          ) : null}
        </div>
      )}

      {/* Selected Stock Display */}
      {selectedStock && (
        <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/30 rounded-md">
          <div className="text-sm text-blue-800 dark:text-blue-200">
            선택된 종목: <strong>{selectedStock.name_kr}</strong> ({selectedStock.symbol})
          </div>
        </div>
      )}
    </div>
  );
}