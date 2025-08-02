'use client';

import { useState, useEffect, useRef } from 'react';
import { Activity, Zap, Database, Clock } from 'lucide-react';

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  status: 'good' | 'warning' | 'error';
  threshold: number;
}

interface PerformanceMonitorProps {
  searchTime?: number;
  totalStocks?: number;
  resultsCount?: number;
  isVisible?: boolean;
  className?: string;
}

export default function PerformanceMonitor({
  searchTime = 0,
  totalStocks = 0,
  resultsCount = 0,
  isVisible = true,
  className = ''
}: PerformanceMonitorProps) {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [fps, setFps] = useState(0);
  const [memoryUsage, setMemoryUsage] = useState(0);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());

  // FPS monitoring
  useEffect(() => {
    let animationId: number;

    const updateFPS = () => {
      frameCountRef.current++;
      const now = performance.now();
      
      if (now - lastTimeRef.current >= 1000) {
        setFps(Math.round((frameCountRef.current * 1000) / (now - lastTimeRef.current)));
        frameCountRef.current = 0;
        lastTimeRef.current = now;
      }
      
      animationId = requestAnimationFrame(updateFPS);
    };

    if (isVisible) {
      updateFPS();
    }

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isVisible]);

  // Memory usage monitoring
  useEffect(() => {
    const updateMemoryUsage = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        setMemoryUsage(Math.round(memory.usedJSHeapSize / 1024 / 1024));
      }
    };

    const interval = setInterval(updateMemoryUsage, 1000);
    updateMemoryUsage();

    return () => clearInterval(interval);
  }, []);

  // Update metrics when search parameters change
  useEffect(() => {
    const newMetrics: PerformanceMetric[] = [
      {
        name: 'Search Time',
        value: searchTime,
        unit: 'ms',
        status: searchTime <= 50 ? 'good' : searchTime <= 100 ? 'warning' : 'error',
        threshold: 50
      },
      {
        name: 'Dataset Size',
        value: totalStocks,
        unit: 'stocks',
        status: 'good',
        threshold: 0
      },
      {
        name: 'Results Found',
        value: resultsCount,
        unit: 'results',
        status: 'good',
        threshold: 0
      },
      {
        name: 'Frame Rate',
        value: fps,
        unit: 'fps',
        status: fps >= 55 ? 'good' : fps >= 30 ? 'warning' : 'error',
        threshold: 55
      },
      {
        name: 'Memory Usage',
        value: memoryUsage,
        unit: 'MB',
        status: memoryUsage <= 50 ? 'good' : memoryUsage <= 100 ? 'warning' : 'error',
        threshold: 50
      }
    ];

    setMetrics(newMetrics);
  }, [searchTime, totalStocks, resultsCount, fps, memoryUsage]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (name: string) => {
    switch (name) {
      case 'Search Time':
        return <Zap className="h-3 w-3" />;
      case 'Dataset Size':
        return <Database className="h-3 w-3" />;
      case 'Results Found':
        return <Clock className="h-3 w-3" />;
      case 'Frame Rate':
        return <Activity className="h-3 w-3" />;
      case 'Memory Usage':
        return <Activity className="h-3 w-3" />;
      default:
        return <Activity className="h-3 w-3" />;
    }
  };

  const calculateOverallPerformance = () => {
    const goodCount = metrics.filter(m => m.status === 'good').length;
    const totalCount = metrics.length;
    
    if (totalCount === 0) return 0;
    return Math.round((goodCount / totalCount) * 100);
  };

  const overallPerformance = calculateOverallPerformance();

  if (!isVisible) return null;

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm p-3 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-800 flex items-center gap-1">
          <Activity className="h-4 w-4" />
          Performance Monitor
        </h3>
        <div className={`px-2 py-1 rounded text-xs font-medium ${
          overallPerformance >= 80 ? 'bg-green-100 text-green-700' :
          overallPerformance >= 60 ? 'bg-yellow-100 text-yellow-700' :
          'bg-red-100 text-red-700'
        }`}>
          {overallPerformance}% Optimal
        </div>
      </div>

      <div className="space-y-2">
        {metrics.map((metric, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`p-1 rounded ${getStatusColor(metric.status)}`}>
                {getStatusIcon(metric.name)}
              </div>
              <span className="text-xs text-gray-600">{metric.name}</span>
            </div>
            <div className="text-xs font-mono text-gray-800">
              {metric.value.toLocaleString()} {metric.unit}
            </div>
          </div>
        ))}
      </div>

      {searchTime > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-100">
          <div className="text-xs text-gray-500">
            Search Performance: {searchTime < 10 ? 'Lightning Fast' : 
                               searchTime < 50 ? 'Very Fast' : 
                               searchTime < 100 ? 'Fast' : 'Needs Optimization'} ⚡
          </div>
        </div>
      )}
    </div>
  );
}

// Compact version for inline display
export function CompactPerformanceIndicator({ 
  searchTime, 
  className = '' 
}: { 
  searchTime: number; 
  className?: string; 
}) {
  const getPerformanceColor = (time: number) => {
    if (time <= 10) return 'text-green-600';
    if (time <= 50) return 'text-blue-600';
    if (time <= 100) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceLabel = (time: number) => {
    if (time <= 10) return 'Lightning';
    if (time <= 50) return 'Very Fast';
    if (time <= 100) return 'Fast';
    return 'Slow';
  };

  if (searchTime <= 0) return null;

  return (
    <div className={`inline-flex items-center gap-1 ${className}`}>
      <Zap className={`h-3 w-3 ${getPerformanceColor(searchTime)}`} />
      <span className={`text-xs ${getPerformanceColor(searchTime)}`}>
        {searchTime}ms ({getPerformanceLabel(searchTime)})
      </span>
    </div>
  );
}