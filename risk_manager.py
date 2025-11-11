"""
NexusDEX AI - Advanced Risk Manager
====================================
Мощна risk management система с:
- Daily loss limits (circuit breaker)
- Position sizing calculation
- Portfolio heat tracking
- Maximum drawdown protection
- Auto de-leverage при опасност
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """Risk limits configuration за user"""
    max_daily_loss_percent: float = 5.0  # Max 5% daily loss
    max_position_size_percent: float = 10.0  # Max 10% per trade
    max_open_positions: int = 5  # Max 5 concurrent positions
    max_portfolio_heat: float = 15.0  # Max 15% total risk exposure
    max_drawdown_percent: float = 20.0  # Max 20% drawdown
    risk_per_trade_percent: float = 1.0  # Default 1% risk per trade
    leverage_max: int = 10  # Max leverage 10x
    daily_trade_limit: int = 20  # Max 20 trades per day


@dataclass
class PositionRisk:
    """Risk parameters за отделна позиция"""
    entry_price: float
    stop_loss: float
    position_size: float
    leverage: int
    risk_amount: float
    risk_percent: float


class RiskManager:
    """
    Advanced Risk Management System
    Предпазва account от катастрофични загуби
    """
    
    def __init__(self, risk_limits: Optional[RiskLimits] = None):
        """Initialize risk manager with limits"""
        self.limits = risk_limits or RiskLimits()
        self.daily_stats = {}
        self.active_positions = []
        self.circuit_breaker_active = False
    
    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        risk_percent: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Изчислява оптимален position size базиран на risk
        
        Args:
            account_balance: Total account balance
            entry_price: Planned entry price
            stop_loss_price: Planned stop loss
            risk_percent: Risk per trade (default: from limits)
        
        Returns:
            (position_size, risk_amount) tuple
        
        Example:
            size, risk = risk_manager.calculate_position_size(
                account_balance=10000,
                entry_price=45000,
                stop_loss_price=44000,
                risk_percent=1.0
            )
        """
        if risk_percent is None:
            risk_percent = self.limits.risk_per_trade_percent
        
        # Calculate risk amount in dollars
        risk_amount = account_balance * (risk_percent / 100)
        
        # Calculate price distance to stop loss
        price_distance = abs(entry_price - stop_loss_price)
        risk_per_unit = price_distance
        
        # Calculate position size
        # Position size = Risk amount / Risk per unit
        position_size = risk_amount / risk_per_unit
        
        # Check max position size limit
        max_position_value = account_balance * (self.limits.max_position_size_percent / 100)
        max_position_size = max_position_value / entry_price
        
        if position_size > max_position_size:
            logger.warning(
                f"⚠️ Position size {position_size:.4f} exceeds max "
                f"{max_position_size:.4f}, reducing..."
            )
            position_size = max_position_size
            risk_amount = position_size * risk_per_unit
        
        logger.info(
            f"📊 Position sizing: Size={position_size:.4f}, "
            f"Risk=${risk_amount:.2f} ({risk_percent}%)"
        )
        
        return position_size, risk_amount
    
    def validate_new_position(
        self,
        account_balance: float,
        position_risk: PositionRisk,
        current_positions: List[Dict]
    ) -> Tuple[bool, str]:
        """
        Валидира дали нова позиция е позволена
        
        Args:
            account_balance: Current account balance
            position_risk: Risk parameters за новата позиция
            current_positions: List of active positions
        
        Returns:
            (is_valid, reason) tuple
        
        Example:
            valid, reason = risk_manager.validate_new_position(
                account_balance=10000,
                position_risk=position_risk,
                current_positions=active_positions
            )
            if not valid:
                print(f"Trade rejected: {reason}")
        """
        # Check circuit breaker
        if self.circuit_breaker_active:
            return False, "🚨 CIRCUIT BREAKER ACTIVE - Daily loss limit reached"
        
        # Check max open positions
        if len(current_positions) >= self.limits.max_open_positions:
            return False, f"⚠️ Max open positions limit ({self.limits.max_open_positions}) reached"
        
        # Check daily trade limit
        today = datetime.now().date()
        daily_trades = self._get_daily_trade_count(today)
        if daily_trades >= self.limits.daily_trade_limit:
            return False, f"⚠️ Daily trade limit ({self.limits.daily_trade_limit}) reached"
        
        # Calculate current portfolio heat
        current_heat = self._calculate_portfolio_heat(current_positions, account_balance)
        new_heat = current_heat + position_risk.risk_percent
        
        if new_heat > self.limits.max_portfolio_heat:
            return False, (
                f"⚠️ Portfolio heat too high: {new_heat:.2f}% "
                f"(max: {self.limits.max_portfolio_heat}%)"
            )
        
        # Check position size
        position_value = position_risk.position_size * position_risk.entry_price
        max_position_value = account_balance * (self.limits.max_position_size_percent / 100)
        
        if position_value > max_position_value:
            return False, (
                f"⚠️ Position size too large: ${position_value:.2f} "
                f"(max: ${max_position_value:.2f})"
            )
        
        # Check leverage
        if position_risk.leverage > self.limits.leverage_max:
            return False, (
                f"⚠️ Leverage too high: {position_risk.leverage}x "
                f"(max: {self.limits.leverage_max}x)"
            )
        
        # All checks passed
        logger.info("✅ Position validation passed")
        return True, "Position approved"
    
    def _calculate_portfolio_heat(
        self,
        positions: List[Dict],
        account_balance: float
    ) -> float:
        """
        Изчислява общия risk exposure на портфолиото
        
        Portfolio Heat = Сумата от всички активни рискове
        
        Returns:
            Total risk exposure като процент от balance
        """
        total_risk = 0.0
        
        for position in positions:
            # Calculate risk за тази позиция
            entry_price = position.get('entry_price', 0)
            stop_loss = position.get('stop_loss', 0)
            size = position.get('size', 0)
            
            if entry_price and stop_loss and size:
                risk_per_unit = abs(entry_price - stop_loss)
                position_risk = risk_per_unit * size
                risk_percent = (position_risk / account_balance) * 100
                total_risk += risk_percent
        
        return total_risk
    
    def check_daily_loss_limit(
        self,
        account_balance: float,
        starting_balance: float
    ) -> Tuple[bool, float]:
        """
        Проверява далиDaily Loss Limit е достигнат
        Ако е - активира Circuit Breaker
        
        Args:
            account_balance: Current balance
            starting_balance: Balance в началото на деня
        
        Returns:
            (limit_reached, loss_percent) tuple
        
        Example:
            limit_reached, loss_pct = risk_manager.check_daily_loss_limit(
                account_balance=9300,
                starting_balance=10000
            )
            if limit_reached:
                print(f"🚨 Stop trading! Loss: {loss_pct}%")
        """
        # Calculate daily loss
        daily_loss = starting_balance - account_balance
        loss_percent = (daily_loss / starting_balance) * 100
        
        # Check if limit exceeded
        if loss_percent >= self.limits.max_daily_loss_percent:
            self.circuit_breaker_active = True
            logger.critical(
                f"🚨 CIRCUIT BREAKER ACTIVATED! "
                f"Daily loss: {loss_percent:.2f}% "
                f"(limit: {self.limits.max_daily_loss_percent}%)"
            )
            return True, loss_percent
        
        return False, loss_percent
    
    def check_max_drawdown(
        self,
        current_balance: float,
        peak_balance: float
    ) -> Tuple[bool, float]:
        """
        Проверява максимален drawdown
        
        Args:
            current_balance: Current account balance
            peak_balance: Highest balance ever reached
        
        Returns:
            (limit_reached, drawdown_percent) tuple
        
        Example:
            dd_reached, dd_pct = risk_manager.check_max_drawdown(
                current_balance=8500,
                peak_balance=10000
            )
        """
        drawdown = peak_balance - current_balance
        drawdown_percent = (drawdown / peak_balance) * 100
        
        if drawdown_percent >= self.limits.max_drawdown_percent:
            logger.critical(
                f"🚨 MAX DRAWDOWN REACHED! "
                f"Drawdown: {drawdown_percent:.2f}% "
                f"(limit: {self.limits.max_drawdown_percent}%)"
            )
            return True, drawdown_percent
        
        return False, drawdown_percent
    
    def should_reduce_position_size(
        self,
        consecutive_losses: int,
        current_drawdown: float
    ) -> Tuple[bool, float]:
        """
        Определя дали да намали position size след загуби
        
        Adaptive Risk: След consecutive losses намаляваме risk
        
        Args:
            consecutive_losses: Брой consecutive losing trades
            current_drawdown: Current drawdown percent
        
        Returns:
            (should_reduce, new_risk_percent) tuple
        
        Example:
            reduce, new_risk = risk_manager.should_reduce_position_size(
                consecutive_losses=3,
                current_drawdown=8.5
            )
        """
        base_risk = self.limits.risk_per_trade_percent
        
        # Reduce risk based on consecutive losses
        if consecutive_losses >= 5:
            reduction_factor = 0.25  # 75% reduction
        elif consecutive_losses >= 3:
            reduction_factor = 0.50  # 50% reduction
        elif consecutive_losses >= 2:
            reduction_factor = 0.75  # 25% reduction
        else:
            reduction_factor = 1.0  # No reduction
        
        # Further reduce based on drawdown
        if current_drawdown >= 15:
            reduction_factor *= 0.5
        elif current_drawdown >= 10:
            reduction_factor *= 0.75
        
        new_risk = base_risk * reduction_factor
        
        if reduction_factor < 1.0:
            logger.warning(
                f"⚠️ Reducing risk: {base_risk}% → {new_risk}% "
                f"(losses: {consecutive_losses}, DD: {current_drawdown:.1f}%)"
            )
            return True, new_risk
        
        return False, base_risk
    
    def calculate_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Kelly Criterion за оптимален position sizing
        
        Kelly % = W - [(1 - W) / R]
        където:
        W = win rate (0-1)
        R = avg_win / avg_loss
        
        Args:
            win_rate: Win rate (напр. 0.55 за 55%)
            avg_win: Average win size
            avg_loss: Average loss size (positive number)
        
        Returns:
            Optimal risk percent (обикновено използваме половината за safety)
        
        Example:
            kelly = risk_manager.calculate_kelly_criterion(
                win_rate=0.60,
                avg_win=150,
                avg_loss=100
            )
        """
        if avg_loss == 0:
            return 0.0
        
        R = avg_win / avg_loss  # Win/Loss ratio
        kelly = win_rate - ((1 - win_rate) / R)
        
        # Kelly може да е negative (значи strategy губи)
        if kelly <= 0:
            logger.warning("⚠️ Negative Kelly - Strategy is losing!")
            return 0.0
        
        # Half Kelly за по-conservative approach
        half_kelly = kelly / 2
        
        # Cap на 5% (защото full Kelly може да е агресивен)
        optimal_risk = min(half_kelly * 100, 5.0)
        
        logger.info(
            f"📊 Kelly Criterion: {kelly*100:.2f}% "
            f"(Half Kelly: {optimal_risk:.2f}%)"
        )
        
        return optimal_risk
    
    def _get_daily_trade_count(self, date) -> int:
        """Get trade count за конкретна дата"""
        return self.daily_stats.get(str(date), {}).get('trade_count', 0)
    
    def _increment_daily_trade_count(self, date):
        """Increment trade count"""
        date_str = str(date)
        if date_str not in self.daily_stats:
            self.daily_stats[date_str] = {'trade_count': 0}
        self.daily_stats[date_str]['trade_count'] += 1
    
    def reset_daily_limits(self):
        """
        Reset daily limits в началото на нов trading day
        Трябва да се извиква всеки ден в 00:00 UTC
        """
        self.circuit_breaker_active = False
        self.daily_stats = {}
        logger.info("✅ Daily risk limits reset")
    
    def get_risk_status(
        self,
        account_balance: float,
        starting_balance: float,
        peak_balance: float,
        active_positions: List[Dict]
    ) -> Dict:
        """
        Връща comprehensive risk status report
        
        Returns:
            {
                'circuit_breaker': False,
                'daily_loss_pct': 2.5,
                'drawdown_pct': 8.2,
                'portfolio_heat': 12.5,
                'positions_count': 3,
                'daily_trades': 8,
                'risk_level': 'MEDIUM'
            }
        """
        # Calculate metrics
        daily_loss = ((starting_balance - account_balance) / starting_balance) * 100
        drawdown = ((peak_balance - account_balance) / peak_balance) * 100
        portfolio_heat = self._calculate_portfolio_heat(active_positions, account_balance)
        
        # Determine risk level
        if self.circuit_breaker_active or daily_loss >= self.limits.max_daily_loss_percent:
            risk_level = 'CRITICAL'
        elif portfolio_heat >= self.limits.max_portfolio_heat * 0.8:
            risk_level = 'HIGH'
        elif portfolio_heat >= self.limits.max_portfolio_heat * 0.5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'circuit_breaker': self.circuit_breaker_active,
            'daily_loss_pct': round(daily_loss, 2),
            'daily_loss_limit': self.limits.max_daily_loss_percent,
            'drawdown_pct': round(drawdown, 2),
            'drawdown_limit': self.limits.max_drawdown_percent,
            'portfolio_heat': round(portfolio_heat, 2),
            'portfolio_heat_limit': self.limits.max_portfolio_heat,
            'positions_count': len(active_positions),
            'positions_limit': self.limits.max_open_positions,
            'daily_trades': self._get_daily_trade_count(datetime.now().date()),
            'daily_trades_limit': self.limits.daily_trade_limit,
            'risk_level': risk_level
        }


# Helper function
def create_risk_manager(
    max_daily_loss: float = 5.0,
    max_position_size: float = 10.0,
    risk_per_trade: float = 1.0
) -> RiskManager:
    """
    Quick creation на risk manager с custom limits
    
    Usage:
        risk_mgr = create_risk_manager(
            max_daily_loss=3.0,
            risk_per_trade=0.5
        )
    """
    limits = RiskLimits(
        max_daily_loss_percent=max_daily_loss,
        max_position_size_percent=max_position_size,
        risk_per_trade_percent=risk_per_trade
    )
    return RiskManager(limits)
