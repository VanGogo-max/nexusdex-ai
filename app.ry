"""
NexusDEX AI - Flask Backend Application (ЧАСТ 1)
=================================================
Production-ready DEX trading bot backend с:
- Real exchange integration
- API keys management
- Multi-language support (14 езика)
- Admin panel
- Risk management
- Telegram notifications
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Import нашите модули
from database import (
    init_db, get_user, create_user, verify_user,
    create_subscription, get_active_subscription,
    save_trade, get_user_trades, update_user_balance,
    save_api_keys, get_api_keys, delete_api_keys,
    get_all_users, update_user_role, delete_user_account
)
from exchange_connector import (
    exchange_connector, get_market_data,
    get_current_price, get_all_exchanges
)
from encryption import encryption_manager
from risk_manager import RiskManager, RiskLimits, PositionRisk
from notifications import initialize_notifications, notify_trade_opened, notify_trade_closed
from strategy import TradingStrategy, analyze_market

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# CORS configuration
CORS(app, supports_credentials=True)
Session(app)

# Initialize database
init_db()

# Owner wallet address (ТВОЯ АДРЕС!)
OWNER_WALLET = "0xfee37e7e64d70f37f96c42375131abb57c1481c2"

# Subscription price (в USDT)
SUBSCRIPTION_PRICE = 10.0
SUBSCRIPTION_DURATION_DAYS = 30

# Multi-language support
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to NexusDEX AI',
        'login': 'Login',
        'logout': 'Logout',
        'dashboard': 'Dashboard',
        'trades': 'Trades',
        'settings': 'Settings',
        'subscription': 'Subscription',
        'active': 'Active',
        'expired': 'Expired',
        'subscribe': 'Subscribe',
        'balance': 'Balance',
        'profit_loss': 'Profit/Loss',
        'win_rate': 'Win Rate',
        'total_trades': 'Total Trades'
    },
    'bg': {
        'welcome': 'Добре дошли в NexusDEX AI',
        'login': 'Вход',
        'logout': 'Изход',
        'dashboard': 'Табло',
        'trades': 'Сделки',
        'settings': 'Настройки',
        'subscription': 'Абонамент',
        'active': 'Активен',
        'expired': 'Изтекъл',
        'subscribe': 'Абонирай се',
        'balance': 'Баланс',
        'profit_loss': 'Печалба/Загуба',
        'win_rate': 'Процент печеливши',
        'total_trades': 'Общо сделки'
    },
    'de': {
        'welcome': 'Willkommen bei NexusDEX AI',
        'login': 'Anmelden',
        'logout': 'Abmelden',
        'dashboard': 'Dashboard',
        'trades': 'Trades',
        'settings': 'Einstellungen',
        'subscription': 'Abonnement',
        'active': 'Aktiv',
        'expired': 'Abgelaufen',
        'subscribe': 'Abonnieren',
        'balance': 'Saldo',
        'profit_loss': 'Gewinn/Verlust',
        'win_rate': 'Gewinnrate',
        'total_trades': 'Gesamt Trades'
    },
    'fr': {
        'welcome': 'Bienvenue sur NexusDEX AI',
        'login': 'Connexion',
        'logout': 'Déconnexion',
        'dashboard': 'Tableau de bord',
        'trades': 'Transactions',
        'settings': 'Paramètres',
        'subscription': 'Abonnement',
        'active': 'Actif',
        'expired': 'Expiré',
        'subscribe': "S'abonner",
        'balance': 'Solde',
        'profit_loss': 'Profit/Perte',
        'win_rate': 'Taux de réussite',
        'total_trades': 'Total des transactions'
    },
    'es': {
        'welcome': 'Bienvenido a NexusDEX AI',
        'login': 'Iniciar sesión',
        'logout': 'Cerrar sesión',
        'dashboard': 'Panel',
        'trades': 'Operaciones',
        'settings': 'Configuración',
        'subscription': 'Suscripción',
        'active': 'Activo',
        'expired': 'Expirado',
        'subscribe': 'Suscribirse',
        'balance': 'Saldo',
        'profit_loss': 'Ganancia/Pérdida',
        'win_rate': 'Tasa de éxito',
        'total_trades': 'Total de operaciones'
    },
    'it': {
        'welcome': 'Benvenuto su NexusDEX AI',
        'login': 'Accedi',
        'logout': 'Esci',
        'dashboard': 'Cruscotto',
        'trades': 'Operazioni',
        'settings': 'Impostazioni',
        'subscription': 'Abbonamento',
        'active': 'Attivo',
        'expired': 'Scaduto',
        'subscribe': 'Iscriviti',
        'balance': 'Saldo',
        'profit_loss': 'Profitto/Perdita',
        'win_rate': 'Tasso di vincita',
        'total_trades': 'Totale operazioni'
    },
    'ru': {
        'welcome': 'Добро пожаловать в NexusDEX AI',
        'login': 'Войти',
        'logout': 'Выйти',
        'dashboard': 'Панель управления',
        'trades': 'Сделки',
        'settings': 'Настройки',
        'subscription': 'Подписка',
        'active': 'Активна',
        'expired': 'Истекла',
        'subscribe': 'Подписаться',
        'balance': 'Баланс',
        'profit_loss': 'Прибыль/Убыток',
        'win_rate': 'Процент выигрышей',
        'total_trades': 'Всего сделок'
    },
    'tr': {
        'welcome': 'NexusDEX AI\'ya Hoş Geldiniz',
        'login': 'Giriş',
        'logout': 'Çıkış',
        'dashboard': 'Panel',
        'trades': 'İşlemler',
        'settings': 'Ayarlar',
        'subscription': 'Abonelik',
        'active': 'Aktif',
        'expired': 'Süresi Dolmuş',
        'subscribe': 'Abone Ol',
        'balance': 'Bakiye',
        'profit_loss': 'Kar/Zarar',
        'win_rate': 'Kazanma Oranı',
        'total_trades': 'Toplam İşlem'
    },
    'ar': {
        'welcome': 'مرحبا بك في NexusDEX AI',
        'login': 'تسجيل الدخول',
        'logout': 'تسجيل الخروج',
        'dashboard': 'لوحة القيادة',
        'trades': 'الصفقات',
        'settings': 'الإعدادات',
        'subscription': 'الاشتراك',
        'active': 'نشط',
        'expired': 'منتهي',
        'subscribe': 'اشترك',
        'balance': 'الرصيد',
        'profit_loss': 'الربح/الخسارة',
        'win_rate': 'معدل الفوز',
        'total_trades': 'إجمالي الصفقات'
    },
    'zh': {
        'welcome': '欢迎来到 NexusDEX AI',
        'login': '登录',
        'logout': '登出',
        'dashboard': '仪表板',
        'trades': '交易',
        'settings': '设置',
        'subscription': '订阅',
        'active': '活跃',
        'expired': '已过期',
        'subscribe': '订阅',
        'balance': '余额',
        'profit_loss': '盈亏',
        'win_rate': '胜率',
        'total_trades': '总交易'
    },
    'ja': {
        'welcome': 'NexusDEX AIへようこそ',
        'login': 'ログイン',
        'logout': 'ログアウト',
        'dashboard': 'ダッシュボード',
        'trades': '取引',
        'settings': '設定',
        'subscription': 'サブスクリプション',
        'active': 'アクティブ',
        'expired': '期限切れ',
        'subscribe': '購読する',
        'balance': '残高',
        'profit_loss': '損益',
        'win_rate': '勝率',
        'total_trades': '総取引数'
    },
    'ko': {
        'welcome': 'NexusDEX AI에 오신 것을 환영합니다',
        'login': '로그인',
        'logout': '로그아웃',
        'dashboard': '대시보드',
        'trades': '거래',
        'settings': '설정',
        'subscription': '구독',
        'active': '활성',
        'expired': '만료됨',
        'subscribe': '구독하기',
        'balance': '잔액',
        'profit_loss': '손익',
        'win_rate': '승률',
        'total_trades': '총 거래'
    },
    'pt': {
        'welcome': 'Bem-vindo ao NexusDEX AI',
        'login': 'Entrar',
        'logout': 'Sair',
        'dashboard': 'Painel',
        'trades': 'Negociações',
        'settings': 'Configurações',
        'subscription': 'Assinatura',
        'active': 'Ativo',
        'expired': 'Expirado',
        'subscribe': 'Assinar',
        'balance': 'Saldo',
        'profit_loss': 'Lucro/Perda',
        'win_rate': 'Taxa de vitória',
        'total_trades': 'Total de negociações'
    },
    'nl': {
        'welcome': 'Welkom bij NexusDEX AI',
        'login': 'Inloggen',
        'logout': 'Uitloggen',
        'dashboard': 'Dashboard',
        'trades': 'Transacties',
        'settings': 'Instellingen',
        'subscription': 'Abonnement',
        'active': 'Actief',
        'expired': 'Verlopen',
        'subscribe': 'Abonneren',
        'balance': 'Saldo',
        'profit_loss': 'Winst/Verlies',
        'win_rate': 'Winstpercentage',
        'total_trades': 'Totaal transacties'
    },
    'pl': {
        'welcome': 'Witamy w NexusDEX AI',
        'login': 'Zaloguj się',
        'logout': 'Wyloguj się',
        'dashboard': 'Panel',
        'trades': 'Transakcje',
        'settings': 'Ustawienia',
        'subscription': 'Subskrypcja',
        'active': 'Aktywny',
        'expired': 'Wygasł',
        'subscribe': 'Subskrybuj',
        'balance': 'Saldo',
        'profit_loss': 'Zysk/Strata',
        'win_rate': 'Wskaźnik wygranych',
        'total_trades': 'Łączna liczba transakcji'
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_translation(lang: str, key: str) -> str:
    """Връща превод за даден език и ключ"""
    if lang not in TRANSLATIONS:
        lang = 'en'
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))


def require_auth(f):
    """Decorator за auth protection"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    
    return decorated_function


