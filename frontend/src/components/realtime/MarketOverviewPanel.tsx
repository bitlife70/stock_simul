'use client';

import React, { useState, useEffect } from 'react';
import { webSocketService, RealTimeMarketData } from '@/lib/websocket-service';
import { useTranslation } from 'react-i18next';

interface MarketOverviewPanelProps {
  className?: string;
}

const MarketOverviewPanel: React.FC<MarketOverviewPanelProps> = ({ className = '' }) => {
  const { t } = useTranslation();
  const [marketData, setMarketData] = useState<RealTimeMarketData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [marketStatus, setMarketStatus] = useState<string>('closed');

  useEffect(() => {
    const handleMarketData = (data: RealTimeMarketData) => {
      setMarketData(data);
    };

    const connectWebSocket = async () => {
      try {
        await webSocketService.connect();
        setIsConnected(true);
        webSocketService.subscribe('market_data', handleMarketData);
        webSocketService.setUpdateFrequency('market_data', 1000); // 1초마다 업데이트
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        setIsConnected(false);
      }
    };

    const updateMarketStatus = () => {
      setMarketStatus(webSocketService.getMarketStatus());
    };

    connectWebSocket();
    updateMarketStatus();
    
    // 시장 상태를 1분마다 업데이트
    const statusInterval = setInterval(updateMarketStatus, 60000);

    return () => {
      webSocketService.unsubscribe('market_data', handleMarketData);
      clearInterval(statusInterval);
    };
  }, []);

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('ko-KR').format(num);
  };

  const formatCurrency = (num: number): string => {
    if (num >= 1e12) {
      return `${(num / 1e12).toFixed(1)}조원`;
    } else if (num >= 1e8) {
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

  const getMarketStatusDisplay = (status: string) => {
    const statusMap: Record<string, { text: string; color: string; dot: string }> = {
      'pre_market': { text: '장전거래', color: 'text-yellow-600', dot: 'bg-yellow-500' },
      'open': { text: '장중', color: 'text-green-600', dot: 'bg-green-500' },
      'lunch_break': { text: '점심시간', color: 'text-orange-600', dot: 'bg-orange-500' },
      'post_market': { text: '장후거래', color: 'text-purple-600', dot: 'bg-purple-500' },
      'closed': { text: '장마감', color: 'text-gray-600', dot: 'bg-gray-500' }
    };
    return statusMap[status] || statusMap['closed'];
  };

  if (!marketData) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">시장 데이터 로딩 중...</p>
          </div>
        </div>
      </div>
    );
  }

  const statusInfo = getMarketStatusDisplay(marketStatus);

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            한국 증시 현황
          </h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${statusInfo.dot}`}></div>
              <span className={`text-sm font-medium ${statusInfo.color}`}>
                {statusInfo.text}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-xs text-gray-500">
                {isConnected ? '실시간' : '연결 끊김'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* 주요 지수 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* KOSPI */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">KOSPI</h3>
              <span className="text-xs text-gray-500">
                {new Date(marketData.timestamp).toLocaleTimeString('ko-KR')}
              </span>
            </div>
            <div className="flex items-end space-x-3">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatNumber(marketData.kospi.index)}
              </span>
              <div className="flex flex-col">
                <span className={`text-sm font-medium ${getChangeColor(marketData.kospi.change)}`}>
                  {marketData.kospi.change >= 0 ? '+' : ''}{formatNumber(marketData.kospi.change)}
                </span>
                <span className={`text-sm ${getChangeColor(marketData.kospi.changePercent)}`}>
                  {formatPercent(marketData.kospi.changePercent)}
                </span>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
              <div>거래량: {formatNumber(marketData.kospi.volume)}</div>
              <div>거래대금: {formatCurrency(marketData.kospi.value)}</div>
            </div>
          </div>

          {/* KOSDAQ */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">KOSDAQ</h3>
              <span className="text-xs text-gray-500">
                {new Date(marketData.timestamp).toLocaleTimeString('ko-KR')}
              </span>
            </div>
            <div className="flex items-end space-x-3">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatNumber(marketData.kosdaq.index)}
              </span>
              <div className="flex flex-col">
                <span className={`text-sm font-medium ${getChangeColor(marketData.kosdaq.change)}`}>
                  {marketData.kosdaq.change >= 0 ? '+' : ''}{formatNumber(marketData.kosdaq.change)}
                </span>
                <span className={`text-sm ${getChangeColor(marketData.kosdaq.changePercent)}`}>
                  {formatPercent(marketData.kosdaq.changePercent)}
                </span>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
              <div>거래량: {formatNumber(marketData.kosdaq.volume)}</div>
              <div>거래대금: {formatCurrency(marketData.kosdaq.value)}</div>
            </div>
          </div>
        </div>

        {/* 시장 동향 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* 시장 강도 */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">시장 강도</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-red-600">상승</span>
                <span className="text-xs font-medium">{marketData.marketBreadth.up}개</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-blue-600">하락</span>
                <span className="text-xs font-medium">{marketData.marketBreadth.down}개</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-gray-600">보합</span>
                <span className="text-xs font-medium">{marketData.marketBreadth.unchanged}개</span>
              </div>
              <div className="border-t border-gray-300 dark:border-gray-600 pt-2 mt-2">
                <div className="flex justify-between">
                  <span className="text-xs text-red-600">상한가</span>
                  <span className="text-xs font-medium text-red-600">{marketData.marketBreadth.upperLimit}개</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs text-blue-600">하한가</span>
                  <span className="text-xs font-medium text-blue-600">{marketData.marketBreadth.lowerLimit}개</span>
                </div>
              </div>
            </div>
          </div>

          {/* 외국인 순매수 */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">외국인 순매수</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-gray-600">KOSPI</span>
                <span className={`text-xs font-medium ${getChangeColor(marketData.foreignFlow.kospiNet)}`}>
                  {formatCurrency(marketData.foreignFlow.kospiNet)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-gray-600">KOSDAQ</span>
                <span className={`text-xs font-medium ${getChangeColor(marketData.foreignFlow.kosdaqNet)}`}>
                  {formatCurrency(marketData.foreignFlow.kosdaqNet)}
                </span>
              </div>
              <div className="border-t border-gray-300 dark:border-gray-600 pt-2 mt-2">
                <div className="flex justify-between">
                  <span className="text-xs text-gray-900 dark:text-white font-medium">합계</span>
                  <span className={`text-xs font-bold ${getChangeColor(marketData.foreignFlow.totalNet)}`}>
                    {formatCurrency(marketData.foreignFlow.totalNet)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 시장 심리 */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">시장 심리</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-gray-600">공포탐욕지수</span>
                <span className="text-xs font-medium">
                  {marketData.marketSentiment.fearGreedIndex.toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-gray-600">VIX KOSPI</span>
                <span className="text-xs font-medium">
                  {marketData.marketSentiment.vixKospi.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-gray-600">풋콜비율</span>
                <span className="text-xs font-medium">
                  {marketData.marketSentiment.putCallRatio.toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 프로그램 매매 */}
        <div className="mt-6">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">프로그램 매매</h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-xs text-gray-600 mb-1">매수</div>
                <div className="text-sm font-medium text-red-600">
                  {formatCurrency(marketData.programTrading.buyValue)}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-600 mb-1">매도</div>
                <div className="text-sm font-medium text-blue-600">
                  {formatCurrency(marketData.programTrading.sellValue)}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-600 mb-1">순매수</div>
                <div className={`text-sm font-bold ${getChangeColor(marketData.programTrading.netValue)}`}>
                  {formatCurrency(marketData.programTrading.netValue)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketOverviewPanel;