#!/usr/bin/env python3
"""
Korean Stock Market Data - KOSPI & KOSDAQ Major Stocks
실제 한국 주식 시장의 주요 종목 데이터
"""

# KOSPI 주요 종목 (시가총액 기준 상위 종목들)
KOSPI_STOCKS = [
    # 대형주 (시가총액 10조원 이상)
    {"symbol": "005930", "name": "Samsung Electronics", "name_kr": "삼성전자", "sector": "반도체", "market_cap": 400000},
    {"symbol": "000660", "name": "SK Hynix", "name_kr": "SK하이닉스", "sector": "반도체", "market_cap": 80000},
    {"symbol": "207940", "name": "Samsung Biologics", "name_kr": "삼성바이오로직스", "sector": "바이오", "market_cap": 75000},
    {"symbol": "005935", "name": "Samsung Electronics Pfd", "name_kr": "삼성전자우", "sector": "반도체", "market_cap": 30000},
    {"symbol": "035420", "name": "NAVER", "name_kr": "NAVER", "sector": "인터넷", "market_cap": 45000},
    {"symbol": "005380", "name": "Hyundai Motor", "name_kr": "현대차", "sector": "자동차", "market_cap": 40000},
    {"symbol": "051910", "name": "LG Chem", "name_kr": "LG화학", "sector": "화학", "market_cap": 35000},
    {"symbol": "006400", "name": "Samsung SDI", "name_kr": "삼성SDI", "sector": "배터리", "market_cap": 30000},
    {"symbol": "035720", "name": "Kakao", "name_kr": "카카오", "sector": "인터넷", "market_cap": 25000},
    {"symbol": "055550", "name": "Shinhan Financial Group", "name_kr": "신한지주", "sector": "금융", "market_cap": 28000},
    
    # 중대형주 (시가총액 1조~10조원)
    {"symbol": "105560", "name": "KB Financial Group", "name_kr": "KB금융", "sector": "금융", "market_cap": 25000},
    {"symbol": "012330", "name": "Hyundai Mobis", "name_kr": "현대모비스", "sector": "자동차부품", "market_cap": 20000},
    {"symbol": "028260", "name": "Samsung C&T", "name_kr": "삼성물산", "sector": "건설", "market_cap": 18000},
    {"symbol": "066570", "name": "LG Electronics", "name_kr": "LG전자", "sector": "전자", "market_cap": 15000},
    {"symbol": "003670", "name": "POSCO Holdings", "name_kr": "포스코홀딩스", "sector": "철강", "market_cap": 22000},
    {"symbol": "096770", "name": "SK Innovation", "name_kr": "SK이노베이션", "sector": "정유", "market_cap": 12000},
    {"symbol": "017670", "name": "SK Telecom", "name_kr": "SK텔레콤", "sector": "통신", "market_cap": 14000},
    {"symbol": "030200", "name": "KT", "name_kr": "KT", "sector": "통신", "market_cap": 10000},
    {"symbol": "009150", "name": "Samsung Electro-Mechanics", "name_kr": "삼성전기", "sector": "전자부품", "market_cap": 12000},
    {"symbol": "018260", "name": "Samsung SDS", "name_kr": "삼성SDS", "sector": "IT서비스", "market_cap": 10000},
    
    # 대표 중형주
    {"symbol": "032830", "name": "Samsung Life Insurance", "name_kr": "삼성생명", "sector": "보험", "market_cap": 8000},
    {"symbol": "068270", "name": "Celltrion", "name_kr": "셀트리온", "sector": "바이오", "market_cap": 15000},
    {"symbol": "000270", "name": "Kia", "name_kr": "기아", "sector": "자동차", "market_cap": 30000},
    {"symbol": "323410", "name": "Kakao Bank", "name_kr": "카카오뱅크", "sector": "인터넷은행", "market_cap": 18000},
    {"symbol": "036570", "name": "NCsoft", "name_kr": "엔씨소프트", "sector": "게임", "market_cap": 12000},
    {"symbol": "251270", "name": "Netmarble", "name_kr": "넷마블", "sector": "게임", "market_cap": 8000},
    {"symbol": "015760", "name": "Korea Electric Power", "name_kr": "한국전력", "sector": "전력", "market_cap": 15000},
    {"symbol": "316140", "name": "Woori Financial Group", "name_kr": "우리금융지주", "sector": "금융", "market_cap": 10000},
    {"symbol": "024110", "name": "Industrial Bank of Korea", "name_kr": "기업은행", "sector": "은행", "market_cap": 8000},
    {"symbol": "011200", "name": "HMM", "name_kr": "HMM", "sector": "해운", "market_cap": 12000},
    
    # 기타 주요 종목
    {"symbol": "090430", "name": "Amorepacific", "name_kr": "아모레퍼시픽", "sector": "화장품", "market_cap": 6000},
    {"symbol": "161390", "name": "Hanwha Q CELLS", "name_kr": "한화큐셀", "sector": "태양광", "market_cap": 5000},
    {"symbol": "047050", "name": "POSCO International", "name_kr": "포스코인터내셔널", "sector": "상사", "market_cap": 4000},
    {"symbol": "000720", "name": "Hyundai Engineering & Construction", "name_kr": "현대건설", "sector": "건설", "market_cap": 5000},
    {"symbol": "034730", "name": "SK", "name_kr": "SK", "sector": "지주회사", "market_cap": 15000},
    {"symbol": "018880", "name": "Korean Air", "name_kr": "대한항공", "sector": "항공", "market_cap": 4000},
    {"symbol": "003550", "name": "LG", "name_kr": "LG", "sector": "지주회사", "market_cap": 8000},
    {"symbol": "001040", "name": "CJ", "name_kr": "CJ", "sector": "지주회사", "market_cap": 3000},
    {"symbol": "267250", "name": "HD Hyundai", "name_kr": "HD현대", "sector": "지주회사", "market_cap": 6000},
    {"symbol": "138040", "name": "Meritz Financial Group", "name_kr": "메리츠금융지주", "sector": "금융", "market_cap": 5000},
]

# KOSDAQ 주요 종목 (기술주 및 성장주 중심)
KOSDAQ_STOCKS = [
    # 대형 KOSDAQ (시가총액 1조원 이상)
    {"symbol": "091990", "name": "Celltrion Healthcare", "name_kr": "셀트리온헬스케어", "sector": "바이오", "market_cap": 8000},
    {"symbol": "196170", "name": "AlteogenInc", "name_kr": "알테오젠", "sector": "바이오", "market_cap": 5000},
    {"symbol": "039030", "name": "Ion Beam Applications", "name_kr": "이온빔", "sector": "의료기기", "market_cap": 3000},
    {"symbol": "058470", "name": "Richemont Korea", "name_kr": "리베스트", "sector": "패션", "market_cap": 2000},
    {"symbol": "214320", "name": "Fila Holdings", "name_kr": "휠라홀딩스", "sector": "의류", "market_cap": 4000},
    {"symbol": "041510", "name": "SM Entertainment", "name_kr": "SM", "sector": "엔터테인먼트", "market_cap": 3000},
    {"symbol": "122870", "name": "YG Entertainment", "name_kr": "YG엔터테인먼트", "sector": "엔터테인먼트", "market_cap": 2000},
    {"symbol": "035900", "name": "JYP Entertainment", "name_kr": "JYP Ent.", "sector": "엔터테인먼트", "market_cap": 2500},
    {"symbol": "293490", "name": "Kakao Games", "name_kr": "카카오게임즈", "sector": "게임", "market_cap": 4000},
    {"symbol": "112040", "name": "Krafton", "name_kr": "크래프톤", "sector": "게임", "market_cap": 15000},
    
    # 중형 KOSDAQ (IT, 바이오, 게임)
    {"symbol": "067310", "name": "HLB", "name_kr": "HLB", "sector": "바이오", "market_cap": 3000},
    {"symbol": "326030", "name": "SK Biopharmaceuticals", "name_kr": "SK바이오팜", "sector": "제약", "market_cap": 5000},
    {"symbol": "328130", "name": "Lunit", "name_kr": "루닛", "sector": "의료AI", "market_cap": 2000},
    {"symbol": "217270", "name": "Naver Webtoon", "name_kr": "네이버웹툰", "sector": "콘텐츠", "market_cap": 3000},
    {"symbol": "263750", "name": "Pearlabyss", "name_kr": "펄어비스", "sector": "게임", "market_cap": 2500},
    {"symbol": "194480", "name": "Devsisters", "name_kr": "데브시스터즈", "sector": "게임", "market_cap": 1500},
    {"symbol": "053800", "name": "Ansim", "name_kr": "안랩", "sector": "보안SW", "market_cap": 1000},
    {"symbol": "060280", "name": "Curocell", "name_kr": "큐로셀", "sector": "바이오", "market_cap": 1500},
    {"symbol": "214150", "name": "Classum", "name_kr": "클래썸", "sector": "교육", "market_cap": 800},
    {"symbol": "234920", "name": "Viva Republica", "name_kr": "비바리퍼블리카", "sector": "핀테크", "market_cap": 2000},
    
    # 성장주 (IT/바이오/신기술)
    {"symbol": "065350", "name": "Dada", "name_kr": "신성델타테크", "sector": "디스플레이", "market_cap": 800},
    {"symbol": "173130", "name": "Woongjin", "name_kr": "오스템임플란트", "sector": "의료기기", "market_cap": 1200},
    {"symbol": "078340", "name": "Globepoint", "name_kr": "컴투스", "sector": "게임", "market_cap": 1500},
    {"symbol": "095570", "name": "AJ Networks", "name_kr": "AJ네트웍스", "sector": "유통", "market_cap": 1000},
    {"symbol": "141080", "name": "LegoChem Biosciences", "name_kr": "레고켐바이오", "sector": "바이오", "market_cap": 1800},
    {"symbol": "950130", "name": "Lotte Rental", "name_kr": "엑세스바이오", "sector": "진단키트", "market_cap": 1000},
    {"symbol": "086520", "name": "Ecopro", "name_kr": "에코프로", "sector": "2차전지소재", "market_cap": 8000},
    {"symbol": "247540", "name": "Ecopro BM", "name_kr": "에코프로비엠", "sector": "2차전지소재", "market_cap": 12000},
    {"symbol": "450080", "name": "Ecopro HN", "name_kr": "에코프로에이치엔", "sector": "2차전지소재", "market_cap": 3000},
    {"symbol": "058610", "name": "AMC", "name_kr": "에이엠씨", "sector": "2차전지", "market_cap": 1500},
    
    # K-컬처 관련
    {"symbol": "180400", "name": "KOSDAQ China", "name_kr": "KOSDAQ차이나", "sector": "중국사업", "market_cap": 500},
    {"symbol": "048410", "name": "Worldon", "name_kr": "현대바이오", "sector": "바이오", "market_cap": 800},
    {"symbol": "290380", "name": "대한제당", "name_kr": "대한제당", "sector": "식품", "market_cap": 600},
    {"symbol": "131290", "name": "Sajo Daerim", "name_kr": "티에스인베스트먼트", "sector": "투자", "market_cap": 400},
]

