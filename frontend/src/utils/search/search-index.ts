/**
 * Advanced Client-Side Search Index
 * Provides instant search with Korean character support, fuzzy matching, and weighted results
 */

import type { Stock } from '@/types';
import {
  extractChosung,
  matchesChosung,
  normalizeKoreanText,
  koreanSimilarity,
  correctKoreanTypo,
  correctEnglishTypo,
  isKoreanConsonant
} from './korean-utils';

export interface SearchableStock {
  stock: Stock;
  searchTerms: {
    symbol: string;
    nameKr: string;
    nameEn: string;
    chosungKr: string;
    sector: string;
    normalizedKr: string;
    normalizedEn: string;
  };
  weights: {
    symbol: number;
    nameKr: number;
    nameEn: number;
    sector: number;
    marketCap: number;
  };
}

export interface SearchResult {
  stock: Stock;
  score: number;
  matchType: 'exact' | 'prefix' | 'chosung' | 'fuzzy' | 'sector';
  matchedField: 'symbol' | 'nameKr' | 'nameEn' | 'sector';
  highlightRanges: Array<{ start: number; end: number; field: string }>;
}

export interface SearchOptions {
  maxResults?: number;
  minScore?: number;
  enableFuzzy?: boolean;
  enableChosung?: boolean;
  enableTypoCorrection?: boolean;
  weights?: {
    exactMatch?: number;
    prefixMatch?: number;
    chosungMatch?: number;
    fuzzyMatch?: number;
    sectorMatch?: number;
  };
}

export class StockSearchIndex {
  private searchableStocks: SearchableStock[] = [];
  private symbolIndex: Map<string, SearchableStock> = new Map();
  private prefixTrie: TrieNode = new TrieNode();
  private chosungIndex: Map<string, SearchableStock[]> = new Map();
  private sectorIndex: Map<string, SearchableStock[]> = new Map();
  
  private defaultOptions: Required<SearchOptions> = {
    maxResults: 10,
    minScore: 0.1,
    enableFuzzy: true,
    enableChosung: true,
    enableTypoCorrection: true,
    weights: {
      exactMatch: 1.0,
      prefixMatch: 0.8,
      chosungMatch: 0.6,
      fuzzyMatch: 0.4,
      sectorMatch: 0.3
    }
  };

  /**
   * 주식 데이터로 검색 인덱스 초기화
   */
  buildIndex(stocks: Stock[]): void {
    console.time('Building search index');
    
    this.searchableStocks = stocks.map(stock => this.createSearchableStock(stock));
    this.buildSymbolIndex();
    this.buildPrefixTrie();
    this.buildChosungIndex();
    this.buildSectorIndex();
    
    console.timeEnd('Building search index');
    console.log(`Search index built for ${stocks.length} stocks`);
    console.log(`Memory usage estimate: ${this.getMemoryUsageEstimate()} MB`);
  }

  /**
   * 메인 검색 함수
   */
  search(query: string, options: SearchOptions = {}): SearchResult[] {
    const startTime = performance.now();
    const opts = { ...this.defaultOptions, ...options };
    
    if (!query || query.trim().length === 0) {
      return [];
    }

    const normalizedQuery = query.trim();
    const results = new Map<string, SearchResult>();

    // 1. 심볼 정확 매칭 (최고 우선순위)
    this.addExactSymbolMatches(normalizedQuery, results, opts);

    // 2. 한글명 정확 매칭
    this.addExactNameMatches(normalizedQuery, results, opts);

    // 3. 접두사 매칭
    this.addPrefixMatches(normalizedQuery, results, opts);

    // 4. 초성 검색 (한글 자음 입력 시)
    if (opts.enableChosung && this.isChosungQuery(normalizedQuery)) {
      this.addChosungMatches(normalizedQuery, results, opts);
    }

    // 5. 섹터 매칭
    this.addSectorMatches(normalizedQuery, results, opts);

    // 6. 퍼지 매칭 (오타 교정 포함)
    if (opts.enableFuzzy) {
      this.addFuzzyMatches(normalizedQuery, results, opts);
    }

    // 7. 자판 오타 교정 후 재시도
    if (opts.enableTypoCorrection) {
      this.addTypoCorrectedMatches(normalizedQuery, results, opts);
    }

    // 결과 정렬 및 필터링
    const sortedResults = Array.from(results.values())
      .filter(result => result.score >= opts.minScore)
      .sort((a, b) => {
        // 스코어 우선, 시가총액 보조
        if (Math.abs(a.score - b.score) > 0.01) {
          return b.score - a.score;
        }
        return (b.stock.market_cap || 0) - (a.stock.market_cap || 0);
      })
      .slice(0, opts.maxResults);

    const endTime = performance.now();
    console.log(`Search completed in ${(endTime - startTime).toFixed(2)}ms for query: "${query}"`);
    
    return sortedResults;
  }

