# 🚀 NexusDEX AI - Advanced DEX Trading Bot

**Production-Ready DEX Trading Bot** с реална интеграция към 15+ DEX борси без KYC изисквания.

---

## 📋 Съдържание

- [Характеристики](#характеристики)
- [Поддържани Борси](#поддържани-борси)
- [Инсталация](#инсталация)
- [Конфигурация](#конфигурация)
- [Използване](#използване)
- [API Документация](#api-документация)
- [Deployment](#deployment)
- [Сигурност](#сигурност)

---

## ✨ Характеристики

### Trading
- ✅ **Multi-timeframe анализ** (1h/5m/1m)
- ✅ **ML confidence scoring** (≥60% threshold)
- ✅ **Advanced indicators** (RSI, MACD, Bollinger Bands, ATR, ADX)
- ✅ **Session filtering** (Asian/European/US sessions)
- ✅ **Adaptive position sizing**
- ✅ **Partial exits** (0.5R/1R/1.5R/2R)
- ✅ **Real-time position monitoring**

### Risk Management
- 🛡️ **Daily loss limits** (circuit breaker)
- 🛡️ **Position size limits**
- 🛡️ **Portfolio heat tracking**
- 🛡️ **Maximum drawdown protection**
- 🛡️ **Liquidation warnings**
- 🛡️ **Auto de-leverage**

### Platform Features
- 💼 **3 Trading режима**: Demo / Paper / Live
- 🔐 **MetaMask интеграция**
- 💳 **$10/месец USDT абонамент**
- 📱 **Telegram notifications**
- 🌐 **14 езика поддържани**
- 👑 **Admin панел**
- 🔒 **Encrypted API keys storage**

---

## 🏦 Поддържани Борси

### Arbitrum
- GMX
- Gains Network (gTrade)
- MUX Protocol
- Vela Exchange
- Vertex Protocol
- HMX
- Rage Trade
- Level Finance

### Optimism
- Kwenta (Synthetix)
- Perpetual Protocol
- MUX Protocol

### Polygon
- Gains Network
- QuickSwap Perps

### BSC
- Level Finance
- MUX Protocol
- ApolloX

### Solana
- Jupiter Perps
- Zeta Markets

### Standalone
- dYdX (dYdX Chain)
- Hyperliquid (L1)
- Kava Kinetix

---

## 📦 Инсталация

### Предварителни изисквания
- Python 3.9+
- PostgreSQL 13+
- Git

### Стъпка 1: Clone Repository

```bash
git clone https://github.com/yourusername/nexusdex-ai.git
cd nexusdex-ai
```

### Стъпка 2: Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Стъпка 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Стъпка 4: Database Setup

```bash
# Създай PostgreSQL database
createdb nexusdex_ai

# Database ще се инициализира автоматично при първи старт
```

### Стъпка 5: Environment Variables

```bash
# Копирай .env.example като .env
cp .env.example .env

# Редактирай .env и попълни:
nano .env
```

**Минимални settings за старт:**

```bash
DATABASE_URL=postgresql://user:password@localhost/nexusdex_ai
OWNER_WALLET=0xfee37e7e64d70f37f96c42375131abb57c1481c2
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
TRADING_MODE=paper
```

---

## ⚙️ Конфигурация

### Telegram Bot Setup

1. **Създай bot:**
   - Отвори Telegram
   - Търси `@BotFather`
   - Изпрати `/newbot`
   - Следвай инструкциите
   - Копирай Bot Token

2. **Вземи Chat ID:**
   - Търси `@userinfobot`
   - Изпрати `/start`
   - Копирай твоя ID

3. **Добави в .env:**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=123456789
```

### Trading Mode

Избери режим в `.env`:

```bash
# DEMO - симулирани данни (за testing)
TRADING_MODE=demo

# PAPER - реални цени, виртуални пари (препоръчително)
TRADING_MODE=paper

# LIVE - реални пари (ВНИМАВАЙ!)
TRADING_MODE=live
```

### Risk Management

Настрой limits в `.env`:

```bash
MAX_DAILY_LOSS_PERCENT=5.0        # Max 5% daily loss
MAX_POSITION_SIZE_PERCENT=10.0    # Max 10% per trade
RISK_PER_TRADE_PERCENT=1.0        # Default 1% risk
MAX_OPEN_POSITIONS=5              # Max concurrent positions
MAX_LEVERAGE=10                   # Max leverage
```

---

## 🎮 Използване

### Старт на Application

```bash
python app.py
```

Application ще стартира на `http://localhost:5000`

### Trading Modes Обяснение

#### 1. DEMO Mode
- Симулирани данни
- Фалшиви цени
- За тестване на UI/UX
- **Не използвай за real trading analysis**

#### 2. PAPER Trading (Препоръчително)
- **Реални цени** от борсите
- **Виртуални пари** (не рискуваш реални средства)
- Пълна симулация на real trading
- **Използвай за strategy testing**

#### 3. LIVE Trading (Внимание!)
- **Реални пари**
- Реални загуби възможни
- Изисква API keys
- **Използвай само ако си сигурен**

### Първи Стъпки

1. **Register:**
   - Отвори http://localhost:5000
   - Connect MetaMask
   - Register с твоя wallet

2. **Subscribe:**
   - Изпрати 10 USDT към owner wallet
   - Активирай subscription

3. **Configure Settings:**
   - Settings → Risk Management
   - Настрой limits според твоя risk tolerance

4. **Start Trading:**
   - Dashboard → Select Exchange
   - Select Trading Pair
   - Review Signals
   - Execute Trades

---

## 📚 API Документация

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "wallet_address": "0x...",
  "email": "user@example.com",
  "username": "username"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "wallet_address": "0x..."
}
```

### Trading

#### Get Trading Signal
```http
POST /api/trading/signal
Content-Type: application/json

{
  "exchange": "dydx",
  "pair": "BTC/USD",
  "account_balance": 10000
}
```

#### Execute Trade
```http
POST /api/trading/execute
Content-Type: application/json

{
  "exchange": "dydx",
  "pair": "BTC/USD",
  "side": "LONG",
  "entry_price": 45000,
  "stop_loss": 44500,
  "take_profit": 46000,
  "size": 0.1,
  "leverage": 5
}
```

#### Get Open Positions
```http
GET /api/trading/positions
```

#### Close Position
```http
POST /api/trading/close/{trade_id}
Content-Type: application/json

{
  "exit_price": 45800,
  "reason": "TAKE_PROFIT"
}
```

### Exchanges

#### List All Exchanges
```http
GET /api/exchanges/list
```

#### Get Market Price
```http
GET /api/market/price/{exchange_id}/{pair}

Example: GET /api/market/price/dydx/BTC-USD
```

#### Get OHLCV Data
```http
GET /api/market/ohlcv/{exchange_id}/{pair}?timeframe=1h&limit=100
```

---

## 🚀 Deployment

### Render.com Deployment

1. **Create Render Account**
   - Отиди на https://render.com
   - Sign up (безплатно)

2. **Create PostgreSQL Database**
   - Dashboard → New → PostgreSQL
   - Копирай Internal Database URL

3. **Create Web Service**
   - Dashboard → New → Web Service
   - Connect твоя GitHub repo
   - Settings:
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn app:app`
     - **Environment:** Python 3

4. **Add Environment Variables**
   - Settings → Environment
   - Добави всички variables от `.env`
   - DATABASE_URL използвай от PostgreSQL

5. **Deploy**
   - Click "Create Web Service"
   - Render ще deploy автоматично

### Docker Deployment (Alternative)

```bash
# Build image
docker build -t nexusdex-ai .

# Run container
docker run -p 5000:5000 \
  --env-file .env \
  nexusdex-ai
```

---

## 🔒 Сигурност

### API Keys Encryption

API keys се криптират преди да се запазят:

```python
from encryption import encrypt_data, decrypt_data

# Encrypt
encrypted = encrypt_data("my_api_key")

# Decrypt
decrypted = decrypt_data(encrypted)
```

### Важни Security Notes

1. ⚠️ **НИКОГА не commit-вай `.env` файла**
2. ⚠️ **Запази `ENCRYPTION_SECRET_KEY` на сигурно място**
3. ⚠️ **Използвай strong passwords за database**
4. ⚠️ **Enable 2FA на exchange accounts**
5. ⚠️ **Test с paper trading първо**
6. ⚠️ **Използвай API keys с limited permissions**
7. ⚠️ **Monitor positions 24/7 в LIVE mode**

### Препоръки

- Използвай **read-only API keys** за paper trading
- Използвай **trade-only API keys** (no withdraw) за live
- **Никога не давай withdraw permissions**
- Използвай **separate wallets** за trading
- Провявай **regular backups** на database

---

## 📱 Telegram Commands

След настройка на Telegram bot, ще получаваш:

- 🟢 **Trade Opened** notifications
- 🔴 **Trade Closed** notifications
- 🎯 **Take Profit hit**
- 🛑 **Stop Loss hit**
- 📊 **Daily P&L Summary**
- ⚠️ **Error Alerts**
- 🚨 **Critical Alerts** (circuit breaker, liquidation)

---

## 🌍 Multi-Language Support

Поддържани езици:
- 🇬🇧 English (EN)
- 🇧🇬 Bulgarian (BG)
- 🇩🇪 German (DE)
- 🇫🇷 French (FR)
- 🇪🇸 Spanish (ES)
- 🇮🇹 Italian (IT)
- 🇷🇺 Russian (RU)
- 🇹🇷 Turkish (TR)
- 🇸🇦 Arabic (AR)
- 🇨🇳 Chinese (ZH)
- 🇯🇵 Japanese (JA)
- 🇰🇷 Korean (KO)
- 🇵🇹 Portuguese (PT)
- 🇳🇱 Dutch (NL)
- 🇵🇱 Polish (PL)

Смени език: `?lang=bg` в URL

---

## 👨‍💻 Development

### Project Structure

```
nexusdex-ai/
├── app.py                    # Flask backend
├── exchange_connector.py     # CCXT integration
├── trading_engine.py         # Trading execution
├── strategy.py              # Trading strategy
├── risk_manager.py          # Risk management
├── notifications.py         # Telegram notifications
├── encryption.py            # Encryption utilities
├── database.py              # Database models
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # Документация
└── templates/
    └── index.html          # Frontend
```

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Submit pull request

---

## 📞 Support

- **Owner:** 0xfee37e7e64d70f37f96c42375131abb57c1481c2
- **Telegram:** @nexusdex_ai_support (example)
- **Issues:** GitHub Issues

---

## 📄 License

MIT License - виж LICENSE файл

---

## ⚠️ Disclaimer

**ВАЖНО:**

1. Trading криптовалути носи висок риск
2. Може да загубиш всички инвестирани средства
3. Използвай paper trading за testing
4. Тестирай внимателно преди live trading
5. Никога не инвестирай повече от колкото можеш да загубиш
6. Този софтуер е предоставен "AS IS"
7. Авторът не носи отговорност за загуби

**Use at your own risk!**

---

Made with ❤️ for DeFi traders
