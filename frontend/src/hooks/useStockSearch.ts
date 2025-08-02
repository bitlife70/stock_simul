import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import type { Stock } from '@/types';
import { stockSearchIndex, SearchIndex } from '@/lib/search-index';
import { API_BASE_URL } from '@/lib/config';

interface SearchResult {
  stock: Stock;
  score: number;
  matchType: 'exact' | 'starts_with' | 'contains' | 'chosung' | 'fuzzy';
  matchedText: string;
  highlightIndices: number[];
}

interface UseStockSearchOptions {
  maxResults?: number;
  fuzzyThreshold?: number;
  enableHistory?: boolean;
  enableSuggestions?: boolean;
  debounceMs?: number;
}

interface UseStockSearchReturn {
  // Search state
  query: string;
  setQuery: (query: string) => void;
  results: SearchResult[];
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  
  // Search control
  executeSearch: (searchQuery: string) => void;
  clearSearch: () => void;
  
  // Enhanced features
  suggestions: string[];
  searchHistory: string[];
  popularStocks: Stock[];
  
  // Performance metrics
  searchTime: number;
  totalStocks: number;
  
  // Utility functions
  getHighlightInfo: (text: string, indices: number[]) => {
    before: string;
    match: string;
    after: string;
  };
  addToHistory: (query: string) => void;
  clearHistory: () => void;
}

const RECENT_SEARCHES_KEY = 'stockSearch_recentSearches';
const MAX_HISTORY_SIZE = 10;

