'use client';

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import MarketOverviewPanel from './MarketOverviewPanel';
import TopMoversWidget from './TopMoversWidget';
import LiveStrategyMonitor from './LiveStrategyMonitor';
import SystemHealthWidget from './SystemHealthWidget';
import { webSocketService, MockDataGenerator } from '@/lib/websocket-service';
import { MarketAlert } from '@/types';

interface MarketMonitoringDashboardProps {
  className?: string;
}

const MarketMonitoringDashboard: React.FC<MarketMonitoringDashboardProps> = ({ className = '' }) => {
  const { t } = useTranslation();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5); // seconds
  const [layoutMode, setLayoutMode] = useState<'grid' | 'compact' | 'focused'>('grid');
  const [alerts, setAlerts] = useState<MarketAlert[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [mockDataGenerator] = useState(new MockDataGenerator());

  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        await webSocketService.connect();
        setIsConnected(true);
        
        // Start mock data generation for development
        mockDataGenerator.start();
        
        // Subscribe to market alerts
        webSocketService.subscribe('market_alerts', handleMarketAlerts);
        
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error);
        setIsConnected(false);
      }
    };

    const handleMarketAlerts = (alertData: MarketAlert[]) => {
      setAlerts(alertData);
      
      // Play sound for high severity alerts if enabled
      if (soundEnabled && alertData.some(alert => alert.severity === 'high' || alert.severity === 'critical')) {
        playAlertSound();
      }
    };

    connectWebSocket();

    return () => {
      mockDataGenerator.stop();
      webSocketService.unsubscribe('market_alerts', handleMarketAlerts);
    };
  }, [mockDataGenerator, soundEnabled]);

  const playAlertSound = () => {
    // Create a simple beep sound
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  };

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
    setIsFullscreen(!isFullscreen);
  };

  const refreshData = () => {
    // Request immediate data refresh from all services
    webSocketService.requestUpdate('market_data');
    webSocketService.requestUpdate('top_movers');
    webSocketService.requestUpdate('strategy_updates');
    webSocketService.requestUpdate('system_health');
  };

  const exportData = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      marketStatus: webSocketService.getMarketStatus(),
      isConnected,
      alerts: alerts.length,
      exportedAt: new Date().toLocaleString('ko-KR')
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `market_monitor_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const getLayoutClass = () => {
    switch (layoutMode) {
      case 'compact':
        return 'grid-cols-1 lg:grid-cols-2 gap-4';
      case 'focused':
        return 'grid-cols-1 gap-6';
      default:
        return 'grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6';
    }
  };

  const getMarketStatusDisplay = () => {
    const status = webSocketService.getMarketStatus();
    const statusMap: Record<string, { text: string; color: string; description: string }> = {
      'pre_market': { 
        text: '장전거래', 
        color: 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20', 
        description: '정규장 시작 전 거래 시간입니다.' 
      },
      'open': { 
        text: '정규장 거래중', 
        color: 'text-green-600 bg-green-50 dark:bg-green-900/20', 
        description: '정규장 거래가 진행 중입니다.' 
      },
      'lunch_break': { 
        text: '점심시간', 
        color: 'text-orange-600 bg-orange-50 dark:bg-orange-900/20', 
        description: '점심시간 거래 중단 중입니다.' 
      },
      'post_market': { 
        text: '장후거래', 
        color: 'text-purple-600 bg-purple-50 dark:bg-purple-900/20', 
        description: '정규장 종료 후 거래 시간입니다.' 
      },
      'closed': { 
        text: '장마감', 
        color: 'text-gray-600 bg-gray-50 dark:bg-gray-900/20', 
        description: '거래가 종료되었습니다.' 
      }
    };
    return statusMap[status] || statusMap['closed'];
  };

  const marketStatus = getMarketStatusDisplay();

  return (
    <div className={`min-h-screen bg-gray-100 dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-6">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                실시간 시장 모니터링
              </h1>
              
              {/* Market Status Indicator */}
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${marketStatus.color}`}>
                {marketStatus.text}
              </div>
              
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {isConnected ? '실시간 연결됨' : '연결 끊김'}
                </span>
              </div>
            </div>
            
            {/* Controls */}
            <div className="flex items-center space-x-4">
              {/* Alert Counter */}
              {alerts.length > 0 && (
                <div className="flex items-center space-x-2">
                  <div className="bg-red-100 dark:bg-red-900/20 text-red-600 text-xs px-2 py-1 rounded-full">
                    알림 {alerts.length}개
                  </div>
                </div>
              )}
              
              {/* Layout Mode Selector */}
              <select
                value={layoutMode}
                onChange={(e) => setLayoutMode(e.target.value as any)}
                className="text-sm border border-gray-300 dark:border-gray-600 rounded-md px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="grid">그리드 뷰</option>
                <option value="compact">컴팩트 뷰</option>
                <option value="focused">포커스 뷰</option>
              </select>
              
              {/* Sound Toggle */}
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className={`p-2 rounded-md ${
                  soundEnabled 
                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' 
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                } hover:bg-opacity-80 transition-colors`}
                title={soundEnabled ? '알림음 끄기' : '알림음 켜기'}
              >
                {soundEnabled ? '🔊' : '🔇'}
              </button>
              
              {/* Refresh Button */}
              <button
                onClick={refreshData}
                className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="데이터 새로고침"
              >
                🔄
              </button>
              
              {/* Export Button */}
              <button
                onClick={exportData}
                className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="데이터 내보내기"
              >
                📊
              </button>
              
              {/* Fullscreen Toggle */}
              <button
                onClick={toggleFullscreen}
                className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title={isFullscreen ? '전체화면 종료' : '전체화면'}
              >
                {isFullscreen ? '🗗' : '🗖'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Market Status Description */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>현재 시장 상태:</strong> {marketStatus.description}
            <span className="ml-4 text-xs text-blue-600 dark:text-blue-300">
              마지막 업데이트: {new Date().toLocaleString('ko-KR')}
            </span>
          </p>
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className={`grid ${getLayoutClass()}`}>
          {/* Market Overview - Always visible */}
          <div className={layoutMode === 'focused' ? 'col-span-full' : 'lg:col-span-2'}>
            <MarketOverviewPanel />
          </div>
          
          {/* Top Movers */}
          <div className={layoutMode === 'compact' ? 'lg:col-span-1' : ''}>
            <TopMoversWidget />
          </div>
          
          {/* Live Strategy Monitor */}
          <div className={layoutMode === 'grid' ? 'lg:col-span-2' : layoutMode === 'focused' ? 'col-span-full' : ''}>
            <LiveStrategyMonitor />
          </div>
          
          {/* System Health */}
          <div className={layoutMode === 'compact' ? 'lg:col-span-1' : ''}>
            <SystemHealthWidget />
          </div>
        </div>
      </div>

      {/* Alert Panel - Slide in from bottom when alerts exist */}
      {alerts.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                활성 알림 ({alerts.length}개)
              </h3>
              <button
                onClick={() => setAlerts([])}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                모두 해제
              </button>
            </div>
            <div className="flex space-x-4 overflow-x-auto">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className={`flex-shrink-0 p-3 rounded-lg border-l-4 ${
                    alert.severity === 'critical' 
                      ? 'bg-red-50 border-red-500 dark:bg-red-900/20'
                      : alert.severity === 'high'
                      ? 'bg-yellow-50 border-yellow-500 dark:bg-yellow-900/20'
                      : 'bg-blue-50 border-blue-500 dark:bg-blue-900/20'
                  }`}
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {alert.title}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {alert.message}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(alert.timestamp).toLocaleTimeString('ko-KR')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketMonitoringDashboard;