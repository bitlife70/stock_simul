'use client';

import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle, Shield, Activity } from 'lucide-react';
import type { Portfolio, PortfolioStrategy, DashboardMetrics, KoreanMarketData } from '@/types';

interface PortfolioDashboardProps {
  portfolio?: Portfolio;
  metrics?: DashboardMetrics;
  marketData?: KoreanMarketData;
}

const PortfolioDashboard: React.FC<PortfolioDashboardProps> = ({
  portfolio,
  metrics,
  marketData
}) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1D' | '1W' | '1M' | '3M' | '1Y'>('1M');
  const [performanceData, setPerformanceData] = useState<Array<{ date: string; portfolio: number; kospi: number; kosdaq: number }>>([]);

  // Korean Won formatting
  const formatKRW = (amount: number): string => {
    if (amount >= 100000000) { // 1억 이상
      return `${(amount / 100000000).toFixed(1)}억원`;
    } else if (amount >= 10000) { // 1만 이상
      return `${(amount / 10000).toFixed(0)}만원`;
    } else {
      return `${amount.toLocaleString()}원`;
    }
  };

  const formatPercentage = (value: number): string => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Mock performance data for demo
  useEffect(() => {
    const generateMockData = () => {
      const data = [];
      const startDate = new Date();
      startDate.setMonth(startDate.getMonth() - 3);
      
      for (let i = 0; i < 90; i++) {
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        
        data.push({
          date: date.toISOString().split('T')[0],
          portfolio: 100 + Math.random() * 20 - 10 + i * 0.1,
          kospi: 100 + Math.random() * 15 - 7.5 + i * 0.05,
          kosdaq: 100 + Math.random() * 25 - 12.5 + i * 0.08
        });
      }
      
      setPerformanceData(data);
    };

    generateMockData();
  }, [selectedTimeframe]);

  const mockMetrics: DashboardMetrics = metrics || {
    portfolio_value: 125000000,
    daily_pnl: 2500000,
    daily_pnl_percentage: 2.04,
    total_return: 12.5,
    benchmark_return: 8.3,
    active_positions: 12,
    cash_balance: 15000000,
    margin_used: 35000000,
    risk_exposure: 68.5
  };

  const mockMarketData: KoreanMarketData = marketData || {
    kospi_index: 2485.67,
    kosdaq_index: 745.23,
    won_dollar_rate: 1320.50,
    market_status: 'open',
    chaebol_concentration: 35.2,
    sector_weights: {
      '기술주': 28.5,
      '금융': 18.2,
      '제조업': 15.8,
      '화학': 12.1,
      '소비재': 10.4,
      '기타': 15.0
    }
  };

  const sectorData = Object.entries(mockMarketData.sector_weights).map(([sector, weight]) => ({
    name: sector,
    value: weight,
    color: getColorForSector(sector)
  }));

  function getColorForSector(sector: string): string {
    const colors = {
      '기술주': '#3B82F6',
      '금융': '#10B981',
      '제조업': '#F59E0B',
      '화학': '#EF4444',
      '소비재': '#8B5CF6',
      '기타': '#6B7280'
    };
    return colors[sector as keyof typeof colors] || '#6B7280';
  }

  const riskData = [
    { name: '개별종목위험', value: 25.3, color: '#EF4444' },
    { name: '섹터집중위험', value: 18.7, color: '#F59E0B' },
    { name: '재벌집중위험', value: 15.2, color: '#10B981' },
    { name: '환율위험', value: 12.8, color: '#3B82F6' },
    { name: '유동성위험', value: 8.5, color: '#8B5CF6' },
    { name: '기타위험', value: 19.5, color: '#6B7280' }
  ];

  return (
    <div className="space-y-6">
      {/* Header with Market Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">포트폴리오 대시보드</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  mockMarketData.market_status === 'open' ? 'bg-green-500' :
                  mockMarketData.market_status === 'pre_market' ? 'bg-yellow-500' :
                  mockMarketData.market_status === 'lunch_break' ? 'bg-orange-500' : 'bg-gray-500'
                }`}></div>
                <span>
                  {mockMarketData.market_status === 'open' ? '장중' :
                   mockMarketData.market_status === 'pre_market' ? '장전' :
                   mockMarketData.market_status === 'lunch_break' ? '점심시간' : '장마감'}
                </span>
              </div>
              <span>KOSPI {mockMarketData.kospi_index.toFixed(2)}</span>
              <span>KOSDAQ {mockMarketData.kosdaq_index.toFixed(2)}</span>
              <span>달러환율 {mockMarketData.won_dollar_rate.toFixed(2)}원</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-gray-900">
              {formatKRW(mockMetrics.portfolio_value)}
            </div>
            <div className={`flex items-center ${
              mockMetrics.daily_pnl >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {mockMetrics.daily_pnl >= 0 ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              <span className="font-semibold">
                {formatKRW(Math.abs(mockMetrics.daily_pnl))} ({formatPercentage(mockMetrics.daily_pnl_percentage)})
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">총 수익률</p>
              <p className={`text-2xl font-bold ${
                mockMetrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatPercentage(mockMetrics.total_return)}
              </p>
              <p className="text-xs text-gray-500">
                벤치마크 대비 +{(mockMetrics.total_return - mockMetrics.benchmark_return).toFixed(2)}%
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">활성 포지션</p>
              <p className="text-2xl font-bold text-gray-900">{mockMetrics.active_positions}개</p>
              <p className="text-xs text-gray-500">현금 비중 {((mockMetrics.cash_balance / mockMetrics.portfolio_value) * 100).toFixed(1)}%</p>
            </div>
            <Activity className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">리스크 노출도</p>
              <p className={`text-2xl font-bold ${
                mockMetrics.risk_exposure > 70 ? 'text-red-600' :
                mockMetrics.risk_exposure > 50 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {mockMetrics.risk_exposure.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">
                {mockMetrics.risk_exposure > 70 ? '높음' :
                 mockMetrics.risk_exposure > 50 ? '보통' : '낮음'}
              </p>
            </div>
            <Shield className="w-8 h-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">신용 사용률</p>
              <p className="text-2xl font-bold text-gray-900">
                {((mockMetrics.margin_used / mockMetrics.portfolio_value) * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">{formatKRW(mockMetrics.margin_used)} 사용중</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Performance Chart and Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">성과 분석</h3>
            <div className="flex space-x-1">
              {(['1D', '1W', '1M', '3M', '1Y'] as const).map((timeframe) => (
                <button
                  key={timeframe}
                  onClick={() => setSelectedTimeframe(timeframe)}
                  className={`px-3 py-1 text-xs rounded ${
                    selectedTimeframe === timeframe
                      ? 'bg-blue-100 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {timeframe}
                </button>
              ))}
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                />
                <YAxis tickFormatter={(value) => `${value.toFixed(0)}%`} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString('ko-KR')}
                  formatter={(value: number, name: string) => [
                    `${value.toFixed(2)}%`,
                    name === 'portfolio' ? '포트폴리오' : name === 'kospi' ? 'KOSPI' : 'KOSDAQ'
                  ]}
                />
                <Line type="monotone" dataKey="portfolio" stroke="#3B82F6" strokeWidth={2} name="portfolio" />
                <Line type="monotone" dataKey="kospi" stroke="#10B981" strokeWidth={1} strokeDasharray="5 5" name="kospi" />
                <Line type="monotone" dataKey="kosdaq" stroke="#F59E0B" strokeWidth={1} strokeDasharray="5 5" name="kosdaq" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Allocation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">섹터 배분</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sectorData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sectorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {sectorData.map((sector) => (
              <div key={sector.name} className="flex items-center">
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: sector.color }}
                ></div>
                <span className="text-sm text-gray-600">
                  {sector.name} {sector.value.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk Analysis */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">리스크 분석</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-md font-medium text-gray-800 mb-3">리스크 구성</h4>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tickFormatter={(value) => `${value}%`} />
                  <YAxis type="category" dataKey="name" width={80} />
                  <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                  <Bar dataKey="value" fill={(entry) => entry.color} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div>
            <h4 className="text-md font-medium text-gray-800 mb-3">한국 시장 리스크 지표</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">재벌 집중도</span>
                <div className="flex items-center">
                  <div className="w-24 bg-gray-200 rounded-full h-2 mr-3">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${mockMarketData.chaebol_concentration}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{mockMarketData.chaebol_concentration.toFixed(1)}%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">환율 변동성 (90일)</span>
                <span className="text-sm font-medium text-orange-600">중간</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">가격 제한폭 리스크</span>
                <span className="text-sm font-medium text-green-600">낮음</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">유동성 리스크</span>
                <span className="text-sm font-medium text-yellow-600">보통</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioDashboard;