"""
NexusDEX AI - Database Module
==============================
PostgreSQL база данни с пълна структура за:
- Users (wallet auth)
- Subscriptions ($10/month USDT)
- API Keys (encrypted)
- Trades (real + paper trading)
- Risk management
- Admin logs
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Database connection string от environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/nexusdex_ai')


def get_db_connection():
    """Създава connection към PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        raise


def init_db():
    """
    Инициализира database schema
    Създава всички таблици ако не съществуват
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                wallet_address VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE,
                username VARCHAR(100),
                role VARCHAR(20) DEFAULT 'user',
                balance DECIMAL(20, 8) DEFAULT 0,
                paper_balance DECIMAL(20, 8) DEFAULT 10000,
                peak_balance DECIMAL(20, 8) DEFAULT 0,
                total_pnl DECIMAL(20, 8) DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                payment_tx VARCHAR(255) UNIQUE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                auto_renew BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API Keys table (encrypted)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                exchange VARCHAR(50) NOT NULL,
                api_key TEXT NOT NULL,
                api_secret TEXT NOT NULL,
                api_passphrase TEXT,
                permissions TEXT DEFAULT 'read,trade',
                is_testnet BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                UNIQUE(user_id, exchange)
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                exchange VARCHAR(50) NOT NULL,
                pair VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                entry_price DECIMAL(20, 8) NOT NULL,
                exit_price DECIMAL(20, 8),
                stop_loss DECIMAL(20, 8),
                take_profit DECIMAL(20, 8),
                size DECIMAL(20, 8) NOT NULL,
                leverage INTEGER DEFAULT 1,
                pnl DECIMAL(20, 8),
                pnl_percent DECIMAL(10, 4),
                status VARCHAR(20) DEFAULT 'OPEN',
                close_reason VARCHAR(50),
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                duration INTEGER,
                is_paper_trade BOOLEAN DEFAULT TRUE,
                confidence_score DECIMAL(5, 2),
                strategy_name VARCHAR(100)
            )
        """)
        
        # Risk management table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
                max_daily_loss_percent DECIMAL(5, 2) DEFAULT 5.0,
                max_position_size_percent DECIMAL(5, 2) DEFAULT 10.0,
                risk_per_trade_percent DECIMAL(5, 2) DEFAULT 1.0,
                max_open_positions INTEGER DEFAULT 5,
                max_portfolio_heat DECIMAL(5, 2) DEFAULT 15.0,
                max_drawdown_percent DECIMAL(5, 2) DEFAULT 20.0,
                leverage_max INTEGER DEFAULT 10,
                daily_trade_limit INTEGER DEFAULT 20,
                circuit_breaker_active BOOLEAN DEFAULT FALSE,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Daily stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                starting_balance DECIMAL(20, 8),
                ending_balance DECIMAL(20, 8),
                daily_pnl DECIMAL(20, 8),
                daily_pnl_percent DECIMAL(10, 4),
                trades_count INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                best_trade DECIMAL(20, 8),
                worst_trade DECIMAL(20, 8),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        """)
        
        # Admin logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id SERIAL PRIMARY KEY,
                admin_id INTEGER REFERENCES users(id),
                action VARCHAR(100) NOT NULL,
                target_user_id INTEGER,
                details TEXT,
                ip_address VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Notifications log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications_log (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                type VARCHAR(50) NOT NULL,
                channel VARCHAR(20),
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN
            )
        """)
        
        # Create indexes за performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_user_status ON trades(user_id, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_stats_user_date ON daily_stats(user_id, date)")
        
        conn.commit()
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# USER FUNCTIONS
# ============================================================================

