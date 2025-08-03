
# 주식 종목 검색 기능 분석 및 개선 방안 보고서

## 1. 개요

본 문서는 현재 시스템의 주식 종목 검색 기능이 정상적으로 동작하지 않는 원인을 기술적으로 분석하고, 이에 대한 구체적인 해결 방안을 제시합니다. 현재 검색 기능은 초기 로딩 시간이 매우 길고, 특정 조건에서만 제한적으로 동작하거나 전혀 동작하지 않는 문제가 있습니다.

## 2. 현상 및 문제점 분석

### 2.1. 핵심 문제: 비효율적인 클라이언트 측 검색 구조

- **현상**: 프론트엔드의 `useStockSearch` Hook (`frontend/src/hooks/useStockSearch.ts`)은 애플리케이션 로딩 시, 백엔드의 `GET /api/v1/stocks?limit=10000` API를 호출하여 **최대 10,000개의 전체 주식 목록을 클라이언트로 한 번에 다운로드**합니다.
- **문제점**:
    1.  **초기 로딩 성능 저하**: 수만 개의 데이터를 클라이언트로 전송하고, 이를 기반으로 검색 인덱스를 생성하는 과정은 상당한 시간을 소요시킵니다. 이로 인해 사용자는 검색 기능을 사용하기까지 긴 로딩 시간을 경험하게 됩니다.
    2.  **과도한 메모리 사용**: 전체 데이터를 클라이언트 메모리에 상주시키는 방식은 사용자 기기에 큰 부담을 주며, 특히 모바일 환경이나 저사양 PC에서 심각한 성능 저하를 유발합니다.
    3.  **확장성 부재**: 주식 종목 수가 증가하거나 데이터가 복잡해질수록 성능 문제는 더욱 악화될 것입니다.

### 2.2. 서버 측 검색 API 미사용

- **현상**: 백엔드에는 `GET /search` (`backend/routers/market_data.py`)라는 효율적인 **서버 측 검색 API가 이미 구현되어 있습니다.** 이 API는 데이터베이스에서 직접 `ILIKE` 연산을 통해 검색을 수행하므로, 클라이언트에 불필요한 전체 데이터를 전송할 필요가 없습니다.
- **문제점**: 현재 프론트엔드 로직은 이 효율적인 서버 측 API를 전혀 활용하지 않고, `GET /stocks`를 통해 전체 데이터를 가져오는 비효율적인 방식을 고수하고 있습니다. 이는 명백한 설계 오류 또는 미완성된 구현으로 판단됩니다.

### 2.3. 백엔드 검색 로직의 기능적 한계

- **현상**: `DataService.search_stocks` (`backend/services/data_service.py`) 메소드는 데이터베이스의 `symbol`과 `name` 컬럼에 대해 단순 `ILIKE` 검색만 수행합니다.
- **문제점**:
    1.  **초성 검색 미지원**: UI의 플레이스홀더에는 'ㅅㅅㅈㅈ'와 같은 초성 검색이 예시로 제시되어 있으나, 실제 백엔드 로직은 이를 처리할 수 없습니다.
    2.  **고급 검색 기능 부재**: 오타 교정, 유사도 기반 검색, 검색어 자동 완성 등 사용자 편의성을 높일 수 있는 기능이 전무합니다.
    3.  **부적절한 Fallback 처리**: DB 검색 실패 시, `"삼성전자"`라는 특정 종목만 하드코딩하여 반환하는 로직은 실제 운영 환경에 적합하지 않습니다.

## 3. 해결 방안

### 3.1. 클라이언트 측 검색 로직 폐기 및 서버 측 API 연동 (권장)

