'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import { Search, X, Clock, TrendingUp, Award, Zap, Activity } from 'lucide-react';
import type { Stock } from '@/types';
import { useStockSearch } from '@/hooks/useStockSearch';
import { formatKoreanStockName, translateSectorToKorean } from '@/lib/korean-utils';

interface StockSearchProps {
  onStockSelect: (stock: Stock) => void;
  selectedStock?: Stock | null;
  placeholder?: string;
}

interface HighlightedTextProps {
  text: string;
  highlightInfo: {
    before: string;
    match: string;
    after: string;
  };
}

const HighlightedText = ({ text, highlightInfo }: HighlightedTextProps) => {
  return (
    <span>
      {highlightInfo.before}
      {highlightInfo.match && (
        <mark className="bg-yellow-200 text-yellow-900 font-medium px-1 rounded">
          {highlightInfo.match}
        </mark>
      )}
      {highlightInfo.after}
    </span>
  );
};

export default function StockSearch({ 
  onStockSelect, 
  selectedStock, 
  placeholder = "종목 검색 (예: 삼성전자, 005930, ㅅㅅㅈㅈ)" 
}: StockSearchProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [showHistory, setShowHistory] = useState(false);
  const [showPopular, setShowPopular] = useState(false);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  
  // Use the lightning-fast search hook
  const {
    query,
    setQuery,
    results,
    isLoading,
    isInitialized,
    error,
    suggestions,
    searchHistory,
    popularStocks,
    searchTime,
    totalStocks,
    getHighlightInfo,
    addToHistory,
    clearHistory
  } = useStockSearch({
    maxResults: 20,
    enableHistory: true,
    enableSuggestions: true
  });

  // Handle search results and display logic
  const displayResults = useMemo(() => {
    if (!query.trim()) {
      if (showHistory && searchHistory.length > 0) {
        return 'history';
      }
      if (showPopular && popularStocks.length > 0) {
        return 'popular';
      }
      return 'none';
    }
    return results.length > 0 ? 'results' : 'empty';
  }, [query, results, showHistory, showPopular, searchHistory, popularStocks]);
  
  // Reset selected index when results change
  useEffect(() => {
    setSelectedIndex(-1);
  }, [results]);

  // Handle click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowHistory(false);
        setShowPopular(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Get current list for keyboard navigation
  const getCurrentList = () => {
    switch (displayResults) {
      case 'results':
        return results.map(r => r.stock);
      case 'history':
        return [];
      case 'popular':
        return popularStocks;
      default:
        return [];
    }
  };
  
  const currentList = getCurrentList();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setIsOpen(true);
    setShowHistory(value.length === 0);
    setShowPopular(value.length === 0);
  };

  const handleStockSelect = (stock: Stock, addToSearchHistory = true) => {
    onStockSelect(stock);
    const displayText = `${stock.name_kr} (${stock.symbol})`;
    setQuery(displayText);
    setIsOpen(false);
    setSelectedIndex(-1);
    setShowHistory(false);
    setShowPopular(false);
    
    // Add to search history
    if (addToSearchHistory) {
      addToHistory(stock.name_kr);
    }
  };
  
  const handleHistorySelect = (historyQuery: string) => {
    setQuery(historyQuery);
    setShowHistory(false);
    setShowPopular(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (displayResults === 'history') {
          setSelectedIndex(prev => 
            prev < searchHistory.length - 1 ? prev + 1 : 0
          );
        } else if (currentList.length > 0) {
          setSelectedIndex(prev => 
            prev < currentList.length - 1 ? prev + 1 : 0
          );
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (displayResults === 'history') {
          setSelectedIndex(prev => 
            prev > 0 ? prev - 1 : searchHistory.length - 1
          );
        } else if (currentList.length > 0) {
          setSelectedIndex(prev => 
            prev > 0 ? prev - 1 : currentList.length - 1
          );
        }
        break;
      case 'Enter':
        e.preventDefault();
        if (displayResults === 'history' && selectedIndex >= 0 && selectedIndex < searchHistory.length) {
          handleHistorySelect(searchHistory[selectedIndex]);
        } else if (selectedIndex >= 0 && selectedIndex < currentList.length) {
          handleStockSelect(currentList[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        setShowHistory(false);
        setShowPopular(false);
        inputRef.current?.blur();
        break;
    }
  };

  const handleClearSelection = () => {
    setQuery('');
    setIsOpen(true);
    setSelectedIndex(-1);
    setShowHistory(true);
    setShowPopular(true);
    onStockSelect(null as unknown as Stock);
    inputRef.current?.focus();
  };
  
  const handleFocus = () => {
    if (!query.trim()) {
      setShowHistory(true);
      setShowPopular(true);
    }
    setIsOpen(true);
  };

  // Update query when selectedStock changes
  useEffect(() => {
    if (selectedStock) {
      setQuery(`${selectedStock.name_kr} (${selectedStock.symbol})`);
    }
  }, [selectedStock]);
  
  // Get market badge color
  const getMarketBadgeColor = (market: string) => {
    switch (market) {
      case 'KOSPI':
        return 'bg-blue-100 text-blue-800';
      case 'KOSDAQ':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 bg-white text-gray-900 placeholder-gray-500"
          disabled={!isInitialized}
          autoComplete="off"
        />
        {query && (
          <button
            onClick={handleClearSelection}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
        
        {/* Performance indicator */}
        {isInitialized && !isLoading && (
          <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
            <Activity className="h-4 w-4 text-green-500" title={`${searchTime}ms response time`} />
          </div>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-hidden">
          {/* Performance indicator */}
          {isInitialized && searchTime > 0 && query.trim() && (
            <div className="px-3 py-1 text-xs text-gray-500 bg-gray-50 border-b flex items-center justify-between">
              <span className="flex items-center gap-1">
                <Zap className="h-3 w-3" />
                {searchTime}ms • {totalStocks.toLocaleString()}개 종목
              </span>
              {results.length > 0 && (
                <span>{results.length}개 결과</span>
              )}
            </div>
          )}
          
          {/* Search Results */}
          {displayResults === 'results' && (
            <ul ref={listRef} className="max-h-64 overflow-y-auto">
              {results.map((result, index) => (
                <li
                  key={result.stock.symbol}
                  onClick={() => handleStockSelect(result.stock)}
                  className={`px-4 py-3 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0 ${
                    index === selectedIndex
                      ? 'bg-blue-50 text-blue-900'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 flex items-center gap-2">
                        <HighlightedText 
                          text={result.stock.name_kr} 
                          highlightInfo={getHighlightInfo(result.stock.name_kr, result.highlightIndices)}
                        />
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getMarketBadgeColor(result.stock.market)}`}>
                          {result.stock.market}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 flex items-center gap-2">
                        <span>{result.stock.symbol}</span>
                        {result.matchType === 'chosung' && (
                          <span className="text-xs bg-purple-100 text-purple-700 px-1 rounded">초성</span>
                        )}
                        {result.matchType === 'exact' && (
                          <span className="text-xs bg-green-100 text-green-700 px-1 rounded">완전일치</span>
                        )}
                      </div>
                    </div>
                    <div className="text-right text-xs text-gray-400">
                      <div>점수: {result.score}</div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
          
          {/* Search History */}
          {displayResults === 'history' && searchHistory.length > 0 && (
            <div className="max-h-32 overflow-y-auto">
              <div className="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-50 border-b flex items-center gap-1">
                <Clock className="h-3 w-3" />
                최근 검색
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    clearHistory();
                  }}
                  className="ml-auto text-gray-400 hover:text-gray-600"
                >
                  지우기
                </button>
              </div>
              {searchHistory.map((historyItem, index) => (
                <div
                  key={index}
                  onClick={() => handleHistorySelect(historyItem)}
                  className={`px-4 py-2 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0 ${
                    index === selectedIndex
                      ? 'bg-blue-50 text-blue-900'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="text-sm text-gray-700">{historyItem}</div>
                </div>
              ))}
            </div>
          )}
          
          {/* Popular Stocks */}
          {displayResults === 'popular' && popularStocks.length > 0 && (
            <div className="max-h-48 overflow-y-auto">
              <div className="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-50 border-b flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                인기 종목
              </div>
              {popularStocks.map((stock, index) => (
                <div
                  key={stock.symbol}
                  onClick={() => handleStockSelect(stock, false)}
                  className={`px-4 py-2 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0 ${
                    index === selectedIndex
                      ? 'bg-blue-50 text-blue-900'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium text-gray-900 flex items-center gap-2">
                        {stock.name_kr}
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getMarketBadgeColor(stock.market)}`}>
                          {stock.market}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">{stock.symbol}</div>
                    </div>
                    <Award className="h-4 w-4 text-yellow-500" />
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Empty State */}
          {displayResults === 'empty' && (
            <div className="px-4 py-6 text-center text-gray-500">
              <div className="text-sm">
                '{query}' 검색 결과가 없습니다
              </div>
              {suggestions.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-gray-400 mb-1">추천 검색어:</div>
                  <div className="flex flex-wrap gap-1">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => setQuery(suggestion)}
                        className="px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-gray-600">
              {!isInitialized ? '검색 엔진 초기화 중...' : '검색 중...'}
            </span>
          </div>
        </div>
      )}
      
      {/* Error State */}
      {error && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-red-200 rounded-lg shadow-lg p-4">
          <div className="text-center text-red-600">
            <div className="font-medium">검색 오류</div>
            <div className="text-sm mt-1">{error}</div>
          </div>
        </div>
      )}
    </div>
  );
}