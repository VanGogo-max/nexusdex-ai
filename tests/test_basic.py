"""
NexusDEX AI - Basic Tests
==========================
Unit tests за основни функционалности
"""

import pytest
import numpy as np
from encryption import encryption_manager
from risk_manager import RiskManager, RiskLimits, PositionRisk
from strategy import TradingStrategy

# ============================================================================
# ENCRYPTION TESTS
# ============================================================================

def test_encryption_decrypt():
    """Test encryption и decryption"""
    original = "test_api_key_12345"
    
    # Encrypt
    encrypted = encryption_manager.encrypt(original)
    assert encrypted != original
    assert len(encrypted) > 0
    
    # Decrypt
    decrypted = encryption_manager.decrypt(encrypted)
    assert decrypted == original


def test_encryption_dict():
    """Test encryption на dictionary"""
    original_dict = {
        'api_key': 'key123',
        'api_secret': 'secret456'
    }
    
    # Encrypt
    encrypted_dict = encryption_manager.encrypt_dict(original_dict)
    assert encrypted_dict['api_key'] != original_dict['api_key']
    assert encrypted_dict['api_secret'] != original_dict['api_secret']
    
    # Decrypt
    decrypted_dict = encryption_manager.decrypt_dict(encrypted_dict)
    assert decrypted_dict['api_key'] == original_dict['api_key']
    assert decrypted_dict['api_secret'] == original_dict['api_secret']


def test_password_hashing():
    """Test password hashing и verification"""
    password = "user_password_123"
    
    # Hash password
    hashed, salt = encryption_manager.hash_password(password)
    assert hashed != password
    assert len(salt) > 0
    
    # Verify correct password
    assert encryption_manager.verify_password(password, hashed, salt) is True
    
    # Verify wrong password
    assert encryption_manager.verify_password("wrong_password", hashed, salt) is False


# ============================================================================
# RISK MANAGER TESTS
# ============================================================================

def test_position_sizing():
    """Test position size calculation"""
    risk_manager = RiskManager()
    
    size, risk_amount = risk_manager.calculate_position_size(
        account_balance=10000,
        entry_price=45000,
        stop_loss_price=44000,
        risk_percent=1.0
    )
    
    # Risk amount трябва да е ~1% от balance
    assert 90 <= risk_amount <= 110  # ~100 USDT (1%)
    
    # Position size трябва да е разумен
    assert size > 0
    assert size < 1.0  # Не трябва да е повече от 1 BTC


def test_validate_position():
    """Test position validation"""
    risk_manager = RiskManager(RiskLimits(
        max_daily_loss_percent=5.0,
        max_position_size_percent=10.0,
        max_open_positions=5
    ))
    
    position_risk = PositionRisk(
        entry_price=45000,
        stop_loss=44000,
        position_size=0.1,
        leverage=5,
        risk_amount=100,
        risk_percent=1.0
    )
    
    # Valid position
    valid, reason = risk_manager.validate_new_position(
        account_balance=10000,
        position_risk=position_risk,
        current_positions=[]
    )
    
    assert valid is True
    assert "approved" in reason.lower()


def test_circuit_breaker():
    """Test daily loss circuit breaker"""
    risk_manager = RiskManager(RiskLimits(max_daily_loss_percent=5.0))
    
    # Test под limit
    limit_reached, loss_pct = risk_manager.check_daily_loss_limit(
        account_balance=9700,
        starting_balance=10000
    )
    assert limit_reached is False
    assert loss_pct == 3.0
    
    # Test над limit
    limit_reached, loss_pct = risk_manager.check_daily_loss_limit(
        account_balance=9400,
        starting_balance=10000
    )
    assert limit_reached is True
    assert loss_pct == 6.0


def test_kelly_criterion():
    """Test Kelly Criterion calculation"""
    risk_manager = RiskManager()
    
    # Profitable strategy
    kelly = risk_manager.calculate_kelly_criterion(
        win_rate=0.60,  # 60% win rate
        avg_win=150,
        avg_loss=100
    )
    
    assert kelly > 0
    assert kelly <= 5.0  # Capped at 5%
    
    # Losing strategy
    kelly = risk_manager.calculate_kelly_criterion(
        win_rate=0.40,  # 40% win rate
        avg_win=100,
        avg_loss=150
    )
    
    assert kelly == 0  # Should return 0 за negative Kelly


