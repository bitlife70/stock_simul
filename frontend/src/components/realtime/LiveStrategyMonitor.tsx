'use client';

import React, { useState, useEffect } from 'react';
import { webSocketService, LiveStrategyData } from '@/lib/websocket-service';
import { useTranslation } from 'react-i18next';

interface LiveStrategyMonitorProps {
  className?: string;
}

const LiveStrategyMonitor: React.FC<LiveStrategyMonitorProps> = ({ className = '' }) => {
  const { t } = useTranslation();
  const [strategyData, setStrategyData] = useState<LiveStrategyData | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'positions' | 'signals'>('overview');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const handleStrategyData = (data: LiveStrategyData) => {
      setStrategyData(data);
      if (!selectedStrategy && data.strategies.length > 0) {
        setSelectedStrategy(data.strategies[0].id);
      }
    };

    const connectWebSocket = async () => {
      try {
        await webSocketService.connect();
        setIsConnected(true);
        webSocketService.subscribe('strategy_updates', handleStrategyData);
        webSocketService.setUpdateFrequency('strategy_updates', 2000); // 2초마다 업데이트
      } catch (error) {
        console.error('Failed to connect to WebSocket for strategy updates:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      webSocketService.unsubscribe('strategy_updates', handleStrategyData);
    };
  }, [selectedStrategy]);

  // Mock data generator for development
  useEffect(() => {
    if (!strategyData) {
      const generateMockData = (): LiveStrategyData => {
        return {
          strategies: [
            {
              id: 'strategy_1',
              name: '한국형 모멘텀 전략',
              currentValue: 105000000 + (Math.random() - 0.5) * 2000000,
              dailyPnl: (Math.random() - 0.5) * 1000000,
              dailyPnlPercent: (Math.random() - 0.5) * 3,
              totalReturn: 5.0 + (Math.random() - 0.5) * 2,
              positions: [
                {
                  symbol: '005930',
                  name: '삼성전자',
                  quantity: 100,
                  currentPrice: 75000 + (Math.random() - 0.5) * 2000,
                  unrealizedPnl: (Math.random() - 0.5) * 500000,
                  unrealizedPnlPercent: (Math.random() - 0.5) * 5
                },
                {
                  symbol: '000660',
                  name: 'SK하이닉스',
                  quantity: 50,
                  currentPrice: 130000 + (Math.random() - 0.5) * 5000,
                  unrealizedPnl: (Math.random() - 0.5) * 300000,
                  unrealizedPnlPercent: (Math.random() - 0.5) * 4
                },
                {
                  symbol: '035420',
                  name: 'NAVER',
                  quantity: 30,
                  currentPrice: 200000 + (Math.random() - 0.5) * 10000,
                  unrealizedPnl: (Math.random() - 0.5) * 200000,
                  unrealizedPnlPercent: (Math.random() - 0.5) * 3
                }
              ],
              signals: [
                {
                  type: Math.random() > 0.5 ? 'buy' : 'sell',
                  symbol: '005380',
                  price: 50000 + Math.random() * 10000,
                  confidence: Math.random() * 40 + 60,
                  timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString()
                },
                {
                  type: Math.random() > 0.5 ? 'buy' : 'sell',
                  symbol: '035720',
                  price: 40000 + Math.random() * 20000,
                  confidence: Math.random() * 30 + 70,
                  timestamp: new Date(Date.now() - Math.random() * 7200000).toISOString()
                }
              ]
            },
            {
              id: 'strategy_2',
              name: '코스닥 가치 성장 전략',
              currentValue: 52000000 + (Math.random() - 0.5) * 1000000,
              dailyPnl: (Math.random() - 0.5) * 500000,
              dailyPnlPercent: (Math.random() - 0.5) * 2,
              totalReturn: 4.2 + (Math.random() - 0.5) * 3,
              positions: [
                {
                  symbol: '036570',
                  name: '엔씨소프트',
                  quantity: 20,
                  currentPrice: 250000 + (Math.random() - 0.5) * 15000,
                  unrealizedPnl: (Math.random() - 0.5) * 400000,
                  unrealizedPnlPercent: (Math.random() - 0.5) * 6
                },
                {
                  symbol: '035900',
                  name: 'JYP Ent.',
                  quantity: 100,
                  currentPrice: 80000 + (Math.random() - 0.5) * 5000,
                  unrealizedPnl: (Math.random() - 0.5) * 200000,
                  unrealizedPnlPercent: (Math.random() - 0.5) * 4
                }
              ],
              signals: [
                {
                  type: Math.random() > 0.5 ? 'buy' : 'sell',
                  symbol: '251270',
                  price: 30000 + Math.random() * 10000,
                  confidence: Math.random() * 25 + 75,
                  timestamp: new Date(Date.now() - Math.random() * 1800000).toISOString()
                }
              ]
            }
          ]
        };
      };

      setStrategyData(generateMockData());
      const interval = setInterval(() => {
        setStrategyData(generateMockData());
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [strategyData]);

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('ko-KR').format(Math.round(num));
  };

  const formatCurrency = (num: number): string => {
    if (num >= 1e8) {
      return `${(num / 1e8).toFixed(1)}억원`;
    } else if (num >= 1e4) {
      return `${(num / 1e4).toFixed(1)}만원`;
    }
    return `${formatNumber(num)}원`;
  };

  const formatPercent = (num: number): string => {
    return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
  };

  const getChangeColor = (value: number): string => {
    if (value > 0) return 'text-red-600'; // 상승 - 빨간색
    if (value < 0) return 'text-blue-600'; // 하락 - 파란색
    return 'text-gray-600'; // 보합 - 회색
  };

  const getChangeIcon = (value: number): string => {
    if (value > 0) return '▲';
    if (value < 0) return '▼';
    return '—';
  };

  const getSignalColor = (type: 'buy' | 'sell'): string => {
    return type === 'buy' ? 'text-red-600 bg-red-50 dark:bg-red-900/20' : 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-orange-600';
  };

  if (!strategyData) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">실시간 전략 데이터 로딩 중...</p>
          </div>
        </div>
      </div>
    );
  }

  const currentStrategy = strategyData.strategies.find(s => s.id === selectedStrategy) || strategyData.strategies[0];

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            실시간 전략 모니터링
          </h2>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs text-gray-500">
              {isConnected ? '실시간' : '연결 끊김'}
            </span>
          </div>
        </div>

        {/* Strategy Selector */}
        <div className="flex flex-wrap gap-2">
          {strategyData.strategies.map((strategy) => (
            <button
              key={strategy.id}
              onClick={() => setSelectedStrategy(strategy.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedStrategy === strategy.id
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              {strategy.name}
            </button>
          ))}
        </div>
      </div>

      {/* Strategy Overview */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-500 mb-1">현재 자산</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {formatCurrency(currentStrategy.currentValue)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500 mb-1">일일 손익</div>
            <div className={`text-lg font-bold ${getChangeColor(currentStrategy.dailyPnl)}`}>
              {getChangeIcon(currentStrategy.dailyPnl)} {formatCurrency(Math.abs(currentStrategy.dailyPnl))}
            </div>
            <div className={`text-xs ${getChangeColor(currentStrategy.dailyPnlPercent)}`}>
              {formatPercent(currentStrategy.dailyPnlPercent)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500 mb-1">총 수익률</div>
            <div className={`text-lg font-bold ${getChangeColor(currentStrategy.totalReturn)}`}>
              {formatPercent(currentStrategy.totalReturn)}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500 mb-1">활성 포지션</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {currentStrategy.positions.length}개
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex">
          {[
            { id: 'overview', name: '개요', count: null },
            { id: 'positions', name: '포지션', count: currentStrategy.positions.length },
            { id: 'signals', name: '시그널', count: currentStrategy.signals.length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.name}
              {tab.count !== null && (
                <span className="ml-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs px-2 py-0.5 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Performance Chart Placeholder */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 h-48 flex items-center justify-center">
              <div className="text-center">
                <div className="text-gray-400 text-sm">실시간 수익률 차트</div>
                <div className="text-xs text-gray-500 mt-1">차트 라이브러리 연동 필요</div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">총 투자금액</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {formatCurrency(currentStrategy.positions.reduce((sum, pos) => sum + (pos.currentPrice * pos.quantity), 0))}
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">미실현 손익</div>
                <div className={`text-sm font-medium ${getChangeColor(
                  currentStrategy.positions.reduce((sum, pos) => sum + pos.unrealizedPnl, 0)
                )}`}>
                  {formatCurrency(Math.abs(currentStrategy.positions.reduce((sum, pos) => sum + pos.unrealizedPnl, 0)))}
                </div>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">최근 시그널</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {currentStrategy.signals.length > 0 
                    ? `${currentStrategy.signals[0].type === 'buy' ? '매수' : '매도'} ${currentStrategy.signals[0].symbol}`
                    : '없음'
                  }
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'positions' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">보유 포지션</h3>
              <span className="text-xs text-gray-500">
                총 {currentStrategy.positions.length}개 종목
              </span>
            </div>
            
            {currentStrategy.positions.map((position) => (
              <div key={position.symbol} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div>
                      <div className="font-medium text-sm text-gray-900 dark:text-white">{position.name}</div>
                      <div className="text-xs text-gray-500">{position.symbol}</div>
                    </div>
                  </div>
                  <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                    보유량: {formatNumber(position.quantity)}주 × {formatNumber(position.currentPrice)}원
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatCurrency(position.currentPrice * position.quantity)}
                  </div>
                  <div className={`text-sm font-medium ${getChangeColor(position.unrealizedPnl)}`}>
                    {getChangeIcon(position.unrealizedPnl)} {formatCurrency(Math.abs(position.unrealizedPnl))}
                  </div>
                  <div className={`text-xs ${getChangeColor(position.unrealizedPnlPercent)}`}>
                    {formatPercent(position.unrealizedPnlPercent)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'signals' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">최근 거래 시그널</h3>
              <span className="text-xs text-gray-500">
                최근 {currentStrategy.signals.length}개 시그널
              </span>
            </div>

            {currentStrategy.signals.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                최근 거래 시그널이 없습니다.
              </div>
            ) : (
              currentStrategy.signals.map((signal, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getSignalColor(signal.type)}`}>
                      {signal.type === 'buy' ? '매수' : '매도'}
                    </span>
                    <div>
                      <div className="font-medium text-sm text-gray-900 dark:text-white">{signal.symbol}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(signal.timestamp).toLocaleString('ko-KR')}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {formatNumber(signal.price)}원
                    </div>
                    <div className={`text-xs ${getConfidenceColor(signal.confidence)}`}>
                      신뢰도 {signal.confidence.toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveStrategyMonitor;