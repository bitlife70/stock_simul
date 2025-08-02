'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Play, Save, RefreshCw, Settings, TrendingUp, Shield, 
  AlertTriangle, BarChart3, Target, Zap, Brain
} from 'lucide-react';
import type { Stock, KoreanStrategy, StrategyParameter, PerformanceHistory } from '@/types';

const koreanStrategySchema = z.object({
  name: z.string().min(1, '전략 이름을 입력해주세요'),
  description: z.string().optional(),
  strategy_id: z.string().min(1, '전략을 선택해주세요'),
  parameters: z.record(z.union([z.string(), z.number(), z.boolean()])),
  initial_capital: z.number().min(1000000, '최소 100만원 이상 입력해주세요'),
  start_date: z.string().min(1, '시작 날짜를 선택해주세요'),
  end_date: z.string().min(1, '종료 날짜를 선택해주세요'),
  risk_level: z.enum(['conservative', 'moderate', 'aggressive']),
  korean_constraints: z.object({
    max_single_position: z.number().min(0.01).max(1),
    max_chaebol_exposure: z.number().min(0).max(1),
    use_price_limits: z.boolean(),
    avoid_suspension_risk: z.boolean(),
  })
});

type KoreanStrategyFormData = z.infer<typeof koreanStrategySchema>;

interface KoreanStrategyBuilderProps {
  selectedStock?: Stock | null;
  onStrategyRun: (strategy: KoreanStrategyFormData) => void;
  onStrategySave: (strategy: KoreanStrategyFormData) => void;
  onOptimize?: (strategy: KoreanStrategyFormData) => void;
  loading?: boolean;
}

