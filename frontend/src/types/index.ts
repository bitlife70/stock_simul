export interface Stock {
  symbol: string;
  name: string;
  name_kr: string;
  market: string;
}

export interface StockData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StrategyTemplate {
  id: string;
  name: string;
  name_kr: string;
  description: string;
  parameters: {
    [key: string]: {
      type: 'number' | 'string' | 'boolean';
      default: string | number | boolean;
      min?: number;
      max?: number;
      description: string;
    };
  };
}

export interface StrategyFormData {
  name: string;
  description?: string;
  template_id: string;
  parameters: Record<string, string | number | boolean>;
  initial_capital: number;
  start_date: string;
  end_date: string;
}

export interface BacktestResult {
  total_return: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  max_drawdown: number;
  sharpe_ratio: number;
  final_capital: number;
  cagr: number;
  volatility: number;
  profit_factor: number;
  max_consecutive_wins: number;
  max_consecutive_losses: number;
  avg_profit: number;
  avg_loss: number;
  max_profit: number;
  max_loss: number;
  avg_hold_days: number;
  total_fees: number;
  net_profit: number;
  benchmark_return?: number;
  daily_returns?: number[];
  equity_curve?: Array<{ date: string; value: number; benchmark?: number }>;
  trades: BacktestTrade[];
  risk_metrics?: RiskMetrics;
}

export interface BacktestTrade {
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

// Professional trading types
export interface Trade {
  entry_date: string;
  exit_date: string;
  symbol: string;
  side: 'long' | 'short';
  entry_price: number;
  exit_price: number;
  quantity: number;
  pnl: number;
  pnl_percentage: number;
  duration_days: number;
}

export interface RiskMetrics {
  var_95: number;
  var_99: number;
  beta_kospi: number;
  beta_kosdaq: number;
  information_ratio: number;
  calmar_ratio: number;
  sortino_ratio: number;
  max_consecutive_losses: number;
  avg_win: number;
  avg_loss: number;
}

export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  strategies: PortfolioStrategy[];
  total_allocation: number;
  initial_capital: number;
  current_value: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioStrategy {
  strategy_id: string;
  name: string;
  allocation_percentage: number;
  symbols: string[];
  current_value: number;
  performance: StrategyPerformance;
  risk_metrics: RiskMetrics;
}

export interface StrategyPerformance {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  last_updated: string;
}

// Korean market specific types
export interface KoreanMarketData {
  kospi_index: number;
  kosdaq_index: number;
  won_dollar_rate: number;
  market_status: 'pre_market' | 'open' | 'lunch_break' | 'post_market' | 'closed';
  chaebol_concentration: number;
  sector_weights: Record<string, number>;
}

export interface KoreanRiskConstraints {
  max_single_position: number;
  max_chaebol_exposure: number;
  max_sector_concentration: number;
  price_limit_exposure: number;
  daily_trading_limit: number;
}

export interface PositionSize {
  symbol: string;
  name_kr: string;
  current_price: number;
  target_allocation: number;
  max_position_krw: number;
  recommended_shares: number;
  risk_score: number;
  price_limit_risk: 'low' | 'medium' | 'high';
}

// Advanced strategy types
export interface KoreanStrategy {
  id: string;
  name: string;
  name_kr: string;
  category: 'momentum' | 'value' | 'growth' | 'defensive' | 'sector_rotation' | 'chaebol_focus';
  description: string;
  korean_market_focus: boolean;
  crisis_tested: boolean;
  parameters: StrategyParameter[];
  performance_history: PerformanceHistory[];
  risk_profile: 'conservative' | 'moderate' | 'aggressive';
}

export interface StrategyParameter {
  key: string;
  name: string;
  name_kr: string;
  type: 'number' | 'string' | 'boolean' | 'select';
  default_value: string | number | boolean;
  min_value?: number;
  max_value?: number;
  options?: string[];
  description: string;
  korean_market_constraint?: boolean;
}

export interface PerformanceHistory {
  period: string;
  return_percentage: number;
  benchmark_return: number;
  volatility: number;
  max_drawdown: number;
  sharpe_ratio: number;
}

// Dashboard and analytics types
export interface DashboardMetrics {
  portfolio_value: number;
  daily_pnl: number;
  daily_pnl_percentage: number;
  total_return: number;
  benchmark_return: number;
  active_positions: number;
  cash_balance: number;
  margin_used: number;
  risk_exposure: number;
}

export interface MarketAlert {
  id: string;
  type: 'price_limit' | 'volume_spike' | 'news' | 'technical' | 'risk';
  severity: 'low' | 'medium' | 'high' | 'critical';
  symbol?: string;
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

// Korean localization
export interface KoreanFormatting {
  currency: (amount: number) => string;
  percentage: (value: number) => string;
  number: (value: number) => string;
  dateTime: (date: string | Date) => string;
}

// Real-time market monitoring types
export interface RealTimeMarketData {
  kospi: {
    index: number;
    change: number;
    changePercent: number;
    volume: number;
    value: number;
  };
  kosdaq: {
    index: number;
    change: number;
    changePercent: number;
    volume: number;
    value: number;
  };
  marketBreadth: {
    up: number;
    down: number;
    unchanged: number;
    upperLimit: number;
    lowerLimit: number;
  };
  foreignFlow: {
    kospiNet: number;
    kosdaqNet: number;
    totalNet: number;
  };
  programTrading: {
    buyValue: number;
    sellValue: number;
    netValue: number;
  };
  marketSentiment: {
    fearGreedIndex: number;
    vixKospi: number;
    putCallRatio: number;
  };
  timestamp: string;
}

export interface TopMoversData {
  upperLimit: Array<{
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
  }>;
  lowerLimit: Array<{
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
  }>;
  volumeLeaders: Array<{
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
    turnoverRatio: number;
  }>;
  sectorPerformance: Array<{
    sector: string;
    sectorKr: string;
    change: number;
    changePercent: number;
    marketCap: number;
  }>;
}

export interface LiveStrategyData {
  strategies: Array<{
    id: string;
    name: string;
    currentValue: number;
    dailyPnl: number;
    dailyPnlPercent: number;
    totalReturn: number;
    positions: Array<{
      symbol: string;
      name: string;
      quantity: number;
      currentPrice: number;
      unrealizedPnl: number;
      unrealizedPnlPercent: number;
    }>;
    signals: Array<{
      type: 'buy' | 'sell';
      symbol: string;
      price: number;
      confidence: number;
      timestamp: string;
    }>;
  }>;
}

export interface SystemHealthData {
  apiStatus: {
    marketData: 'online' | 'offline' | 'degraded';
    backtesting: 'online' | 'offline' | 'degraded';
    database: 'online' | 'offline' | 'degraded';
  };
  performance: {
    apiResponseTime: number;
    dataFeedLatency: number;
    cacheHitRate: number;
    errorRate: number;
  };
  system: {
    activeUsers: number;
    systemLoad: number;
    memoryUsage: number;
    diskUsage: number;
  };
  lastUpdated: string;
}