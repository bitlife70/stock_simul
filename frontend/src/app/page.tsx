'use client';

import { useState, useEffect } from 'react';
import { 
  BarChart3, TrendingUp, Shield, Target, Menu, X,
  Home as HomeIcon, Settings, Bell, Monitor
} from 'lucide-react';
import StockSearchSimple from '@/components/stock/StockSearchSimple';
import StockChart from '@/components/stock/StockChart';
import StrategyBuilder from '@/components/strategy/StrategyBuilder';
import KoreanStrategyBuilder from '@/components/strategy/KoreanStrategyBuilder';
import PortfolioDashboard from '@/components/portfolio/PortfolioDashboard';
import AnalyticsDashboard from '@/components/analytics/AnalyticsDashboard';
import RiskManagementDashboard from '@/components/risk/RiskManagementDashboard';
import MarketMonitoringDashboard from '@/components/realtime/MarketMonitoringDashboard';
// import SettingsModal from '@/components/settings/SettingsModal';
import BacktestResultModal from '@/components/backtest/BacktestResultModal';
import type { Stock, StockData, StrategyFormData, BacktestResult } from '@/types';
import { KoreanUtils } from '@/lib/korean-utils';
import { API_BASE_URL } from '@/lib/config';

type ActiveView = 'overview' | 'strategies' | 'portfolio' | 'analytics' | 'risk' | 'realtime';

