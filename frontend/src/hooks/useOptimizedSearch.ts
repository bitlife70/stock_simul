/**
 * Optimized Search Hook
 * Provides instant client-side search with performance monitoring
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { Stock } from '@/types';
import { searchIndex, type SearchResult, type SearchOptions } from '@/utils/search/search-index';

interface SearchMetrics {
  searchTime: number;
  resultCount: number;
  queryLength: number;
  indexSize: number;
  cacheHit: boolean;
}

interface UseOptimizedSearchProps {
  onStockSelect?: (stock: Stock) => void;
  maxResults?: number;
  minScore?: number;
  enableAnalytics?: boolean;
  cacheSize?: number;
}

interface SearchCache {
  query: string;
  results: SearchResult[];
  timestamp: number;
}

export function useOptimizedSearch({
  onStockSelect,
  maxResults = 10,
  minScore = 0.1,
  enableAnalytics = true,
  cacheSize = 100
}: UseOptimizedSearchProps = {}) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isIndexReady, setIsIndexReady] = useState(false);
  const [metrics, setMetrics] = useState<SearchMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // 검색 캐시
  const searchCache = useRef<Map<string, SearchCache>>(new Map());
  const metricsHistory = useRef<SearchMetrics[]>([]);
  
  // 디바운스 타이머
  const debounceTimer = useRef<NodeJS.Timeout>();
  
  // 인덱스 초기화
  useEffect(() => {
    initializeIndex();
  }, []);

  const initializeIndex = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // API에서 모든 주식 데이터 한번에 가져오기
      const response = await fetch('http://localhost:8002/api/v1/stocks?limit=1000');
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      const stocks: Stock[] = await response.json();
      
      // 인덱스 빌드
      searchIndex.buildIndex(stocks);
      setIsIndexReady(true);
      
      console.log('Search index initialized:', searchIndex.getIndexStats());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to initialize search';
      setError(errorMessage);
      console.error('Search index initialization failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const performSearch = useCallback((searchQuery: string) => {
    if (!isIndexReady || !searchQuery.trim()) {
      setResults([]);
      setMetrics(null);
      return;
    }

    const startTime = performance.now();
    const normalizedQuery = searchQuery.trim();
    
    // 캐시 확인
    let cacheHit = false;
    const cached = searchCache.current.get(normalizedQuery);
    if (cached && (Date.now() - cached.timestamp) < 60000) { // 1분 캐시
      setResults(cached.results);
      cacheHit = true;
    } else {
      // 새로운 검색 수행
      const searchOptions: SearchOptions = {
        maxResults,
        minScore,
        enableFuzzy: true,
        enableChosung: true,
        enableTypoCorrection: true
      };
      
      const searchResults = searchIndex.search(normalizedQuery, searchOptions);
      setResults(searchResults);
      
      // 캐시 저장
      if (searchCache.current.size >= cacheSize) {
        // LRU 캐시: 가장 오래된 항목 제거
        const oldestKey = searchCache.current.keys().next().value;
        searchCache.current.delete(oldestKey);
      }
      searchCache.current.set(normalizedQuery, {
        query: normalizedQuery,
        results: searchResults,
        timestamp: Date.now()
      });
    }
    
    const endTime = performance.now();
    const searchTime = endTime - startTime;
    
    // 성능 메트릭 수집
    if (enableAnalytics) {
      const newMetrics: SearchMetrics = {
        searchTime,
        resultCount: results.length,
        queryLength: normalizedQuery.length,
        indexSize: searchIndex.getIndexStats().totalStocks,
        cacheHit
      };
      
      setMetrics(newMetrics);
      metricsHistory.current.push(newMetrics);
      
      // 메트릭 히스토리 크기 제한
      if (metricsHistory.current.length > 1000) {
        metricsHistory.current.shift();
      }
      
      // 성능 경고
      if (searchTime > 50) {
        console.warn(`Slow search detected: ${searchTime.toFixed(2)}ms for query "${normalizedQuery}"`);
      }
    }
  }, [isIndexReady, maxResults, minScore, enableAnalytics, cacheSize]);

  // 디바운스된 검색
  const debouncedSearch = useCallback((searchQuery: string) => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    
    // 빈 쿼리는 즉시 처리
    if (!searchQuery.trim()) {
      performSearch(searchQuery);
      return;
    }
    
    // 1-2글자는 빠른 디바운스, 그 이상은 더 빠르게
    const debounceDelay = searchQuery.length <= 2 ? 150 : 50;
    
    debounceTimer.current = setTimeout(() => {
      performSearch(searchQuery);
    }, debounceDelay);
  }, [performSearch]);

  // 쿼리 변경 처리
  useEffect(() => {
    debouncedSearch(query);
    
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [query, debouncedSearch]);

  // 주식 선택 처리
  const selectStock = useCallback((stock: Stock) => {
    onStockSelect?.(stock);
    
    // 선택된 주식을 캐시에서 우선순위 높게
    const selectedQuery = query.trim();
    if (selectedQuery && searchCache.current.has(selectedQuery)) {
      const cached = searchCache.current.get(selectedQuery)!;
      searchCache.current.delete(selectedQuery);
      searchCache.current.set(selectedQuery, { ...cached, timestamp: Date.now() });
    }
  }, [onStockSelect, query]);

  // 캐시 클리어
  const clearCache = useCallback(() => {
    searchCache.current.clear();
    console.log('Search cache cleared');
  }, []);

  // 성능 통계
  const getPerformanceStats = useCallback(() => {
    if (metricsHistory.current.length === 0) return null;
    
    const history = metricsHistory.current;
    const recentHistory = history.slice(-100); // 최근 100개 검색
    
    return {
      totalSearches: history.length,
      averageSearchTime: recentHistory.reduce((sum, m) => sum + m.searchTime, 0) / recentHistory.length,
      maxSearchTime: Math.max(...recentHistory.map(m => m.searchTime)),
      minSearchTime: Math.min(...recentHistory.map(m => m.searchTime)),
      cacheHitRate: recentHistory.filter(m => m.cacheHit).length / recentHistory.length,
      averageResultCount: recentHistory.reduce((sum, m) => sum + m.resultCount, 0) / recentHistory.length,
      indexStats: searchIndex.getIndexStats()
    };
  }, []);

  // 인덱스 재구성
  const rebuildIndex = useCallback(() => {
    setIsIndexReady(false);
    clearCache();
    initializeIndex();
  }, []);

  return {
    // 상태
    query,
    results,
    isLoading,
    isIndexReady,
    error,
    metrics,
    
    // 액션
    setQuery,
    selectStock,
    clearCache,
    rebuildIndex,
    
    // 분석
    getPerformanceStats,
    
    // 유틸리티
    highlightMatch: (text: string, highlights: Array<{ start: number; end: number }>) => {
      if (!highlights.length) return text;
      
      let result = '';
      let lastIndex = 0;
      
      for (const { start, end } of highlights.sort((a, b) => a.start - b.start)) {
        result += text.slice(lastIndex, start);
        result += `<mark class="bg-yellow-200 text-yellow-900 px-1 rounded">${text.slice(start, end)}</mark>`;
        lastIndex = end;
      }
      
      result += text.slice(lastIndex);
      return result;
    }
  };
}