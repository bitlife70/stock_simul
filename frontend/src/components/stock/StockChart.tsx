'use client';

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time, ColorType } from 'lightweight-charts';

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
}

export default function StockChart({ 
  symbol, 
  data, 
  height = 400, 
  showVolume = true 
}: StockChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // 차트 생성
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      localization: {
        priceFormatter: (price: number) => {
          return new Intl.NumberFormat('ko-KR', {
            style: 'currency',
            currency: 'KRW',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
          }).format(price);
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
    });

    // 캔들스틱 시리즈 추가
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#e91e63',
      downColor: '#2196f3',
      borderVisible: false,
      wickUpColor: '#e91e63',
      wickDownColor: '#2196f3',
    });

    // 볼륨 시리즈 추가 (필요한 경우)
    let volumeSeries = null;
    if (showVolume) {
      volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      });
      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });
    }

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

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
      if (chart) {
        chart.remove();
      }
    };
  }, [height, showVolume]);

  useEffect(() => {
    if (!candlestickSeriesRef.current || !data.length) return;

    setLoading(true);

    try {
      // 데이터를 Lightweight Charts 형식으로 변환
      const candlestickData: CandlestickData[] = data.map(item => ({
        time: new Date(item.date).getTime() / 1000 as Time,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));

      // 캔들스틱 데이터 설정
      candlestickSeriesRef.current.setData(candlestickData);

      // 볼륨 데이터 설정 (필요한 경우)
      if (volumeSeriesRef.current && showVolume) {
        const volumeData = data.map(item => ({
          time: new Date(item.date).getTime() / 1000 as Time,
          value: item.volume,
          color: item.close >= item.open ? '#e91e6340' : '#2196f340',
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
  }, [data, showVolume]);

  if (!data.length) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg"
        style={{ height }}
      >
        <div className="text-center text-gray-500">
          <div className="text-lg font-medium">차트 데이터가 없습니다</div>
          <div className="text-sm mt-1">종목을 선택해주세요</div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10 rounded-lg">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-gray-600">차트 로딩중...</span>
          </div>
        </div>
      )}
      
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {symbol && (
          <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">{symbol} 주가 차트</h3>
          </div>
        )}
        <div ref={chartContainerRef} className="w-full" />
      </div>
    </div>
  );
}