  private createSearchableStock(stock: Stock): SearchableStock {
    const chosungKr = extractChosung(stock.name_kr);
    const normalizedKr = normalizeKoreanText(stock.name_kr);
    const normalizedEn = stock.name.toLowerCase().replace(/\s+/g, '');

    return {
      stock,
      searchTerms: {
        symbol: stock.symbol.toUpperCase(),
        nameKr: stock.name_kr,
        nameEn: stock.name,
        chosungKr,
        sector: stock.sector || '',
        normalizedKr,
        normalizedEn
      },
      weights: {
        symbol: 1.0,
        nameKr: 0.9,
        nameEn: 0.7,
        sector: 0.5,
        marketCap: Math.log10((stock.market_cap || 1000) / 1000) / 10 // 시가총액 가중치
      }
    };
  }

  private buildSymbolIndex(): void {
    for (const searchableStock of this.searchableStocks) {
      this.symbolIndex.set(searchableStock.searchTerms.symbol, searchableStock);
    }
  }

  private buildPrefixTrie(): void {
    for (const searchableStock of this.searchableStocks) {
      // 심볼 prefix
      this.insertIntoTrie(searchableStock.searchTerms.symbol, searchableStock);
      // 한글명 prefix
      this.insertIntoTrie(searchableStock.searchTerms.normalizedKr, searchableStock);
      // 영문명 prefix
      this.insertIntoTrie(searchableStock.searchTerms.normalizedEn, searchableStock);
    }
  }

  private buildChosungIndex(): void {
    for (const searchableStock of this.searchableStocks) {
      const chosung = searchableStock.searchTerms.chosungKr;
      if (!this.chosungIndex.has(chosung)) {
        this.chosungIndex.set(chosung, []);
      }
      this.chosungIndex.get(chosung)!.push(searchableStock);
    }
  }

  private buildSectorIndex(): void {
    for (const searchableStock of this.searchableStocks) {
      const sector = searchableStock.searchTerms.sector;
      if (sector) {
        if (!this.sectorIndex.has(sector)) {
          this.sectorIndex.set(sector, []);
        }
        this.sectorIndex.get(sector)!.push(searchableStock);
      }
    }
  }

  private insertIntoTrie(word: string, stock: SearchableStock): void {
    let node = this.prefixTrie;
    for (const char of word.toLowerCase()) {
      if (!node.children.has(char)) {
        node.children.set(char, new TrieNode());
      }
      node = node.children.get(char)!;
      node.stocks.push(stock);
    }
  }

  private addExactSymbolMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    const upperQuery = query.toUpperCase();
    const stock = this.symbolIndex.get(upperQuery);
    