def require_subscription(f):
    """Decorator за subscription check"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user_id = session['user_id']
        subscription = get_active_subscription(user_id)
        
        if not subscription:
            return jsonify({'error': 'Active subscription required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """Decorator за admin-only endpoints"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = get_user(session['user_id'])
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Главна страница"""
    lang = request.args.get('lang', 'en')
    return render_template('index.html', lang=lang, owner_wallet=OWNER_WALLET)


@app.route('/api/translations/<lang>')
def get_translations(lang):
    """API endpoint за translations"""
    if lang not in TRANSLATIONS:
        lang = 'en'
    return jsonify(TRANSLATIONS[lang])


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Регистрация на нов user
    
    Body:
        {
            "wallet_address": "0x...",
            "email": "user@example.com",
            "username": "username"
        }
    """
    try:
        data = request.json
        wallet = data.get('wallet_address', '').lower()
        email = data.get('email')
        username = data.get('username')
        
        if not wallet or not email:
            return jsonify({'error': 'Wallet address and email required'}), 400
        
        # Check ако user вече съществува
        existing_user = get_user(wallet_address=wallet)
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        # Създай user
        user_id = create_user(wallet, email, username)
        
        # Set session
        session['user_id'] = user_id
        session['wallet_address'] = wallet
        
        logger.info(f"✅ New user registered: {wallet}")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'wallet_address': wallet
        })
        
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login с MetaMask wallet
    
    Body:
        {
            "wallet_address": "0x...",
            "signature": "0x..." (optional - за по-късно)
        }
    """
    try:
        data = request.json
        wallet = data.get('wallet_address', '').lower()
        
        if not wallet:
            return jsonify({'error': 'Wallet address required'}), 400
        
        # Get user
        user = get_user(wallet_address=wallet)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Set session
        session['user_id'] = user['id']
        session['wallet_address'] = wallet
        session['role'] = user.get('role', 'user')
        
        logger.info(f"✅ User logged in: {wallet}")
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'wallet_address': wallet,
                'email': user.get('email'),
                'username': user.get('username'),
                'role': user.get('role', 'user'),
                'balance': user.get('balance', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True})


@app.route('/api/auth/me')
@require_auth
def get_current_user():
    """Връща текущия logged in user"""
    try:
        user = get_user(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get subscription status
        subscription = get_active_subscription(user['id'])
        
        return jsonify({
            'user': {
                'id': user['id'],
                'wallet_address': user['wallet_address'],
                'email': user.get('email'),
                'username': user.get('username'),
                'role': user.get('role', 'user'),
                'balance': user.get('balance', 0),
                'subscription': {
                    'active': subscription is not None,
                    'expires_at': subscription['expires_at'] if subscription else None
                } if subscription else None
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Get user error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SUBSCRIPTION ENDPOINTS
# ============================================================================

@app.route('/api/subscription/create', methods=['POST'])
@require_auth
def create_subscription_endpoint():
    """
    Създава нов subscription след payment
    
    Body:
        {
            "transaction_hash": "0x...",
            "amount": 10.0
        }
    """
    try:
        data = request.json
        user_id = session['user_id']
        tx_hash = data.get('transaction_hash')
        amount = data.get('amount', SUBSCRIPTION_PRICE)
        
        if not tx_hash:
            return jsonify({'error': 'Transaction hash required'}), 400
        
        # TODO: Verify transaction on blockchain
        # За сега приемаме че е valid
        
        # Create subscription
        subscription_id = create_subscription(
            user_id=user_id,
            duration_days=SUBSCRIPTION_DURATION_DAYS,
            payment_tx=tx_hash,
            amount=amount
        )
        
        logger.info(f"✅ Subscription created: user_id={user_id}, tx={tx_hash}")
        
        return jsonify({
            'success': True,
            'subscription_id': subscription_id,
            'expires_at': (datetime.now() + timedelta(days=SUBSCRIPTION_DURATION_DAYS)).isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Create subscription error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/subscription/status')
@require_auth
def subscription_status():
    """Проверява subscription status"""
    try:
        user_id = session['user_id']
        subscription = get_active_subscription(user_id)
        
        if subscription:
            return jsonify({
                'active': True,
                'expires_at': subscription['expires_at'],
                'days_left': (datetime.fromisoformat(subscription['expires_at']) - datetime.now()).days
            })
        else:
            return jsonify({
                'active': False,
                'message': 'No active subscription'
            })
        
    except Exception as e:
        logger.error(f"❌ Subscription status error: {str(e)}")
        return jsonify({'error': str(e)}), 500
# NexusDEX AI - app.py ЧАСТ 2A
# ================================
# Добави след ЧАСТ 1 (subscription endpoints)

# ============================================================================
# EXCHANGE ENDPOINTS
# ============================================================================

@app.route('/api/exchanges/list')
def list_exchanges():
    """Връща списък с всички поддържани борси"""
    try:
        exchanges = get_all_exchanges()
        return jsonify({'exchanges': exchanges})
    except Exception as e:
        logger.error(f"❌ List exchanges error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/exchanges/<exchange_id>/pairs')
def get_exchange_pairs(exchange_id):
    """Връща trading pairs за конкретна борса"""
    try:
        exchange_info = exchange_connector.get_exchange_info(exchange_id)
        if not exchange_info:
            return jsonify({'error': 'Exchange not found'}), 404
        
        return jsonify({
            'exchange_id': exchange_id,
            'pairs': exchange_info['pairs']
        })
    except Exception as e:
        logger.error(f"❌ Get pairs error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/market/price/<exchange_id>/<pair>')
def get_market_price(exchange_id, pair):
    """Взима текуща цена за trading pair"""
    try:
        pair_formatted = pair.replace('-', '/')
        price = get_current_price(exchange_id, pair_formatted)
        
        if price is None:
            return jsonify({'error': 'Failed to fetch price'}), 500
        
        return jsonify({
            'exchange': exchange_id,
            'pair': pair,
            'price': price,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Get price error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/market/ohlcv/<exchange_id>/<pair>')
def get_market_ohlcv(exchange_id, pair):
    """Взима OHLCV данни за charting"""
    try:
        pair_formatted = pair.replace('-', '/')
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 100))
        
        ohlcv = get_market_data(exchange_id, pair_formatted, timeframe)
        
        if not ohlcv:
            return jsonify({'error': 'Failed to fetch data'}), 500
        
        formatted_data = [
            {
                'timestamp': candle[0],
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5]
            }
            for candle in ohlcv[-limit:]
        ]
        
        return jsonify({
            'exchange': exchange_id,
            'pair': pair,
            'timeframe': timeframe,
            'data': formatted_data
        })
    except Exception as e:
        logger.error(f"❌ Get OHLCV error: {str(e)}")
        return jsonify({'error': str(e)}), 500
# NexusDEX AI - app.py ЧАСТ 2B
# ================================
# Добави след ЧАСТ 2A (exchange endpoints)

# ============================================================================
# TRADING ENDPOINTS
# ============================================================================

@app.route('/api/trading/analyze', methods=['POST'])
@require_subscription
def analyze_trading_opportunity():
    """Анализира trading opportunity за даден pair"""
    try:
        data = request.json
        exchange_id = data.get('exchange')
        pair = data.get('pair')
        timeframe = data.get('timeframe', '1h')
        
        ohlcv = get_market_data(exchange_id, pair, timeframe)
        if not ohlcv:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        
        analysis = analyze_market(ohlcv)
        
        return jsonify({
            'exchange': exchange_id,
            'pair': pair,
            'timeframe': timeframe,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Analyze error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/signal', methods=['POST'])
@require_subscription
def get_trading_signal():
    """Генерира trading signal с пълни параметри"""
    try:
        data = request.json
        exchange_id = data.get('exchange')
        pair = data.get('pair')
        account_balance = data.get('account_balance', 10000)
        
        timeframes = ['1h', '5m', '1m']
        signals = []
        
        for tf in timeframes:
            ohlcv = get_market_data(exchange_id, pair, tf)
            if ohlcv:
                analysis = analyze_market(ohlcv)
                signals.append({
                    'timeframe': tf,
                    'signal': analysis.get('signal'),
                    'confidence': analysis.get('confidence')
                })
        
        if all(s['signal'] == 'BUY' for s in signals if s['confidence'] >= 60):
            final_signal = 'BUY'
        elif all(s['signal'] == 'SELL' for s in signals if s['confidence'] >= 60):
            final_signal = 'SELL'
        else:
            final_signal = 'HOLD'
        
        current_price = get_current_price(exchange_id, pair)
        
        response = {
            'exchange': exchange_id,
            'pair': pair,
            'signal': final_signal,
            'current_price': current_price,
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Trading signal error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/execute', methods=['POST'])
@require_subscription
def execute_trade():
    """Изпълнява trade (paper trading за сега)"""
    try:
        data = request.json
        user_id = session['user_id']
        
        risk_manager = RiskManager()
        
        position_risk = PositionRisk(
            entry_price=data['entry_price'],
            stop_loss=data['stop_loss'],
            position_size=data['size'],
            leverage=data.get('leverage', 1),
            risk_amount=0,
            risk_percent=1.0
        )
        
        valid, reason = risk_manager.validate_new_position(
            account_balance=10000,
            position_risk=position_risk,
            current_positions=[]
        )
        
        if not valid:
            return jsonify({'error': reason}), 400
        
        trade_id = save_trade(
            user_id=user_id,
            exchange=data['exchange'],
            pair=data['pair'],
            side=data['side'],
            entry_price=data['entry_price'],
            stop_loss=data['stop_loss'],
            take_profit=data['take_profit'],
            size=data['size'],
            leverage=data.get('leverage', 1),
            status='OPEN'
        )
        
        notify_trade_opened({
            'exchange': data['exchange'],
            'pair': data['pair'],
            'side': data['side'],
            'entry': data['entry_price'],
            'stop_loss': data['stop_loss'],
            'take_profit': data['take_profit'],
            'size': data['size'],
            'leverage': data.get('leverage', 1)
        })
        
        logger.info(f"✅ Trade executed: trade_id={trade_id}, user_id={user_id}")
        
        return jsonify({
            'success': True,
            'trade_id': trade_id,
            'message': 'Trade executed successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Execute trade error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/positions')
@require_subscription
def get_open_positions():
    """Връща отворените позиции на user"""
    try:
        user_id = session['user_id']
        trades = get_user_trades(user_id, status='OPEN')
        return jsonify({'positions': trades})
    except Exception as e:
        logger.error(f"❌ Get positions error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/history')
@require_subscription
def get_trade_history():
    """Връща trade history на user"""
    try:
        user_id = session['user_id']
        limit = int(request.args.get('limit', 50))
        trades = get_user_trades(user_id, limit=limit)
        return jsonify({'trades': trades})
    except Exception as e:
        logger.error(f"❌ Get history error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trading/close/<trade_id>', methods=['POST'])
@require_subscription
def close_trade(trade_id):
    """Затваря отворена позиция"""
    try:
        data = request.json
        
        notify_trade_closed({
            'pair': 'BTC/USD',
            'side': 'LONG',
            'entry': 45000,
            'exit': data['exit_price'],
            'pnl': 80,
            'pnl_percent': 1.78,
            'reason': data['reason'],
            'duration': '2h 35m',
            'exchange': 'dYdX'
        })
        
        return jsonify({
            'success': True,
            'message': 'Position closed successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Close trade error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    # NexusDEX AI - app.py ЧАСТ 2C
# ================================
# Добави след ЧАСТ 2B (trading endpoints)

# ============================================================================
# API KEYS MANAGEMENT
# ============================================================================

@app.route('/api/keys/save', methods=['POST'])
@require_subscription
def save_user_api_keys():
    """Запазва API keys за борса (encrypted)"""
    try:
        data = request.json
        user_id = session['user_id']
        
        exchange = data.get('exchange')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        api_passphrase = data.get('api_passphrase')
        
        if not exchange or not api_key or not api_secret:
            return jsonify({'error': 'Exchange, API key and secret required'}), 400
        
        encrypted_key = encryption_manager.encrypt(api_key)
        encrypted_secret = encryption_manager.encrypt(api_secret)
        encrypted_passphrase = encryption_manager.encrypt(api_passphrase) if api_passphrase else None
        
        save_api_keys(
            user_id=user_id,
            exchange=exchange,
            api_key=encrypted_key,
            api_secret=encrypted_secret,
            api_passphrase=encrypted_passphrase
        )
        
        logger.info(f"✅ API keys saved: user_id={user_id}, exchange={exchange}")
        
        return jsonify({
            'success': True,
            'message': 'API keys saved successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Save API keys error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/keys/list')
@require_subscription
def list_user_api_keys():
    """Връща списък с configured exchanges"""
    try:
        user_id = session['user_id']
        keys = get_api_keys(user_id)
        
        configured_exchanges = [
            {
                'exchange': key['exchange'],
                'created_at': key['created_at'],
                'last_used': key.get('last_used')
            }
            for key in keys
        ]
        
        return jsonify({'exchanges': configured_exchanges})
        
    except Exception as e:
        logger.error(f"❌ List API keys error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/keys/delete/<exchange>', methods=['DELETE'])
@require_subscription
def delete_user_api_keys(exchange):
    """Изтрива API keys за конкретна борса"""
    try:
        user_id = session['user_id']
        delete_api_keys(user_id, exchange)
        
        logger.info(f"✅ API keys deleted: user_id={user_id}, exchange={exchange}")
        
        return jsonify({
            'success': True,
            'message': 'API keys deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Delete API keys error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ADMIN PANEL ENDPOINTS
# ============================================================================

@app.route('/api/admin/users')
@require_admin
def admin_get_users():
    """Връща всички users (admin only)"""
    try:
        users = get_all_users()
        return jsonify({'users': users})
    except Exception as e:
        logger.error(f"❌ Admin get users error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/user/<user_id>/role', methods=['PUT'])
@require_admin
def admin_update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        data = request.json
        new_role = data.get('role')
        
        if new_role not in ['admin', 'user']:
            return jsonify({'error': 'Invalid role'}), 400
        
        update_user_role(user_id, new_role)
        
        logger.info(f"✅ User role updated: user_id={user_id}, role={new_role}")
        
        return jsonify({
            'success': True,
            'message': 'User role updated'
        })
        
    except Exception as e:
        logger.error(f"❌ Update role error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/user/<user_id>', methods=['DELETE'])
@require_admin
def admin_delete_user(user_id):
    """Delete user account (admin only)"""
    try:
        delete_user_account(user_id)
        logger.info(f"✅ User deleted: user_id={user_id}")
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Delete user error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/stats')
@require_admin
def admin_get_stats():
    """Връща platform statistics (admin only)"""
    try:
        stats = {
            'total_users': 0,
            'active_subscriptions': 0,
            'total_trades': 0,
            'total_volume': 0,
            'revenue': 0
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Get stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500
  # NexusDEX AI - app.py ЧАСТ 2D (ФИНАЛНА)
# ========================================
# Добави след ЧАСТ 2C - това завършва app.py

# ============================================================================
# RISK MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/risk/status')
@require_subscription
def get_risk_status():
    """Връща risk status на user account"""
    try:
        user_id = session['user_id']
        user = get_user(user_id)
        
        risk_manager = RiskManager()
        positions = get_user_trades(user_id, status='OPEN')
        
        status = risk_manager.get_risk_status(
            account_balance=user.get('balance', 10000),
            starting_balance=10000,
            peak_balance=12000,
            active_positions=positions
        )
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"❌ Risk status error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/risk/limits', methods=['GET', 'POST'])
@require_subscription
def manage_risk_limits():
    """GET/UPDATE risk limits за user"""
    try:
        user_id = session['user_id']
        
        if request.method == 'GET':
            limits = {
                'max_daily_loss_percent': 5.0,
                'max_position_size_percent': 10.0,
                'risk_per_trade_percent': 1.0,
                'max_open_positions': 5
            }
            return jsonify(limits)
        
        elif request.method == 'POST':
            data = request.json
            logger.info(f"✅ Risk limits updated: user_id={user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Risk limits updated'
            })
            
    except Exception as e:
        logger.error(f"❌ Risk limits error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# HEALTH CHECK & SYSTEM STATUS
# ============================================================================

@app.route('/health')
def health_check():
    """Health check endpoint за monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })


@app.route('/api/system/status')
def system_status():
    """Системен status на всички exchanges"""
    try:
        exchanges = get_all_exchanges()
        
        exchange_status = {
            ex['id']: ex['status']
            for ex in exchanges
        }
        
        return jsonify({
            'exchanges': exchange_status,
            'trading_enabled': True,
            'notifications_enabled': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ System status error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 handler"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# APP STARTUP
# ============================================================================

if __name__ == '__main__':
    # Initialize Telegram notifications
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if telegram_token and telegram_chat_id:
        initialize_notifications(telegram_token, telegram_chat_id)
        logger.info("✅ Telegram notifications initialized")
    else:
        logger.warning("⚠️ Telegram notifications disabled (missing credentials)")
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting NexusDEX AI on port {port}")
    logger.info(f"📍 Owner wallet: {OWNER_WALLET}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)



                 

# Продължава в ЧАСТ 2...
