import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
import logging
from datetime import datetime, time, date
import pytz
from scipy import stats

logger = logging.getLogger(__name__)

class TechnicalIndicatorCalculator:
    """Korean stock market optimized technical indicator calculator"""
    
    def __init__(self):
        # Korean market configuration
        self.korean_tz = pytz.timezone('Asia/Seoul')
        self.trading_start = time(9, 0)  # 9:00 AM
        self.trading_end = time(15, 30)  # 3:30 PM
        self.lunch_start = time(11, 30)  # 11:30 AM
        self.lunch_end = time(12, 30)   # 12:30 PM
        self.price_limit_percent = 0.30  # 30% daily price limit (상한가/하한가)
        
        # Korean market holidays (simplified set)
        self.korean_holidays = {
            '2024-01-01', '2024-02-09', '2024-02-10', '2024-02-11', '2024-02-12',
            '2024-03-01', '2024-04-10', '2024-05-05', '2024-05-06', '2024-05-15',
            '2024-06-06', '2024-08-15', '2024-09-16', '2024-09-17', '2024-09-18',
            '2024-10-03', '2024-10-09', '2024-12-25'
        }
    
    def calculate_all_indicators(self, df: pd.DataFrame, symbol: str = None) -> pd.DataFrame:
        """Calculate all technical indicators for a stock with Korean market optimizations"""
        try:
            result_df = df.copy()
            
            # Filter out Korean market holidays and adjust for trading sessions
            result_df = self._adjust_for_korean_market_sessions(result_df)
            
            # Core Technical Indicators
            result_df = self._calculate_moving_averages(result_df)
            result_df = self._calculate_rsi(result_df)
            result_df = self._calculate_macd(result_df)
            result_df = self._calculate_bollinger_bands(result_df)
            result_df = self._calculate_stochastic(result_df)
            
            # Advanced Momentum Indicators
            result_df = self._calculate_williams_r(result_df)
            result_df = self._calculate_cci(result_df)
            result_df = self._calculate_roc(result_df)
            result_df = self._calculate_momentum(result_df)
            
            # Volume Indicators
            result_df = self._calculate_volume_indicators(result_df)
            result_df = self._calculate_vwap(result_df)
            result_df = self._calculate_mfi(result_df)
            
            # Volatility Indicators
            result_df = self._calculate_atr(result_df)
            result_df = self._calculate_keltner_channels(result_df)
            
            # Support/Resistance Levels
            result_df = self._calculate_pivot_points(result_df)
            result_df = self._calculate_fibonacci_levels(result_df)
            
            # Korean Market Specific Indicators
            if symbol:
                result_df = self.calculate_korean_specific_indicators(result_df, symbol)
            
            # Price Pattern Recognition
            result_df = self._calculate_candlestick_patterns(result_df)
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various moving averages optimized for Korean market"""
        try:
            close_prices = df['close']
            high_prices = df['high']
            low_prices = df['low']
            volume = df['volume']
            
            # Simple Moving Averages (Korean preferred periods)
            periods = [5, 10, 15, 20, 25, 30, 60, 120, 200]
            for period in periods:
                df[f'ma_{period}'] = close_prices.rolling(window=period, min_periods=1).mean()
            
            # Exponential Moving Averages
            ema_periods = [9, 12, 21, 26, 50]
            for period in ema_periods:
                df[f'ema_{period}'] = close_prices.ewm(span=period, min_periods=1).mean()
            
            # Weighted Moving Average (Korean market favorite)
            df['wma_20'] = self._calculate_wma(close_prices, 20)
            df['wma_60'] = self._calculate_wma(close_prices, 60)
            
            # Hull Moving Average (Responsive to Korean market volatility)
            df['hma_21'] = self._calculate_hma(close_prices, 21)
            
            # Triangular Moving Average
            df['tma_20'] = self._calculate_tma(close_prices, 20)
            
            # Volume Weighted Moving Average
            df['vwma_20'] = (close_prices * volume).rolling(window=20).sum() / volume.rolling(window=20).sum()
            
            # High-Low-Close Average (Korean chart analysis)
            df['hlc_avg'] = (high_prices + low_prices + close_prices) / 3
            df['hlc_ma_20'] = df['hlc_avg'].rolling(window=20).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return df
    
    def _calculate_wma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return prices.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    def _calculate_hma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Hull Moving Average"""
        half_period = int(period / 2)
        wma_half = self._calculate_wma(prices, half_period)
        wma_full = self._calculate_wma(prices, period)
        raw_hma = 2 * wma_half - wma_full
        return self._calculate_wma(raw_hma, int(np.sqrt(period)))
    
    def _calculate_tma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Triangular Moving Average"""
        sma1 = prices.rolling(window=period).mean()
        return sma1.rolling(window=period).mean()
    
    def _adjust_for_korean_market_sessions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adjust data for Korean market trading sessions and holidays"""
        try:
            # Remove Korean holidays if date column exists
            if 'date' in df.columns or df.index.name == 'date':
                date_col = df.index if df.index.name == 'date' else df['date']
                mask = ~date_col.astype(str).str[:10].isin(self.korean_holidays)
                df = df[mask]
            
            # Mark trading session periods (for intraday data if available)
            if 'datetime' in df.columns:
                df['trading_session'] = df['datetime'].apply(self._get_trading_session)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adjusting for Korean market sessions: {e}")
            return df
    
    def _get_trading_session(self, dt: datetime) -> str:
        """Determine trading session for Korean market"""
        try:
            time_only = dt.time()
            if time_only < self.trading_start or time_only > self.trading_end:
                return 'closed'
            elif self.lunch_start <= time_only <= self.lunch_end:
                return 'lunch'
            elif self.trading_start <= time_only < self.lunch_start:
                return 'morning'
            else:
                return 'afternoon'
        except:
            return 'unknown'
    
    def _calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """Calculate Stochastic Oscillator optimized for Korean market"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            
            # Calculate %K
            lowest_low = low_prices.rolling(window=k_period).min()
            highest_high = high_prices.rolling(window=k_period).max()
            df['stoch_k'] = 100 * (close_prices - lowest_low) / (highest_high - lowest_low)
            
            # Calculate %D (smoothed %K)
            df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
            
            # Calculate Slow %D
            df['stoch_slow_d'] = df['stoch_d'].rolling(window=d_period).mean()
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return df
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Williams %R"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            
            highest_high = high_prices.rolling(window=period).max()
            lowest_low = low_prices.rolling(window=period).min()
            
            df['williams_r'] = -100 * (highest_high - close_prices) / (highest_high - lowest_low)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {e}")
            return df
    
    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Commodity Channel Index"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            
            # Calculate Typical Price
            tp = (high_prices + low_prices + close_prices) / 3
            
            # Calculate moving average of typical price
            ma_tp = tp.rolling(window=period).mean()
            
            # Calculate mean deviation
            mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
            
            # Calculate CCI
            df['cci'] = (tp - ma_tp) / (0.015 * mad)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return df
    
    def _calculate_roc(self, df: pd.DataFrame, periods: List[int] = [10, 20]) -> pd.DataFrame:
        """Calculate Rate of Change"""
        try:
            close_prices = df['close']
            
            for period in periods:
                df[f'roc_{period}'] = ((close_prices - close_prices.shift(period)) / close_prices.shift(period)) * 100
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating ROC: {e}")
            return df
    
    def _calculate_momentum(self, df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """Calculate Momentum indicator"""
        try:
            close_prices = df['close']
            df['momentum'] = close_prices - close_prices.shift(period)
            
            # Momentum percentage
            df['momentum_pct'] = (close_prices / close_prices.shift(period) - 1) * 100
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Momentum: {e}")
            return df
    
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Volume Weighted Average Price"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            volume = df['volume']
            
            # Calculate typical price
            typical_price = (high_prices + low_prices + close_prices) / 3
            
            # Calculate VWAP
            df['vwap'] = (typical_price * volume).cumsum() / volume.cumsum()
            
            # Calculate daily VWAP (reset daily if date info available)
            if 'date' in df.columns or df.index.name == 'date':
                date_col = df.index.date if df.index.name == 'date' else df['date']
                df['vwap_daily'] = df.groupby(date_col).apply(
                    lambda x: (x['close'] * x['volume']).cumsum() / x['volume'].cumsum()
                ).values
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return df
    
    def _calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Money Flow Index"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            volume = df['volume']
            
            # Calculate typical price
            typical_price = (high_prices + low_prices + close_prices) / 3
            
            # Calculate money flow
            money_flow = typical_price * volume
            
            # Positive and negative money flow
            positive_flow = pd.Series(0.0, index=df.index)
            negative_flow = pd.Series(0.0, index=df.index)
            
            for i in range(1, len(df)):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow.iloc[i] = money_flow.iloc[i]
                elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                    negative_flow.iloc[i] = money_flow.iloc[i]
            
            # Calculate MFI
            positive_mf = positive_flow.rolling(window=period).sum()
            negative_mf = negative_flow.rolling(window=period).sum()
            
            mfi_ratio = positive_mf / negative_mf
            df['mfi'] = 100 - (100 / (1 + mfi_ratio))
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating MFI: {e}")
            return df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            
            # Calculate True Range
            tr1 = high_prices - low_prices
            tr2 = abs(high_prices - close_prices.shift(1))
            tr3 = abs(low_prices - close_prices.shift(1))
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Calculate ATR
            df['atr'] = true_range.rolling(window=period).mean()
            
            # ATR as percentage of price
            df['atr_pct'] = (df['atr'] / close_prices) * 100
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return df
    
    def _calculate_keltner_channels(self, df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> pd.DataFrame:
        """Calculate Keltner Channels"""
        try:
            close_prices = df['close']
            
            # Calculate middle line (EMA)
            df['keltner_mid'] = close_prices.ewm(span=period).mean()
            
            # Calculate ATR if not already calculated
            if 'atr' not in df.columns:
                df = self._calculate_atr(df)
            
            # Calculate upper and lower bands
            df['keltner_upper'] = df['keltner_mid'] + (multiplier * df['atr'])
            df['keltner_lower'] = df['keltner_mid'] - (multiplier * df['atr'])
            
            # Calculate position within channels
            df['keltner_position'] = (close_prices - df['keltner_lower']) / (df['keltner_upper'] - df['keltner_lower'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Keltner Channels: {e}")
            return df
    
    def _calculate_pivot_points(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Pivot Points for Korean market"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            
            # Calculate pivot point
            df['pivot'] = (high_prices.shift(1) + low_prices.shift(1) + close_prices.shift(1)) / 3
            
            # Calculate support and resistance levels
            df['r1'] = 2 * df['pivot'] - low_prices.shift(1)
            df['s1'] = 2 * df['pivot'] - high_prices.shift(1)
            df['r2'] = df['pivot'] + (high_prices.shift(1) - low_prices.shift(1))
            df['s2'] = df['pivot'] - (high_prices.shift(1) - low_prices.shift(1))
            df['r3'] = high_prices.shift(1) + 2 * (df['pivot'] - low_prices.shift(1))
            df['s3'] = low_prices.shift(1) - 2 * (high_prices.shift(1) - df['pivot'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Pivot Points: {e}")
            return df
    
    def _calculate_fibonacci_levels(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Fibonacci retracement levels"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            
            # Calculate rolling high and low
            rolling_high = high_prices.rolling(window=period).max()
            rolling_low = low_prices.rolling(window=period).min()
            
            # Calculate Fibonacci levels
            range_hl = rolling_high - rolling_low
            
            df['fib_23.6'] = rolling_high - 0.236 * range_hl
            df['fib_38.2'] = rolling_high - 0.382 * range_hl
            df['fib_50.0'] = rolling_high - 0.500 * range_hl
            df['fib_61.8'] = rolling_high - 0.618 * range_hl
            df['fib_78.6'] = rolling_high - 0.786 * range_hl
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {e}")
            return df
    
    def _calculate_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate basic candlestick pattern recognition"""
        try:
            open_prices = df['open']
            high_prices = df['high']
            low_prices = df['low']
            close_prices = df['close']
            
            # Calculate body and shadow sizes
            body_size = abs(close_prices - open_prices)
            upper_shadow = high_prices - np.maximum(open_prices, close_prices)
            lower_shadow = np.minimum(open_prices, close_prices) - low_prices
            
            # Doji pattern (small body)
            df['doji'] = body_size < (high_prices - low_prices) * 0.1
            
            # Hammer pattern
            df['hammer'] = (lower_shadow > body_size * 2) & (upper_shadow < body_size * 0.5)
            
            # Shooting star pattern
            df['shooting_star'] = (upper_shadow > body_size * 2) & (lower_shadow < body_size * 0.5)
            
            # Bullish/Bearish patterns
            df['bullish_candle'] = close_prices > open_prices
            df['bearish_candle'] = close_prices < open_prices
            
            # Long body candles (strong momentum)
            avg_body = body_size.rolling(window=20).mean()
            df['long_body'] = body_size > avg_body * 1.5
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating candlestick patterns: {e}")
            return df
    
    def _calculate_rsi(self, df: pd.DataFrame, periods: list = [9, 14, 25]) -> pd.DataFrame:
        """Calculate RSI with Korean market adjustments"""
        try:
            close_prices = df['close']
            
            for period in periods:
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                df[f'rsi_{period}'] = rsi
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return df
    
    def _calculate_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
        """Calculate MACD"""
        try:
            close_prices = df['close']
            
            # Calculate MACD line
            ema_fast = close_prices.ewm(span=fast).mean()
            ema_slow = close_prices.ewm(span=slow).mean()
            df['macd'] = ema_fast - ema_slow
            
            # Calculate Signal line
            df['macd_signal'] = df['macd'].ewm(span=signal).mean()
            
            # Calculate Histogram
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return df
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period=20, std_dev=2) -> pd.DataFrame:
        """Calculate Bollinger Bands with Korean market adjustments"""
        try:
            close_prices = df['close']
            
            # Calculate middle band (SMA)
            df['bb_middle'] = close_prices.rolling(window=period).mean()
            
            # Calculate standard deviation
            rolling_std = close_prices.rolling(window=period).std()
            
            # Calculate upper and lower bands
            df['bb_upper'] = df['bb_middle'] + (rolling_std * std_dev)
            df['bb_lower'] = df['bb_middle'] - (rolling_std * std_dev)
            
            # Calculate band width
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Calculate %B (position within bands)
            df['bb_percent'] = (close_prices - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators optimized for Korean market"""
        try:
            volume = df['volume']
            close_prices = df['close']
            high_prices = df['high']
            low_prices = df['low']
            
            # Volume Moving Averages (Korean market preferred periods)
            df['volume_ma_5'] = volume.rolling(window=5).mean()
            df['volume_ma_10'] = volume.rolling(window=10).mean()
            df['volume_ma_20'] = volume.rolling(window=20).mean()
            df['volume_ma_60'] = volume.rolling(window=60).mean()
            
            # Volume Ratio (Korean retail activity indicator)
            df['volume_ratio_10'] = volume / df['volume_ma_10']
            df['volume_ratio_20'] = volume / df['volume_ma_20']
            
            # Volume Spike Detection (Korean market characteristic)
            df['volume_spike'] = (volume > df['volume_ma_20'] * 2.0).astype(int)
            df['extreme_volume'] = (volume > df['volume_ma_20'] * 5.0).astype(int)
            
            # On-Balance Volume (OBV)
            price_change = close_prices.diff()
            volume_direction = np.where(price_change > 0, volume, 
                                      np.where(price_change < 0, -volume, 0))
            df['obv'] = volume_direction.cumsum()
            
            # OBV Moving Average
            df['obv_ma_10'] = df['obv'].rolling(window=10).mean()
            
            # Price-Volume Trend (PVT)
            pct_change = close_prices.pct_change()
            df['pvt'] = (pct_change * volume).cumsum()
            
            # Accumulation/Distribution Line
            money_flow_multiplier = ((close_prices - low_prices) - (high_prices - close_prices)) / (high_prices - low_prices)
            money_flow_volume = money_flow_multiplier * volume
            df['ad_line'] = money_flow_volume.cumsum()
            
            # Chaikin Money Flow (Korean market liquidity indicator)
            df['cmf'] = money_flow_volume.rolling(window=20).sum() / volume.rolling(window=20).sum()
            
            # Volume Rate of Change
            df['volume_roc'] = volume.pct_change(periods=10) * 100
            
            # Price Volume Trend Oscillator
            df['pvt_oscillator'] = df['pvt'] - df['pvt'].rolling(window=10).mean()
            
            # Korean Market Volume Analysis
            # Institutional vs Retail volume patterns (simplified)
            df['institutional_volume'] = np.where(
                (df['volume_ratio_20'] > 1.5) & (abs(close_prices.pct_change()) < 0.05),
                volume, 0
            )
            df['retail_volume'] = np.where(
                (df['volume_ratio_20'] > 2.0) & (abs(close_prices.pct_change()) > 0.05),
                volume, 0
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")
            return df
    
    def calculate_korean_specific_indicators(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Calculate indicators specific to Korean market"""
        try:
            close_prices = df['close']
            high_prices = df['high']
            low_prices = df['low']
            volume = df['volume']
            open_prices = df['open']
            
            # Determine market type and characteristics
            market_type = self._get_market_type(symbol)
            
            # Korean Price Limit Detection (상한가/하한가)
            prev_close = close_prices.shift(1)
            df['upper_limit_hit'] = (close_prices >= prev_close * (1 + self.price_limit_percent)).astype(int)
            df['lower_limit_hit'] = (close_prices <= prev_close * (1 - self.price_limit_percent)).astype(int)
            df['near_upper_limit'] = (close_prices >= prev_close * (1 + self.price_limit_percent * 0.8)).astype(int)
            df['near_lower_limit'] = (close_prices <= prev_close * (1 - self.price_limit_percent * 0.8)).astype(int)
            
            # Enhanced Korean Price Analysis
            df['price_limit_approach_speed'] = (close_prices - prev_close) / prev_close * 100
            df['consecutive_limit_days'] = self._calculate_consecutive_limit_days(df)
            df['limit_break_probability'] = self._calculate_limit_break_probability(df)
            
            # Korean Trading Session Analysis
            # Morning session strength (9:00-11:30)
            df['morning_strength'] = (close_prices - df['open']) / df['open'] * 100
            
            # Korean Market Momentum Indicators
            df['korean_momentum_3'] = close_prices.pct_change(periods=3) * 100
            df['korean_momentum_5'] = close_prices.pct_change(periods=5) * 100
            df['korean_momentum_10'] = close_prices.pct_change(periods=10) * 100
            df['korean_momentum_20'] = close_prices.pct_change(periods=20) * 100
            
            # Korean Volatility Adjustments
            volatility_multiplier = 1.3 if market_type == "KOSDAQ" else 1.0
            base_volatility = (high_prices - low_prices) / close_prices * 100
            df['korean_volatility'] = base_volatility * volatility_multiplier
            
            # Retail vs Institutional Activity Indicators
            # High volume with small price change (institutional)
            price_change_pct = abs(close_prices.pct_change() * 100)
            volume_ma_20 = volume.rolling(window=20).mean()
            
            df['institutional_activity'] = np.where(
                (volume > volume_ma_20 * 1.5) & (price_change_pct < 3.0),
                1, 0
            )
            
            df['retail_frenzy'] = np.where(
                (volume > volume_ma_20 * 3.0) & (price_change_pct > 5.0),
                1, 0
            )
            
            # Korean Market Strength Index
            # Combines volume, price movement, and market type
            strength_score = 0
            if 'volume_ratio_20' in df.columns:
                strength_score += np.where(df['volume_ratio_20'] > 2.0, 1, 0)
            strength_score += np.where(abs(close_prices.pct_change() * 100) > 5.0, 1, 0)
            strength_score += np.where(df['korean_volatility'] > df['korean_volatility'].rolling(20).mean(), 1, 0)
            df['korean_strength_index'] = strength_score
            
            # Korean Chart Pattern Indicators
            # Gap Up/Down Detection (Korean market characteristic)
            gap_threshold = 0.02  # 2%
            df['gap_up'] = ((df['open'] - prev_close) / prev_close > gap_threshold).astype(int)
            df['gap_down'] = ((prev_close - df['open']) / prev_close > gap_threshold).astype(int)
            df['gap_fill'] = np.where(
                df['gap_up'].shift(1) == 1,
                (close_prices <= prev_close.shift(1)).astype(int),
                np.where(
                    df['gap_down'].shift(1) == 1,
                    (close_prices >= prev_close.shift(1)).astype(int),
                    0
                )
            )
            
            # Korean Market Cycle Indicator
            # 5-day and 20-day relative strength
            ma_5 = close_prices.rolling(window=5).mean()
            ma_20 = close_prices.rolling(window=20).mean()
            df['korean_cycle'] = np.where(
                (close_prices > ma_5) & (ma_5 > ma_20),
                2,  # Strong uptrend
                np.where(
                    (close_prices < ma_5) & (ma_5 < ma_20),
                    -2,  # Strong downtrend
                    np.where(
                        close_prices > ma_20,
                        1,  # Mild uptrend
                        -1  # Mild downtrend
                    )
                )
            )
            
            # Korean Won Precision Adjustments
            # Round to appropriate Korean Won denominations
            df['rounded_close'] = np.where(
                close_prices >= 100000,
                (close_prices / 1000).round() * 1000,  # Round to nearest 1000 won
                np.where(
                    close_prices >= 10000,
                    (close_prices / 100).round() * 100,  # Round to nearest 100 won
                    np.where(
                        close_prices >= 1000,
                        (close_prices / 10).round() * 10,  # Round to nearest 10 won
                        close_prices.round()  # Round to nearest won
                    )
                )
            )
            
            # Market Type Specific Adjustments
            if market_type == "KOSDAQ":
                # KOSDAQ tends to be more volatile and retail-driven
                df['kosdaq_retail_indicator'] = np.where(
                    (df['retail_frenzy'] == 1) & (df['korean_volatility'] > 8.0),
                    1, 0
                )
            else:
                # KOSPI tends to be more institutional
                df['kospi_institutional_indicator'] = np.where(
                    (df['institutional_activity'] == 1) & (df['korean_volatility'] < 5.0),
                    1, 0
                )
            
            # Korean Market Session Indicators
            # Pre-market and after-hours would need additional data
            # For now, mark regular trading strength
            df['regular_session_strength'] = (
                (close_prices - df['open']) / df['open'] * 100
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Korean specific indicators: {e}")
            return df
    
    def _get_market_type(self, symbol: str) -> str:
        """Determine if stock is KOSPI or KOSDAQ (simplified)"""
        # This is a simplified version - in production, would query database
        # KOSPI stocks generally have 6-digit codes starting with 0
        # KOSDAQ stocks have various patterns
        try:
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith('0'):
                    return "KOSPI"
                else:
                    return "KOSDAQ"
            return "KOSPI"  # Default
        except:
            return "KOSPI"
    
    def _calculate_consecutive_limit_days(self, df: pd.DataFrame) -> pd.Series:
        """Calculate consecutive days of price limit hits"""
        try:
            limit_hits = (df['upper_limit_hit'] == 1) | (df['lower_limit_hit'] == 1)
            
            # Create groups for consecutive periods
            consecutive_groups = (limit_hits != limit_hits.shift()).cumsum()
            
            # Count consecutive days for each group
            consecutive_counts = limit_hits.groupby(consecutive_groups).cumsum()
            
            # Only keep counts where limit_hits is True
            return consecutive_counts * limit_hits
            
        except Exception as e:
            logger.error(f"Error calculating consecutive limit days: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    def _calculate_limit_break_probability(self, df: pd.DataFrame) -> pd.Series:
        """Calculate probability of breaking through price limits"""
        try:
            # Simplified probability based on volume and momentum
            volume_factor = df['volume_ratio_20'].fillna(1.0)
            momentum_factor = abs(df['korean_momentum_3'].fillna(0.0)) / 10.0
            
            # Higher volume and momentum increase break probability
            probability = np.minimum(
                (volume_factor * 0.3 + momentum_factor * 0.7) / 2.0,
                1.0
            )
            
            return probability
            
        except Exception as e:
            logger.error(f"Error calculating limit break probability: {e}")
            return pd.Series([0.5] * len(df), index=df.index)
    
    def calculate_strategy_signals(self, df: pd.DataFrame, strategy_config: Dict) -> pd.DataFrame:
        """Calculate buy/sell signals based on strategy configuration"""
        try:
            # Initialize signal columns
            df['buy_signal'] = False
            df['sell_signal'] = False
            df['signal_strength'] = 0.0
            
            # Parse strategy conditions
            entry_conditions = strategy_config.get('entry_conditions', {})
            exit_conditions = strategy_config.get('exit_conditions', {})
            
            # Calculate entry signals
            if entry_conditions:
                df = self._evaluate_conditions(df, entry_conditions, 'buy_signal')
            
            # Calculate exit signals
            if exit_conditions:
                df = self._evaluate_conditions(df, exit_conditions, 'sell_signal')
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating strategy signals: {e}")
            return df
    
    def _evaluate_conditions(self, df: pd.DataFrame, conditions: Dict, signal_column: str) -> pd.DataFrame:
        """Evaluate strategy conditions and set signals"""
        try:
            # This is a simplified version - in production, would have a full condition parser
            signal_mask = pd.Series([True] * len(df), index=df.index)
            
            for condition in conditions.get('conditions', []):
                indicator = condition.get('indicator')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if indicator in df.columns:
                    if operator == 'greater_than':
                        mask = df[indicator] > value
                    elif operator == 'less_than':
                        mask = df[indicator] < value
                    elif operator == 'crosses_above':
                        # Simple cross detection
                        mask = (df[indicator] > value) & (df[indicator].shift(1) <= value)
                    elif operator == 'crosses_below':
                        mask = (df[indicator] < value) & (df[indicator].shift(1) >= value)
                    else:
                        continue
                    
                    # Combine conditions based on logic (AND/OR)
                    logic = conditions.get('logic', 'AND')
                    if logic == 'AND':
                        signal_mask = signal_mask & mask
                    else:  # OR
                        signal_mask = signal_mask | mask
            
            df[signal_column] = signal_mask
            
            return df
            
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return df
    
    def get_available_indicators(self) -> Dict[str, List[str]]:
        """Get list of all available technical indicators organized by category"""
        return {
            "moving_averages": [
                "ma_5", "ma_10", "ma_15", "ma_20", "ma_25", "ma_30", "ma_60", "ma_120", "ma_200",
                "ema_9", "ema_12", "ema_21", "ema_26", "ema_50",
                "wma_20", "wma_60", "hma_21", "tma_20", "vwma_20",
                "hlc_avg", "hlc_ma_20"
            ],
            "momentum_oscillators": [
                "rsi_9", "rsi_14", "rsi_25",
                "stoch_k", "stoch_d", "stoch_slow_d",
                "williams_r", "cci", "roc_10", "roc_20",
                "momentum", "momentum_pct"
            ],
            "trend_indicators": [
                "macd", "macd_signal", "macd_histogram",
                "bb_upper", "bb_middle", "bb_lower", "bb_width", "bb_percent",
                "keltner_upper", "keltner_mid", "keltner_lower", "keltner_position"
            ],
            "volume_indicators": [
                "volume_ma_5", "volume_ma_10", "volume_ma_20", "volume_ma_60",
                "volume_ratio_10", "volume_ratio_20", "volume_spike", "extreme_volume",
                "obv", "obv_ma_10", "pvt", "pvt_oscillator",
                "ad_line", "cmf", "volume_roc",
                "institutional_volume", "retail_volume",
                "vwap", "vwap_daily", "mfi"
            ],
            "volatility_indicators": [
                "atr", "atr_pct", "korean_volatility"
            ],
            "support_resistance": [
                "pivot", "r1", "r2", "r3", "s1", "s2", "s3",
                "fib_23.6", "fib_38.2", "fib_50.0", "fib_61.8", "fib_78.6"
            ],
            "pattern_recognition": [
                "doji", "hammer", "shooting_star", "bullish_candle", "bearish_candle", "long_body"
            ],
            "korean_market_specific": [
                "upper_limit_hit", "lower_limit_hit", "near_upper_limit", "near_lower_limit",
                "morning_strength", "korean_momentum_3", "korean_momentum_5", 
                "korean_momentum_10", "korean_momentum_20",
                "institutional_activity", "retail_frenzy", "korean_strength_index",
                "gap_up", "gap_down", "gap_fill", "korean_cycle",
                "rounded_close", "regular_session_strength"
            ],
            "market_type_specific": [
                "kosdaq_retail_indicator", "kospi_institutional_indicator"
            ]
        }
    
    def calculate_indicator_summary(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate summary statistics for key indicators"""
        try:
            summary = {}
            
            if len(df) == 0:
                return summary
            
            latest_row = df.iloc[-1]
            
            # Price indicators
            if 'close' in df.columns:
                summary['current_price'] = float(latest_row['close'])
                summary['price_change_1d'] = float((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) >= 2 else 0
                summary['price_change_5d'] = float(df['close'].pct_change(periods=5).iloc[-1] * 100) if len(df) >= 6 else 0
                summary['price_change_20d'] = float(df['close'].pct_change(periods=20).iloc[-1] * 100) if len(df) >= 21 else 0
            
            # Moving averages signals
            if 'ma_20' in df.columns and 'close' in df.columns:
                summary['above_ma20'] = bool(latest_row['close'] > latest_row['ma_20'])
            if 'ma_60' in df.columns and 'close' in df.columns:
                summary['above_ma60'] = bool(latest_row['close'] > latest_row['ma_60'])
            
            # RSI signal
            if 'rsi_14' in df.columns:
                rsi_value = float(latest_row['rsi_14'])
                summary['rsi_14'] = rsi_value
                summary['rsi_signal'] = 'overbought' if rsi_value > 70 else 'oversold' if rsi_value < 30 else 'neutral'
            
            # MACD signal
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                summary['macd_bullish'] = bool(latest_row['macd'] > latest_row['macd_signal'])
            
            # Volume analysis
            if 'volume_ratio_20' in df.columns:
                volume_ratio = float(latest_row['volume_ratio_20'])
                summary['volume_ratio'] = volume_ratio
                summary['volume_signal'] = 'high' if volume_ratio > 2.0 else 'normal' if volume_ratio > 0.5 else 'low'
            
            # Korean market specific
            if 'korean_strength_index' in df.columns:
                summary['korean_strength'] = int(latest_row['korean_strength_index'])
            
            if 'korean_volatility' in df.columns:
                summary['volatility'] = float(latest_row['korean_volatility'])
            
            # Pattern signals
            pattern_signals = []
            if 'gap_up' in df.columns and latest_row['gap_up'] == 1:
                pattern_signals.append('gap_up')
            if 'gap_down' in df.columns and latest_row['gap_down'] == 1:
                pattern_signals.append('gap_down')
            if 'upper_limit_hit' in df.columns and latest_row['upper_limit_hit'] == 1:
                pattern_signals.append('price_limit_up')
            if 'lower_limit_hit' in df.columns and latest_row['lower_limit_hit'] == 1:
                pattern_signals.append('price_limit_down')
            
            summary['pattern_signals'] = pattern_signals
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating indicator summary: {e}")
            return {}
    
    def validate_indicator_data(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Validate that required data columns exist for indicator calculation"""
        validation = {
            'has_ohlcv': all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']),
            'sufficient_data': len(df) >= 200,  # Need at least 200 periods for all indicators
            'no_missing_prices': not df[['open', 'high', 'low', 'close']].isnull().any().any() if 'close' in df.columns else False,
            'positive_volume': (df['volume'] > 0).all() if 'volume' in df.columns else False,
            'chronological_order': df.index.is_monotonic_increasing if hasattr(df.index, 'is_monotonic_increasing') else True
        }
        
        validation['ready_for_calculation'] = all(validation.values())
        
        return validation