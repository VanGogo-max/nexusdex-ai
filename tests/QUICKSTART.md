# ⚡ NexusDEX AI - Бърз Старт

5-минутен setup guide за локален старт на приложението.

---

## 📋 Минимални Изисквания

- Python 3.9+
- PostgreSQL 13+
- Git

---

## 🚀 Бърз Setup (5 минути)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/nexusdex-ai.git
cd nexusdex-ai
```

### 2. Virtual Environment

```bash
# Създай virtual environment
python -m venv venv

# Активирай го
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Setup

```bash
# Option A: Local PostgreSQL
createdb nexusdex_ai

# Option B: Docker PostgreSQL (по-лесно)
docker run -d \
  --name nexusdex-postgres \
  -e POSTGRES_DB=nexusdex_ai \
  -e POSTGRES_USER=nexusdex_user \
  -e POSTGRES_PASSWORD=password123 \
  -p 5432:5432 \
  postgres:15-alpine
```

### 5. Environment Variables

```bash
# Копирай .env template
cp .env.example .env

# Редактирай .env (минимум):
nano .env
```

**Минимални settings:**
```bash
DATABASE_URL=postgresql://nexusdex_user:password123@localhost/nexusdex_ai
OWNER_WALLET=0xfee37e7e64d70f37f96c42375131abb57c1481c2
TRADING_MODE=paper
SECRET_KEY=change-this-to-random-32-chars
```

### 6. Telegram Bot (Optional но препоръчително)

```bash
# 1. Отвори Telegram
# 2. Търси @BotFather
# 3. Изпрати: /newbot
# 4. Следвай инструкциите
# 5. Копирай Bot Token

# За Chat ID:
# 1. Търси @userinfobot
# 2. Изпрати: /start
# 3. Копирай твоя ID

# Добави в .env:
TELEGRAM_BOT_TOKEN=твоя_bot_token
TELEGRAM_CHAT_ID=твоя_chat_id
```

### 7. Стартирай App

```bash
python app.py
```

✅ App работи на: http://localhost:5000

---

## 🎮 Първи Стъпки

### 1. Отвори Browser

```
http://localhost:5000
```

### 2. Connect MetaMask

- Click "Connect Wallet"
- Approve в MetaMask
- Account ще се създаде автоматично

### 3. Explore Dashboard

- Виж stats
- Check exchanges
- Analyze trading pairs

### 4. Test Paper Trading

- Select exchange (напр. dYdX)
- Select pair (напр. BTC/USD)
- Click "Analyze Market"
- Execute trade ако signal е good

---

## 🐳 Docker Setup (Alternative)

Ако предпочиташ Docker:

```bash
# Стартирай всичко с docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f web

# Stop
docker-compose down
```

---

## 🧪 Тестване

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📱 Telegram Test

След setup на bot:

1. Направи test trade
2. Трябва да получиш notification в Telegram
3. Ако не работи, check:
   - Bot token верен ли е
   - Chat ID верен ли е
   - Bot е started ли (изпрати му /start)

---

## 🔧 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL running
# Windows:
sc query postgresql-x64-15

# Linux:
sudo systemctl status postgresql

# Docker:
docker ps | grep postgres
```

### MetaMask Not Connecting

1. Check че използваш HTTPS или localhost
2. Refresh page
3. Try в Incognito mode
4. Check MetaMask е installed и unlocked

### Port Already in Use

```bash
# Change port в .env
PORT=5001

# Or kill process на port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Import Errors

```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Default Login

След първия connect с MetaMask:

- **Role:** User (automatic)
- **Balance:** $10,000 (paper money)
- **Subscription:** None (needs activation)

За admin access:
- Твоя wallet (от .env OWNER_WALLET) автоматично е admin

---

## 🎯 Next Steps

1. **Test Paper Trading**
   - Не рискуваш реални пари
   - Реални цени от борсите
   - Perfect за testing strategies

2. **Configure Risk Management**
   - Settings → Risk Limits
   - Настрой според твоя tolerance

3. **Setup Telegram**
   - Real-time notifications
   - Monitor trades 24/7

4. **Add API Keys** (за live trading)
   - Settings → API Keys
   - Add keys от борсите
   - Test connection

5. **Read Full Docs**
   - README.md за пълна документация
   - DEPLOYMENT.md за production

---

## ⚠️ Важни Напомняния

1. **Default е PAPER mode** - не рискуваш реални пари
2. **Test extensively** преди да минеш на LIVE mode
3. **API Keys са криптирани** в database
4. **Telegram е безплатен** - няма hidden costs
5. **Backup твоя .env** файл - съдържа encryption key

---

## 🆘 Support

Ако нещо не работи:

1. Check logs в terminal
2. Check `.env` файла
3. Restart application
4. Read full README.md
5. Check GitHub Issues

---

## ✅ Success Checklist

- [x] PostgreSQL running
- [x] .env configured
- [x] App starts without errors
- [x] Can open http://localhost:5000
- [x] MetaMask connects
- [x] Can see dashboard
- [x] Telegram bot responds (optional)

Ако всичко е ✅ - готов си за trading! 🎉

---

**Happy Trading!** 🚀

За production deployment виж: [DEPLOYMENT.md](DEPLOYMENT.md)
