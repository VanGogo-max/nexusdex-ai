# 🚀 NexusDEX AI - Deployment Guide

Пълно ръководство за deployment на Render.com (безплатно за тестване)

---

## 📋 Предварителни изисквания

- [x] GitHub account
- [x] Render.com account (безплатен)
- [x] Telegram Bot Token (@BotFather)
- [x] Telegram Chat ID (@userinfobot)

---

## 🎯 Стъпка 1: GitHub Setup

### 1.1 Push проекта към GitHub

```bash
# Initialize git repo (ако не е вече)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - NexusDEX AI v2.0"

# Create repo на GitHub и push
git remote add origin https://github.com/yourusername/nexusdex-ai.git
git branch -M main
git push -u origin main
```

### 1.2 Провери .gitignore

Убедете се че `.env` файла **НЕ Е** commit-нат:

```bash
# Виж какво ще се commit-не
git status

# .env НЕ трябва да се вижда тук!
```

---

## 🎯 Стъпка 2: Render.com Account

### 2.1 Register

1. Отиди на https://render.com
2. Click **"Get Started"**
3. Sign up с GitHub account
4. Authorize Render да достъпва твоите repos

### 2.2 Verify Email

- Провери email за verification link
- Click на link-а

---

## 🎯 Стъпка 3: PostgreSQL Database

### 3.1 Create Database

1. **Dashboard → New → PostgreSQL**
2. Попълни:
   - **Name:** `nexusdex-ai-db`
   - **Database:** `nexusdex_ai`
   - **User:** `nexusdex_user`
   - **Region:** Избери най-близък (Europe Frankfurt)
   - **Plan:** **Free** (за тестване)

3. Click **"Create Database"**

### 3.2 Копирай Connection String

1. След creation, отвори database
2. Намери **"Internal Database URL"**
3. Копирай го - изглежда така:
   ```
   postgresql://nexusdex_user:password@dpg-xxx.frankfurt-postgres.render.com/nexusdex_ai
   ```
4. **ЗАПАЗИ ГО** - ще ти трябва!

---

## 🎯 Стъпка 4: Web Service

### 4.1 Create Web Service

1. **Dashboard → New → Web Service**

2. **Connect Repository:**
   - Click "Connect a repository"
   - Избери твоя `nexusdex-ai` repo
   - Click "Connect"

3. **Configure Service:**
   ```
   Name: nexusdex-ai
   Region: Frankfurt (EU Central)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
   Plan: Free
   ```

4. **Advanced Settings:**
   - **Auto-Deploy:** Yes (автоматично deploy при push)
   - **Health Check Path:** `/health`

### 4.2 Environment Variables

Click **"Environment"** tab и добави:

```bash
# Database
DATABASE_URL=<копирай Internal Database URL от PostgreSQL>

# Flask
FLASK_ENV=production
SECRET_KEY=<генерирай random 32+ символа>
PORT=10000

# Owner Wallet (ТВОЯ!)
OWNER_WALLET=0xfee37e7e64d70f37f96c42375131abb57c1481c2

# Telegram Bot
TELEGRAM_BOT_TOKEN=<твоя bot token от @BotFather>
TELEGRAM_CHAT_ID=<твоя chat id от @userinfobot>

# Trading Mode
TRADING_MODE=paper

# Risk Management
MAX_DAILY_LOSS_PERCENT=5.0
MAX_POSITION_SIZE_PERCENT=10.0
RISK_PER_TRADE_PERCENT=1.0
MAX_OPEN_POSITIONS=5
MAX_LEVERAGE=10

# Subscription
SUBSCRIPTION_PRICE_USDT=10.0
SUBSCRIPTION_DURATION_DAYS=30

# CORS
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO

# Admin
ADMIN_WALLETS=0xfee37e7e64d70f37f96c42375131abb57c1481c2
```

**Генериране на SECRET_KEY:**

```python
# В Python:
import secrets
print(secrets.token_hex(32))
```

Или онлайн: https://randomkeygen.com/

### 4.3 Deploy

1. Click **"Create Web Service"**
2. Render ще започне да build и deploy
3. Изчакай 5-10 минути
4. Ще видиш logs в real-time

---

## 🎯 Стъпка 5: Проверка

### 5.1 Check Deployment Status

След successful deployment, ще видиш:
```
✅ Build successful
✅ Deploy live
```

### 5.2 Test Application

Твоя URL ще е нещо като:
```
https://nexusdex-ai.onrender.com
```