export default function KoreanStrategyBuilder({
  selectedStock,
  onStrategyRun,
  onStrategySave,
  onOptimize,
  loading = false
}: KoreanStrategyBuilderProps) {
  const [strategies, setStrategies] = useState<KoreanStrategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<KoreanStrategy | null>(null);
  const [strategiesLoading, setStrategiesLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'basic' | 'parameters' | 'risk' | 'optimization'>('basic');
  const [optimizationResults, setOptimizationResults] = useState<any>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<KoreanStrategyFormData>({
    resolver: zodResolver(koreanStrategySchema),
    defaultValues: {
      initial_capital: 50000000, // 5천만원
      start_date: '2020-01-01',
      end_date: '2024-12-31',
      risk_level: 'moderate',
      parameters: {},
      korean_constraints: {
        max_single_position: 0.2, // 20%
        max_chaebol_exposure: 0.5, // 50%
        use_price_limits: true,
        avoid_suspension_risk: true,
      }
    }
  });

  const strategyId = watch('strategy_id');
  const riskLevel = watch('risk_level');

  // Korean-specific strategies
  const koreanStrategies: KoreanStrategy[] = [
    {
      id: 'chaebol_rotation',
      name: 'Chaebol Rotation Strategy',
      name_kr: '재벌 순환 전략',
      category: 'chaebol_focus',
      description: '대형 재벌주들 간의 상대적 강도를 분석하여 순환 매매하는 전략',
      korean_market_focus: true,
      crisis_tested: true,
      risk_profile: 'moderate',
      parameters: [
        {
          key: 'lookback_period',
          name: 'Lookback Period',
          name_kr: '분석 기간',
          type: 'number',
          default_value: 60,
          min_value: 20,
          max_value: 252,
          description: '상대적 강도 분석을 위한 일수',
          korean_market_constraint: false
        },
        {
          key: 'rotation_threshold',
          name: 'Rotation Threshold',
          name_kr: '순환 임계값',
          type: 'number',
          default_value: 0.05,
          min_value: 0.01,
          max_value: 0.2,
          description: '순환 매매를 위한 성과 차이 임계값',
          korean_market_constraint: false
        },
        {
          key: 'max_holdings',
          name: 'Max Holdings',
          name_kr: '최대 보유 종목수',
          type: 'number',
          default_value: 3,
          min_value: 1,
          max_value: 10,
          description: '동시에 보유할 수 있는 최대 종목 수',
          korean_market_constraint: true
        }
      ],
      performance_history: [
        { period: '2020', return_percentage: 15.2, benchmark_return: 12.4, volatility: 18.5, max_drawdown: -12.3, sharpe_ratio: 0.82 },
        { period: '2021', return_percentage: 22.8, benchmark_return: 18.7, volatility: 22.1, max_drawdown: -15.7, sharpe_ratio: 1.03 },
        { period: '2022', return_percentage: -8.4, benchmark_return: -12.1, volatility: 25.3, max_drawdown: -18.2, sharpe_ratio: -0.33 },
        { period: '2023', return_percentage: 18.9, benchmark_return: 14.2, volatility: 19.8, max_drawdown: -11.5, sharpe_ratio: 0.95 }
      ]
    },
    {
      id: 'won_dollar_momentum',
      name: 'Won-Dollar Impact Strategy',
      name_kr: '원달러 영향 전략',
      category: 'momentum',
      description: '원달러 환율 변동이 개별 종목에 미치는 영향을 분석한 모멘텀 전략',
      korean_market_focus: true,
      crisis_tested: true,
      risk_profile: 'aggressive',
      parameters: [
        {
          key: 'fx_sensitivity',
          name: 'FX Sensitivity',
          name_kr: '환율 민감도',
          type: 'number',
          default_value: 0.7,
          min_value: 0.1,
          max_value: 2.0,
          description: '환율 변동에 대한 민감도 필터',
          korean_market_constraint: true
        },
        {
          key: 'momentum_period',
          name: 'Momentum Period',
          name_kr: '모멘텀 기간',
          type: 'number',
          default_value: 20,
          min_value: 5,
          max_value: 100,
          description: '모멘텀 계산을 위한 기간',
          korean_market_constraint: false
        }
      ],
      performance_history: [
        { period: '2020', return_percentage: 28.5, benchmark_return: 12.4, volatility: 32.1, max_drawdown: -22.8, sharpe_ratio: 0.89 },
        { period: '2021', return_percentage: 35.2, benchmark_return: 18.7, volatility: 35.8, max_drawdown: -25.3, sharpe_ratio: 0.98 },
        { period: '2022', return_percentage: -15.7, benchmark_return: -12.1, volatility: 38.5, max_drawdown: -31.2, sharpe_ratio: -0.41 },
        { period: '2023', return_percentage: 24.3, benchmark_return: 14.2, volatility: 29.7, max_drawdown: -18.5, sharpe_ratio: 0.82 }
      ]
    },
    {
      id: 'kosdaq_value_growth',
      name: 'KOSDAQ Value-Growth Hybrid',
      name_kr: '코스닥 가치-성장 하이브리드',
      category: 'value',
      description: '코스닥 시장의 저평가된 성장주를 발굴하는 하이브리드 전략',
      korean_market_focus: true,
      crisis_tested: false,
      risk_profile: 'moderate',
      parameters: [
        {
          key: 'pe_threshold',
          name: 'PE Threshold',
          name_kr: 'PER 임계값',
          type: 'number',
          default_value: 15.0,
          min_value: 5.0,
          max_value: 30.0,
          description: '가치주 선별을 위한 PER 상한선',
          korean_market_constraint: false
        },
        {
          key: 'growth_threshold',
          name: 'Growth Threshold',
          name_kr: '성장률 임계값',
          type: 'number',
          default_value: 0.15,
          min_value: 0.05,
          max_value: 0.5,
          description: '매출 성장률 하한선',
          korean_market_constraint: false
        }
      ],
      performance_history: [
        { period: '2020', return_percentage: 45.8, benchmark_return: 25.4, volatility: 38.2, max_drawdown: -28.5, sharpe_ratio: 1.2 },
        { period: '2021', return_percentage: 18.3, benchmark_return: 15.8, volatility: 35.7, max_drawdown: -22.1, sharpe_ratio: 0.51 },
        { period: '2022', return_percentage: -25.4, benchmark_return: -28.7, volatility: 42.1, max_drawdown: -38.2, sharpe_ratio: -0.60 },
        { period: '2023', return_percentage: 32.1, benchmark_return: 24.8, volatility: 33.5, max_drawdown: -19.8, sharpe_ratio: 0.96 }
      ]
    }
  ];

  useEffect(() => {
    setStrategies(koreanStrategies);
  }, []);

  useEffect(() => {
    if (strategyId) {
      const strategy = strategies.find(s => s.id === strategyId);
      setSelectedStrategy(strategy || null);
      
      if (strategy) {
        const defaultParams: Record<string, string | number | boolean> = {};
        strategy.parameters.forEach((param) => {
          defaultParams[param.key] = param.default_value;
        });
        setValue('parameters', defaultParams);
      }
    }
  }, [strategyId, strategies, setValue]);

  const formatKRW = (amount: number): string => {
    if (amount >= 100000000) {
      return `${(amount / 100000000).toFixed(1)}억원`;
    } else if (amount >= 10000) {
      return `${(amount / 10000).toFixed(0)}만원`;
    } else {
      return `${amount.toLocaleString()}원`;
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'conservative': return 'text-green-600 bg-green-50';
      case 'moderate': return 'text-yellow-600 bg-yellow-50';
      case 'aggressive': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskLevelText = (level: string) => {
    switch (level) {
      case 'conservative': return '보수적';
      case 'moderate': return '중간';
      case 'aggressive': return '공격적';
      default: return '알 수 없음';
    }
  };

  const onSubmit = (data: KoreanStrategyFormData, action: 'run' | 'save' | 'optimize') => {
    if (!selectedStock && action === 'run') {
      alert('먼저 종목을 선택해주세요.');
      return;
    }

    if (action === 'run') {
      onStrategyRun(data);
    } else if (action === 'save') {
      onStrategySave(data);
    } else if (action === 'optimize' && onOptimize) {
      onOptimize(data);
    }
  };

  const handleOptimization = async () => {
    // Mock optimization results
    setOptimizationResults({
      best_parameters: {
        lookback_period: 45,
        rotation_threshold: 0.08,
        max_holdings: 4
      },
      expected_return: 16.8,
      expected_volatility: 19.2,
      expected_sharpe: 0.88,
      optimization_score: 0.92
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800">한국형 전략 설정</h2>
        <button
          type="button"
          onClick={() => reset()}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          초기화
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {[
          { id: 'basic', label: '기본 설정', icon: Settings },
          { id: 'parameters', label: '매개변수', icon: Target },
          { id: 'risk', label: '리스크 관리', icon: Shield },
          { id: 'optimization', label: '최적화', icon: Brain }
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
        <form className="space-y-6">
          {/* Basic Settings Tab */}
          {activeTab === 'basic' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    전략 이름 *
                  </label>
                  <input
                    {...register('name')}
                    type="text"
                    placeholder="한국형 투자전략"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.name && (
                    <p className="text-sm text-red-600 mt-1">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    초기 자본 *
                  </label>
                  <input
                    {...register('initial_capital', { valueAsNumber: true })}
                    type="number"
                    min="1000000"
                    step="10000000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.initial_capital && (
                    <p className="text-sm text-red-600 mt-1">{errors.initial_capital.message}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    현재 설정: {formatKRW(watch('initial_capital') || 0)}
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  전략 선택 *
                </label>
                <select
                  {...register('strategy_id')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">전략을 선택해주세요</option>
                  {strategies.map(strategy => (
                    <option key={strategy.id} value={strategy.id}>
                      {strategy.name_kr} - {strategy.description}
                    </option>
                  ))}
                </select>
                {errors.strategy_id && (
                  <p className="text-sm text-red-600 mt-1">{errors.strategy_id.message}</p>
                )}
              </div>

              {selectedStrategy && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-blue-800">{selectedStrategy.name_kr}</h4>
                      <p className="text-sm text-blue-700 mt-1">{selectedStrategy.description}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${getRiskLevelColor(selectedStrategy.risk_profile)}`}>
                          {getRiskLevelText(selectedStrategy.risk_profile)}
                        </span>
                        {selectedStrategy.korean_market_focus && (
                          <span className="px-2 py-1 text-xs bg-red-50 text-red-600 rounded-full">
                            한국시장 특화
                          </span>
                        )}
                        {selectedStrategy.crisis_tested && (
                          <span className="px-2 py-1 text-xs bg-green-50 text-green-600 rounded-full">
                            위기 검증됨
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    시작 날짜 *
                  </label>
                  <input
                    {...register('start_date')}
                    type="date"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.start_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.start_date.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    종료 날짜 *
                  </label>
                  <input
                    {...register('end_date')}
                    type="date"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {errors.end_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.end_date.message}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Parameters Tab */}
          {activeTab === 'parameters' && selectedStrategy && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-800">매개변수 설정</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedStrategy.parameters.map((param) => (
                  <div key={param.key} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="block text-sm font-medium text-gray-700">
                        {param.name_kr}
                      </label>
                      {param.korean_market_constraint && (
                        <span className="px-2 py-1 text-xs bg-orange-50 text-orange-600 rounded">
                          한국시장 제약
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">{param.description}</p>
                    {param.type === 'number' ? (
                      <input
                        {...register(`parameters.${param.key}`, { valueAsNumber: true })}
                        type="number"
                        min={param.min_value}
                        max={param.max_value}
                        step={param.min_value !== undefined && param.min_value < 1 ? 0.01 : 1}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    ) : param.type === 'boolean' ? (
                      <select
                        {...register(`parameters.${param.key}`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="true">예</option>
                        <option value="false">아니오</option>
                      </select>
                    ) : param.type === 'select' && param.options ? (
                      <select
                        {...register(`parameters.${param.key}`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {param.options.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        {...register(`parameters.${param.key}`)}
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Management Tab */}
          {activeTab === 'risk' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-800">한국 시장 리스크 관리</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  리스크 수준 *
                </label>
                <select
                  {...register('risk_level')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="conservative">보수적 - 안정성 우선</option>
                  <option value="moderate">중간 - 균형잡힌 접근</option>
                  <option value="aggressive">공격적 - 수익성 우선</option>
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    개별 종목 최대 비중 (%)
                  </label>
                  <input
                    {...register('korean_constraints.max_single_position', { valueAsNumber: true })}
                    type="number"
                    min="0.01"
                    max="1"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    현재: {((watch('korean_constraints.max_single_position') || 0) * 100).toFixed(0)}%
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    재벌 최대 노출 비중 (%)
                  </label>
                  <input
                    {...register('korean_constraints.max_chaebol_exposure', { valueAsNumber: true })}
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    현재: {((watch('korean_constraints.max_chaebol_exposure') || 0) * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center">
                  <input
                    {...register('korean_constraints.use_price_limits')}
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-700">
                    가격 제한폭 고려 (상한가/하한가)
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    {...register('korean_constraints.avoid_suspension_risk')}
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-700">
                    거래정지 위험 종목 회피
                  </label>
                </div>
              </div>

              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex">
                  <AlertTriangle className="h-5 w-5 text-orange-400 mt-0.5" />
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-orange-800">한국 시장 특성 고려사항</h4>
                    <p className="text-sm text-orange-700 mt-1">
                      • 일일 가격 제한폭: ±30% (KOSPI), ±30% (KOSDAQ)<br />
                      • 재벌 집중도가 높은 시장 특성<br />
                      • 외국인 투자자 동향의 높은 영향<br />
                      • 환율 변동성의 직접적 영향
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Optimization Tab */}
          {activeTab === 'optimization' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-800">매개변수 최적화</h3>
                <button
                  type="button"
                  onClick={handleOptimization}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <Zap className="h-4 w-4" />
                  최적화 실행
                </button>
              </div>

              {optimizationResults ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-green-800 mb-3">최적화 결과</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-green-700">예상 수익률</p>
                      <p className="text-lg font-semibold text-green-800">
                        {optimizationResults.expected_return.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-green-700">예상 변동성</p>
                      <p className="text-lg font-semibold text-green-800">
                        {optimizationResults.expected_volatility.toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-green-700">예상 샤프 비율</p>
                      <p className="text-lg font-semibold text-green-800">
                        {optimizationResults.expected_sharpe.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-green-700">최적화 점수</p>
                      <p className="text-lg font-semibold text-green-800">
                        {(optimizationResults.optimization_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-sm text-green-700 mb-2">최적 매개변수:</p>
                    <div className="text-sm text-green-800">
                      {Object.entries(optimizationResults.best_parameters).map(([key, value]) => (
                        <div key={key}>• {key}: {String(value)}</div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Brain className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>전략을 선택한 후 최적화를 실행해보세요.</p>
                  <p className="text-sm mt-1">AI가 최적의 매개변수를 찾아드립니다.</p>
                </div>
              )}
            </div>
          )}

          {/* Selected Stock Info */}
          {selectedStock && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">선택된 종목</h4>
              <p className="text-blue-700">
                {selectedStock.name_kr} ({selectedStock.symbol}) - {selectedStock.market}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleSubmit((data) => onSubmit(data, 'run'))}
              disabled={loading || isSubmitting || !selectedStock}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  실행중...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  백테스팅 실행
                </>
              )}
            </button>

            <button
              type="button"
              onClick={handleSubmit((data) => onSubmit(data, 'save'))}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Save className="h-4 w-4" />
              전략 저장
            </button>

            {onOptimize && (
              <button
                type="button"
                onClick={handleSubmit((data) => onSubmit(data, 'optimize'))}
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Brain className="h-4 w-4" />
                최적화
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}