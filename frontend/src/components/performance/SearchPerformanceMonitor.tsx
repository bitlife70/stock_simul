/**
 * Search Performance Monitor Component
 * Real-time monitoring and analytics for search performance
 */

'use client';

import { useState, useEffect } from 'react';
import { Activity, TrendingUp, Clock, Database, Search, BarChart3, AlertTriangle } from 'lucide-react';
import { useOptimizedSearch } from '@/hooks/useOptimizedSearch';

interface PerformanceMetric {
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'stable';
  status?: 'good' | 'warning' | 'error';
  description: string;
}

export default function SearchPerformanceMonitor() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [liveMetrics, setLiveMetrics] = useState<PerformanceMetric[]>([]);
  
  const { getPerformanceStats, metrics } = useOptimizedSearch({
    enableAnalytics: true
  });

  useEffect(() => {
    updateMetrics();
    const interval = setInterval(updateMetrics, 5000); // 5초마다 업데이트
    
    return () => clearInterval(interval);
  }, []);

  const updateMetrics = () => {
    const stats = getPerformanceStats();
    if (!stats) return;

    const newMetrics: PerformanceMetric[] = [
      {
        label: '평균 검색 시간',
        value: `${stats.averageSearchTime.toFixed(1)}ms`,
        trend: stats.averageSearchTime < 30 ? 'stable' : stats.averageSearchTime < 100 ? 'up' : 'down',
        status: stats.averageSearchTime < 50 ? 'good' : stats.averageSearchTime < 100 ? 'warning' : 'error',
        description: '목표: < 50ms'
      },
      {
        label: '최대 검색 시간',
        value: `${stats.maxSearchTime.toFixed(1)}ms`,
        status: stats.maxSearchTime < 100 ? 'good' : stats.maxSearchTime < 200 ? 'warning' : 'error',
        description: '최대 응답 시간'
      },
      {
        label: '캐시 히트율',
        value: `${(stats.cacheHitRate * 100).toFixed(1)}%`,
        trend: stats.cacheHitRate > 0.7 ? 'up' : stats.cacheHitRate > 0.4 ? 'stable' : 'down',
        status: stats.cacheHitRate > 0.6 ? 'good' : stats.cacheHitRate > 0.3 ? 'warning' : 'error',
        description: '캐시 효율성'
      },
      {
        label: '평균 결과 수',
        value: `${stats.averageResultCount.toFixed(1)}개`,
        status: 'good',
        description: '검색당 평균 결과'
      },
      {
        label: '총 검색 수',
        value: stats.totalSearches.toString(),
        status: 'good',
        description: '누적 검색 횟수'
      },
      {
        label: '인덱스 크기',
        value: `${stats.indexStats.totalStocks}개`,
        status: 'good',
        description: '인덱싱된 종목 수'
      },
      {
        label: '메모리 사용량',
        value: `${stats.indexStats.memoryUsageMB.toFixed(1)}MB`,
        status: stats.indexStats.memoryUsageMB < 10 ? 'good' : stats.indexStats.memoryUsageMB < 20 ? 'warning' : 'error',
        description: '목표: < 10MB'
      }
    ];

    setLiveMetrics(newMetrics);
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'good': return 'text-green-600 bg-green-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'error': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-3 w-3 text-green-500" />;
      case 'down': return <AlertTriangle className="h-3 w-3 text-red-500" />;
      default: return null;
    }
  };

  const getOverallStatus = () => {
    const errorCount = liveMetrics.filter(m => m.status === 'error').length;
    const warningCount = liveMetrics.filter(m => m.status === 'warning').length;
    
    if (errorCount > 0) return { status: 'error', message: `${errorCount}개 문제 발견` };
    if (warningCount > 0) return { status: 'warning', message: `${warningCount}개 주의사항` };
    return { status: 'good', message: '모든 지표 정상' };
  };

  const overallStatus = getOverallStatus();

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* 컴팩트 모니터 */}
      {!isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg shadow-lg transition-all duration-200 hover:shadow-xl ${
            getStatusColor(overallStatus.status)
          }`}
        >
          <Activity className="h-4 w-4" />
          <span className="text-sm font-medium">검색 성능</span>
          {metrics && (
            <span className="text-xs opacity-75">
              {metrics.searchTime.toFixed(0)}ms
            </span>
          )}
        </button>
      )}

      {/* 확장된 모니터 */}
      {isExpanded && (
        <div className="bg-white rounded-lg shadow-xl border border-gray-200 p-4 w-80 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">검색 성능 모니터</h3>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-400 hover:text-gray-600 text-xl"
            >
              ×
            </button>
          </div>

          {/* 전체 상태 */}
          <div className={`mb-4 p-3 rounded-lg ${getStatusColor(overallStatus.status)}`}>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                overallStatus.status === 'good' ? 'bg-green-500' :
                overallStatus.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="font-medium">{overallStatus.message}</span>
            </div>
          </div>

          {/* 실시간 메트릭 */}
          <div className="space-y-3">
            {liveMetrics.map((metric, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">
                      {metric.label}
                    </span>
                    {getTrendIcon(metric.trend)}
                  </div>
                  <div className="text-xs text-gray-500">{metric.description}</div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(metric.status)}`}>
                  {metric.value}
                </div>
              </div>
            ))}
          </div>

          {/* 현재 검색 정보 */}
          {metrics && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-2 mb-2">
                <Search className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">현재 검색</span>
              </div>
              <div className="text-xs text-gray-600 space-y-1">
                <div>응답 시간: {metrics.searchTime.toFixed(2)}ms</div>
                <div>결과 수: {metrics.resultCount}개</div>
                <div>캐시: {metrics.cacheHit ? '히트' : '미스'}</div>
              </div>
            </div>
          )}

          {/* 액션 버튼들 */}
          <div className="mt-4 flex space-x-2">
            <button
              onClick={updateMetrics}
              className="flex-1 px-3 py-2 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              새로고침
            </button>
            <button
              onClick={() => {
                console.log('Performance Stats:', getPerformanceStats());
                alert('성능 데이터가 콘솔에 출력되었습니다.');
              }}
              className="flex-1 px-3 py-2 text-xs bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              로그 출력
            </button>
          </div>

          {/* 성능 팁 */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-start space-x-2">
              <BarChart3 className="h-4 w-4 text-blue-600 mt-0.5" />
              <div className="text-xs text-blue-700">
                <div className="font-medium mb-1">최적화 팁</div>
                <ul className="space-y-1 text-blue-600">
                  <li>• 평균 검색 시간 50ms 미만 유지</li>
                  <li>• 캐시 히트율 60% 이상 권장</li>
                  <li>• 메모리 사용량 10MB 미만 권장</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}