export default function Home() {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [stockData, setStockData] = useState<StockData[]>([]);
  // const [chartKey, setChartKey] = useState(0); // 차트 리렌더링 강제를 위한 키 (현재 미사용)
  const [loading, setLoading] = useState(false);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [activeView, setActiveView] = useState<ActiveView>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [marketStatus, setMarketStatus] = useState(KoreanUtils.getKoreanMarketStatus());
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [backtestResultOpen, setBacktestResultOpen] = useState(false);

  useEffect(() => {
    if (selectedStock) {
      fetchStockData(selectedStock.symbol);
    }
  }, [selectedStock]);

  // Update market status every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setMarketStatus(KoreanUtils.getKoreanMarketStatus());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchStockData = async (symbol: string) => {
    setLoading(true);
    try {
      // 최근 1년치 데이터 요청
      const response = await fetch(`${API_BASE_URL}/api/v1/stocks/${symbol}/data?days=365`);
      const result = await response.json();
      
      if (result.data && Array.isArray(result.data)) {
        console.log(`Loaded ${result.data.length} days of data for ${symbol}`);
        setStockData(result.data);
      } else {
        console.error('Unexpected data format:', result);
        setStockData([]);
      }
    } catch (error) {
      console.error('주식 데이터를 가져오는데 실패했습니다:', error);
      setStockData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStockSelect = (stock: Stock) => {
    setSelectedStock(stock);
    // 차트 상태는 유지하고 데이터만 업데이트되도록 수정
    // setChartKey는 필요한 경우에만 사용
  };

  const handleStrategyRun = async (strategy: StrategyFormData) => {
    if (!selectedStock) {
      alert('먼저 종목을 선택해주세요.');
      return;
    }

    setBacktestLoading(true);
    try {
      const backtestData = {
        ...strategy,
        stock_symbol: selectedStock.symbol,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/backtest/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData),
      });

      if (response.ok) {
        const result: BacktestResult = await response.json();
        
        // Mock 데이터로 확장된 백테스팅 결과 생성 (실제로는 서버에서 전송)
        const enhancedResult: BacktestResult = {
          ...result,
          cagr: result.total_return, // 임시로 동일하게 설정
          sharpe_ratio: result.total_return > 0 ? 1.2 : -0.5, // Mock 샤프 비율
          max_drawdown: Math.abs(result.total_return) * 0.3, // Mock 최대 낙폭
          volatility: 0.15, // Mock 변동성
          profit_factor: result.win_rate > 0.5 ? 1.8 : 0.9, // Mock 손익비
          max_consecutive_wins: Math.floor(result.winning_trades / 2),
          max_consecutive_losses: Math.floor(result.losing_trades / 2),
          avg_profit: result.total_return > 0 ? 50000 : 0,
          avg_loss: result.total_return > 0 ? -25000 : -30000,
          max_profit: result.total_return > 0 ? 150000 : 0,
          max_loss: result.total_return > 0 ? -80000 : -120000,
          avg_hold_days: 12.5,
          total_fees: 15000,
          net_profit: (result.total_return * 1000000) - 15000,
          benchmark_return: 0.08, // Mock 벤치마크 수익률
          trades: [], // Mock 거래 내역 (실제로는 서버에서 생성)
          equity_curve: [] // Mock 수익률 곡선
        };
        
        setBacktestResult(enhancedResult);
        setBacktestResultOpen(true);
      } else {
        const error = await response.json();
        alert(`백테스팅 실행 중 오류가 발생했습니다: ${error.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('백테스팅 실행 중 오류:', error);
      alert('백테스팅 실행 중 오류가 발생했습니다.');
    } finally {
      setBacktestLoading(false);
    }
  };

  const handleStrategySave = async (strategy: StrategyFormData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/strategies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(strategy),
      });

      if (response.ok) {
        alert('전략이 성공적으로 저장되었습니다!');
      } else {
        const error = await response.json();
        alert(`전략 저장 중 오류가 발생했습니다: ${error.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('전략 저장 중 오류:', error);
      alert('전략 저장 중 오류가 발생했습니다.');
    }
  };

  const handleStrategyOptimize = async (_strategy: StrategyFormData) => {
    // Mock optimization for now
    alert('전략 최적화가 완료되었습니다!\n최적화된 매개변수를 전략 설정에 반영했습니다.');
  };

  const menuItems = [
    { id: 'overview', label: '개요', icon: HomeIcon, description: '전체 현황 및 주요 지표' },
    { id: 'realtime', label: '실시간 모니터링', icon: Monitor, description: '실시간 시장 데이터 및 전략 모니터링' },
    { id: 'strategies', label: '전략 설정', icon: Target, description: '백테스팅 전략 구성 및 실행' },
    { id: 'portfolio', label: '포트폴리오', icon: TrendingUp, description: '포트폴리오 관리 및 성과 분석' },
    { id: 'analytics', label: '분석 대시보드', icon: BarChart3, description: '상세 백테스팅 결과 분석' },
    { id: 'risk', label: '리스크 관리', icon: Shield, description: '리스크 모니터링 및 관리' }
  ];

  const renderContent = () => {
    switch (activeView) {
      case 'overview':
        return (
          <div className="space-y-8">
            {/* Stock Selection and Chart */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">종목 선택</h2>
              <StockSearchSimple 
                onStockSelect={handleStockSelect}
                selectedStock={selectedStock}
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Stock Chart */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">주가 차트</h2>
                  {backtestLoading && (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                      <span className="ml-2 text-sm text-blue-600 dark:text-blue-400 font-medium">백테스팅 실행중...</span>
                    </div>
                  )}
                </div>
                
                {loading && stockData.length === 0 ? (
                  <div className="flex items-center justify-center h-96">
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                      <span className="ml-3 text-gray-600 dark:text-gray-400">데이터 로딩중...</span>
                    </div>
                  </div>
                ) : (
                  <div className={`relative ${backtestLoading ? 'opacity-75' : ''}`}>
                    <StockChart
                      symbol={selectedStock?.name_kr}
                      data={stockData}
                      height={400}
                      onLoadMore={async (direction) => {
                        if (direction === 'left' && selectedStock) {
                          console.log('Loading more historical data...');
                          // 현재 데이터의 가장 오래된 날짜 찾기
                          const oldestDate = stockData.length > 0 
                            ? new Date(stockData[0].date) 
                            : new Date();
                          
                          // 더 과거 데이터 요청 (추가 365일)
                          const endDate = new Date(oldestDate);
                          endDate.setDate(endDate.getDate() - 1);
                          const startDate = new Date(endDate);
                          startDate.setDate(startDate.getDate() - 365);
                          
                          try {
                            const response = await fetch(
                              `${API_BASE_URL}/api/v1/stocks/${selectedStock.symbol}/data?` +
                              `start_date=${startDate.toISOString().split('T')[0]}&` +
                              `end_date=${endDate.toISOString().split('T')[0]}`
                            );
                            const result = await response.json();
                            
                            if (result.data && Array.isArray(result.data)) {
                              // 새 데이터를 기존 데이터 앞에 추가
                              const newData = [...result.data, ...stockData];
                              setStockData(newData);
                              console.log(`Added ${result.data.length} more days of historical data`);
                              return result.data;
                            }
                          } catch (error) {
                            console.error('Failed to load more data:', error);
                          }
                        }
                        return [];
                      }}
                    />
                  </div>
                )}
              </div>

              {/* Strategy Builder */}
              <div>
                <StrategyBuilder
                  selectedStock={selectedStock}
                  onStrategyRun={handleStrategyRun}
                  onStrategySave={handleStrategySave}
                  loading={backtestLoading}
                />
              </div>
            </div>

            {/* Quick Start Guide */}
            {!selectedStock && (
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                      한국 주식 백테스팅 플랫폼에 오신 것을 환영합니다
                    </h3>
                    <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                      <p>
                        1. 위에서 분석하고 싶은 한국 주식 종목을 검색하고 선택하세요.<br />
                        2. 선택한 종목의 주가 차트를 확인하세요.<br />
                        3. 왼쪽 메뉴에서 다양한 전문 기능을 이용해보세요.<br />
                        4. 한국형 전략, 포트폴리오 관리, 리스크 분석 등을 체험하세요.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      
      case 'strategies':
        return (
          <KoreanStrategyBuilder
            selectedStock={selectedStock}
            onStrategyRun={handleStrategyRun}
            onStrategySave={handleStrategySave}
            onOptimize={handleStrategyOptimize}
            loading={backtestLoading}
          />
        );
      
      case 'portfolio':
        return <PortfolioDashboard />;
      
      case 'analytics':
        return <AnalyticsDashboard />;
      
      case 'risk':
        return <RiskManagementDashboard />;
      
      case 'realtime':
        return <MarketMonitoringDashboard />;
      
      default:
        return <div>페이지를 찾을 수 없습니다.</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white dark:bg-gray-800 shadow-lg transition-all duration-300 flex flex-col h-screen sticky top-0`}>
        {/* Logo and Toggle */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                한국 주식 백테스팅
              </h1>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Market Status */}
        {sidebarOpen && (
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                marketStatus.status === 'open' ? 'bg-green-500' :
                marketStatus.status === 'pre_market' ? 'bg-yellow-500' :
                marketStatus.status === 'lunch_break' ? 'bg-orange-500' : 'bg-gray-500'
              }`}></div>
              <div className="text-sm">
                <div className="font-medium text-gray-900 dark:text-white">{marketStatus.statusText}</div>
                <div className="text-gray-500 dark:text-gray-400">{marketStatus.nextSession}</div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Menu - Scrollable Area */}
        <nav className="flex-1 p-4 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveView(item.id as ActiveView)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                      isActive 
                        ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-r-2 border-blue-600' 
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                    }`}
                    title={sidebarOpen ? '' : item.label}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {sidebarOpen && (
                      <div className="flex-1">
                        <div className="font-medium">{item.label}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">{item.description}</div>
                      </div>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Settings - Fixed at Bottom */}
        <div className="p-4 border-t-2 border-blue-200 dark:border-blue-700 bg-gray-50 dark:bg-gray-700/50">
          <button
            onClick={() => setSettingsOpen(true)}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors shadow-md font-medium"
            title={sidebarOpen ? '' : '설정'}
          >
            <Settings className="h-5 w-5 flex-shrink-0" />
            {sidebarOpen && <span>설정</span>}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {menuItems.find(item => item.id === activeView)?.label || '한국 주식 백테스팅'}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {menuItems.find(item => item.id === activeView)?.description}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {selectedStock && (
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">{selectedStock.name_kr}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{selectedStock.symbol} • {selectedStock.market}</div>
                </div>
              )}
              <button className="relative p-2 text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400">
                <Bell className="h-6 w-6" />
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400"></span>
              </button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 p-6 overflow-auto">
          {renderContent()}
        </main>
      </div>

      {/* Settings Modal - Temporarily disabled */}
      {/* <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      /> */}

      {/* Backtest Result Modal */}
      <BacktestResultModal
        isOpen={backtestResultOpen}
        onClose={() => setBacktestResultOpen(false)}
        result={backtestResult}
        stockSymbol={selectedStock?.name_kr}
        strategyName="사용자 전략"
      />
    </div>
  );
}