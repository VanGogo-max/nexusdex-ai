"""
NexusDEX AI - Configuration
============================
Централна конфигурация на цялото приложение
Зарежда settings от environment variables
"""

import os
import sys
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables от .env файл
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database - CRITICAL FIX: No localhost fallback!
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Validate DATABASE_URL immediately
    if not DATABASE_URL:
        print("❌ CRITICAL ERROR: DATABASE_URL environment variable is not set!", file=sys.stderr)
        raise ValueError("DATABASE_URL environment variable is required!")
    
    if 'localhost' in DATABASE_URL or '127.0.0.1' in DATABASE_URL:
        print(f"❌ CRITICAL ERROR: DATABASE_URL points to localhost: {DATABASE_URL}", file=sys.stderr)
        raise ValueError("DATABASE_URL must not point to localhost in production!")
    
    print(f"✅ DATABASE_URL configured: {DATABASE_URL[:30]}...", file=sys.stderr)
    
    # Owner Wallet (ТВОЯ АДРЕС!)
    OWNER_WALLET = os.environ.get(
        'OWNER_WALLET',
        '0xfee37e7e64d70f37f96c42375131abb57c1481c2'
    ).lower()
    
    # Trading Mode
    TRADING_MODE = os.environ.get('TRADING_MODE', 'paper')  # demo | paper | live
    
    # Subscription Settings
    SUBSCRIPTION_PRICE = float(os.environ.get('SUBSCRIPTION_PRICE_USDT', 10.0))
    SUBSCRIPTION_DURATION_DAYS = int(os.environ.get('SUBSCRIPTION_DURATION_DAYS', 30))
    
    # Risk Management Defaults
    MAX_DAILY_LOSS_PERCENT = float(os.environ.get('MAX_DAILY_LOSS_PERCENT', 5.0))
    MAX_POSITION_SIZE_PERCENT = float(os.environ.get('MAX_POSITION_SIZE_PERCENT', 10.0))
    RISK_PER_TRADE_PERCENT = float(os.environ.get('RISK_PER_TRADE_PERCENT', 1.0))
    MAX_OPEN_POSITIONS = int(os.environ.get('MAX_OPEN_POSITIONS', 5))
    MAX_LEVERAGE = int(os.environ.get('MAX_LEVERAGE', 10))
    MAX_PORTFOLIO_HEAT = float(os.environ.get('MAX_PORTFOLIO_HEAT', 15.0))
    MAX_DRAWDOWN_PERCENT = float(os.environ.get('MAX_DRAWDOWN_PERCENT', 20.0))
    DAILY_TRADE_LIMIT = int(os.environ.get('DAILY_TRADE_LIMIT', 20))
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    
    # Encryption
    ENCRYPTION_SECRET_KEY = os.environ.get('ENCRYPTION_SECRET_KEY')
    
    # API Rate Limiting
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))  # requests per minute
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Session Settings
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'true').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 60 * 60  # 7 days
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Admin Wallets
    ADMIN_WALLETS = [
        wallet.strip().lower()
        for wallet in os.environ.get('ADMIN_WALLETS', OWNER_WALLET).split(',')
        if wallet.strip()
    ]
    
    # Multi-language Support
    SUPPORTED_LANGUAGES = [
        'en', 'bg', 'de', 'fr', 'es', 'it', 'ru',
        'tr', 'ar', 'zh', 'ja', 'ko', 'pt', 'nl', 'pl'
    ]
    DEFAULT_LANGUAGE = 'en'
    
    # Exchange API Keys Configuration
    EXCHANGE_API_KEYS = {
        'dydx': {
            'api_key': os.environ.get('DYDX_API_KEY'),
            'api_secret': os.environ.get('DYDX_API_SECRET'),
            'api_passphrase': os.environ.get('DYDX_API_PASSPHRASE'),
            'testnet': os.environ.get('DYDX_TESTNET', 'false').lower() == 'true'
        },
        'hyperliquid': {
            'api_key': os.environ.get('HYPERLIQUID_API_KEY'),
            'api_secret': os.environ.get('HYPERLIQUID_API_SECRET'),
            'testnet': os.environ.get('HYPERLIQUID_TESTNET', 'false').lower() == 'true'
        },
        'gmx': {
            'private_key': os.environ.get('GMX_PRIVATE_KEY'),
            'rpc_url': os.environ.get('GMX_RPC_URL', 'https://arb1.arbitrum.io/rpc')
        },
        'gains': {
            'private_key': os.environ.get('GAINS_PRIVATE_KEY'),
            'rpc_url': os.environ.get('GAINS_RPC_URL', 'https://arb1.arbitrum.io/rpc')
        },
        'jupiter': {
            'wallet_private_key': os.environ.get('JUPITER_WALLET_PRIVATE_KEY'),
            'rpc_url': os.environ.get('JUPITER_RPC_URL', 'https://api.mainnet-beta.solana.com')
        },
        'zeta': {
            'wallet_private_key': os.environ.get('ZETA_WALLET_PRIVATE_KEY'),
            'rpc_url': os.environ.get('ZETA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        },
        'kwenta': {
            'private_key': os.environ.get('KWENTA_PRIVATE_KEY'),
            'rpc_url': os.environ.get('KWENTA_RPC_URL', 'https://mainnet.optimism.io')
        },
        'perp': {
            'private_key': os.environ.get('PERP_PRIVATE_KEY'),
            'rpc_url': os.environ.get('PERP_RPC_URL', 'https://mainnet.optimism.io')
        },
        'quickswap': {
            'private_key': os.environ.get('QUICKSWAP_PRIVATE_KEY'),
            'rpc_url': os.environ.get('QUICKSWAP_RPC_URL', 'https://polygon-rpc.com')
        },
        'apollox': {
            'api_key': os.environ.get('APOLLOX_API_KEY'),
            'api_secret': os.environ.get('APOLLOX_API_SECRET'),
            'testnet': os.environ.get('APOLLOX_TESTNET', 'false').lower() == 'true'
        },
        'mux': {
            'private_key': os.environ.get('MUX_PRIVATE_KEY'),
            'rpc_urls': {
                'arbitrum': os.environ.get('MUX_RPC_URL_ARBITRUM', 'https://arb1.arbitrum.io/rpc'),
                'optimism': os.environ.get('MUX_RPC_URL_OPTIMISM', 'https://mainnet.optimism.io'),
                'bsc': os.environ.get('MUX_RPC_URL_BSC', 'https://bsc-dataseed1.binance.org')
            }
        }
    }
    
    # Strategy Settings
    MIN_CONFIDENCE_THRESHOLD = 60.0  # Минимален ML confidence за trade
    TIMEFRAMES = ['1h', '5m', '1m']  # Multi-timeframe анализ
    
    # Technical Indicators Parameters
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    BB_PERIOD = 20
    BB_STD_DEV = 2
    
    ATR_PERIOD = 14
    ADX_PERIOD = 14
    ADX_THRESHOLD = 25  # Strong trend над 25
    
    # Position Sizing
    DEFAULT_STOP_LOSS_ATR_MULTIPLIER = 2.0
    DEFAULT_TAKE_PROFIT_ATR_MULTIPLIER = 3.0
    
    # Session Times (UTC)
    TRADING_SESSIONS = {
        'asian': ('00:00', '08:00'),
        'european': ('08:00', '16:00'),
        'us': ('16:00', '23:59')
    }
    
    # Preferred Trading Sessions (празно = всички)
    PREFERRED_SESSIONS = []  # ['us', 'european'] или []
    
    # External Services
    SENTRY_DSN = os.environ.get('SENTRY_DSN')  # Optional error tracking
    HEALTHCHECK_URL = os.environ.get('HEALTHCHECK_URL')  # Optional uptime monitoring
    
    @classmethod
    def get_exchange_config(cls, exchange_id: str) -> Dict:
        """
        Връща конфигурация за конкретна борса
        
        Args:
            exchange_id: ID на борсата (напр. 'dydx')
        
        Returns:
            Dictionary с API keys и settings
        """
        return cls.EXCHANGE_API_KEYS.get(exchange_id, {})
    
    @classmethod
    def is_admin(cls, wallet_address: str) -> bool:
        """
        Проверява дали wallet е admin
        
        Args:
            wallet_address: Wallet address за проверка
        
        Returns:
            True ако е admin
        """
        return wallet_address.lower() in cls.ADMIN_WALLETS
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """
        Валидира конфигурацията и връща warnings
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        # Check critical settings
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("⚠️ Using default SECRET_KEY - change in production!")
        
        if not cls.TELEGRAM_ENABLED:
            warnings.append("ℹ️ Telegram notifications disabled (missing token/chat_id)")
        
        if cls.TRADING_MODE == 'live':
            warnings.append("🚨 LIVE TRADING MODE ENABLED - Real money at risk!")
            
            # Check if any exchange keys are configured
            has_keys = any(
                bool(config.get('api_key') or config.get('private_key'))
                for config in cls.EXCHANGE_API_KEYS.values()
            )
            
            if not has_keys:
                warnings.append("⚠️ LIVE mode but no exchange API keys configured!")
        
        if not cls.ENCRYPTION_SECRET_KEY:
            warnings.append("ℹ️ Encryption key will be auto-generated - save it to .env!")
        
        # Check risk limits
        if cls.MAX_DAILY_LOSS_PERCENT > 10:
            warnings.append(f"⚠️ High daily loss limit: {cls.MAX_DAILY_LOSS_PERCENT}%")
        
        if cls.MAX_LEVERAGE > 20:
            warnings.append(f"⚠️ High max leverage: {cls.MAX_LEVERAGE}x")
        
        return warnings
    
    @classmethod
    def print_config_summary(cls):
        """Принтира summary на конфигурацията"""
        print("\n" + "="*60)
        print("🚀 NexusDEX AI - Configuration Summary")
        print("="*60)
        print(f"Environment: {cls.FLASK_ENV}")
        print(f"Trading Mode: {cls.TRADING_MODE.upper()}")
        print(f"Owner Wallet: {cls.OWNER_WALLET}")
        print(f"Database: ✅ Configured")
        print(f"Telegram: {'✅ Enabled' if cls.TELEGRAM_ENABLED else '❌ Disabled'}")
        print(f"Subscription: ${cls.SUBSCRIPTION_PRICE} USDT / {cls.SUBSCRIPTION_DURATION_DAYS} days")
        print(f"Max Daily Loss: {cls.MAX_DAILY_LOSS_PERCENT}%")
        print(f"Max Leverage: {cls.MAX_LEVERAGE}x")
        print(f"Languages: {len(cls.SUPPORTED_LANGUAGES)} supported")
        print(f"Admin Wallets: {len(cls.ADMIN_WALLETS)}")
        
        # Warnings
        warnings = cls.validate_config()
        if warnings:
            print("\n⚠️ Warnings:")
            for warning in warnings:
                print(f"  {warning}")
        else:
            print("\n✅ Configuration looks good!")
        
        print("="*60 + "\n")


class DevelopmentConfig(Config):
    """Development environment configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    TRADING_MODE = 'paper'
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Additional production checks
    @classmethod
    def validate_config(cls) -> List[str]:
        warnings = super().validate_config()
        
        # Extra production checks
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("🚨 CRITICAL: Change SECRET_KEY in production!")
        
        return warnings


# Get config based on environment
def get_config() -> Config:
    """
    Връща подходящата конфигурация според environment
    
    Returns:
        Config instance
    """
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env == 'development':
        return DevelopmentConfig()
    else:
        return ProductionConfig()


# Export config instance
config = get_config()