export const useStockSearch = (options: UseStockSearchOptions = {}): UseStockSearchReturn => {
  const {
    maxResults = 15,
    fuzzyThreshold = 0.7,
    enableHistory = true,
    enableSuggestions = true,
    debounceMs = 0 // No debounce for instant search
  } = options;

  // State management
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [popularStocks, setPopularStocks] = useState<Stock[]>([]);
  const [searchTime, setSearchTime] = useState(0);
  const [totalStocks, setTotalStocks] = useState(0);

  // Refs for performance optimization
  const debounceTimerRef = useRef<NodeJS.Timeout>();
  const searchCountRef = useRef(0);

  // Initialize search index
  useEffect(() => {
    let isMounted = true;

    const initializeSearch = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch stock data from API
        console.time('Stock data fetch');
        const response = await fetch(`${API_BASE_URL}/api/v1/stocks?limit=10000`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch stocks: ${response.statusText}`);
        }

        const stockData = await response.json();
        console.timeEnd('Stock data fetch');

        if (isMounted) {
          // Initialize search index
          await stockSearchIndex.initialize(stockData);
          
          // Get popular stocks and stats
          const popular = stockSearchIndex.getPopularStocks();
          const stats = stockSearchIndex.getStats();
          
          setPopularStocks(popular);
          setTotalStocks(stats.totalStocks);
          setIsInitialized(true);
          
          console.log(`Search initialized with ${stats.totalStocks} stocks`);
        }
      } catch (err) {
        console.error('Failed to initialize stock search:', err);
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to initialize search');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    initializeSearch();

    return () => {
      isMounted = false;
    };
  }, []);

  // Load search history from localStorage
  useEffect(() => {
    if (enableHistory) {
      try {
        const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          setSearchHistory(Array.isArray(parsed) ? parsed : []);
        }
      } catch (err) {
        console.warn('Failed to load search history:', err);
      }
    }
  }, [enableHistory]);

  // Execute search function
  const executeSearch = useCallback((searchQuery: string) => {
    if (!isInitialized || !searchQuery.trim()) {
      setResults([]);
      setSuggestions([]);
      setSearchTime(0);
      return;
    }

    const startTime = performance.now();
    searchCountRef.current += 1;
    const searchId = searchCountRef.current;

    try {
      // Perform lightning-fast search
      const searchResults = stockSearchIndex.search(searchQuery, {
        maxResults,
        fuzzyThreshold
      });

      // Get suggestions if enabled
      let searchSuggestions: string[] = [];
      if (enableSuggestions && searchQuery.length > 0) {
        searchSuggestions = stockSearchIndex.getSuggestions(searchQuery, 5);
      }

      const endTime = performance.now();
      const duration = Math.round((endTime - startTime) * 100) / 100;

      // Only update if this is the most recent search
      if (searchId === searchCountRef.current) {
        setResults(searchResults);
        setSuggestions(searchSuggestions);
        setSearchTime(duration);
        setError(null);
      }

    } catch (err) {
      console.error('Search execution failed:', err);
      if (searchId === searchCountRef.current) {
        setError(err instanceof Error ? err.message : 'Search failed');
        setResults([]);
        setSuggestions([]);
      }
    }
  }, [isInitialized, maxResults, fuzzyThreshold, enableSuggestions]);

  // Handle query changes with optional debouncing
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (debounceMs > 0) {
      debounceTimerRef.current = setTimeout(() => {
        executeSearch(query);
      }, debounceMs);
    } else {
      executeSearch(query);
    }

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, executeSearch, debounceMs]);

  // Clear search function
  const clearSearch = useCallback(() => {
    setQuery('');
    setResults([]);
    setSuggestions([]);
    setSearchTime(0);
    setError(null);
  }, []);

  // Add to search history
  const addToHistory = useCallback((searchQuery: string) => {
    if (!enableHistory || !searchQuery.trim()) return;

    const trimmedQuery = searchQuery.trim();
    
    setSearchHistory(prev => {
      const filtered = prev.filter(item => item !== trimmedQuery);
      const updated = [trimmedQuery, ...filtered].slice(0, MAX_HISTORY_SIZE);
      
      try {
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
      } catch (err) {
        console.warn('Failed to save search history:', err);
      }
      
      return updated;
    });
  }, [enableHistory]);

  // Clear search history
  const clearHistory = useCallback(() => {
    setSearchHistory([]);
    try {
      localStorage.removeItem(RECENT_SEARCHES_KEY);
    } catch (err) {
      console.warn('Failed to clear search history:', err);
    }
  }, []);

  // Get highlight information for displaying search results
  const getHighlightInfo = useCallback((text: string, indices: number[]) => {
    if (!indices || indices.length < 2) {
      return { before: text, match: '', after: '' };
    }

    const [start, end] = indices;
    const before = text.substring(0, start);
    const match = text.substring(start, end + 1);
    const after = text.substring(end + 1);

    return { before, match, after };
  }, []);

  // Memoized return object for performance
  const returnValue = useMemo((): UseStockSearchReturn => ({
    // Search state
    query,
    setQuery,
    results,
    isLoading,
    isInitialized,
    error,
    
    // Search control
    executeSearch,
    clearSearch,
    
    // Enhanced features
    suggestions,
    searchHistory,
    popularStocks,
    
    // Performance metrics
    searchTime,
    totalStocks,
    
    // Utility functions
    getHighlightInfo,
    addToHistory,
    clearHistory
  }), [
    query,
    results,
    isLoading,
    isInitialized,
    error,
    executeSearch,
    clearSearch,
    suggestions,
    searchHistory,
    popularStocks,
    searchTime,
    totalStocks,
    getHighlightInfo,
    addToHistory,
    clearHistory
  ]);

  return returnValue;
};

// Hook for getting search statistics and debugging info
export const useStockSearchStats = () => {
  const [stats, setStats] = useState({
    totalStocks: 0,
    sectorCount: 0,
    popularStocks: 0,
    initialized: false
  });

  useEffect(() => {
    const updateStats = () => {
      setStats(stockSearchIndex.getStats());
    };

    // Update stats periodically
    const interval = setInterval(updateStats, 5000);
    updateStats(); // Initial update

    return () => clearInterval(interval);
  }, []);

  return stats;
};

// Export types for external use
export type { SearchResult, UseStockSearchOptions, UseStockSearchReturn };