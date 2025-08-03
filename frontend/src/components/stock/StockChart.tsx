'use client';

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, LineData, Time, ColorType, LogicalRange } from 'lightweight-charts';
import { useTheme } from '@/contexts/ThemeContext';

interface StockData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface StockChartProps {
  symbol?: string;
  data: StockData[];
  height?: number;
  showVolume?: boolean;
  onLoadMore?: (direction: 'left' | 'right') => Promise<StockData[]>;
}

interface StockDetailInfo {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change: number;
  changePercent: number;
}

export default function StockChart({ 
  symbol, 
  data, 
  height = 400, 
  showVolume = true,
  onLoadMore
}: StockChartProps) {
  const { theme } = useTheme();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const ma5SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const ma20SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const ma60SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const [loading, setLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<StockDetailInfo | null>(null);
  const [isChartReady, setIsChartReady] = useState(false);
  const [chartMounted, setChartMounted] = useState(false);

  // 데이터 메모이제이션 및 정렬
  const sortedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    return [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [data]);

  // 이동평균선 계산 함수
  const calculateMovingAverage = useCallback((data: StockData[], period: number): LineData[] => {
    const result: LineData[] = [];
    
    for (let i = period - 1; i < data.length; i++) {
      const sum = data.slice(i - period + 1, i + 1).reduce((acc, item) => acc + item.close, 0);
      const average = sum / period;
      
      result.push({
        time: new Date(data[i].date).getTime() / 1000 as Time,
        value: average,
      });
    }
    
    return result;
  }, []);

  // 최신 데이터 세부정보 계산
  const latestDetail = useMemo((): StockDetailInfo | null => {
    if (sortedData.length === 0) return null;
    
    const latest = sortedData[sortedData.length - 1];
    const previous = sortedData.length > 1 ? sortedData[sortedData.length - 2] : null;
    
    const change = previous ? latest.close - previous.close : 0;
    const changePercent = previous ? (change / previous.close) * 100 : 0;
    
    return {
      date: latest.date,
      open: latest.open,
      high: latest.high,
      low: latest.low,
      close: latest.close,
      volume: latest.volume,
      change,
      changePercent
    };
  }, [sortedData]);

  // 선택된 세부정보 설정 (호버 또는 최신 데이터)
  const displayDetail = selectedDetail || latestDetail;

  // 차트 테마 설정 (메모이제이션)
  const chartTheme = useMemo(() => {
    const isDark = theme === 'dark';
    return {
      layout: {
        background: { 
          type: ColorType.Solid, 
          color: isDark ? '#1a1a1a' : '#ffffff' 
        },
        textColor: isDark ? '#ffffff' : '#333333',
      },
      grid: {
        vertLines: { color: isDark ? '#2a2a2a' : '#f0f0f0' },
        horzLines: { color: isDark ? '#2a2a2a' : '#f0f0f0' },
      },
      timeScale: {
        borderColor: isDark ? '#404040' : '#cccccc',
      },
      rightPriceScale: {
        borderColor: isDark ? '#404040' : '#cccccc',
      },
    };
  }, [theme]);

  // 스크롤 이벤트 핸들러
  const handleVisibleLogicalRangeChange = useCallback(async (newRange: LogicalRange | null) => {
    if (!newRange || !onLoadMore || isLoadingMore) return;
    
    // 왼쪽 끝에 도달했을 때 과거 데이터 로드
    if (newRange.from < 10) {
      setIsLoadingMore(true);
      try {
        await onLoadMore('left');
      } catch (error) {
        console.error('Failed to load more data:', error);
      } finally {
        setIsLoadingMore(false);
      }
    }
  }, [onLoadMore, isLoadingMore]);

  useEffect(() => {
    if (!chartContainerRef.current || sortedData.length === 0) return;

    // 차트 생성
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      ...chartTheme,
      crosshair: {
        mode: 1,
        vertLine: {
          labelBackgroundColor: theme === 'dark' ? '#333333' : '#ffffff',
          color: theme === 'dark' ? '#666666' : '#999999',
        },
        horzLine: {
          labelBackgroundColor: theme === 'dark' ? '#333333' : '#ffffff',
          color: theme === 'dark' ? '#666666' : '#999999',
        },
      },
      timeScale: {
        ...chartTheme.timeScale,
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        ...chartTheme.rightPriceScale,
        scaleMargins: {
          top: 0.1,
          bottom: showVolume ? 0.3 : 0.1,
        },
      },
      localization: {
        priceFormatter: (price: number) => {
          return `₩${price.toLocaleString('ko-KR')}`;
        },
        timeFormatter: (time: Time) => {
          const date = new Date(time as number * 1000);
          return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
          });
        },
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true,
      },
    });

    // 캔들스틱 시리즈 추가 (한국 스타일: 상승=빨강, 하락=파랑)
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#ff4444',
      downColor: '#4488ff',
      borderUpColor: '#ff4444',
      borderDownColor: '#4488ff',
      wickUpColor: '#ff4444',
      wickDownColor: '#4488ff',
      borderVisible: true,
      priceLineVisible: false,
    });

    // 이동평균선 시리즈 추가
    const ma5Series = chart.addLineSeries({
      color: '#ff9800',
      lineWidth: 1,
      title: 'MA5',
      lastValueVisible: false,
      priceLineVisible: false,
    });

    const ma20Series = chart.addLineSeries({
      color: '#9c27b0',
      lineWidth: 1,
      title: 'MA20',
      lastValueVisible: false,
      priceLineVisible: false,
    });

    const ma60Series = chart.addLineSeries({
      color: '#2196f3',
      lineWidth: 1,
      title: 'MA60',
      lastValueVisible: false,
      priceLineVisible: false,
    });

    // 볼륨 시리즈 추가 (필요한 경우)
    let volumeSeries = null;
    if (showVolume) {
      volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume',
      });
    }

    // 스크롤 이벤트 리스너 추가
    chart.timeScale().subscribeVisibleLogicalRangeChange(handleVisibleLogicalRangeChange);

    // 툴팁 추가
    const toolTipDiv = document.createElement('div');
    toolTipDiv.style.cssText = `
      position: absolute;
      display: none;
      padding: 8px;
      box-sizing: border-box;
      font-size: 12px;
      text-align: left;
      z-index: 1000;
      top: 12px;
      left: 12px;
      pointer-events: none;
      border: 1px solid;
      border-radius: 4px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ${theme === 'dark' 
        ? 'background: rgba(0, 0, 0, 0.8); color: white; border-color: #333;' 
        : 'background: rgba(255, 255, 255, 0.9); color: black; border-color: #ccc;'
      }
    `;
    chartContainerRef.current.appendChild(toolTipDiv);

    // Crosshair 이벤트 구독 - 실시간 마우스 호버 정보
    chart.subscribeCrosshairMove(param => {
      // 마우스가 차트를 벗어났거나 유효하지 않은 위치에 있을 때
      const seriesPrices = (param as { seriesPrices?: Map<unknown, unknown> }).seriesPrices;
      if (!param.point || !param.time || !seriesPrices || !seriesPrices.size) {
        toolTipDiv.style.display = 'none';
        // 마우스가 차트 영역을 벗어나면 최신 날짜 정보로 복원
        setSelectedDetail(null);
        return;
      }

      const candlestickPrice = seriesPrices.get(candlestickSeries) as {
        open: number;
        high: number;
        low: number;
        close: number;
      } | undefined;
      if (!candlestickPrice) {
        toolTipDiv.style.display = 'none';
        setSelectedDetail(null);
        return;
      }

      const date = new Date(param.time as number * 1000);
      const dateStr = date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        weekday: 'short'
      });

      // 십자선이 가리키는 날짜의 OHLCV 정보를 실시간으로 찾아서 표시
      const targetDate = date.toISOString().split('T')[0];
      const targetData = sortedData.find(d => d.date === targetDate);
      
      if (targetData) {
        const dataIndex = sortedData.indexOf(targetData);
        const previousData = dataIndex > 0 ? sortedData[dataIndex - 1] : null;
        const change = previousData ? targetData.close - previousData.close : 0;
        const changePercent = previousData ? (change / previousData.close) * 100 : 0;
        
        // 선택된 날짜의 세부정보를 실시간으로 업데이트
        setSelectedDetail({
          date: targetData.date,
          open: targetData.open,
          high: targetData.high,
          low: targetData.low,
          close: targetData.close,
          volume: targetData.volume,
          change,
          changePercent
        });
      }

      const formatPrice = (price: number) => `₩${price.toLocaleString('ko-KR')}`;
      const formatVolume = (volume: number) => {
        if (volume >= 1000000) {
          return `${(volume / 1000000).toFixed(1)}M`;
        } else if (volume >= 10000) {
          return `${(volume / 10000).toFixed(1)}만`;
        }
        return volume.toLocaleString('ko-KR');
      };

      // 볼륨 정보도 툴팁에 추가
      const volumePrice = targetData ? targetData.volume : 0;
      
      toolTipDiv.innerHTML = `
        <div style="margin-bottom: 6px; font-weight: bold; font-size: 13px;">${symbol || '주식'} - ${dateStr}</div>
        <div style="margin-bottom: 2px;">시가: ${formatPrice(candlestickPrice.open)}</div>
        <div style="margin-bottom: 2px;">고가: <span style="color: #ff4444; font-weight: bold;">${formatPrice(candlestickPrice.high)}</span></div>
        <div style="margin-bottom: 2px;">저가: <span style="color: #4488ff; font-weight: bold;">${formatPrice(candlestickPrice.low)}</span></div>
        <div style="margin-bottom: 2px;">종가: ${formatPrice(candlestickPrice.close)}</div>
        <div style="margin-bottom: 4px;">거래량: ${formatVolume(volumePrice)}</div>
        <div style="margin-top: 4px; font-size: 10px; opacity: 0.8; border-top: 1px solid ${theme === 'dark' ? '#444' : '#ddd'}; padding-top: 2px;">
          <span style="color: #ff9800;">●</span> MA5 
          <span style="color: #9c27b0;">●</span> MA20 
          <span style="color: #2196f3;">●</span> MA60
        </div>
      `;

      // 툴팁 위치 조정 (화면 경계 처리)
      const containerRect = chartContainerRef.current?.getBoundingClientRect();
      if (containerRect) {
        let left = param.point.x + 12;
        let top = param.point.y + 12;
        
        // 툴팁이 오른쪽으로 넘치지 않게 조정
        if (left + 200 > containerRect.width) {
          left = param.point.x - 212;
        }
        
        // 툴팁이 아래로 넘치지 않게 조정
        if (top + 150 > containerRect.height) {
          top = param.point.y - 150;
        }
        
        toolTipDiv.style.left = Math.max(10, left) + 'px';
        toolTipDiv.style.top = Math.max(10, top) + 'px';
      }

      toolTipDiv.style.display = 'block';
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;
    ma5SeriesRef.current = ma5Series;
    ma20SeriesRef.current = ma20Series;
    ma60SeriesRef.current = ma60Series;
    setIsChartReady(true);
    setChartMounted(true);

    // 반응형 차트
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      setIsChartReady(false);
      setChartMounted(false);
      if (chart) {
        chart.remove();
      }
    };
  }, [height, showVolume, theme, chartTheme, handleVisibleLogicalRangeChange, sortedData, symbol || '']);

  useEffect(() => {
    if (!candlestickSeriesRef.current || !isChartReady || sortedData.length === 0) return;

    setLoading(true);

    try {
      // 캔들스틱 데이터 변환
      const candlestickData: CandlestickData[] = sortedData.map(item => ({
        time: new Date(item.date).getTime() / 1000 as Time,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));

      // 캔들스틱 데이터 설정
      candlestickSeriesRef.current.setData(candlestickData);

      // 이동평균선 데이터 계산 및 설정
      if (ma5SeriesRef.current) {
        const ma5Data = calculateMovingAverage(sortedData, 5);
        ma5SeriesRef.current.setData(ma5Data);
      }

      if (ma20SeriesRef.current) {
        const ma20Data = calculateMovingAverage(sortedData, 20);
        ma20SeriesRef.current.setData(ma20Data);
      }

      if (ma60SeriesRef.current) {
        const ma60Data = calculateMovingAverage(sortedData, 60);
        ma60SeriesRef.current.setData(ma60Data);
      }

      // 볼륨 데이터 설정 (필요한 경우)
      if (volumeSeriesRef.current && showVolume) {
        const volumeData = sortedData.map(item => ({
          time: new Date(item.date).getTime() / 1000 as Time,
          value: item.volume,
          color: item.close >= item.open ? '#ff444440' : '#4488ff40',
        }));
        volumeSeriesRef.current.setData(volumeData);
      }

      // 차트를 데이터에 맞게 조정
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }
    } catch (error) {
      console.error('차트 데이터 설정 중 오류 발생:', error);
    } finally {
      setLoading(false);
    }
  }, [sortedData, showVolume, calculateMovingAverage, isChartReady]);

  if (!data.length) {
    return (
      <div 
        className={`flex items-center justify-center border rounded-lg ${
          theme === 'dark' 
            ? 'bg-gray-800 border-gray-600' 
            : 'bg-gray-50 border-gray-200'
        }`}
        style={{ height }}
      >
        <div className={`text-center ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
          <div className="text-lg font-medium">차트 데이터가 없습니다</div>
          <div className="text-sm mt-1">종목을 선택해주세요</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        {(loading || isLoadingMore) && chartMounted && (
          <div className={`absolute inset-0 bg-opacity-50 flex items-center justify-center z-10 rounded-lg ${
            theme === 'dark' ? 'bg-gray-900' : 'bg-white'
          }`}>
            <div className={`flex items-center p-3 rounded-lg shadow-lg ${
              theme === 'dark' ? 'bg-gray-800 border border-gray-600' : 'bg-white border border-gray-200'
            }`}>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
              <span className={`ml-2 text-sm font-medium ${
                theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
              }`}>
                {isLoadingMore ? '추가 데이터 로딩중...' : '차트 데이터 로딩중...'}
              </span>
            </div>
          </div>
        )}
        
        {!chartMounted && (
          <div className={`absolute inset-0 bg-opacity-75 flex items-center justify-center z-10 rounded-lg ${
            theme === 'dark' ? 'bg-gray-900' : 'bg-white'
          }`}>
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
              <span className={`ml-2 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                차트 초기화중...
              </span>
            </div>
          </div>
        )}
        
        <div className={`border rounded-lg overflow-hidden ${
          theme === 'dark' 
            ? 'border-gray-600' 
            : 'border-gray-200'
        }`}>
          {symbol && (
            <div className={`px-4 py-2 border-b ${
              theme === 'dark' 
                ? 'bg-gray-800 border-gray-600' 
                : 'bg-gray-50 border-gray-200'
            }`}>
              <h3 className={`font-semibold ${
                theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
              }`}>
                {symbol} 주가 차트
              </h3>
              <div className="flex items-center mt-1 text-xs space-x-4">
                <div className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-orange-500 mr-1"></span>
                  <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>MA5</span>
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-purple-500 mr-1"></span>
                  <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>MA20</span>
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 rounded-full bg-blue-500 mr-1"></span>
                  <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>MA60</span>
                </div>
              </div>
            </div>
          )}
          <div ref={chartContainerRef} className="w-full" />
        </div>
      </div>

      {/* 주가 세부정보 */}
      {displayDetail && (
        <div className={`border rounded-lg p-4 ${
          theme === 'dark' 
            ? 'bg-gray-800 border-gray-600' 
            : 'bg-white border-gray-200'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <h4 className={`font-semibold ${
              theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
            }`}>
              주가 세부정보
            </h4>
            <div className={`text-sm ${
              theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            }`}>
              {new Date(displayDetail.date).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'short'
              })}
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                시가 (Open)
              </div>
              <div className={`text-lg font-semibold ${
                theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
              }`}>
                ₩{displayDetail.open.toLocaleString('ko-KR')}
              </div>
            </div>

            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                고가 (High)
              </div>
              <div className="text-lg font-semibold text-red-500">
                ₩{displayDetail.high.toLocaleString('ko-KR')}
              </div>
            </div>

            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                저가 (Low)
              </div>
              <div className="text-lg font-semibold text-blue-500">
                ₩{displayDetail.low.toLocaleString('ko-KR')}
              </div>
            </div>

            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                종가 (Close)
              </div>
              <div className={`text-lg font-semibold ${
                displayDetail.change > 0 ? 'text-red-500' :
                displayDetail.change < 0 ? 'text-blue-500' :
                theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
              }`}>
                ₩{displayDetail.close.toLocaleString('ko-KR')}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                전일 대비
              </div>
              <div className={`text-lg font-semibold ${
                displayDetail.change > 0 ? 'text-red-500' :
                displayDetail.change < 0 ? 'text-blue-500' :
                theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
              }`}>
                {displayDetail.change > 0 ? '+' : ''}₩{displayDetail.change.toLocaleString('ko-KR')}
              </div>
            </div>

            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                변화율
              </div>
              <div className={`text-lg font-semibold ${
                displayDetail.changePercent > 0 ? 'text-red-500' :
                displayDetail.changePercent < 0 ? 'text-blue-500' :
                theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
              }`}>
                {displayDetail.changePercent > 0 ? '+' : ''}{displayDetail.changePercent.toFixed(2)}%
              </div>
            </div>

            <div className={`text-center p-3 rounded-lg ${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <div className={`text-xs font-medium mb-1 ${
                theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}>
                거래량 (Volume)
              </div>
              <div className={`text-lg font-semibold ${
                theme === 'dark' ? 'text-gray-200' : 'text-gray-800'
              }`}>
                {displayDetail.volume >= 1000000 ? `${(displayDetail.volume / 1000000).toFixed(1)}백만` : 
                 displayDetail.volume >= 10000 ? `${(displayDetail.volume / 10000).toFixed(1)}만` : 
                 displayDetail.volume.toLocaleString('ko-KR')}
              </div>
            </div>
          </div>

          <div className={`text-xs text-center mt-3 ${
            theme === 'dark' ? 'text-gray-500' : 'text-gray-400'
          }`}>
            {selectedDetail ? 
              `• 마우스 호버로 선택된 날짜 (${new Date(selectedDetail.date).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })})` : 
              '• 최신 데이터 표시중'
            }
          </div>
        </div>
      )}
    </div>
  );
}