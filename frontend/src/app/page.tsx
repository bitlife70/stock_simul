'use client';

import { useState, useEffect } from 'react';
import { 
  BarChart3, TrendingUp, Shield, Target, Menu, X,
  Home as HomeIcon, Activity, Settings, Bell, Monitor
} from 'lucide-react';
import StockSearchSimple from '@/components/stock/StockSearchSimple';
import StockChart from '@/components/stock/StockChart';
import StrategyBuilder from '@/components/strategy/StrategyBuilder';
import KoreanStrategyBuilder from '@/components/strategy/KoreanStrategyBuilder';
import PortfolioDashboard from '@/components/portfolio/PortfolioDashboard';
import AnalyticsDashboard from '@/components/analytics/AnalyticsDashboard';
import RiskManagementDashboard from '@/components/risk/RiskManagementDashboard';
import MarketMonitoringDashboard from '@/components/realtime/MarketMonitoringDashboard';
import type { Stock, StockData, StrategyFormData, BacktestResult } from '@/types';
import { KoreanUtils } from '@/lib/korean-utils';

type ActiveView = 'overview' | 'strategies' | 'portfolio' | 'analytics' | 'risk' | 'realtime';

export default function Home() {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(false);
  const [backtestLoading, setBacktestLoading] = useState(false);
  const [activeView, setActiveView] = useState<ActiveView>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [marketStatus, setMarketStatus] = useState(KoreanUtils.getKoreanMarketStatus());

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
      const response = await fetch(`http://localhost:8003/api/v1/stocks/${symbol}/data`);
      const data = await response.json();
      setStockData(data.slice(-365)); // 최근 1년 데이터만 표시
    } catch (error) {
      console.error('주식 데이터를 가져오는데 실패했습니다:', error);
      setStockData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStockSelect = (stock: Stock) => {
    setSelectedStock(stock);
  };

  const handleStrategyRun = async (strategy: StrategyFormData | any) => {
    setBacktestLoading(true);
    try {
      const backtestData = {
        ...strategy,
        stock_symbol: selectedStock?.symbol,
      };

      const response = await fetch('http://localhost:8003/api/v1/backtest/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData),
      });

      if (response.ok) {
        const result: BacktestResult = await response.json();
        alert(`백테스팅 완료!\n총 수익률: ${(result.total_return * 100).toFixed(2)}%\n승률: ${(result.win_rate * 100).toFixed(2)}%`);
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

  const handleStrategySave = async (strategy: StrategyFormData | any) => {
    try {
      const response = await fetch('http://localhost:8003/api/v1/strategies', {
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

  const handleStrategyOptimize = async (strategy: any) => {
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
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">종목 선택</h2>
              <StockSearchSimple 
                onStockSelect={handleStockSelect}
                selectedStock={selectedStock}
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Stock Chart */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">주가 차트</h2>
                {loading ? (
                  <div className="flex items-center justify-center h-96">
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                      <span className="ml-3 text-gray-600">데이터 로딩중...</span>
                    </div>
                  </div>
                ) : (
                  <StockChart
                    symbol={selectedStock?.name_kr}
                    data={stockData}
                    height={400}
                  />
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
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      한국 주식 백테스팅 플랫폼에 오신 것을 환영합니다
                    </h3>
                    <div className="mt-2 text-sm text-blue-700">
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
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        {/* Logo and Toggle */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h1 className="text-lg font-bold text-gray-900">
                한국 주식 백테스팅
              </h1>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Market Status */}
        {sidebarOpen && (
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                marketStatus.status === 'open' ? 'bg-green-500' :
                marketStatus.status === 'pre_market' ? 'bg-yellow-500' :
                marketStatus.status === 'lunch_break' ? 'bg-orange-500' : 'bg-gray-500'
              }`}></div>
              <div className="text-sm">
                <div className="font-medium text-gray-900">{marketStatus.statusText}</div>
                <div className="text-gray-500">{marketStatus.nextSession}</div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Menu */}
        <nav className="flex-1 p-4">
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
                        ? 'bg-blue-100 text-blue-600 border-r-2 border-blue-600' 
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                    title={sidebarOpen ? '' : item.label}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    {sidebarOpen && (
                      <div className="flex-1">
                        <div className="font-medium">{item.label}</div>
                        <div className="text-xs text-gray-500">{item.description}</div>
                      </div>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Settings */}
        <div className="p-4 border-t border-gray-200">
          <button
            className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
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
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {menuItems.find(item => item.id === activeView)?.label || '한국 주식 백테스팅'}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {menuItems.find(item => item.id === activeView)?.description}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {selectedStock && (
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">{selectedStock.name_kr}</div>
                  <div className="text-xs text-gray-500">{selectedStock.symbol} • {selectedStock.market}</div>
                </div>
              )}
              <button className="relative p-2 text-gray-400 hover:text-gray-500">
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
    </div>
  );
}