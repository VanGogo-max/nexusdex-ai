"""
NexusDEX AI - Real Trading Engine
==================================
Реален trading engine който:
- Изпълнява trades на борсите
- Управлява open positions
- Синхронизира с database
- Проверява risk management
- Изпраща notifications
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import asyncio

from exchange_connector import exchange_connector, get_current_price
from database import (
    save_trade, get_user_trades, get_user,
    update_user_balance, get_api_keys
)
from encryption import encryption_manager
from risk_manager import RiskManager, RiskLimits, PositionRisk
from notifications import (
    notify_trade_opened, notify_trade_closed,
    notify_error, notify_critical
)

logger = logging.getLogger(__name__)


class TradingMode:
    """Trading режими"""
    DEMO = "demo"  # Симулирани данни
    PAPER = "paper"  # Реални цени, фалшиви пари
    LIVE = "live"  # Реални пари


class TradingEngine:
    """
    Главен trading engine
    Управлява целия lifecycle на trades
    """
    
    def __init__(self, mode: str = TradingMode.PAPER):
        """
        Initialize trading engine
        
        Args:
            mode: Trading mode (demo/paper/live)
        """
        self.mode = mode
        self.risk_manager = RiskManager()
        self.active_positions = {}  # {trade_id: position_data}
        
        logger.info(f"🚀 Trading Engine initialized in {mode.upper()} mode")
    
    def execute_trade(
        self,
        user_id: int,
        exchange: str,
        pair: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        size: float,
        leverage: int = 1,
        confidence_score: Optional[float] = None
    ) -> Tuple[bool, Optional[int], str]:
        """
        Изпълнява trade
        
        Args:
            user_id: User ID
            exchange: Exchange ID (напр. 'dydx')
            pair: Trading pair (напр. 'BTC/USD')
            side: 'LONG' или 'SHORT'
            entry_price: Entry цена
            stop_loss: Stop loss цена
            take_profit: Take profit цена
            size: Position size
            leverage: Leverage (default: 1)
            confidence_score: ML confidence (optional)
        
        Returns:
            (success, trade_id, message)
        """
        try:
            # Get user
            user = get_user(user_id)
            if not user:
                return False, None, "User not found"
            
            # Check subscription
            # TODO: Add subscription check
            
            # Validate risk
            position_risk = PositionRisk(
                entry_price=entry_price,
                stop_loss=stop_loss,
                position_size=size,
                leverage=leverage,
                risk_amount=0,
                risk_percent=1.0
            )
            
            # Get active positions за risk check
            active_trades = get_user_trades(user_id, status='OPEN')
            
            valid, reason = self.risk_manager.validate_new_position(
                account_balance=user.get('paper_balance', 10000),
                position_risk=position_risk,
                current_positions=active_trades
            )
            
            if not valid:
                logger.warning(f"⚠️ Trade rejected: {reason}")
                return False, None, reason
            
            # Execute based on mode
            if self.mode == TradingMode.LIVE:
                # LIVE mode - реално изпълнение на борсата
                success, order_id = self._execute_live_trade(
                    user_id, exchange, pair, side, entry_price,
                    size, leverage
                )
                
                if not success:
                    return False, None, "Failed to execute live trade"
            
            elif self.mode == TradingMode.PAPER:
                # PAPER mode - симулирано изпълнение с реални цени
                success = True
                order_id = f"paper_{datetime.now().timestamp()}"
            
            else:  # DEMO mode
                success = True
                order_id = f"demo_{datetime.now().timestamp()}"
            
            # Save trade to database
            is_paper = self.mode != TradingMode.LIVE
            
            trade_id = save_trade(
                user_id=user_id,
                exchange=exchange,
                pair=pair,
                side=side,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                size=size,
                leverage=leverage,
                status='OPEN',
                is_paper=is_paper,
                confidence_score=confidence_score
            )
            
            # Store в active positions
            self.active_positions[trade_id] = {
                'user_id': user_id,
                'exchange': exchange,
                'pair': pair,
                'side': side,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'size': size,
                'leverage': leverage,
                'opened_at': datetime.now()
            }
            
            # Send notification
            notify_trade_opened({
                'exchange': exchange,
                'pair': pair,
                'side': side,
                'entry': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'size': size,
                'leverage': leverage
            })
            
            logger.info(
                f"✅ Trade executed: trade_id={trade_id}, "
                f"user_id={user_id}, {pair} {side}"
            )
            
            return True, trade_id, "Trade executed successfully"
            
        except Exception as e:
            logger.error(f"❌ Execute trade error: {str(e)}")
            notify_error(f"Trade execution failed: {str(e)}")
            return False, None, str(e)
    
    def _execute_live_trade(
        self,
        user_id: int,
        exchange: str,
        pair: str,
        side: str,
        price: float,
        size: float,
        leverage: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Изпълнява РЕАЛЕН trade на борсата
        
        Returns:
            (success, order_id)
        """
        try:
            # Get user's API keys
            api_keys = get_api_keys(user_id, exchange)
            if not api_keys:
                logger.error(f"❌ No API keys found for {exchange}")
                return False, None
            
            keys = api_keys[0]
            
            # Decrypt API keys
            api_key = encryption_manager.decrypt(keys['api_key'])
            api_secret = encryption_manager.decrypt(keys['api_secret'])
            api_passphrase = None
            if keys.get('api_passphrase'):
                api_passphrase = encryption_manager.decrypt(keys['api_passphrase'])
            
            # Get exchange instance
            if exchange not in exchange_connector.exchanges:
                logger.error(f"❌ Exchange {exchange} not available")
                return False, None
            
            exchange_obj = exchange_connector.exchanges[exchange]
            
            # Configure API keys
            exchange_obj.apiKey = api_key
            exchange_obj.secret = api_secret
            if api_passphrase:
                exchange_obj.password = api_passphrase
            
            # Determine order side
            order_side = 'buy' if side == 'LONG' else 'sell'
            
            # Create market order
            # NOTE: Различни борси имат различни API methods
            # Този код е общ пример - за конкретна борса трябва customization
            
            order = exchange_obj.create_order(
                symbol=pair,
                type='market',
                side=order_side,
                amount=size,
                params={
                    'leverage': leverage
                }
            )
            
            order_id = order.get('id')
            
            logger.info(
                f"✅ LIVE trade executed on {exchange}: "
                f"order_id={order_id}, {pair} {side}"
            )
            
            return True, order_id
            
        except Exception as e:
            logger.error(f"❌ Live trade execution failed: {str(e)}")
            return False, None
    
    def close_position(
        self,
        trade_id: int,
        exit_price: float,
        reason: str = "MANUAL"
    ) -> Tuple[bool, str]:
        """
        Затваря open position
        
        Args:
            trade_id: Trade ID
            exit_price: Exit цена
            reason: Reason за затваряне (TAKE_PROFIT, STOP_LOSS, MANUAL)
        
        Returns:
            (success, message)
        """
        try:
            # Get position от active_positions
            if trade_id not in self.active_positions:
                return False, "Position not found"
            
            position = self.active_positions[trade_id]
            
            # Calculate P&L
            entry = position['entry_price']
            side = position['side']
            size = position['size']
            leverage = position['leverage']
            
            if side == 'LONG':
                pnl_per_unit = exit_price - entry
            else:  # SHORT
                pnl_per_unit = entry - exit_price
            
            pnl = pnl_per_unit * size * leverage
            pnl_percent = (pnl_per_unit / entry) * 100 * leverage
            
            # Calculate duration
            duration = datetime.now() - position['opened_at']
            duration_str = self._format_duration(duration.total_seconds())
            
            # Update database
            # TODO: Update trade в database с exit_price, pnl, closed_at
            
            # Update user balance
            user_id = position['user_id']
            user = get_user(user_id)
            new_balance = user.get('paper_balance', 10000) + pnl
            update_user_balance(user_id, new_balance, is_paper=True)
            
            # Remove от active positions
            del self.active_positions[trade_id]
            
            # Send notification
            notify_trade_closed({
                'pair': position['pair'],
                'side': side,
                'entry': entry,
                'exit': exit_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'reason': reason,
                'duration': duration_str,
                'exchange': position['exchange']
            })
            
            logger.info(
                f"✅ Position closed: trade_id={trade_id}, "
                f"P&L=${pnl:.2f} ({pnl_percent:+.2f}%)"
            )
            
            return True, "Position closed successfully"
            
        except Exception as e:
            logger.error(f"❌ Close position error: {str(e)}")
            return False, str(e)
    
    def monitor_positions(self):
        """
        Мониторинг на open positions
        Проверява дали да затвори позиции based on:
        - Stop loss hit
        - Take profit hit
        - Liquidation близо
        """
        try:
            for trade_id, position in list(self.active_positions.items()):
                exchange = position['exchange']
                pair = position['pair']
                side = position['side']
                entry = position['entry_price']
                stop_loss = position['stop_loss']
                take_profit = position['take_profit']
                
                # Get current price
                current_price = get_current_price(exchange, pair)
                if not current_price:
                    continue
                
                # Check stop loss
                if side == 'LONG' and current_price <= stop_loss:
                    logger.info(f"🛑 Stop loss hit: trade_id={trade_id}")
                    self.close_position(trade_id, current_price, "STOP_LOSS")
                    continue
                
                elif side == 'SHORT' and current_price >= stop_loss:
                    logger.info(f"🛑 Stop loss hit: trade_id={trade_id}")
                    self.close_position(trade_id, current_price, "STOP_LOSS")
                    continue
                
                # Check take profit
                if side == 'LONG' and current_price >= take_profit:
                    logger.info(f"🎯 Take profit hit: trade_id={trade_id}")
                    self.close_position(trade_id, current_price, "TAKE_PROFIT")
                    continue
                
                elif side == 'SHORT' and current_price <= take_profit:
                    logger.info(f"🎯 Take profit hit: trade_id={trade_id}")
                    self.close_position(trade_id, current_price, "TAKE_PROFIT")
                    continue
                
                # Check liquidation warning (for leveraged positions)
                if position['leverage'] > 1:
                    liquidation_price = self._calculate_liquidation_price(
                        entry, side, position['leverage']
                    )
                    
                    distance_percent = abs(current_price - liquidation_price) / current_price * 100
                    
                    if distance_percent < 5:  # Под 5% до ликвидация
                        logger.critical(
                            f"🚨 LIQUIDATION WARNING: trade_id={trade_id}, "
                            f"distance={distance_percent:.2f}%"
                        )
                        
                        # Send critical notification
                        notify_critical(
                            f"⚠️ LIQUIDATION WARNING!\n\n"
                            f"Trade #{trade_id}\n"
                            f"Pair: {pair}\n"
                            f"Current Price: ${current_price:,.2f}\n"
                            f"Liquidation Price: ${liquidation_price:,.2f}\n"
                            f"Distance: {distance_percent:.2f}%"
                        )
            
        except Exception as e:
            logger.error(f"❌ Monitor positions error: {str(e)}")
    
    def _calculate_liquidation_price(
        self,
        entry_price: float,
        side: str,
        leverage: int
    ) -> float:
        """
        Изчислява приблизителна liquidation цена
        
        Simplified formula:
        LONG: liquidation = entry * (1 - 1/leverage)
        SHORT: liquidation = entry * (1 + 1/leverage)
        """
        if side == 'LONG':
            return entry_price * (1 - 1/leverage)
        else:
            return entry_price * (1 + 1/leverage)
    
    def _format_duration(self, seconds: float) -> str:
        """Форматира duration в human readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    async def start_monitoring_loop(self):
        """
        Стартира async loop за position monitoring
        Трябва да се извиква в отделен thread/process
        """
        logger.info("🔄 Starting position monitoring loop...")
        
        while True:
            try:
                self.monitor_positions()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute if error
    
    def get_position_status(self, trade_id: int) -> Optional[Dict]:
        """
        Връща статуса на конкретна позиция
        
        Returns:
            {
                'trade_id': 123,
                'pair': 'BTC/USD',
                'side': 'LONG',
                'entry_price': 45000,
                'current_price': 45500,
                'unrealized_pnl': 50,
                'unrealized_pnl_percent': 1.11
            }
        """
        if trade_id not in self.active_positions:
            return None
        
        position = self.active_positions[trade_id]
        
        # Get current price
        current_price = get_current_price(
            position['exchange'],
            position['pair']
        )
        
        if not current_price:
            return None
        
        # Calculate unrealized P&L
        entry = position['entry_price']
        side = position['side']
        size = position['size']
        leverage = position['leverage']
        
        if side == 'LONG':
            pnl_per_unit = current_price - entry
        else:
            pnl_per_unit = entry - current_price
        
        unrealized_pnl = pnl_per_unit * size * leverage
        unrealized_pnl_percent = (pnl_per_unit / entry) * 100 * leverage
        
        return {
            'trade_id': trade_id,
            'pair': position['pair'],
            'side': side,
            'entry_price': entry,
            'current_price': current_price,
            'stop_loss': position['stop_loss'],
            'take_profit': position['take_profit'],
            'size': size,
            'leverage': leverage,
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_percent': unrealized_pnl_percent,
            'opened_at': position['opened_at'].isoformat()
        }
    
    def get_all_positions_status(self, user_id: int) -> List[Dict]:
        """Връща статуса на всички позиции на user"""
        positions = []
        
        for trade_id, position in self.active_positions.items():
            if position['user_id'] == user_id:
                status = self.get_position_status(trade_id)
                if status:
                    positions.append(status)
        
        return positions


# Global trading engine instance
trading_engine = None


def initialize_trading_engine(mode: str = TradingMode.PAPER):
    """
    Initialize global trading engine
    
    Usage:
        initialize_trading_engine(TradingMode.PAPER)
    """
    global trading_engine
    trading_engine = TradingEngine(mode)
    logger.info(f"✅ Global trading engine initialized in {mode.upper()} mode")


def execute_trade_quick(
    user_id: int,
    exchange: str,
    pair: str,
    side: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    size: float,
    **kwargs
) -> Tuple[bool, Optional[int], str]:
    """
    Quick helper function за trade execution
    
    Usage:
        success, trade_id, msg = execute_trade_quick(
            user_id=1,
            exchange='dydx',
            pair='BTC/USD',
            side='LONG',
            entry_price=45000,
            stop_loss=44500,
            take_profit=46000,
            size=0.1
        )
    """
    if not trading_engine:
        return False, None, "Trading engine not initialized"
    
    return trading_engine.execute_trade(
        user_id, exchange, pair, side,
        entry_price, stop_loss, take_profit,
        size, **kwargs
    )


def close_position_quick(trade_id: int, exit_price: float, reason: str = "MANUAL") -> Tuple[bool, str]:
    """
    Quick helper за position closing
    
    Usage:
        success, msg = close_position_quick(trade_id=123, exit_price=45800)
    """
    if not trading_engine:
        return False, "Trading engine not initialized"
    
    return trading_engine.close_position(trade_id, exit_price, reason)