def create_user(wallet_address: str, email: Optional[str] = None, username: Optional[str] = None) -> int:
    """
    Създава нов user
    
    Returns:
        user_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (wallet_address, email, username)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (wallet_address.lower(), email, username))
        
        user_id = cursor.fetchone()['id']
        
        # Create default risk settings
        cursor.execute("""
            INSERT INTO risk_settings (user_id)
            VALUES (%s)
        """, (user_id,))
        
        conn.commit()
        logger.info(f"✅ User created: id={user_id}, wallet={wallet_address}")
        
        return user_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Create user failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_user(user_id: Optional[int] = None, wallet_address: Optional[str] = None) -> Optional[Dict]:
    """Взима user по ID или wallet address"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if user_id:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        elif wallet_address:
            cursor.execute("SELECT * FROM users WHERE wallet_address = %s", (wallet_address.lower(),))
        else:
            return None
        
        user = cursor.fetchone()
        return dict(user) if user else None
        
    except Exception as e:
        logger.error(f"❌ Get user failed: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()


def get_all_users(limit: int = 100) -> List[Dict]:
    """Взима всички users (за admin panel)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, wallet_address, email, username, role, balance, 
                   total_trades, winning_trades, created_at, is_active
            FROM users
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        users = cursor.fetchall()
        return [dict(user) for user in users]
        
    except Exception as e:
        logger.error(f"❌ Get all users failed: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()


def update_user_balance(user_id: int, new_balance: float, is_paper: bool = True):
    """Update user balance"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        field = 'paper_balance' if is_paper else 'balance'
        cursor.execute(f"""
            UPDATE users
            SET {field} = %s,
                peak_balance = GREATEST(peak_balance, %s)
            WHERE id = %s
        """, (new_balance, new_balance, user_id))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Update balance failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def update_user_role(user_id: int, role: str):
    """Update user role (admin panel)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE users
            SET role = %s
            WHERE id = %s
        """, (role, user_id))
        
        conn.commit()
        logger.info(f"✅ User role updated: id={user_id}, role={role}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Update role failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def delete_user_account(user_id: int):
    """Delete user account (CASCADE delete всичко)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        logger.info(f"✅ User deleted: id={user_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Delete user failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def verify_user(wallet_address: str) -> bool:
    """Проверява дали user съществува"""
    user = get_user(wallet_address=wallet_address)
    return user is not None


# ============================================================================
# SUBSCRIPTION FUNCTIONS
# ============================================================================

def create_subscription(
    user_id: int,
    payment_tx: str,
    amount: float,
    duration_days: int = 30
) -> int:
    """Създава нов subscription"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        cursor.execute("""
            INSERT INTO subscriptions (user_id, payment_tx, amount, expires_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, payment_tx, amount, expires_at))
        
        subscription_id = cursor.fetchone()['id']
        conn.commit()
        
        logger.info(f"✅ Subscription created: id={subscription_id}, user_id={user_id}")
        return subscription_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Create subscription failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_active_subscription(user_id: int) -> Optional[Dict]:
    """Взима активен subscription на user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM subscriptions
            WHERE user_id = %s
              AND is_active = TRUE
              AND expires_at > CURRENT_TIMESTAMP
            ORDER BY expires_at DESC
            LIMIT 1
        """, (user_id,))
        
        sub = cursor.fetchone()
        return dict(sub) if sub else None
        
    except Exception as e:
        logger.error(f"❌ Get subscription failed: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# API KEYS FUNCTIONS
# ============================================================================

def save_api_keys(
    user_id: int,
    exchange: str,
    api_key: str,
    api_secret: str,
    api_passphrase: Optional[str] = None
):
    """Запазва encrypted API keys"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO api_keys (user_id, exchange, api_key, api_secret, api_passphrase)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, exchange)
            DO UPDATE SET
                api_key = EXCLUDED.api_key,
                api_secret = EXCLUDED.api_secret,
                api_passphrase = EXCLUDED.api_passphrase,
                created_at = CURRENT_TIMESTAMP
        """, (user_id, exchange, api_key, api_secret, api_passphrase))
        
        conn.commit()
        logger.info(f"✅ API keys saved: user_id={user_id}, exchange={exchange}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Save API keys failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_api_keys(user_id: int, exchange: Optional[str] = None) -> List[Dict]:
    """Взима API keys за user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if exchange:
            cursor.execute("""
                SELECT * FROM api_keys
                WHERE user_id = %s AND exchange = %s
            """, (user_id, exchange))
        else:
            cursor.execute("SELECT * FROM api_keys WHERE user_id = %s", (user_id,))
        
        keys = cursor.fetchall()
        return [dict(key) for key in keys]
        
    except Exception as e:
        logger.error(f"❌ Get API keys failed: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()


def delete_api_keys(user_id: int, exchange: str):
    """Изтрива API keys"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM api_keys
            WHERE user_id = %s AND exchange = %s
        """, (user_id, exchange))
        
        conn.commit()
        logger.info(f"✅ API keys deleted: user_id={user_id}, exchange={exchange}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Delete API keys failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# TRADE FUNCTIONS
# ============================================================================

def save_trade(
    user_id: int,
    exchange: str,
    pair: str,
    side: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    size: float,
    leverage: int = 1,
    status: str = 'OPEN',
    is_paper: bool = True,
    confidence_score: Optional[float] = None
) -> int:
    """Запазва trade"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO trades (
                user_id, exchange, pair, side, entry_price, stop_loss,
                take_profit, size, leverage, status, is_paper_trade, confidence_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, exchange, pair, side, entry_price, stop_loss,
              take_profit, size, leverage, status, is_paper, confidence_score))
        
        trade_id = cursor.fetchone()['id']
        conn.commit()
        
        logger.info(f"✅ Trade saved: id={trade_id}, user_id={user_id}")
        return trade_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Save trade failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


def get_user_trades(
    user_id: int,
    status: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """Взима trades на user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if status:
            cursor.execute("""
                SELECT * FROM trades
                WHERE user_id = %s AND status = %s
                ORDER BY opened_at DESC
                LIMIT %s
            """, (user_id, status, limit))
        else:
            cursor.execute("""
                SELECT * FROM trades
                WHERE user_id = %s
                ORDER BY opened_at DESC
                LIMIT %s
            """, (user_id, limit))
        
        trades = cursor.fetchall()
        return [dict(trade) for trade in trades]
        
    except Exception as e:
        logger.error(f"❌ Get trades failed: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()
