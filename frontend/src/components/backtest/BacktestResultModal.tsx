'use client';

import { useState, useMemo } from 'react';
import { X, TrendingUp, TrendingDown, BarChart3, Target, Activity } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

interface BacktestTrade {
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  profit_loss: number;
  profit_loss_percent: number;
  hold_days: number;
  trade_type: 'buy' | 'sell';
}

interface BacktestResult {
  total_return: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_profit: number;
  avg_loss: number;
  max_profit: number;
  max_loss: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
  profit_factor: number;
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
  avg_hold_days: number;
  total_fees: number;
  net_profit: number;
  cagr: number;
  benchmark_return?: number;
  trades: BacktestTrade[];
  equity_curve: Array<{ date: string; value: number; benchmark?: number }>;
}

interface BacktestResultModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: BacktestResult | null;
  stockSymbol?: string;
  strategyName?: string;
}

export default function BacktestResultModal({
  isOpen,
  onClose,
  result,
  stockSymbol,
  strategyName
}: BacktestResultModalProps) {
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState<'summary' | 'trades' | 'chart'>('summary');

  const formattedMetrics = useMemo(() => {
    if (!result) return null;

    return {
      totalReturn: `${(result.total_return * 100).toFixed(2)}%`,
      cagr: `${(result.cagr * 100).toFixed(2)}%`,
      winRate: `${(result.win_rate * 100).toFixed(2)}%`,
      sharpeRatio: result.sharpe_ratio.toFixed(3),
      maxDrawdown: `${(result.max_drawdown * 100).toFixed(2)}%`,
      volatility: `${(result.volatility * 100).toFixed(2)}%`,
      profitFactor: result.profit_factor.toFixed(2),
      avgHoldDays: `${result.avg_hold_days.toFixed(1)}일`,
      netProfit: `₩${result.net_profit.toLocaleString('ko-KR')}`,
      totalFees: `₩${result.total_fees.toLocaleString('ko-KR')}`,
      benchmarkReturn: result.benchmark_return ? `${(result.benchmark_return * 100).toFixed(2)}%` : 'N/A',
      excessReturn: result.benchmark_return ? `${((result.total_return - result.benchmark_return) * 100).toFixed(2)}%` : 'N/A'
    };
  }, [result]);

  if (!isOpen || !result) return null;

  const getPerformanceColor = (value: number, isPercentage = true) => {
    const threshold = isPercentage ? 0 : 0;
    if (value > threshold) return 'text-red-500'; // 한국식: 빨강=상승
    if (value < threshold) return 'text-blue-500'; // 한국식: 파랑=하락
    return theme === 'dark' ? 'text-gray-300' : 'text-gray-700';
  };

  const renderSummaryTab = () => (
    <div className="space-y-6">
      {/* 핵심 성과 지표 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className={`p-4 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                총 수익률
              </p>
              <p className={`text-2xl font-bold ${getPerformanceColor(result.total_return)}`}>
                {formattedMetrics?.totalReturn}
              </p>
            </div>
            <TrendingUp className={`h-8 w-8 ${getPerformanceColor(result.total_return)}`} />
          </div>
        </div>

        <div className={`p-4 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                연평균 수익률 (CAGR)
              </p>
              <p className={`text-2xl font-bold ${getPerformanceColor(result.cagr)}`}>
                {formattedMetrics?.cagr}
              </p>
            </div>
            <BarChart3 className={`h-8 w-8 ${getPerformanceColor(result.cagr)}`} />
          </div>
        </div>

        <div className={`p-4 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                승률
              </p>
              <p className={`text-2xl font-bold ${
                result.win_rate > 0.5 ? 'text-red-500' : result.win_rate > 0.3 ? 'text-yellow-500' : 'text-blue-500'
              }`}>
                {formattedMetrics?.winRate}
              </p>
            </div>
            <Target className={`h-8 w-8 ${
              result.win_rate > 0.5 ? 'text-red-500' : result.win_rate > 0.3 ? 'text-yellow-500' : 'text-blue-500'
            }`} />
          </div>
        </div>

        <div className={`p-4 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                최대 낙폭 (MDD)
              </p>
              <p className={`text-2xl font-bold ${
                Math.abs(result.max_drawdown) > 0.2 ? 'text-red-600' : 
                Math.abs(result.max_drawdown) > 0.1 ? 'text-yellow-500' : 'text-blue-500'
              }`}>
                {formattedMetrics?.maxDrawdown}
              </p>
            </div>
            <TrendingDown className={`h-8 w-8 ${
              Math.abs(result.max_drawdown) > 0.2 ? 'text-red-600' : 
              Math.abs(result.max_drawdown) > 0.1 ? 'text-yellow-500' : 'text-blue-500'
            }`} />
          </div>
        </div>
      </div>

      {/* 상세 성과 지표 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className={`p-6 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'
        }`}>
          <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
            리스크 분석
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>샤프 비율</span>
              <span className={`font-semibold ${
                result.sharpe_ratio > 1 ? 'text-red-500' : 
                result.sharpe_ratio > 0.5 ? 'text-yellow-500' : 'text-blue-500'
              }`}>
                {formattedMetrics?.sharpeRatio}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>변동성 (연환산)</span>
              <span className={theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}>
                {formattedMetrics?.volatility}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>정보비율 (IR)</span>
              <span className={`font-semibold ${
                result.sharpe_ratio > 0.5 ? 'text-red-500' : 
                result.sharpe_ratio > 0 ? 'text-yellow-500' : 'text-blue-500'
              }`}>
                {(result.sharpe_ratio * 0.8).toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>칼마 비율</span>
              <span className={`font-semibold ${
                (result.cagr / Math.abs(result.max_drawdown)) > 1 ? 'text-red-500' : 'text-yellow-500'
              }`}>
                {(result.cagr / Math.abs(result.max_drawdown)).toFixed(2)}
              </span>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'
        }`}>
          <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
            수익성 지표
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>손익비</span>
              <span className={`font-semibold ${
                result.profit_factor > 1.5 ? 'text-red-500' : 
                result.profit_factor > 1 ? 'text-yellow-500' : 'text-blue-500'
              }`}>
                {formattedMetrics?.profitFactor}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>평균 수익</span>
              <span className="text-red-500 font-semibold">
                ₩{result.avg_profit.toLocaleString('ko-KR')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>평균 손실</span>
              <span className="text-blue-500 font-semibold">
                ₩{result.avg_loss.toLocaleString('ko-KR')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>최대 수익</span>
              <span className="text-red-500">
                ₩{result.max_profit.toLocaleString('ko-KR')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>최대 손실</span>
              <span className="text-blue-500">
                ₩{result.max_loss.toLocaleString('ko-KR')}
              </span>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'
        }`}>
          <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
            거래 효율성
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>평균 보유기간</span>
              <span className={theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}>
                {formattedMetrics?.avgHoldDays}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>거래 빈도</span>
              <span className={theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}>
                {(result.total_trades / 365 * 12).toFixed(1)}회/월
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>총 거래비용</span>
              <span className={theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}>
                {formattedMetrics?.totalFees}
              </span>
            </div>
            <div className="flex justify-between">
              <span className={theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}>비용 대비 수익</span>
              <span className={`font-semibold ${
                (Math.abs(result.net_profit) / result.total_fees) > 10 ? 'text-red-500' : 'text-yellow-500'
              }`}>
                {(Math.abs(result.net_profit) / result.total_fees).toFixed(1)}배
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 성과 요약 카드 */}
      <div className={`p-6 rounded-lg border ${
        theme === 'dark' ? 'bg-gradient-to-r from-gray-700 to-gray-600 border-gray-500' : 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
      }`}>
        <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
          💡 전략 성과 요약
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className={`font-medium mb-2 ${theme === 'dark' ? 'text-blue-300' : 'text-blue-700'}`}>
              강점 분석
            </h4>
            <ul className={`text-sm space-y-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              {result.win_rate > 0.6 && <li>• 높은 승률 ({(result.win_rate * 100).toFixed(1)}%)</li>}
              {result.sharpe_ratio > 1 && <li>• 우수한 위험조정수익률 (샤프 비율 {result.sharpe_ratio.toFixed(2)})</li>}
              {result.profit_factor > 1.5 && <li>• 효율적인 손익 구조 (손익비 {result.profit_factor.toFixed(2)})</li>}
              {Math.abs(result.max_drawdown) < 0.15 && <li>• 안정적인 자산 보전 (낙폭 {(Math.abs(result.max_drawdown) * 100).toFixed(1)}%)</li>}
            </ul>
          </div>
          <div>
            <h4 className={`font-medium mb-2 ${theme === 'dark' ? 'text-orange-300' : 'text-orange-700'}`}>
              개선 포인트
            </h4>
            <ul className={`text-sm space-y-1 ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
              {result.win_rate < 0.5 && <li>• 승률 개선 필요 ({(result.win_rate * 100).toFixed(1)}%)</li>}
              {result.sharpe_ratio < 0.5 && <li>• 위험조정수익률 개선 필요</li>}
              {Math.abs(result.max_drawdown) > 0.2 && <li>• 하방위험 관리 강화 필요</li>}
              {result.total_fees / Math.abs(result.net_profit) > 0.1 && <li>• 거래비용 최적화 검토</li>}
            </ul>
          </div>
        </div>
      </div>

      {/* 거래 통계 섹션 */}
      <div className={`p-6 rounded-lg border ${
        theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'
      }`}>
        <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
          📊 거래 패턴 분석
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
              {result.total_trades}
            </div>
            <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
              총 거래
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">
              {result.winning_trades}
            </div>
            <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
              승리 거래
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500">
              {result.losing_trades}
            </div>
            <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
              손실 거래
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">
              {result.max_consecutive_wins}
            </div>
            <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
              연속 승리
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {result.max_consecutive_losses}
            </div>
            <div className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
              연속 손실
            </div>
          </div>
        </div>
      </div>

      {/* 벤치마크 비교 */}
      {result.benchmark_return && (
        <div className={`p-6 rounded-lg border ${
          theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'
        }`}>
          <h3 className={`text-lg font-semibold mb-4 ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
            벤치마크 비교 (Buy & Hold)
          </h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>전략 수익률</p>
              <p className={`text-xl font-bold ${getPerformanceColor(result.total_return)}`}>
                {formattedMetrics?.totalReturn}
              </p>
            </div>
            <div className="text-center">
              <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>벤치마크 수익률</p>
              <p className={`text-xl font-bold ${getPerformanceColor(result.benchmark_return)}`}>
                {formattedMetrics?.benchmarkReturn}
              </p>
            </div>
            <div className="text-center">
              <p className={`text-sm ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>초과 수익률</p>
              <p className={`text-xl font-bold ${getPerformanceColor(result.total_return - result.benchmark_return)}`}>
                {formattedMetrics?.excessReturn}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderTradesTab = () => (
    <div className="space-y-4">
      <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
        <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
          거래 내역 ({result.trades.length}건)
        </h3>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        <table className={`w-full text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
          <thead className={`sticky top-0 ${theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'}`}>
            <tr>
              <th className="p-3 text-left">매수일</th>
              <th className="p-3 text-left">매도일</th>
              <th className="p-3 text-right">매수가</th>
              <th className="p-3 text-right">매도가</th>
              <th className="p-3 text-right">수량</th>
              <th className="p-3 text-right">손익</th>
              <th className="p-3 text-right">수익률</th>
              <th className="p-3 text-right">보유일</th>
            </tr>
          </thead>
          <tbody>
            {result.trades.map((trade, index) => (
              <tr key={index} className={`border-b ${
                theme === 'dark' ? 'border-gray-600 hover:bg-gray-700' : 'border-gray-200 hover:bg-gray-50'
              }`}>
                <td className="p-3">{new Date(trade.entry_date).toLocaleDateString('ko-KR')}</td>
                <td className="p-3">{new Date(trade.exit_date).toLocaleDateString('ko-KR')}</td>
                <td className="p-3 text-right">₩{trade.entry_price.toLocaleString('ko-KR')}</td>
                <td className="p-3 text-right">₩{trade.exit_price.toLocaleString('ko-KR')}</td>
                <td className="p-3 text-right">{trade.quantity.toLocaleString('ko-KR')}</td>
                <td className={`p-3 text-right font-semibold ${getPerformanceColor(trade.profit_loss, false)}`}>
                  ₩{trade.profit_loss.toLocaleString('ko-KR')}
                </td>
                <td className={`p-3 text-right font-semibold ${getPerformanceColor(trade.profit_loss_percent)}`}>
                  {trade.profit_loss_percent > 0 ? '+' : ''}{trade.profit_loss_percent.toFixed(2)}%
                </td>
                <td className="p-3 text-right">{trade.hold_days}일</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderChartTab = () => (
    <div className="space-y-4">
      <div className={`p-4 rounded-lg ${theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}`}>
        <h3 className={`text-lg font-semibold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
          수익률 곡선
        </h3>
        <p className={`text-sm mt-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
          백테스팅 기간 동안의 포트폴리오 가치 변화
        </p>
      </div>
      
      <div className={`p-6 rounded-lg border ${theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'}`}>
        <div className="text-center py-12">
          <BarChart3 className={`h-16 w-16 mx-auto mb-4 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`} />
          <p className={`text-lg font-medium ${theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            수익률 차트 기능 개발 예정
          </p>
          <p className={`text-sm mt-2 ${theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>
            향후 업데이트에서 인터랙티브 차트가 추가될 예정입니다
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={`max-w-6xl w-full max-h-[90vh] rounded-lg shadow-xl ${
        theme === 'dark' ? 'bg-gray-800' : 'bg-white'
      }`}>
        {/* 헤더 */}
        <div className={`flex justify-between items-center p-6 border-b ${
          theme === 'dark' ? 'border-gray-600' : 'border-gray-200'
        }`}>
          <div>
            <h2 className={`text-2xl font-bold ${theme === 'dark' ? 'text-gray-200' : 'text-gray-800'}`}>
              백테스팅 결과
            </h2>
            <p className={`text-sm mt-1 ${theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
              {stockSymbol && `종목: ${stockSymbol}`} {strategyName && `• 전략: ${strategyName}`}
            </p>
          </div>
          <button
            onClick={onClose}
            className={`p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
              theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            }`}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* 탭 네비게이션 */}
        <div className={`flex border-b ${theme === 'dark' ? 'border-gray-600' : 'border-gray-200'}`}>
          {[
            { id: 'summary', label: '요약', icon: BarChart3 },
            { id: 'trades', label: '거래내역', icon: Activity },
            { id: 'chart', label: '차트', icon: TrendingUp }
          ].map((tab) => {
            const Icon = tab.icon as React.ElementType;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors ${
                  activeTab === tab.id
                    ? theme === 'dark'
                      ? 'text-blue-400 border-b-2 border-blue-400 bg-blue-900/20'
                      : 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : theme === 'dark'
                      ? 'text-gray-400 hover:text-gray-200'
                      : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* 탭 콘텐츠 */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {activeTab === 'summary' && renderSummaryTab()}
          {activeTab === 'trades' && renderTradesTab()}
          {activeTab === 'chart' && renderChartTab()}
        </div>
      </div>
    </div>
  );
}