# ============================================================================
# TRADING STRATEGY TESTS
# ============================================================================

def test_rsi_calculation():
    """Test RSI indicator calculation"""
    strategy = TradingStrategy()
    
    # Generate test data
    closes = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                      111, 110, 112, 114, 113, 115, 117, 116, 118, 120])
    
    rsi = strategy._calculate_rsi(closes, period=14)
    
    # RSI трябва да е between 0 и 100
    assert all(0 <= r <= 100 for r in rsi if r > 0)
    
    # Last RSI трябва да е > 50 (uptrend)
    assert rsi[-1] > 50


def test_macd_calculation():
    """Test MACD indicator calculation"""
    strategy = TradingStrategy()
    
    # Generate test data
    closes = np.linspace(100, 120, 50)  # Uptrend
    
    macd_line, signal_line, histogram = strategy._calculate_macd(closes)
    
    # Check shapes
    assert len(macd_line) == len(closes)
    assert len(signal_line) == len(closes)
    assert len(histogram) == len(closes)
    
    # In uptrend, MACD трябва да е positive eventually
    assert macd_line[-1] > 0


def test_bollinger_bands():
    """Test Bollinger Bands calculation"""
    strategy = TradingStrategy()
    
    closes = np.array([100, 102, 101, 103, 102, 104, 103, 105, 104, 106,
                      105, 107, 106, 108, 107, 109, 108, 110, 109, 111])
    
    upper, middle, lower = strategy._calculate_bollinger_bands(closes, period=20)
    
    # Upper трябва да е > middle > lower
    assert all(upper[i] >= middle[i] >= lower[i] 
              for i in range(len(closes)) if middle[i] > 0)


def test_analyze_market_signal():
    """Test пълен market analysis"""
    strategy = TradingStrategy()
    
    # Generate bullish data
    timestamps = list(range(100))
    ohlcv = []
    for i in range(100):
        price = 100 + i * 0.5  # Uptrend
        ohlcv.append([
            timestamps[i],
            price - 0.5,
            price + 1,
            price - 1,
            price,
            1000000
        ])
    
    result = strategy.analyze_market(ohlcv)
    
    # Check result structure
    assert 'signal' in result
    assert 'confidence' in result
    assert result['signal'] in ['BUY', 'SELL', 'HOLD']
    assert 0 <= result['confidence'] <= 100
    
    # В uptrend трябва да види BUY
    if result['confidence'] >= 60:
        assert result['signal'] == 'BUY'


def test_session_check():
    """Test trading session detection"""
    strategy = TradingStrategy()
    
    session = strategy.check_session()
    
    # Should return valid session
    assert session in ['asian', 'european', 'us']


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_trade_flow():
    """Test пълен trade workflow"""
    # 1. Calculate position size
    risk_manager = RiskManager()
    size, risk = risk_manager.calculate_position_size(
        account_balance=10000,
        entry_price=45000,
        stop_loss_price=44500,
        risk_percent=1.0
    )
    
    assert size > 0
    assert risk > 0
    
    # 2. Create position risk
    position_risk = PositionRisk(
        entry_price=45000,
        stop_loss=44500,
        position_size=size,
        leverage=5,
        risk_amount=risk,
        risk_percent=1.0
    )
    
    # 3. Validate position
    valid, reason = risk_manager.validate_new_position(
        account_balance=10000,
        position_risk=position_risk,
        current_positions=[]
    )
    
    assert valid is True
    
    # 4. Analyze market
    strategy = TradingStrategy()
    
    # Generate sample OHLCV
    ohlcv = [[i, 45000, 45100, 44900, 45000 + i, 1000000] for i in range(100)]
    
    analysis = strategy.analyze_market(ohlcv)
    
    assert 'signal' in analysis
    assert 'confidence' in analysis


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