**1. `useStockSearch` Hook 수정 (`frontend/src/hooks/useStockSearch.ts`)**:
   - 컴포넌트 초기화 시 `GET /stocks`를 호출하여 전체 데이터를 가져오는 로직을 **제거**합니다.
   - 사용자가 검색어를 입력할 때마다(Debounce 적용 후), 백엔드의 `GET /search?query={query}` API를 호출하여 검색 결과를 받아오도록 수정합니다.

   **수정 전 (의사 코드):**
   ```typescript
   useEffect(() => {
     // 전체 데이터를 가져와 클라이언트에서 검색 인덱스 생성 (문제 지점)
     fetchAllStocks().then(data => initializeSearchIndex(data));
   }, []);

   const executeSearch = (query) => {
     // 클라이언트 측 인덱스에서 검색
     const results = clientSearchIndex.search(query);
     setResults(results);
   };
   ```

   **수정 후 (의사 코드):**
   ```typescript
   const executeSearch = useCallback(debounce(async (searchQuery) => {
     if (!searchQuery.trim()) {
       setResults([]);
       return;
     }
     setIsLoading(true);
     try {
       // 서버 측 검색 API 호출
       const response = await fetch(`${API_BASE_URL}/api/v1/search?query=${searchQuery}&limit=20`);
       const data = await response.json();
       // 서버로부터 받은 결과로 상태 업데이트
       setResults(data.results);
     } catch (err) {
       setError('Search failed');
     } finally {
       setIsLoading(false);
     }
   }, 300), []); // 300ms Debounce 적용

   useEffect(() => {
     executeSearch(query);
   }, [query, executeSearch]);
   ```

**2. `StockSearch.tsx` 컴포넌트 단순화**:
   - `useStockSearch` Hook의 변경에 따라, `isInitialized`, `totalStocks` 등 클라이언트 측 인덱싱과 관련된 상태 및 로직을 제거하거나 수정합니다.

### 3.2. 백엔드 검색 기능 고도화

**1. 한글 초성 검색 기능 추가**:
   - 데이터베이스에 초성 검색을 위한 별도의 컬럼을 추가하거나, 검색 시점에 초성을 분리하여 쿼리하는 방식을 도입합니다. Python의 `jamo` 라이브러리를 활용할 수 있습니다.

   **예시 (`DataService.search_stocks`):**
   ```python
   from jamo import h2j, j2hcj

   def get_chosung(text):
       return "".join([j2hcj(h2j(char))[0] for char in text if '가' <= char <= '힣'])

   # ...
   chosung_query = get_chosung(query)
   db_results = self.db.query(StockInfo).filter(
       or_(
           StockInfo.name.ilike(f"%{query}%"),
           StockInfo.symbol.ilike(f"%{query}%"),
           StockInfo.chosung.ilike(f"%{chosung_query}%") # 초성 컬럼 검색
       )
   ).limit(limit).all()
   ```

**2. 검색 정확도 및 성능 개선**:
   - **Full-Text Search (FTS)**: PostgreSQL의 `tsvector`나 MySQL의 FTS 인덱스를 도입하여 더 빠르고 정확한 텍스트 검색을 구현합니다.
   - **검색 라이브러리 도입**: Elasticsearch 또는 OpenSearch와 같은 전문 검색 엔진을 도입하여 확장성 있고 고도화된 검색 기능을 제공하는 것을 장기적으로 고려할 수 있습니다.

**3. Fallback 로직 개선**:
   - 하드코딩된 값을 반환하는 대신, "검색 결과 없음"을 명확히 반환하도록 수정합니다.

## 4. 기대 효과

- **응답성 향상**: 사용자는 더 이상 전체 데이터가 로드될 때까지 기다릴 필요 없이, 즉시 검색 기능을 사용할 수 있습니다.
- **성능 및 안정성 개선**: 클라이언트의 메모리 부담을 제거하여 애플리케이션의 전반적인 성능과 안정성을 높입니다.
- **사용자 경험 향상**: 초성 검색 등 고도화된 검색 기능을 통해 사용자가 원하는 종목을 더 쉽고 빠르게 찾을 수 있게 됩니다.
- **확장성 확보**: 서버 기반 검색으로 전환함으로써, 데이터가 증가하더라도 안정적인 성능을 유지할 수 있는 확장 가능한 구조를 갖추게 됩니다.