def get_all_korean_stocks():
    """모든 한국 주식 데이터 반환"""
    all_stocks = []
    
    # KOSPI 종목 추가
    for stock in KOSPI_STOCKS:
        stock_data = {
            **stock,
            "market": "KOSPI",
            "current_price": _generate_realistic_price(stock["market_cap"]),
            "change": round((hash(stock["symbol"]) % 1000 - 500) / 100, 2)  # -5.00 ~ +4.99
        }
        all_stocks.append(stock_data)
    
    # KOSDAQ 종목 추가  
    for stock in KOSDAQ_STOCKS:
        stock_data = {
            **stock,
            "market": "KOSDAQ", 
            "current_price": _generate_realistic_price(stock["market_cap"]),
            "change": round((hash(stock["symbol"]) % 1200 - 600) / 100, 2)  # -6.00 ~ +5.99 (더 변동성 큼)
        }
        all_stocks.append(stock_data)
    
    return all_stocks

def _generate_realistic_price(market_cap_billion):
    """시가총액을 기반으로 현실적인 주가 생성"""
    import random
    
    if market_cap_billion >= 50000:  # 50조원 이상 (삼성전자급)
        return random.randint(65000, 85000)
    elif market_cap_billion >= 20000:  # 20조원 이상 (대형주)
        return random.randint(40000, 200000)
    elif market_cap_billion >= 10000:  # 10조원 이상 (중대형주)
        return random.randint(80000, 400000)
    elif market_cap_billion >= 5000:   # 5조원 이상 (중형주)
        return random.randint(50000, 300000)
    elif market_cap_billion >= 1000:   # 1조원 이상 (중소형주)
        return random.randint(10000, 150000)
    else:  # 1조원 미만 (소형주)
        return random.randint(5000, 50000)

def search_stocks(query, limit=20):
    """종목 검색 기능"""
    if not query:
        return []
    
    query = query.upper().strip()
    all_stocks = get_all_korean_stocks()
    results = []
    
    for stock in all_stocks:
        # 종목코드 매칭
        if query in stock["symbol"]:
            results.append(stock)
        # 한글명 매칭
        elif query.lower() in stock["name_kr"].lower():
            results.append(stock)
        # 영문명 매칭
        elif query.lower() in stock["name"].lower():
            results.append(stock)
        # 섹터 매칭
        elif query.lower() in stock["sector"].lower():
            results.append(stock)
            
        if len(results) >= limit:
            break
    
    return results

def get_stock_by_symbol(symbol):
    """종목코드로 특정 종목 조회"""
    all_stocks = get_all_korean_stocks()
    for stock in all_stocks:
        if stock["symbol"] == symbol:
            return stock
    return None

# 인기 검색어/추천 검색어
POPULAR_SEARCHES = [
    "삼성전자", "SK하이닉스", "NAVER", "카카오", "현대차",
    "LG화학", "셀트리온", "KB금융", "신한지주", "포스코",
    "게임", "바이오", "반도체", "자동차", "금융",
    "005930", "000660", "035420", "035720", "005380"
]

def get_popular_searches():
    """인기 검색어 반환"""
    return POPULAR_SEARCHES[:10]

if __name__ == "__main__":
    # 테스트 코드
    print("=== 한국 주식 데이터 테스트 ===")
    all_stocks = get_all_korean_stocks()
    print(f"총 종목 수: {len(all_stocks)}")
    print(f"KOSPI 종목 수: {len([s for s in all_stocks if s['market'] == 'KOSPI'])}")
    print(f"KOSDAQ 종목 수: {len([s for s in all_stocks if s['market'] == 'KOSDAQ'])}")
    
    print("\n=== 검색 테스트 ===")
    print("삼성 검색:", len(search_stocks("삼성")), "건")
    print("게임 검색:", len(search_stocks("게임")), "건")
    print("005930 검색:", len(search_stocks("005930")), "건")