1. **Health Check:**
   ```
   https://nexusdex-ai.onrender.com/health
   ```
   Трябва да видиш:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-01-15T12:00:00",
     "version": "2.0.0"
   }
   ```

2. **Main Page:**
   ```
   https://nexusdex-ai.onrender.com/
   ```
   Трябва да се зареди frontend-а

### 5.3 Test Telegram Bot

1. Направи тестов request към API
2. Трябва да получиш Telegram notification

---

## 🎯 Стъпка 6: Database Initialization

Database таблиците се създават автоматично при първи старт.

Ако искаш да провериш:

1. Render Dashboard → PostgreSQL → Connect
2. Използвай External Database URL с tool като pgAdmin или:

```bash
psql <External Database URL>
\dt  # List tables
```

Трябва да видиш:
- users
- subscriptions
- api_keys
- trades
- risk_settings
- daily_stats
- admin_logs
- notifications_log

---

## 🎯 Стъпка 7: Custom Domain (Optional)

### 7.1 Add Custom Domain

1. Web Service Settings → Custom Domains
2. Add Domain: `yourdomain.com`
3. Follow DNS configuration instructions

### 7.2 Update CORS

В Environment Variables:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 🎯 Стъпка 8: SSL/HTTPS

✅ Render автоматично предоставя **безплатен SSL**

Твоя site ще е достъпен на:
- ✅ https://nexusdex-ai.onrender.com (secure)
- ❌ http://... (не работи - auto redirect към HTTPS)

---

## 🔧 Troubleshooting

### Build Failed

**Проблем:** Build се провалява

**Решение:**
1. Check build logs в Render
2. Провери `requirements.txt` за typos
3. Убедете се че Python version е >= 3.9

### Database Connection Error

**Проблем:** Cannot connect to database

**Решение:**
1. Провери DATABASE_URL в environment variables
2. Use **Internal Database URL**, не External
3. Убедете се че PostgreSQL service е running

### Telegram Notifications Not Working

**Проблем:** Не получаваш notifications

**Решение:**
1. Провери TELEGRAM_BOT_TOKEN
2. Провери TELEGRAM_CHAT_ID
3. Test bot с `/start` в Telegram
4. Убедете се че bot е added to conversation

### Application Crashing

**Проблем:** App keep crashing

**Решение:**
1. Check logs: Dashboard → Logs
2. Провери за missing environment variables
3. Увери се че gunicorn е в requirements.txt

### Free Tier Limitations

**Render Free Tier:**
- ⏰ Service спира след 15 минути inactivity
- 🔄 Auto-restarts при request (може да отнеме 30-60s)
- 💾 750 hours/месец free
- 📊 100GB bandwidth

**За production:**
- Upgrade към Starter Plan ($7/month)
- Always-on, no sleep
- More resources

---

## 📊 Monitoring

### 8.1 Logs

Real-time logs:
```
Dashboard → Web Service → Logs
```

### 8.2 Metrics

Performance metrics:
```
Dashboard → Web Service → Metrics
```

Виждаш:
- CPU usage
- Memory usage
- Response time
- Request count

### 8.3 Alerts (Optional)

Setup email alerts:
```
Settings → Notifications
```

---

## 🔄 Updates & Redeployment

### Auto-Deploy

Render автоматично redeploy-ва при push към GitHub:

```bash
# Make changes
git add .
git commit -m "Update trading strategy"
git push origin main

# Render автоматично ще rebuild и redeploy
```

### Manual Deploy

Render Dashboard → Web Service → Manual Deploy → Deploy Latest Commit

---

## 🔒 Security Best Practices

### Environment Variables

✅ **DO:**
- Използвай strong SECRET_KEY
- Rotate keys редовно
- Use separate keys за production/staging

❌ **DON'T:**
- Commit .env файла
- Share credentials
- Use default values

### Database

✅ **DO:**
- Regular backups
- Strong password
- Use Internal URL

❌ **DON'T:**
- Expose External URL publicly
- Use weak passwords
- Skip backups

### API Keys

✅ **DO:**
- Encrypt преди storage
- Use limited permissions
- Rotate periodically

❌ **DON'T:**
- Store in plaintext
- Use admin keys
- Share между environments

---

## 💰 Costs

### Free Tier (Current)

- **Web Service:** Free (с limitations)
- **PostgreSQL:** Free (256MB storage)
- **SSL:** Free
- **Total:** $0/месец

### Production Tier (Recommended)

- **Web Service - Starter:** $7/месец
- **PostgreSQL - Starter:** $7/месец
- **Total:** $14/месец

**Без hidden costs!**

---

## 📞 Support

### Render Support

- Docs: https://render.com/docs
- Status: https://status.render.com
- Community: https://community.render.com

### NexusDEX AI Support

- GitHub Issues: https://github.com/yourusername/nexusdex-ai/issues
- Telegram: @nexusdex_support (example)

---

## ✅ Checklist

Преди да пуснеш live:

- [ ] Database created и connected
- [ ] Всички environment variables configured
- [ ] Telegram bot tested
- [ ] Health check работи
- [ ] Frontend се зарежда
- [ ] API endpoints tested
- [ ] Paper trading tested
- [ ] Notifications tested
- [ ] Logs monitored
- [ ] Backups configured

---

## 🎉 Success!

Ако всичко е минало успешно:

✅ Application е deployed на Render
✅ Database работи
✅ Telegram notifications работят
✅ Ready за testing!

**Next Steps:**
1. Register първи admin user
2. Test paper trading
3. Monitor performance
4. Optimize strategy
5. Ready за production!

---

**Happy Trading! 🚀**
