'use client';

import { useState, useEffect } from 'react';
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line,
  AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { 
  Shield, AlertTriangle, TrendingDown, Calculator, Settings,
  Activity, Bell, Target, DollarSign, Zap, Brain, Eye
} from 'lucide-react';
import type { 
  PositionSize, KoreanRiskConstraints, MarketAlert, 
  KoreanMarketData, Portfolio 
} from '@/types';

interface RiskManagementDashboardProps {
  portfolio?: Portfolio;
  marketData?: KoreanMarketData;
  onPositionSizeUpdate?: (positions: PositionSize[]) => void;
  onRiskConstraintUpdate?: (constraints: KoreanRiskConstraints) => void;
}

export default function RiskManagementDashboard({
  portfolio,
  marketData,
  onPositionSizeUpdate,
  onRiskConstraintUpdate
}: RiskManagementDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'position' | 'alerts' | 'simulation'>('overview');
  const [riskConstraints, setRiskConstraints] = useState<KoreanRiskConstraints>({
    max_single_position: 0.2,
    max_chaebol_exposure: 0.5,
    max_sector_concentration: 0.3,
    price_limit_exposure: 0.15,
    daily_trading_limit: 100000000 // 1억원
  });
  const [alerts, setAlerts] = useState<MarketAlert[]>([]);
  const [positionSizes, setPositionSizes] = useState<PositionSize[]>([]);
  const [crisisScenario, setCrisisScenario] = useState<'normal' | 'financial_crisis' | 'geopolitical' | 'covid_like'>('normal');

  const formatKRW = (amount: number): string => {
    if (amount >= 100000000) {
      return `${(amount / 100000000).toFixed(1)}억원`;
    } else if (amount >= 10000) {
      return `${(amount / 10000).toFixed(0)}만원`;
    } else {
      return `${amount.toLocaleString()}원`;
    }
  };

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Mock data for risk assessment
  const riskRadarData = [
    { metric: '개별종목', current: 75, limit: 100, optimal: 60 },
    { metric: '섹터집중', current: 45, limit: 100, optimal: 50 },
    { metric: '재벌집중', current: 85, limit: 100, optimal: 70 },
    { metric: '유동성', current: 30, limit: 100, optimal: 40 },
    { metric: '환율', current: 60, limit: 100, optimal: 50 },
    { metric: '정치적', current: 40, limit: 100, optimal: 30 }
  ];

  const priceImpactData = [
    { symbol: '005930', name: '삼성전자', impact: 0.12, volume: 1500000, liquidity: 'high' },
    { symbol: '000660', name: 'SK하이닉스', impact: 0.25, volume: 800000, liquidity: 'high' },
    { symbol: '035420', name: 'NAVER', impact: 0.35, volume: 600000, liquidity: 'medium' },
    { symbol: '051910', name: 'LG화학', impact: 0.45, volume: 400000, liquidity: 'medium' },
    { symbol: '006400', name: '삼성SDI', impact: 0.68, volume: 250000, liquidity: 'low' }
  ];

  const crisisScenarios = {
    normal: {
      name: '정상 시장',
      volatility_multiplier: 1.0,
      correlation_increase: 0.0,
      liquidity_impact: 0.0,
      description: '일반적인 시장 상황'
    },
    financial_crisis: {
      name: '금융위기',
      volatility_multiplier: 2.5,
      correlation_increase: 0.3,
      liquidity_impact: 0.4,
      description: '2008년 글로벌 금융위기 수준'
    },
    geopolitical: {
      name: '지정학적 위기',
      volatility_multiplier: 1.8,
      correlation_increase: 0.2,
      liquidity_impact: 0.2,
      description: '북한 리스크, 무역분쟁 등'
    },
    covid_like: {
      name: '팬데믹',
      volatility_multiplier: 3.0,
      correlation_increase: 0.4,
      liquidity_impact: 0.3,
      description: '코로나19 수준의 충격'
    }
  };

  // Mock alerts
  useEffect(() => {
    const mockAlerts: MarketAlert[] = [
      {
        id: '1',
        type: 'price_limit',
        severity: 'high',
        symbol: '035420',
        title: '상한가 근접',
        message: 'NAVER가 상한가 5% 이내로 접근했습니다. 매도 타이밍을 고려해보세요.',
        timestamp: new Date().toISOString(),
        acknowledged: false
      },
      {
        id: '2',
        type: 'risk',
        severity: 'medium',
        title: '재벌 집중도 초과',
        message: '삼성그룹 계열사 비중이 50%를 초과했습니다.',
        timestamp: new Date(Date.now() - 1800000).toISOString(), // 30분 전
        acknowledged: false
      },
      {
        id: '3',
        type: 'volume_spike',
        severity: 'low',
        symbol: '000660',
        title: '거래량 급증',
        message: 'SK하이닉스 거래량이 평균 대비 300% 증가했습니다.',
        timestamp: new Date(Date.now() - 3600000).toISOString(), // 1시간 전
        acknowledged: true
      }
    ];
    setAlerts(mockAlerts);
  }, []);

  // Mock position sizes
  useEffect(() => {
    const mockPositions: PositionSize[] = [
      {
        symbol: '005930',
        name_kr: '삼성전자',
        current_price: 74500,
        target_allocation: 0.18,
        max_position_krw: 18000000,
        recommended_shares: 241,
        risk_score: 65,
        price_limit_risk: 'low'
      },
      {
        symbol: '000660',
        name_kr: 'SK하이닉스',
        current_price: 138000,
        target_allocation: 0.12,
        max_position_krw: 12000000,
        recommended_shares: 87,
        risk_score: 78,
        price_limit_risk: 'medium'
      },
      {
        symbol: '035420',
        name_kr: 'NAVER',
        current_price: 185000,
        target_allocation: 0.08,
        max_position_krw: 8000000,
        recommended_shares: 43,
        risk_score: 85,
        price_limit_risk: 'high'
      }
    ];
    setPositionSizes(mockPositions);
  }, []);

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-600 bg-red-50';
    if (score >= 60) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const runCrisisSimulation = () => {
    const scenario = crisisScenarios[crisisScenario];
    // Mock simulation results based on scenario
    const results = {
      expected_loss: -15.2 * scenario.volatility_multiplier,
      var_95: -8.5 * scenario.volatility_multiplier,
      var_99: -12.8 * scenario.volatility_multiplier,
      liquidity_impact: scenario.liquidity_impact * 100,
      recovery_time: Math.ceil(30 * scenario.volatility_multiplier)
    };
    
    alert(`위기 시뮬레이션 결과:\n예상 손실: ${results.expected_loss.toFixed(1)}%\nVaR (95%): ${results.var_95.toFixed(1)}%\n유동성 영향: ${results.liquidity_impact.toFixed(1)}%\n회복 예상 기간: ${results.recovery_time}일`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">리스크 관리 센터</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                <span>전체 리스크 수준: 보통</span>
              </div>
              <span>활성 알림: {alerts.filter(a => !a.acknowledged).length}개</span>
              <span>포지션 수: {positionSizes.length}개</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-right">
              <div className="text-sm text-gray-600">일일 거래 한도</div>
              <div className="text-lg font-semibold text-gray-900">
                {formatKRW(riskConstraints.daily_trading_limit)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="flex border-b border-gray-200">
          {[
            { id: 'overview', label: '리스크 개요', icon: Shield },
            { id: 'position', label: '포지션 관리', icon: Calculator },
            { id: 'alerts', label: '알림 센터', icon: Bell },
            { id: 'simulation', label: '위기 시뮬레이션', icon: Brain }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === id
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
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Risk Metrics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-gradient-to-r from-red-50 to-red-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-red-600">포트폴리오 VaR (95%)</p>
                      <p className="text-2xl font-bold text-red-900">-8.5%</p>
                      <p className="text-xs text-red-700">일일 최대 예상 손실</p>
                    </div>
                    <TrendingDown className="w-8 h-8 text-red-600" />
                  </div>
                </div>

                <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-orange-600">집중도 리스크</p>
                      <p className="text-2xl font-bold text-orange-900">72%</p>
                      <p className="text-xs text-orange-700">재벌+섹터 집중도</p>
                    </div>
                    <Target className="w-8 h-8 text-orange-600" />
                  </div>
                </div>

                <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-yellow-600">유동성 위험</p>
                      <p className="text-2xl font-bold text-yellow-900">35%</p>
                      <p className="text-xs text-yellow-700">저유동성 종목 비중</p>
                    </div>
                    <Activity className="w-8 h-8 text-yellow-600" />
                  </div>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-600">환율 노출도</p>
                      <p className="text-2xl font-bold text-blue-900">68%</p>
                      <p className="text-xs text-blue-700">달러 대비 민감도</p>
                    </div>
                    <DollarSign className="w-8 h-8 text-blue-600" />
                  </div>
                </div>
              </div>

              {/* Risk Radar and Constraints */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">리스크 레이더</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={riskRadarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="metric" />
                        <PolarRadiusAxis domain={[0, 100]} tickCount={5} />
                        <Radar 
                          name="현재 수준" 
                          dataKey="current" 
                          stroke="#EF4444" 
                          fill="#EF4444" 
                          fillOpacity={0.2}
                          strokeWidth={2}
                        />
                        <Radar 
                          name="적정 수준" 
                          dataKey="optimal" 
                          stroke="#10B981" 
                          fill="#10B981" 
                          fillOpacity={0.1}
                          strokeWidth={1}
                          strokeDasharray="5 5"
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">리스크 제약 조건</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-sm font-medium text-gray-700">
                          개별 종목 최대 비중
                        </label>
                        <span className="text-sm text-gray-600">
                          {formatPercentage(riskConstraints.max_single_position)}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0.05"
                        max="0.5"
                        step="0.01"
                        value={riskConstraints.max_single_position}
                        onChange={(e) => setRiskConstraints({
                          ...riskConstraints,
                          max_single_position: parseFloat(e.target.value)
                        })}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-sm font-medium text-gray-700">
                          재벌 최대 노출 비중
                        </label>
                        <span className="text-sm text-gray-600">
                          {formatPercentage(riskConstraints.max_chaebol_exposure)}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0.2"
                        max="0.8"
                        step="0.01"
                        value={riskConstraints.max_chaebol_exposure}
                        onChange={(e) => setRiskConstraints({
                          ...riskConstraints,
                          max_chaebol_exposure: parseFloat(e.target.value)
                        })}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-sm font-medium text-gray-700">
                          섹터 집중도 한도
                        </label>
                        <span className="text-sm text-gray-600">
                          {formatPercentage(riskConstraints.max_sector_concentration)}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0.1"
                        max="0.6"
                        step="0.01"
                        value={riskConstraints.max_sector_concentration}
                        onChange={(e) => setRiskConstraints({
                          ...riskConstraints,
                          max_sector_concentration: parseFloat(e.target.value)
                        })}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <label className="text-sm font-medium text-gray-700">
                          일일 거래 한도
                        </label>
                        <span className="text-sm text-gray-600">
                          {formatKRW(riskConstraints.daily_trading_limit)}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="10000000"
                        max="1000000000"
                        step="10000000"
                        value={riskConstraints.daily_trading_limit}
                        onChange={(e) => setRiskConstraints({
                          ...riskConstraints,
                          daily_trading_limit: parseFloat(e.target.value)
                        })}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Price Impact Analysis */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">가격 충격 분석</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">종목</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">예상 가격충격</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">일평균 거래량</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">유동성 등급</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">권장 분할매매</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {priceImpactData.map((item, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {item.name} ({item.symbol})
                          </td>
                          <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                            item.impact > 0.5 ? 'text-red-600' : 
                            item.impact > 0.3 ? 'text-yellow-600' : 'text-green-600'
                          }`}>
                            {(item.impact * 100).toFixed(2)}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.volume.toLocaleString()}주
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                              item.liquidity === 'high' ? 'bg-green-100 text-green-800' :
                              item.liquidity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {item.liquidity === 'high' ? '높음' : 
                               item.liquidity === 'medium' ? '보통' : '낮음'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.impact > 0.5 ? '10회 이상' : 
                             item.impact > 0.3 ? '5-10회' : '1-3회'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Position Management Tab */}
          {activeTab === 'position' && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex">
                  <Calculator className="h-5 w-5 text-blue-400 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-blue-800">포지션 사이징 가이드</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      현재 리스크 제약 조건과 시장 상황을 고려한 최적 포지션 크기를 제안합니다.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {positionSizes.map((position, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{position.name_kr}</h4>
                        <p className="text-sm text-gray-600">{position.symbol}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${getRiskColor(position.risk_score)}`}>
                        리스크 {position.risk_score}
                      </span>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">현재가</span>
                        <span className="text-sm font-medium">{position.current_price.toLocaleString()}원</span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">목표 비중</span>
                        <span className="text-sm font-medium">{formatPercentage(position.target_allocation)}</span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">최대 투자금액</span>
                        <span className="text-sm font-medium">{formatKRW(position.max_position_krw)}</span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">권장 매수량</span>
                        <span className="text-sm font-medium text-blue-600">
                          {position.recommended_shares.toLocaleString()}주
                        </span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">가격제한 위험</span>
                        <span className={`text-sm font-medium ${
                          position.price_limit_risk === 'high' ? 'text-red-600' :
                          position.price_limit_risk === 'medium' ? 'text-yellow-600' : 'text-green-600'
                        }`}>
                          {position.price_limit_risk === 'high' ? '높음' :
                           position.price_limit_risk === 'medium' ? '보통' : '낮음'}
                        </span>
                      </div>
                    </div>

                    <div className="mt-4">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${position.target_allocation * 100}%` }}
                        ></div>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">포트폴리오 내 비중</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alerts Tab */}
          {activeTab === 'alerts' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">리스크 알림</h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    {alerts.filter(a => !a.acknowledged).length}개의 새 알림
                  </span>
                  <button className="px-3 py-1 text-xs bg-blue-100 text-blue-600 rounded-md hover:bg-blue-200 transition-colors">
                    모두 읽음 처리
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {alerts.map((alert) => (
                  <div key={alert.id} className={`border rounded-lg p-4 ${
                    alert.acknowledged ? 'bg-gray-50 border-gray-200' : 'bg-white border-l-4 ' + getSeverityColor(alert.severity)
                  }`}>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900">{alert.title}</h4>
                          {alert.symbol && (
                            <span className="text-sm text-gray-600">({alert.symbol})</span>
                          )}
                          <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(alert.severity)}`}>
                            {alert.severity === 'critical' ? '긴급' :
                             alert.severity === 'high' ? '높음' :
                             alert.severity === 'medium' ? '보통' : '낮음'}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(alert.timestamp).toLocaleString('ko-KR')}
                        </p>
                      </div>
                      {!alert.acknowledged && (
                        <button
                          onClick={() => {
                            const updatedAlerts = alerts.map(a => 
                              a.id === alert.id ? { ...a, acknowledged: true } : a
                            );
                            setAlerts(updatedAlerts);
                          }}
                          className="ml-4 px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-md hover:bg-gray-200 transition-colors"
                        >
                          확인
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Crisis Simulation Tab */}
          {activeTab === 'simulation' && (
            <div className="space-y-6">
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex">
                  <Brain className="h-5 w-5 text-orange-400 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-orange-800">위기 상황 시뮬레이션</h4>
                    <p className="text-sm text-orange-700 mt-1">
                      다양한 위기 시나리오에서 포트폴리오의 예상 손실과 회복 기간을 분석합니다.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">시나리오 선택</h3>
                  <div className="space-y-3">
                    {Object.entries(crisisScenarios).map(([key, scenario]) => (
                      <div key={key} className="flex items-center">
                        <input
                          type="radio"
                          id={key}
                          name="crisis-scenario"
                          value={key}
                          checked={crisisScenario === key}
                          onChange={(e) => setCrisisScenario(e.target.value as any)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <label htmlFor={key} className="ml-3 block">
                          <div className="text-sm font-medium text-gray-900">{scenario.name}</div>
                          <div className="text-xs text-gray-600">{scenario.description}</div>
                        </label>
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={runCrisisSimulation}
                    className="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                  >
                    <Zap className="h-4 w-4" />
                    시뮬레이션 실행
                  </button>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">시나리오 상세</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">변동성 배수</span>
                      <span className="text-sm font-medium">
                        {crisisScenarios[crisisScenario].volatility_multiplier}x
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">상관관계 증가</span>
                      <span className="text-sm font-medium">
                        +{(crisisScenarios[crisisScenario].correlation_increase * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">유동성 영향</span>
                      <span className="text-sm font-medium">
                        {(crisisScenarios[crisisScenario].liquidity_impact * 100).toFixed(0)}% 감소
                      </span>
                    </div>
                  </div>

                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-800 mb-2">한국 시장 특수 요인</h4>
                    <ul className="text-xs text-gray-600 space-y-1">
                      <li>• 외국인 투자자 이탈 가속화</li>
                      <li>• 원달러 환율 급등 시 수출기업 영향도</li>
                      <li>• 재벌주 집중도에 따른 시스템 리스크</li>
                      <li>• 코스닥 소형주 유동성 고갈 위험</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}