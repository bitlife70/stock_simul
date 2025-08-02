'use client';

import React, { useState, useEffect } from 'react';
import { webSocketService, TopMoversData } from '@/lib/websocket-service';
import { useTranslation } from 'react-i18next';

interface TopMoversWidgetProps {
  className?: string;
}

const TopMoversWidget: React.FC<TopMoversWidgetProps> = ({ className = '' }) => {
  const { t } = useTranslation();
  const [topMoversData, setTopMoversData] = useState<TopMoversData | null>(null);
  const [activeTab, setActiveTab] = useState<'upper_limit' | 'lower_limit' | 'volume' | 'sector'>('upper_limit');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const handleTopMoversData = (data: TopMoversData) => {
      setTopMoversData(data);
    };

    const connectWebSocket = async () => {
      try {
        await webSocketService.connect();
        setIsConnected(true);
        webSocketService.subscribe('top_movers', handleTopMoversData);
        webSocketService.setUpdateFrequency('top_movers', 5000); // 5초마다 업데이트
      } catch (error) {
        console.error('Failed to connect to WebSocket for top movers:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      webSocketService.unsubscribe('top_movers', handleTopMoversData);
    };
  }, []);

  // Mock data generator for development
  useEffect(() => {
    if (!topMoversData) {
      const generateMockData = (): TopMoversData => {
        const generateStocks = (count: number, basePrice: number = 10000) => 
          Array.from({ length: count }, (_, i) => ({
            symbol: `A${String(i + 1).padStart(6, '0')}`,
            name: `종목${i + 1}`,
            price: basePrice + Math.random() * 50000,
            change: (Math.random() - 0.5) * 2000,
            changePercent: (Math.random() - 0.5) * 20,
            volume: Math.floor(Math.random() * 10000000),
            turnoverRatio: Math.random() * 100
          }));

        return {
          upperLimit: generateStocks(10, 30000),
          lowerLimit: generateStocks(10, 5000),
          volumeLeaders: generateStocks(15, 20000),
          sectorPerformance: [
            { sector: 'technology', sectorKr: '기술주', change: 120, changePercent: 2.1, marketCap: 500000000000000 },
            { sector: 'finance', sectorKr: '금융', change: -80, changePercent: -1.3, marketCap: 300000000000000 },
            { sector: 'manufacturing', sectorKr: '제조업', change: 45, changePercent: 0.8, marketCap: 450000000000000 },
            { sector: 'consumer', sectorKr: '소비재', change: -25, changePercent: -0.4, marketCap: 200000000000000 },
            { sector: 'healthcare', sectorKr: '헬스케어', change: 90, changePercent: 1.8, marketCap: 150000000000000 },
          ]
        };
      };

      setTopMoversData(generateMockData());
      const interval = setInterval(() => {
        setTopMoversData(generateMockData());
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [topMoversData]);

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('ko-KR').format(Math.round(num));
  };

  const formatVolume = (volume: number): string => {
    if (volume >= 1e8) {
      return `${(volume / 1e8).toFixed(1)}억`;
    } else if (volume >= 1e4) {
      return `${(volume / 1e4).toFixed(1)}만`;
    }
    return formatNumber(volume);
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

  if (!topMoversData) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">상위 종목 데이터 로딩 중...</p>
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'upper_limit', name: '상한가', count: topMoversData.upperLimit.length },
    { id: 'lower_limit', name: '하한가', count: topMoversData.lowerLimit.length },
    { id: 'volume', name: '거래량 상위', count: topMoversData.volumeLeaders.length },
    { id: 'sector', name: '업종별', count: topMoversData.sectorPerformance.length }
  ] as const;

  const renderStockList = (stocks: any[], showTurnover: boolean = false) => (
    <div className="space-y-2">
      {stocks.slice(0, 10).map((stock, index) => (
        <div key={stock.symbol} className="flex items-center justify-between py-2 px-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
          <div className="flex items-center space-x-3">
            <span className="text-xs text-gray-500 w-6 text-center">{index + 1}</span>
            <div>
              <div className="font-medium text-sm text-gray-900 dark:text-white">{stock.name}</div>
              <div className="text-xs text-gray-500">{stock.symbol}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {formatNumber(stock.price)}원
            </div>
            <div className="flex items-center space-x-1">
              <span className={`text-xs ${getChangeColor(stock.change)}`}>
                {getChangeIcon(stock.change)} {formatPercent(stock.changePercent)}
              </span>
            </div>
            <div className="text-xs text-gray-500">
              {showTurnover ? `회전율 ${stock.turnoverRatio?.toFixed(1)}%` : `거래량 ${formatVolume(stock.volume)}`}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderSectorPerformance = () => (
    <div className="space-y-2">
      {topMoversData.sectorPerformance.map((sector, index) => (
        <div key={sector.sector} className="flex items-center justify-between py-2 px-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
          <div className="flex items-center space-x-3">
            <span className="text-xs text-gray-500 w-6 text-center">{index + 1}</span>
            <div>
              <div className="font-medium text-sm text-gray-900 dark:text-white">{sector.sectorKr}</div>
              <div className="text-xs text-gray-500">
                시총 {(sector.marketCap / 1e12).toFixed(1)}조원
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-sm font-medium ${getChangeColor(sector.change)}`}>
              {getChangeIcon(sector.change)} {formatPercent(sector.changePercent)}
            </div>
            <div className="text-xs text-gray-500">
              {sector.change >= 0 ? '+' : ''}{formatNumber(sector.change)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            상위 종목 & 업종 동향
          </h2>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-xs text-gray-500">
              {isConnected ? '실시간' : '연결 끊김'}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-shrink-0 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.name}
              <span className="ml-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs px-2 py-0.5 rounded-full">
                {tab.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="max-h-96 overflow-y-auto">
          {activeTab === 'upper_limit' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">상한가 종목</h3>
                <span className="text-xs text-red-600 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded">
                  {topMoversData.upperLimit.length}개 종목
                </span>
              </div>
              {renderStockList(topMoversData.upperLimit)}
            </div>
          )}

          {activeTab === 'lower_limit' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">하한가 종목</h3>
                <span className="text-xs text-blue-600 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">
                  {topMoversData.lowerLimit.length}개 종목
                </span>
              </div>
              {renderStockList(topMoversData.lowerLimit)}
            </div>
          )}

          {activeTab === 'volume' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">거래량 상위 종목</h3>
                <span className="text-xs text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">
                  상위 {Math.min(10, topMoversData.volumeLeaders.length)}개
                </span>
              </div>
              {renderStockList(topMoversData.volumeLeaders, true)}
            </div>
          )}

          {activeTab === 'sector' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">업종별 등락률</h3>
                <span className="text-xs text-purple-600 bg-purple-50 dark:bg-purple-900/20 px-2 py-1 rounded">
                  주요 {topMoversData.sectorPerformance.length}개 업종
                </span>
              </div>
              {renderSectorPerformance()}
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {activeTab !== 'sector' && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-xs text-gray-500">평균 등락률</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {(() => {
                    const stocks = activeTab === 'upper_limit' 
                      ? topMoversData.upperLimit 
                      : activeTab === 'lower_limit' 
                      ? topMoversData.lowerLimit 
                      : topMoversData.volumeLeaders;
                    const avgChange = stocks.reduce((sum, stock) => sum + stock.changePercent, 0) / stocks.length;
                    return formatPercent(avgChange);
                  })()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">총 거래량</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {(() => {
                    const stocks = activeTab === 'upper_limit' 
                      ? topMoversData.upperLimit 
                      : activeTab === 'lower_limit' 
                      ? topMoversData.lowerLimit 
                      : topMoversData.volumeLeaders;
                    const totalVolume = stocks.reduce((sum, stock) => sum + stock.volume, 0);
                    return formatVolume(totalVolume);
                  })()}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">평균 주가</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {(() => {
                    const stocks = activeTab === 'upper_limit' 
                      ? topMoversData.upperLimit 
                      : activeTab === 'lower_limit' 
                      ? topMoversData.lowerLimit 
                      : topMoversData.volumeLeaders;
                    const avgPrice = stocks.reduce((sum, stock) => sum + stock.price, 0) / stocks.length;
                    return `${formatNumber(avgPrice)}원`;
                  })()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TopMoversWidget;