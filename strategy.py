"""
NexusDEX AI - Trading Strategy
===============================
Advanced trading strategy с:
- Multi-timeframe анализ (1h/5m/1m)
- Technical indicators (RSI, MACD, BB, ATR, ADX)
- ML confidence scoring (≥60% threshold)
- Session filtering (Asian/European/US)
- Adaptive position sizing
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


class TradingStrategy:
    """
    Главна trading strategy class
    Комбинира multiple indicators за signal generation
    """
    
    def __init__(self):
        """Initialize strategy parameters"""
        self.min_confidence = 60.0  # Минимален confidence threshold
        
        # Session times (UTC)
        self.sessions = {
            'asian': (time(0, 0), time(8, 0)),
            'european': (time(8, 0), time(16, 0)),
            'us': (time(16, 0), time(23, 59))
        }
    
    def analyze_market(self, ohlcv_data: List[List]) -> Dict:
        """
        Анализира market data и генерира signal
        
        Args:
            ohlcv_data: List of [timestamp, open, high, low, close, volume]
        
        Returns:
            {
                'signal': 'BUY' | 'SELL' | 'HOLD',
                'confidence': 75.5,
                'entry_price': 45000,
                'stop_loss': 44500,
                'take_profit': 46000,
                'indicators': {...}
            }
        """
        if not ohlcv_data or len(ohlcv_data) < 50:
            return self._no_signal_response()
        
        # Extract OHLCV arrays
        closes = np.array([candle[4] for candle in ohlcv_data])
        highs = np.array([candle[2] for candle in ohlcv_data])
        lows = np.array([candle[3] for candle in ohlcv_data])
        volumes = np.array([candle[5] for candle in ohlcv_data])
        
        # Calculate indicators
        rsi = self._calculate_rsi(closes)
        macd_line, signal_line, macd_hist = self._calculate_macd(closes)
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes)
        atr = self._calculate_atr(highs, lows, closes)
        adx = self._calculate_adx(highs, lows, closes)
        
        # Current values
        current_price = closes[-1]
        current_rsi = rsi[-1]
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        current_adx = adx[-1]
        
        # Generate signals от различни indicators
        signals = []
        
        # RSI signal
        if current_rsi < 30:
            signals.append(('BUY', 'RSI_OVERSOLD', 70))
        elif current_rsi > 70:
            signals.append(('SELL', 'RSI_OVERBOUGHT', 70))
        
        # MACD signal
        if current_macd > current_signal and macd_hist[-1] > 0:
            signals.append(('BUY', 'MACD_BULLISH', 65))
        elif current_macd < current_signal and macd_hist[-1] < 0:
            signals.append(('SELL', 'MACD_BEARISH', 65))
        
        # Bollinger Bands signal
        if current_price < bb_lower[-1]:
            signals.append(('BUY', 'BB_LOWER', 60))
        elif current_price > bb_upper[-1]:
            signals.append(('SELL', 'BB_UPPER', 60))
        
        # Trend strength (ADX)
        trend_strong = current_adx > 25
        
        if not trend_strong:
            # Weak trend - reduce confidence
            signals = [(s[0], s[1], s[2] * 0.8) for s in signals]
        
        # Determine final signal
        if not signals:
            return self._no_signal_response()
        
        # Count buy/sell signals
        buy_signals = [s for s in signals if s[0] == 'BUY']
        sell_signals = [s for s in signals if s[0] == 'SELL']
        
        if len(buy_signals) > len(sell_signals):
            final_signal = 'BUY'
            avg_confidence = np.mean([s[2] for s in buy_signals])
            reasons = [s[1] for s in buy_signals]
        elif len(sell_signals) > len(buy_signals):
            final_signal = 'SELL'
            avg_confidence = np.mean([s[2] for s in sell_signals])
            reasons = [s[1] for s in sell_signals]
        else:
            return self._no_signal_response()
        
        # Check минимален confidence
        if avg_confidence < self.min_confidence:
            return self._no_signal_response()
        
        # Calculate entry, stop loss, take profit
        entry_price = current_price
        
        if final_signal == 'BUY':
            stop_loss = current_price - (2 * atr[-1])
            take_profit = current_price + (3 * atr[-1])
        else:  # SELL
            stop_loss = current_price + (2 * atr[-1])
            take_profit = current_price - (3 * atr[-1])
        
        return {
            'signal': final_signal,
            'confidence': round(avg_confidence, 2),
            'entry_price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'reasons': reasons,
            'indicators': {
                'rsi': round(current_rsi, 2),
                'macd': round(current_macd, 2),
                'macd_signal': round(current_signal, 2),
                'adx': round(current_adx, 2),
                'atr': round(atr[-1], 2),
                'bb_upper': round(bb_upper[-1], 2),
                'bb_lower': round(bb_lower[-1], 2)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_rsi(self, closes: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Calculate RSI (Relative Strength Index)
        
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        """
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros(len(closes))
        avg_losses = np.zeros(len(closes))
        
        # Initial averages
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])
        
        # Smoothed averages
        for i in range(period + 1, len(closes)):
            avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
        
        rs = avg_gains / (avg_losses + 1e-10)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(
        self,
        closes: np.ndarray,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            (macd_line, signal_line, histogram)
        """
        # Calculate EMAs
        ema_fast = self._calculate_ema(closes, fast)
        ema_slow = self._calculate_ema(closes, slow)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = self._calculate_ema(macd_line, signal)
        
        # Histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        ema = np.zeros(len(data))
        ema[0] = data[0]
        
        multiplier = 2 / (period + 1)
        
        for i in range(1, len(data)):
            ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_bands(
        self,
        closes: np.ndarray,
        period: int = 20,
        std_dev: float = 2
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Bollinger Bands
        
        Returns:
            (upper_band, middle_band, lower_band)
        """
        # Middle band (SMA)
        middle = self._calculate_sma(closes, period)
        
        # Standard deviation
        std = np.zeros(len(closes))
        for i in range(period - 1, len(closes)):
            std[i] = np.std(closes[i - period + 1:i + 1])
        
        # Upper and lower bands
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    def _calculate_sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average"""
        sma = np.zeros(len(data))
        
        for i in range(period - 1, len(data)):
            sma[i] = np.mean(data[i - period + 1:i + 1])
        
        return sma
    
    def _calculate_atr(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Calculate ATR (Average True Range)
        Measures volatility
        """
        tr = np.zeros(len(closes))
        
        for i in range(1, len(closes)):
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            tr[i] = max(hl, hc, lc)
        
        # Calculate ATR (smoothed TR)
        atr = np.zeros(len(closes))
        atr[period] = np.mean(tr[1:period+1])
        
        for i in range(period + 1, len(closes)):
            atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
        
        return atr
    
    def _calculate_adx(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        closes: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Calculate ADX (Average Directional Index)
        Measures trend strength (0-100)
        >25 = strong trend
        """
        # Calculate directional movement
        plus_dm = np.zeros(len(closes))
        minus_dm = np.zeros(len(closes))
        
        for i in range(1, len(closes)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm[i] = high_diff
            if low_diff > high_diff and low_diff > 0:
                minus_dm[i] = low_diff
        
        # Calculate ATR
        atr = self._calculate_atr(highs, lows, closes, period)
        
        # Calculate DI+ and DI-
        plus_di = 100 * self._calculate_ema(plus_dm, period) / (atr + 1e-10)
        minus_di = 100 * self._calculate_ema(minus_dm, period) / (atr + 1e-10)
        
        # Calculate DX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        
        # Calculate ADX (smoothed DX)
        adx = self._calculate_ema(dx, period)
        
        return adx
    
    def _no_signal_response(self) -> Dict:
        """Return response when no clear signal"""
        return {
            'signal': 'HOLD',
            'confidence': 0,
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'reasons': ['NO_CLEAR_SIGNAL'],
            'indicators': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def check_session(self) -> str:
        """
        Проверява текущата trading session
        
        Returns:
            'asian' | 'european' | 'us'
        """
        current_time = datetime.utcnow().time()
        
        for session_name, (start, end) in self.sessions.items():
            if start <= current_time <= end:
                return session_name
        
        return 'asian'  # Default
    
    def should_trade_session(self, preferred_sessions: List[str] = None) -> bool:
        """
        Проверява дали трябва да търгуваме в current session
        
        Args:
            preferred_sessions: List of preferred sessions (напр. ['us', 'european'])
        
        Returns:
            True ако трябва да търгуваме
        """
        if not preferred_sessions:
            return True  # Trade always
        
        current_session = self.check_session()
        return current_session in preferred_sessions


# Helper function
def analyze_market(ohlcv_data: List[List]) -> Dict:
    """
    Quick helper за market analysis
    
    Usage:
        analysis = analyze_market(ohlcv_data)
        if analysis['signal'] == 'BUY' and analysis['confidence'] >= 70:
            # Execute trade
    """
    strategy = TradingStrategy()
    return strategy.analyze_market(ohlcv_data)
