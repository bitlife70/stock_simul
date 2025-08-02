'use client';

import React, { useState, useEffect } from 'react';
import { webSocketService, SystemHealthData } from '@/lib/websocket-service';
import { useTranslation } from 'react-i18next';

interface SystemHealthWidgetProps {
  className?: string;
}

const SystemHealthWidget: React.FC<SystemHealthWidgetProps> = ({ className = '' }) => {
  const { t } = useTranslation();
  const [healthData, setHealthData] = useState<SystemHealthData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [expandedSection, setExpandedSection] = useState<'api' | 'performance' | 'system' | null>(null);

  useEffect(() => {
    const handleHealthData = (data: SystemHealthData) => {
      setHealthData(data);
    };

    const connectWebSocket = async () => {
      try {
        await webSocketService.connect();
        setIsConnected(true);
        webSocketService.subscribe('system_health', handleHealthData);
        webSocketService.setUpdateFrequency('system_health', 5000); // 5초마다 업데이트
      } catch (error) {
        console.error('Failed to connect to WebSocket for system health:', error);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      webSocketService.unsubscribe('system_health', handleHealthData);
    };
  }, []);

  // Mock data generator for development
  useEffect(() => {
    if (!healthData) {
      const generateMockData = (): SystemHealthData => {
        return {
          apiStatus: {
            marketData: Math.random() > 0.1 ? 'online' : Math.random() > 0.5 ? 'degraded' : 'offline',
            backtesting: Math.random() > 0.05 ? 'online' : Math.random() > 0.5 ? 'degraded' : 'offline',
            database: Math.random() > 0.02 ? 'online' : Math.random() > 0.5 ? 'degraded' : 'offline'
          },
          performance: {
            apiResponseTime: Math.random() * 500 + 50,
            dataFeedLatency: Math.random() * 100 + 10,
            cacheHitRate: Math.random() * 20 + 80,
            errorRate: Math.random() * 2
          },
          system: {
            activeUsers: Math.floor(Math.random() * 100) + 10,
            systemLoad: Math.random() * 100,
            memoryUsage: Math.random() * 100,
            diskUsage: Math.random() * 100
          },
          lastUpdated: new Date().toISOString()
        };
      };

      setHealthData(generateMockData());
      const interval = setInterval(() => {
        setHealthData(generateMockData());
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [healthData]);

  const getStatusColor = (status: 'online' | 'offline' | 'degraded'): string => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: 'online' | 'offline' | 'degraded'): string => {
    switch (status) {
      case 'online': return '정상';
      case 'degraded': return '지연';
      case 'offline': return '오프라인';
      default: return '알 수 없음';
    }
  };

  const getStatusTextColor = (status: 'online' | 'offline' | 'degraded'): string => {
    switch (status) {
      case 'online': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'offline': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getPerformanceColor = (value: number, thresholds: { good: number; warning: number }): string => {
    if (value <= thresholds.good) return 'text-green-600';
    if (value <= thresholds.warning) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getUsageColor = (percentage: number): string => {
    if (percentage < 70) return 'bg-green-500';
    if (percentage < 85) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatResponseTime = (ms: number): string => {
    return `${ms.toFixed(0)}ms`;
  };

  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  if (!healthData) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">시스템 상태 로딩 중...</p>
          </div>
        </div>
      </div>
    );
  }

  const overallHealth = Object.values(healthData.apiStatus).every(status => status === 'online') ? 'healthy' : 
                       Object.values(healthData.apiStatus).some(status => status === 'offline') ? 'critical' : 'warning';

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            시스템 상태 모니터링
          </h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                overallHealth === 'healthy' ? 'bg-green-500' : 
                overallHealth === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
              }`}></div>
              <span className={`text-sm font-medium ${
                overallHealth === 'healthy' ? 'text-green-600' : 
                overallHealth === 'warning' ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {overallHealth === 'healthy' ? '정상' : 
                 overallHealth === 'warning' ? '주의' : '위험'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-xs text-gray-500">
                {new Date(healthData.lastUpdated).toLocaleTimeString('ko-KR')}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* API Status Section */}
        <div className="mb-6">
          <button
            onClick={() => setExpandedSection(expandedSection === 'api' ? null : 'api')}
            className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">API 서비스 상태</h3>
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                {Object.values(healthData.apiStatus).map((status, index) => (
                  <div key={index} className={`w-2 h-2 rounded-full ${getStatusColor(status)}`}></div>
                ))}
              </div>
              <span className="text-xs text-gray-500">
                {expandedSection === 'api' ? '▼' : '▶'}
              </span>
            </div>
          </button>

          {expandedSection === 'api' && (
            <div className="mt-3 space-y-2">
              <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-800 rounded border">
                <span className="text-sm text-gray-700 dark:text-gray-300">마켓 데이터 API</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(healthData.apiStatus.marketData)}`}></div>
                  <span className={`text-xs font-medium ${getStatusTextColor(healthData.apiStatus.marketData)}`}>
                    {getStatusText(healthData.apiStatus.marketData)}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-800 rounded border">
                <span className="text-sm text-gray-700 dark:text-gray-300">백테스팅 엔진</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(healthData.apiStatus.backtesting)}`}></div>
                  <span className={`text-xs font-medium ${getStatusTextColor(healthData.apiStatus.backtesting)}`}>
                    {getStatusText(healthData.apiStatus.backtesting)}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 bg-white dark:bg-gray-800 rounded border">
                <span className="text-sm text-gray-700 dark:text-gray-300">데이터베이스</span>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(healthData.apiStatus.database)}`}></div>
                  <span className={`text-xs font-medium ${getStatusTextColor(healthData.apiStatus.database)}`}>
                    {getStatusText(healthData.apiStatus.database)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Performance Metrics Section */}
        <div className="mb-6">
          <button
            onClick={() => setExpandedSection(expandedSection === 'performance' ? null : 'performance')}
            className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">성능 지표</h3>
            <span className="text-xs text-gray-500">
              {expandedSection === 'performance' ? '▼' : '▶'}
            </span>
          </button>

          {expandedSection === 'performance' && (
            <div className="mt-3 grid grid-cols-2 gap-3">
              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="text-xs text-gray-500 mb-1">API 응답시간</div>
                <div className={`text-sm font-medium ${getPerformanceColor(
                  healthData.performance.apiResponseTime, 
                  { good: 100, warning: 300 }
                )}`}>
                  {formatResponseTime(healthData.performance.apiResponseTime)}
                </div>
              </div>
              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="text-xs text-gray-500 mb-1">데이터 피드 지연</div>
                <div className={`text-sm font-medium ${getPerformanceColor(
                  healthData.performance.dataFeedLatency, 
                  { good: 50, warning: 100 }
                )}`}>
                  {formatResponseTime(healthData.performance.dataFeedLatency)}
                </div>
              </div>
              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="text-xs text-gray-500 mb-1">캐시 적중률</div>
                <div className={`text-sm font-medium ${getPerformanceColor(
                  100 - healthData.performance.cacheHitRate, 
                  { good: 10, warning: 30 }
                )}`}>
                  {formatPercentage(healthData.performance.cacheHitRate)}
                </div>
              </div>
              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="text-xs text-gray-500 mb-1">오류율</div>
                <div className={`text-sm font-medium ${getPerformanceColor(
                  healthData.performance.errorRate, 
                  { good: 1, warning: 5 }
                )}`}>
                  {formatPercentage(healthData.performance.errorRate)}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* System Resources Section */}
        <div className="mb-6">
          <button
            onClick={() => setExpandedSection(expandedSection === 'system' ? null : 'system')}
            className="w-full flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">시스템 리소스</h3>
            <span className="text-xs text-gray-500">
              {expandedSection === 'system' ? '▼' : '▶'}
            </span>
          </button>

          {expandedSection === 'system' && (
            <div className="mt-3 space-y-3">
              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">활성 사용자</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {healthData.system.activeUsers}명
                  </span>
                </div>
              </div>
              
              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">시스템 로드</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatPercentage(healthData.system.systemLoad)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getUsageColor(healthData.system.systemLoad)}`}
                    style={{ width: `${Math.min(healthData.system.systemLoad, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">메모리 사용량</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatPercentage(healthData.system.memoryUsage)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getUsageColor(healthData.system.memoryUsage)}`}
                    style={{ width: `${Math.min(healthData.system.memoryUsage, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-3 bg-white dark:bg-gray-800 rounded border">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">디스크 사용량</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatPercentage(healthData.system.diskUsage)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${getUsageColor(healthData.system.diskUsage)}`}
                    style={{ width: `${Math.min(healthData.system.diskUsage, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Quick Summary */}
        {expandedSection === null && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">API 응답</div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {formatResponseTime(healthData.performance.apiResponseTime)}
              </div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">오류율</div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {formatPercentage(healthData.performance.errorRate)}
              </div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">활성 사용자</div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {healthData.system.activeUsers}명
              </div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">메모리</div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {formatPercentage(healthData.system.memoryUsage)}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemHealthWidget;