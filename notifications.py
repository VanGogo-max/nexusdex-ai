"""
NexusDEX AI - Telegram Notifications System
============================================
Изпраща real-time известия към Telegram за:
- Отворени/затворени trades
- Take profit / Stop loss удари
- Daily P&L summary
- Критични грешки
- Maintenance notifications
"""

import logging
import requests
import asyncio
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Типове известия"""
    TRADE_OPENED = "🟢 TRADE OPENED"
    TRADE_CLOSED = "🔴 TRADE CLOSED"
    TAKE_PROFIT_HIT = "🎯 TAKE PROFIT"
    STOP_LOSS_HIT = "🛑 STOP LOSS"
    DAILY_SUMMARY = "📊 DAILY SUMMARY"
    ERROR_ALERT = "⚠️ ERROR"
    CRITICAL_ALERT = "🚨 CRITICAL"
    INFO = "ℹ️ INFO"
    SUCCESS = "✅ SUCCESS"
    WARNING = "⚠️ WARNING"


class TelegramNotifier:
    """
    Telegram Bot за изпращане на известия
    Безплатен сервиз - само трябва Telegram Bot Token
    """
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram Bot API token (от @BotFather)
            chat_id: Telegram Chat ID (user или group)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}" if bot_token else None
        self.enabled = bool(bot_token and chat_id)
        
        if not self.enabled:
            logger.warning("⚠️ Telegram notifications disabled (missing token or chat_id)")
    
    def send_message(
        self,
        message: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False
    ) -> bool:
        """
        Изпраща текстово съобщение към Telegram
        
        Args:
            message: Текстът на съобщението (може HTML/Markdown)
            parse_mode: "HTML" или "Markdown"
            disable_notification: Ако True, изпраща тихо (без звук)
        
        Returns:
            True ако успешно, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Telegram notification (disabled): {message}")
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.debug("✅ Telegram notification sent")
                return True
            else:
                logger.error(f"❌ Telegram API error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram notification: {str(e)}")
            return False
    
    def notify_trade_opened(self, trade_data: Dict) -> bool:
        """
        Известие за отворен trade
        
        Args:
            trade_data: {
                'pair': 'BTC/USD',
                'side': 'LONG',
                'entry': 45000,
                'stop_loss': 44500,
                'take_profit': 46000,
                'size': 0.1,
                'leverage': 5,
                'exchange': 'dYdX'
            }
        """
        message = f"""
{NotificationType.TRADE_OPENED.value}

<b>Exchange:</b> {trade_data.get('exchange', 'Unknown')}
<b>Pair:</b> {trade_data.get('pair', 'N/A')}
<b>Side:</b> {trade_data.get('side', 'N/A')}
<b>Entry:</b> ${trade_data.get('entry', 0):,.2f}
<b>Stop Loss:</b> ${trade_data.get('stop_loss', 0):,.2f}
<b>Take Profit:</b> ${trade_data.get('take_profit', 0):,.2f}
<b>Size:</b> {trade_data.get('size', 0):.4f}
<b>Leverage:</b> {trade_data.get('leverage', 1)}x
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
        
        return self.send_message(message)
    
    def notify_trade_closed(self, trade_data: Dict) -> bool:
        """
        Известие за затворен trade
        
        Args:
            trade_data: {
                'pair': 'BTC/USD',
                'side': 'LONG',
                'entry': 45000,
                'exit': 45800,
                'pnl': 80,
                'pnl_percent': 1.78,
                'reason': 'TAKE_PROFIT',
                'duration': '2h 35m',
                'exchange': 'dYdX'
            }
        """
        pnl = trade_data.get('pnl', 0)
        pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
        
        message = f"""
{NotificationType.TRADE_CLOSED.value} {pnl_emoji}

<b>Exchange:</b> {trade_data.get('exchange', 'Unknown')}
<b>Pair:</b> {trade_data.get('pair', 'N/A')}
<b>Side:</b> {trade_data.get('side', 'N/A')}
<b>Entry:</b> ${trade_data.get('entry', 0):,.2f}
<b>Exit:</b> ${trade_data.get('exit', 0):,.2f}
<b>P&L:</b> ${pnl:,.2f} ({trade_data.get('pnl_percent', 0):+.2f}%)
<b>Reason:</b> {trade_data.get('reason', 'Manual')}
<b>Duration:</b> {trade_data.get('duration', 'N/A')}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
        
        return self.send_message(message)
    
    def notify_daily_summary(self, summary_data: Dict) -> bool:
        """
        Дневен P&L summary
        
        Args:
            summary_data: {
                'date': '2025-01-15',
                'total_trades': 12,
                'winning_trades': 8,
                'losing_trades': 4,
                'win_rate': 66.67,
                'total_pnl': 250.50,
                'best_trade': 85.30,
                'worst_trade': -42.10,
                'starting_balance': 10000,
                'ending_balance': 10250.50
            }
        """
        win_rate = summary_data.get('win_rate', 0)
        total_pnl = summary_data.get('total_pnl', 0)
        pnl_emoji = "🟢" if total_pnl > 0 else "🔴" if total_pnl < 0 else "⚪"
        
        message = f"""
{NotificationType.DAILY_SUMMARY.value} {pnl_emoji}

<b>Date:</b> {summary_data.get('date', 'N/A')}

<b>📈 Performance:</b>
• Total Trades: {summary_data.get('total_trades', 0)}
• Winning: {summary_data.get('winning_trades', 0)} | Losing: {summary_data.get('losing_trades', 0)}
• Win Rate: {win_rate:.2f}%

<b>💰 P&L:</b>
• Total: ${total_pnl:,.2f}
• Best Trade: ${summary_data.get('best_trade', 0):,.2f}
• Worst Trade: ${summary_data.get('worst_trade', 0):,.2f}

<b>💼 Balance:</b>
• Starting: ${summary_data.get('starting_balance', 0):,.2f}
• Ending: ${summary_data.get('ending_balance', 0):,.2f}
• Change: {((summary_data.get('ending_balance', 0) - summary_data.get('starting_balance', 1)) / summary_data.get('starting_balance', 1) * 100):+.2f}%
        """.strip()
        
        return self.send_message(message)
    
    def notify_error(self, error_message: str, details: Optional[str] = None) -> bool:
        """
        Известие за грешка
        
        Args:
            error_message: Кратко описание на грешката
            details: Допълнителни детайли (stack trace, etc.)
        """
        message = f"""
{NotificationType.ERROR_ALERT.value}

<b>Error:</b> {error_message}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
        
        if details:
            message += f"\n\n<b>Details:</b>\n<code>{details[:500]}</code>"
        
        return self.send_message(message)
    
    def notify_critical(self, alert_message: str, details: Optional[str] = None) -> bool:
        """
        Критично известие (circuit breaker, max drawdown, etc.)
        Изпраща се БЕЗ тихо уведомление за да привлече внимание
        
        Args:
            alert_message: Критичното съобщение
            details: Допълнителни детайли
        """
        message = f"""
{NotificationType.CRITICAL_ALERT.value}

<b>⚠️ CRITICAL ALERT ⚠️</b>

{alert_message}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
        
        if details:
            message += f"\n\n<b>Details:</b>\n{details}"
        
        # disable_notification=False за да звучи alert
        return self.send_message(message, disable_notification=False)
    
    def notify_circuit_breaker(self, loss_percent: float, limit: float) -> bool:
        """Специално известие за circuit breaker"""
        return self.notify_critical(
            alert_message=f"🚨 CIRCUIT BREAKER ACTIVATED!\n\n"
                         f"Daily loss reached: {loss_percent:.2f}%\n"
                         f"Limit: {limit:.2f}%\n\n"
                         f"🛑 ALL TRADING STOPPED!",
            details="Bot has been automatically stopped to prevent further losses. "
                   "Review your strategy and reset manually."
        )
    
    def notify_position_liquidation_warning(
        self,
        pair: str,
        current_price: float,
        liquidation_price: float,
        distance_percent: float
    ) -> bool:
        """
        Предупреждение за близка ликвидация
        
        Args:
            pair: Trading pair
            current_price: Текуща цена
            liquidation_price: Ликвидационна цена
            distance_percent: Разстояние до ликвидация (%)
        """
        return self.notify_critical(
            alert_message=f"⚠️ LIQUIDATION WARNING!\n\n"
                         f"Pair: {pair}\n"
                         f"Current Price: ${current_price:,.2f}\n"
                         f"Liquidation Price: ${liquidation_price:,.2f}\n"
                         f"Distance: {distance_percent:.2f}%",
            details="Consider closing position or adding margin to avoid liquidation!"
        )
    
    def notify_info(self, message: str) -> bool:
        """Информационно известие (ниска приоритет)"""
        formatted_message = f"{NotificationType.INFO.value}\n\n{message}"
        return self.send_message(formatted_message, disable_notification=True)
    
    def notify_success(self, message: str) -> bool:
        """Success известие"""
        formatted_message = f"{NotificationType.SUCCESS.value}\n\n{message}"
        return self.send_message(formatted_message, disable_notification=True)
    
    def test_connection(self) -> bool:
        """
        Тества връзката с Telegram API
        
        Returns:
            True ако успешно, False otherwise
        """
        test_message = f"""
✅ <b>NexusDEX AI Telegram Bot Connected!</b>

Your notifications are now active.

<b>Test Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
        
        return self.send_message(test_message)


class NotificationManager:
    """
    Централен мениджър за всички типове известия
    Може да се разшири с Email, Discord, SMS в бъдеще
    """
    
    def __init__(self, telegram_token: Optional[str] = None, telegram_chat_id: Optional[str] = None):
        """Initialize notification manager"""
        self.telegram = TelegramNotifier(telegram_token, telegram_chat_id)
        self.notification_history = []
    
    def send(
        self,
        notification_type: NotificationType,
        data: Dict,
        channels: List[str] = ['telegram']
    ) -> bool:
        """
        Изпраща известие към избраните канали
        
        Args:
            notification_type: Типа на известието
            data: Данните за известието
            channels: Списък с канали ['telegram', 'email', 'discord']
        
        Returns:
            True ако успешно изпратено към поне 1 канал
        """
        success = False
        
        # Store в history
        self.notification_history.append({
            'type': notification_type.value,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'channels': channels
        })
        
        # Telegram channel
        if 'telegram' in channels and self.telegram.enabled:
            if notification_type == NotificationType.TRADE_OPENED:
                success |= self.telegram.notify_trade_opened(data)
            elif notification_type == NotificationType.TRADE_CLOSED:
                success |= self.telegram.notify_trade_closed(data)
            elif notification_type == NotificationType.DAILY_SUMMARY:
                success |= self.telegram.notify_daily_summary(data)
            elif notification_type == NotificationType.ERROR_ALERT:
                success |= self.telegram.notify_error(data.get('message', ''), data.get('details'))
            elif notification_type == NotificationType.CRITICAL_ALERT:
                success |= self.telegram.notify_critical(data.get('message', ''), data.get('details'))
        
        return success
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Връща последните N известия"""
        return self.notification_history[-limit:]


# Global notification manager instance
notification_manager = None


def initialize_notifications(telegram_token: str, telegram_chat_id: str):
    """
    Initialize global notification manager
    
    Usage:
        initialize_notifications(
            telegram_token="123456:ABC-DEF...",
            telegram_chat_id="123456789"
        )
    """
    global notification_manager
    notification_manager = NotificationManager(telegram_token, telegram_chat_id)
    
    # Test connection
    if notification_manager.telegram.enabled:
        notification_manager.telegram.test_connection()


def notify_trade_opened(trade_data: Dict):
    """Quick helper за trade opened notification"""
    if notification_manager:
        notification_manager.send(NotificationType.TRADE_OPENED, trade_data)


def notify_trade_closed(trade_data: Dict):
    """Quick helper за trade closed notification"""
    if notification_manager:
        notification_manager.send(NotificationType.TRADE_CLOSED, trade_data)


def notify_daily_summary(summary_data: Dict):
    """Quick helper за daily summary notification"""
    if notification_manager:
        notification_manager.send(NotificationType.DAILY_SUMMARY, summary_data)


def notify_error(message: str, details: Optional[str] = None):
    """Quick helper за error notification"""
    if notification_manager:
        notification_manager.send(
            NotificationType.ERROR_ALERT,
            {'message': message, 'details': details}
        )


def notify_critical(message: str, details: Optional[str] = None):
    """Quick helper за critical notification"""
    if notification_manager:
        notification_manager.send(
            NotificationType.CRITICAL_ALERT,
            {'message': message, 'details': details}
        )