    if (stock) {
      const score = opts.weights.exactMatch * stock.weights.symbol;
      results.set(stock.stock.symbol, {
        stock: stock.stock,
        score,
        matchType: 'exact',
        matchedField: 'symbol',
        highlightRanges: [{ start: 0, end: stock.stock.symbol.length, field: 'symbol' }]
      });
    }
  }

  private addExactNameMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    const normalizedQuery = normalizeKoreanText(query);
    
    for (const stock of this.searchableStocks) {
      // 한글명 정확 매칭
      if (stock.searchTerms.normalizedKr === normalizedQuery) {
        const score = opts.weights.exactMatch * stock.weights.nameKr;
        if (!results.has(stock.stock.symbol) || results.get(stock.stock.symbol)!.score < score) {
          results.set(stock.stock.symbol, {
            stock: stock.stock,
            score,
            matchType: 'exact',
            matchedField: 'nameKr',
            highlightRanges: [{ start: 0, end: stock.stock.name_kr.length, field: 'nameKr' }]
          });
        }
      }
      
      // 영문명 정확 매칭
      if (stock.searchTerms.normalizedEn === query.toLowerCase().replace(/\s+/g, '')) {
        const score = opts.weights.exactMatch * stock.weights.nameEn;
        if (!results.has(stock.stock.symbol) || results.get(stock.stock.symbol)!.score < score) {
          results.set(stock.stock.symbol, {
            stock: stock.stock,
            score,
            matchType: 'exact',
            matchedField: 'nameEn',
            highlightRanges: [{ start: 0, end: stock.stock.name.length, field: 'nameEn' }]
          });
        }
      }
    }
  }

  private addPrefixMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    const matches = this.findPrefixMatches(query.toLowerCase());
    
    for (const stock of matches) {
      if (!results.has(stock.stock.symbol)) {
        const score = opts.weights.prefixMatch * stock.weights.nameKr * (1 + stock.weights.marketCap);
        results.set(stock.stock.symbol, {
          stock: stock.stock,
          score,
          matchType: 'prefix',
          matchedField: 'nameKr',
          highlightRanges: [{ start: 0, end: query.length, field: 'nameKr' }]
        });
      }
    }
  }

  private addChosungMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    for (const stock of this.searchableStocks) {
      if (matchesChosung(stock.searchTerms.nameKr, query)) {
        if (!results.has(stock.stock.symbol)) {
          const score = opts.weights.chosungMatch * stock.weights.nameKr * (1 + stock.weights.marketCap);
          results.set(stock.stock.symbol, {
            stock: stock.stock,
            score,
            matchType: 'chosung',
            matchedField: 'nameKr',
            highlightRanges: this.getChosungHighlights(stock.searchTerms.nameKr, query)
          });
        }
      }
    }
  }

  private addSectorMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    for (const [sector, stocks] of this.sectorIndex) {
      if (sector.includes(query) || normalizeKoreanText(sector).includes(normalizeKoreanText(query))) {
        for (const stock of stocks) {
          if (!results.has(stock.stock.symbol)) {
            const score = opts.weights.sectorMatch * stock.weights.sector * (1 + stock.weights.marketCap);
            results.set(stock.stock.symbol, {
              stock: stock.stock,
              score,
              matchType: 'sector',
              matchedField: 'sector',
              highlightRanges: [{ start: 0, end: sector.length, field: 'sector' }]
            });
          }
        }
      }
    }
  }

  private addFuzzyMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    const normalizedQuery = normalizeKoreanText(query);
    
    for (const stock of this.searchableStocks) {
      if (!results.has(stock.stock.symbol)) {
        const similarity = koreanSimilarity(stock.searchTerms.normalizedKr, normalizedQuery);
        
        if (similarity > 0.6) { // 60% 이상 유사도
          const score = opts.weights.fuzzyMatch * similarity * stock.weights.nameKr * (1 + stock.weights.marketCap);
          results.set(stock.stock.symbol, {
            stock: stock.stock,
            score,
            matchType: 'fuzzy',
            matchedField: 'nameKr',
            highlightRanges: []
          });
        }
      }
    }
  }

  private addTypoCorrectedMatches(query: string, results: Map<string, SearchResult>, opts: Required<SearchOptions>): void {
    const correctedKorean = correctKoreanTypo(query);
    const correctedEnglish = correctEnglishTypo(query);
    
    if (correctedKorean !== query) {
      const correctedResults = this.search(correctedKorean, { ...opts, enableTypoCorrection: false });
      for (const result of correctedResults) {
        if (!results.has(result.stock.symbol)) {
          results.set(result.stock.symbol, {
            ...result,
            score: result.score * 0.8 // 오타 교정 결과는 점수 감점
          });
        }
      }
    }
    
    if (correctedEnglish !== query) {
      const correctedResults = this.search(correctedEnglish, { ...opts, enableTypoCorrection: false });
      for (const result of correctedResults) {
        if (!results.has(result.stock.symbol)) {
          results.set(result.stock.symbol, {
            ...result,
            score: result.score * 0.8
          });
        }
      }
    }
  }

  private findPrefixMatches(prefix: string): SearchableStock[] {
    let node = this.prefixTrie;
    
    for (const char of prefix) {
      if (!node.children.has(char)) {
        return [];
      }
      node = node.children.get(char)!;
    }
    
    return Array.from(new Set(node.stocks)); // 중복 제거
  }

  private isChosungQuery(query: string): boolean {
    return query.split('').every(char => isKoreanConsonant(char) || /\s/.test(char));
  }

  private getChosungHighlights(text: string, chosungQuery: string): Array<{ start: number; end: number; field: string }> {
    // 초성 매칭 위치 찾기 (실제 구현에서는 더 정교한 로직 필요)
    const highlights: Array<{ start: number; end: number; field: string }> = [];
    const textChosung = extractChosung(text);
    let queryIndex = 0;
    
    for (let i = 0; i < text.length && queryIndex < chosungQuery.length; i++) {
      if (textChosung[i] === chosungQuery[queryIndex]) {
        highlights.push({ start: i, end: i + 1, field: 'nameKr' });
        queryIndex++;
      }
    }
    
    return highlights;
  }

  /**
   * 메모리 사용량 추정 (MB)
   */
  private getMemoryUsageEstimate(): number {
    const stocksSize = this.searchableStocks.length * 500; // 주식당 약 500바이트
    const indexesSize = (this.symbolIndex.size + this.chosungIndex.size + this.sectorIndex.size) * 100;
    const trieSize = this.estimateTrieSize(this.prefixTrie) * 50;
    
    return (stocksSize + indexesSize + trieSize) / (1024 * 1024);
  }

  private estimateTrieSize(node: TrieNode): number {
    let size = 1;
    for (const child of node.children.values()) {
      size += this.estimateTrieSize(child);
    }
    return size;
  }

  /**
   * 인덱스 상태 정보
   */
  getIndexStats() {
    return {
      totalStocks: this.searchableStocks.length,
      symbolIndexSize: this.symbolIndex.size,
      chosungIndexSize: this.chosungIndex.size,
      sectorIndexSize: this.sectorIndex.size,
      memoryUsageMB: this.getMemoryUsageEstimate()
    };
  }
}

/**
 * Trie 노드 클래스
 */
class TrieNode {
  children: Map<string, TrieNode> = new Map();
  stocks: SearchableStock[] = [];
}

// 싱글톤 인스턴스
export const searchIndex = new StockSearchIndex();