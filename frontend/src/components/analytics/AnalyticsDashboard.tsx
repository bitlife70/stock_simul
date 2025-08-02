'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell, ComposedChart
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Activity, DollarSign, Target, AlertTriangle,
  BarChart3, PieChart as PieIcon, Filter, Download, RefreshCw, Calendar
} from 'lucide-react';
import type { BacktestResult, Trade, RiskMetrics, KoreanMarketData } from '@/types';

interface AnalyticsDashboardProps {
  backtestResult?: BacktestResult;
  trades?: Trade[];
  riskMetrics?: RiskMetrics;
  marketData?: KoreanMarketData;
  onExport?: (format: 'pdf' | 'excel') => void;
}

export default function AnalyticsDashboard({
  backtestResult,
  trades = [],
  riskMetrics,
  marketData,
  onExport
}: AnalyticsDashboardProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('1Y');
  const [activeView, setActiveView] = useState<'overview' | 'trades' | 'risk' | 'comparison'>('overview');
  const [equityCurveData, setEquityCurveData] = useState<Array<{
    date: string;
    portfolio: number;
    benchmark: number;
    drawdown: number;
  }>>([]);

  // Korean Won formatting
  const formatKRW = (amount: number): string => {
    if (Math.abs(amount) >= 100000000) {
      return `${(amount / 100000000).toFixed(1)}억원`;
    } else if (Math.abs(amount) >= 10000) {
      return `${(amount / 10000).toFixed(0)}만원`;
    } else {
      return `${amount.toLocaleString()}원`;
    }
  };

  const formatPercentage = (value: number): string => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Mock data generation for demo
  useEffect(() => {
    const generateEquityCurveData = () => {
      const data = [];
      const startDate = new Date('2023-01-01');
      const endDate = new Date('2024-12-31');
      const totalDays = Math.floor((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
      
      let portfolioValue = 100;
      let benchmarkValue = 100;
      let maxValue = 100;
      
      for (let i = 0; i <= totalDays; i += 7) { // Weekly data
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        
        // Simulate portfolio performance with some volatility
        const portfolioReturn = (Math.random() - 0.5) * 0.04 + 0.0008; // ~20% annual with 20% vol
        const benchmarkReturn = (Math.random() - 0.5) * 0.03 + 0.0006; // ~15% annual with 15% vol
        
        portfolioValue *= (1 + portfolioReturn);
        benchmarkValue *= (1 + benchmarkReturn);
        
        maxValue = Math.max(maxValue, portfolioValue);
        const drawdown = ((portfolioValue - maxValue) / maxValue) * 100;
        
        data.push({
          date: date.toISOString().split('T')[0],
          portfolio: ((portfolioValue - 100) / 100) * 100,
          benchmark: ((benchmarkValue - 100) / 100) * 100,
          drawdown: drawdown
        });
      }
      
      setEquityCurveData(data);
    };

    generateEquityCurveData();
  }, [selectedTimeframe]);

  // Mock backtest results
  const mockBacktestResult: BacktestResult = backtestResult || {
    total_return: 24.5,
    win_rate: 0.65,
    total_trades: 87,
    max_drawdown: -12.3,
    sharpe_ratio: 1.42,
    final_capital: 124500000,
    risk_metrics: {
      var_95: -2.8,
      var_99: -4.2,
      beta_kospi: 0.85,
      beta_kosdaq: 1.12,
      information_ratio: 0.68,
      calmar_ratio: 1.99,
      sortino_ratio: 2.15,
      max_consecutive_losses: 4,
      avg_win: 3.2,
      avg_loss: -1.8
    }
  };

  // Mock trades for demo
  const mockTrades: Trade[] = trades.length > 0 ? trades : [
    {
      entry_date: '2024-01-15',
      exit_date: '2024-02-20',
      symbol: '005930',
      side: 'long',
      entry_price: 68000,
      exit_price: 74500,
      quantity: 100,
      pnl: 650000,
      pnl_percentage: 9.56,
      duration_days: 36
    },
    {
      entry_date: '2024-02-28',
      exit_date: '2024-03-15',
      symbol: '000660',
      side: 'long',
      entry_price: 145000,
      exit_price: 138000,
      quantity: 50,
      pnl: -350000,
      pnl_percentage: -4.83,
      duration_days: 16
    },
    // Add more mock trades...
  ];

  const winningTrades = mockTrades.filter(trade => trade.pnl > 0);
  const losingTrades = mockTrades.filter(trade => trade.pnl <= 0);

  const monthlyReturns = [
    { month: '2024-01', return: 5.2, benchmark: 3.1 },
    { month: '2024-02', return: -2.1, benchmark: -1.8 },
    { month: '2024-03', return: 8.7, benchmark: 4.2 },
    { month: '2024-04', return: 3.5, benchmark: 2.8 },
    { month: '2024-05', return: -1.2, benchmark: 0.5 },
    { month: '2024-06', return: 6.8, benchmark: 3.9 },
    { month: '2024-07', return: 4.1, benchmark: 2.1 },
    { month: '2024-08', return: -3.8, benchmark: -2.5 },
    { month: '2024-09', return: 7.2, benchmark: 5.1 },
    { month: '2024-10', return: 2.9, benchmark: 1.8 },
    { month: '2024-11', return: -0.8, benchmark: 1.2 },
    { month: '2024-12', return: 3.4, benchmark: 2.0 }
  ];

  const riskReturnData = [
    { name: '현재 전략', return: mockBacktestResult.total_return, volatility: 18.5, sharpe: mockBacktestResult.sharpe_ratio },
    { name: 'KOSPI', return: 8.3, volatility: 15.2, sharpe: 0.55 },
    { name: 'KOSDAQ', return: 12.1, volatility: 22.8, sharpe: 0.53 },
    { name: '코스피200', return: 7.9, volatility: 14.8, sharpe: 0.53 },
    { name: '기술주 펀드', return: 15.2, volatility: 28.3, sharpe: 0.54 }
  ];

  const sectorExposure = [
    { sector: '기술주', exposure: 35.2, color: '#3B82F6' },
    { sector: '금융', exposure: 18.5, color: '#10B981' },
    { sector: '제조업', exposure: 15.8, color: '#F59E0B' },
    { sector: '화학', exposure: 12.1, color: '#EF4444' },
    { sector: '소비재', exposure: 10.4, color: '#8B5CF6' },
    { sector: '기타', exposure: 8.0, color: '#6B7280' }
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm text-gray-600">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
              {entry.name}: {entry.name.includes('수익률') || entry.name.includes('return') ? 
                formatPercentage(entry.value) : 
                entry.name.includes('원') ? formatKRW(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">백테스팅 분석 대시보드</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>분석 기간: 2023.01.01 ~ 2024.12.31</span>
              <span>총 거래: {mockBacktestResult.total_trades}회</span>
              <span>승률: {(mockBacktestResult.win_rate * 100).toFixed(1)}%</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onExport?.('excel')}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <Download className="h-4 w-4" />
              Excel
            </button>
            <button
              onClick={() => onExport?.('pdf')}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              <Download className="h-4 w-4" />
              PDF
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="flex border-b border-gray-200">
          {[
            { id: 'overview', label: '개요', icon: BarChart3 },
            { id: 'trades', label: '거래 분석', icon: Activity },
            { id: 'risk', label: '리스크 분석', icon: AlertTriangle },
            { id: 'comparison', label: '벤치마크 비교', icon: Target }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveView(id as any)}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeView === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeView === 'overview' && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-600">총 수익률</p>
                      <p className="text-2xl font-bold text-blue-900">
                        {formatPercentage(mockBacktestResult.total_return)}
                      </p>
                      <p className="text-xs text-blue-700">
                        최종 자본: {formatKRW(mockBacktestResult.final_capital)}
                      </p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-blue-600" />
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-600">샤프 비율</p>
                      <p className="text-2xl font-bold text-green-900">
                        {mockBacktestResult.sharpe_ratio.toFixed(2)}
                      </p>
                      <p className="text-xs text-green-700">우수한 위험 대비 수익</p>
                    </div>
                    <Target className="w-8 h-8 text-green-600" />
                  </div>
                </div>

                <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-orange-600">최대 낙폭</p>
                      <p className="text-2xl font-bold text-orange-900">
                        {formatPercentage(mockBacktestResult.max_drawdown)}
                      </p>
                      <p className="text-xs text-orange-700">리스크 통제 양호</p>
                    </div>
                    <TrendingDown className="w-8 h-8 text-orange-600" />
                  </div>
                </div>

                <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-purple-600">승률</p>
                      <p className="text-2xl font-bold text-purple-900">
                        {(mockBacktestResult.win_rate * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-purple-700">
                        {mockBacktestResult.total_trades}회 거래
                      </p>
                    </div>
                    <Activity className="w-8 h-8 text-purple-600" />
                  </div>
                </div>
              </div>

              {/* Equity Curve */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">자산 증감 곡선</h3>
                  <div className="flex space-x-1">
                    {(['1M', '3M', '6M', '1Y', 'ALL'] as const).map((timeframe) => (
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
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={equityCurveData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={(value) => new Date(value).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                      />
                      <YAxis yAxisId="return" orientation="left" tickFormatter={(value) => `${value.toFixed(0)}%`} />
                      <YAxis yAxisId="drawdown" orientation="right" tickFormatter={(value) => `${value.toFixed(0)}%`} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                      <Line 
                        yAxisId="return"
                        type="monotone" 
                        dataKey="portfolio" 
                        stroke="#3B82F6" 
                        strokeWidth={2} 
                        name="포트폴리오 수익률" 
                        dot={false}
                      />
                      <Line 
                        yAxisId="return"
                        type="monotone" 
                        dataKey="benchmark" 
                        stroke="#10B981" 
                        strokeWidth={1} 
                        strokeDasharray="5 5" 
                        name="벤치마크 수익률" 
                        dot={false}
                      />
                      <Area
                        yAxisId="drawdown"
                        type="monotone"
                        dataKey="drawdown"
                        stackId="1"
                        stroke="#EF4444"
                        fill="#FEE2E2"
                        fillOpacity={0.6}
                        name="낙폭"
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Monthly Returns and Sector Exposure */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">월별 수익률</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={monthlyReturns}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="month" 
                          tickFormatter={(value) => new Date(value + '-01').toLocaleDateString('ko-KR', { month: 'short' })}
                        />
                        <YAxis tickFormatter={(value) => `${value}%`} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Bar dataKey="return" fill="#3B82F6" name="전략 수익률" />
                        <Bar dataKey="benchmark" fill="#10B981" name="벤치마크" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">섹터 노출도</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={sectorExposure}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="exposure"
                        >
                          {sectorExposure.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-4">
                    {sectorExposure.map((sector) => (
                      <div key={sector.sector} className="flex items-center">
                        <div
                          className="w-3 h-3 rounded-full mr-2"
                          style={{ backgroundColor: sector.color }}
                        ></div>
                        <span className="text-sm text-gray-600">
                          {sector.sector} {sector.exposure.toFixed(1)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Trades Tab */}
          {activeView === 'trades' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-green-800">수익 거래</h4>
                  <p className="text-2xl font-bold text-green-900">{winningTrades.length}회</p>
                  <p className="text-sm text-green-700">
                    평균 수익: {formatPercentage(mockBacktestResult.risk_metrics?.avg_win || 0)}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-red-800">손실 거래</h4>
                  <p className="text-2xl font-bold text-red-900">{losingTrades.length}회</p>
                  <p className="text-sm text-red-700">
                    평균 손실: {formatPercentage(mockBacktestResult.risk_metrics?.avg_loss || 0)}
                  </p>
                </div>
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-800">평균 보유기간</h4>
                  <p className="text-2xl font-bold text-blue-900">
                    {Math.round(mockTrades.reduce((sum, trade) => sum + trade.duration_days, 0) / mockTrades.length)}일
                  </p>
                  <p className="text-sm text-blue-700">최대 연속 손실: {mockBacktestResult.risk_metrics?.max_consecutive_losses || 0}회</p>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">거래 내역</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          종목
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          매매구분
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          진입일/청산일
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          진입가/청산가
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          수량
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          손익
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          수익률
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          보유기간
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {mockTrades.slice(0, 10).map((trade, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {trade.symbol}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {trade.side === 'long' ? '매수' : '매도'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div>
                              <div>{new Date(trade.entry_date).toLocaleDateString('ko-KR')}</div>
                              <div className="text-gray-500">{new Date(trade.exit_date).toLocaleDateString('ko-KR')}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <div>
                              <div>{trade.entry_price.toLocaleString()}원</div>
                              <div className="text-gray-500">{trade.exit_price.toLocaleString()}원</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {trade.quantity.toLocaleString()}주
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatKRW(trade.pnl)}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            trade.pnl_percentage >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {formatPercentage(trade.pnl_percentage)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {trade.duration_days}일
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Risk Tab */}
          {activeView === 'risk' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700">VaR (95%)</h4>
                  <p className="text-xl font-bold text-red-600">
                    {formatPercentage(mockBacktestResult.risk_metrics?.var_95 || 0)}
                  </p>
                  <p className="text-xs text-gray-500">일일 최대 예상 손실</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700">베타 (KOSPI)</h4>
                  <p className="text-xl font-bold text-blue-600">
                    {mockBacktestResult.risk_metrics?.beta_kospi.toFixed(2) || '0.00'}
                  </p>
                  <p className="text-xs text-gray-500">시장 대비 민감도</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700">정보 비율</h4>
                  <p className="text-xl font-bold text-green-600">
                    {mockBacktestResult.risk_metrics?.information_ratio.toFixed(2) || '0.00'}
                  </p>
                  <p className="text-xs text-gray-500">초과 수익의 일관성</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700">칼마 비율</h4>
                  <p className="text-xl font-bold text-purple-600">
                    {mockBacktestResult.risk_metrics?.calmar_ratio.toFixed(2) || '0.00'}
                  </p>
                  <p className="text-xs text-gray-500">낙폭 대비 수익</p>
                </div>
              </div>

              <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                <div className="flex">
                  <AlertTriangle className="h-5 w-5 text-orange-400 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-orange-800">한국 시장 리스크 요인</h4>
                    <div className="text-sm text-orange-700 mt-2 space-y-1">
                      <p>• 재벌 집중도: 포트폴리오의 재벌주 비중이 높아 집중 리스크 존재</p>
                      <p>• 환율 영향: 원달러 환율 변동이 수출기업 중심으로 직접적 영향</p>
                      <p>• 유동성 위험: 코스닥 소형주의 경우 거래량 부족 시 유동성 리스크</p>
                      <p>• 정치적 리스크: 정책 변화 및 북한 리스크 등 지정학적 요인</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Comparison Tab */}
          {activeView === 'comparison' && (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">위험-수익 산점도</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        type="number" 
                        dataKey="volatility" 
                        name="변동성" 
                        tickFormatter={(value) => `${value}%`}
                        domain={[10, 40]}
                      />
                      <YAxis 
                        type="number" 
                        dataKey="return" 
                        name="수익률"
                        tickFormatter={(value) => `${value}%`}
                      />
                      <Tooltip 
                        cursor={{ strokeDasharray: '3 3' }}
                        formatter={(value: number, name: string) => [
                          name === 'return' ? formatPercentage(value) : `${value.toFixed(1)}%`,
                          name === 'return' ? '수익률' : '변동성'
                        ]}
                      />
                      <Scatter 
                        name="투자 전략" 
                        data={riskReturnData} 
                        fill="#3B82F6"
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">벤치마크 대비 성과</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          구분
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          수익률
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          변동성
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          샤프 비율
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          최대 낙폭
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {riskReturnData.map((item, index) => (
                        <tr key={index} className={index === 0 ? 'bg-blue-50' : 'hover:bg-gray-50'}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {item.name}
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            index === 0 ? 'text-blue-600' : 'text-gray-900'
                          }`}>
                            {formatPercentage(item.return)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.volatility.toFixed(1)}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.sharpe.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {index === 0 ? formatPercentage(mockBacktestResult.max_drawdown) : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}