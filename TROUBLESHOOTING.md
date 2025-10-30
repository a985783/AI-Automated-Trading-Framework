# Troubleshooting Guide

## Installation & Setup Issues

### Problem: `ModuleNotFoundError: No module named 'openai'`

**Cause**: Dependencies not installed

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt

# Verify installation
python3 -c "import openai; print(openai.__version__)"
```

---

### Problem: `FileNotFoundError: config.json not found`

**Cause**: Missing configuration file

**Solution**:
```bash
# Copy example config
cp config.example.json config.json

# Edit with your credentials
nano config.json  # or use your preferred editor

# Required fields must be filled:
# - ARK_API_KEY (for DeepSeek-V3)
# - EXCHANGE (okx or binance)
# - API credentials for your chosen exchange
```

---

### Problem: `Permission denied` when running `start.sh`

**Cause**: Script not executable

**Solution**:
```bash
# Make script executable
chmod +x start.sh

# Then run
./start.sh
```

---

## Connection Issues

### Problem: `ConnectionError: OKX 模拟盘连接失败`

**Cause**: API credentials invalid or network issue

**Checklist**:
- [ ] API key is correct (no typos, no spaces)
- [ ] API secret is correct
- [ ] Passphrase is correct (OKX only)
- [ ] Network connection is stable
- [ ] System time is synchronized (NTP)
- [ ] API permissions allow trading

**Debug**:
```bash
# Check network connectivity
ping okx.com

# Check system time
date

# Test API manually
python3 << 'EOF'
import ccxt
okx = ccxt.okx({
    'apiKey': 'your-key',
    'secret': 'your-secret',
    'password': 'your-passphrase'
})
okx.set_sandbox_mode(True)
try:
    balance = okx.fetch_balance()
    print("✅ Connection successful")
    print(f"USDT balance: {balance['USDT']['free']}")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

---

### Problem: `binance GET https://testnet.binance.vision/api/v3/exchangeInfo 404 Not Found`

**Cause**: Incorrect testnet URL or API key issue

**Solution**:
```python
# Ensure testnet URL is correct in code:
exchange.urls['api']['public'] = 'https://testnet.binance.vision/api/v3'
exchange.urls['api']['private'] = 'https://testnet.binance.vision/api/v3'

# Verify API key is valid for testnet
# Binance testnet API keys are different from mainnet
```

---

### Problem: `Invalid API Key ID`

**Cause**:
- API key is invalid
- API key is for wrong account/testnet
- IP whitelist not configured
- API permissions insufficient

**Solution**:
```bash
# 1. Verify API key on exchange website
# 2. Check IP whitelist settings
# 3. Ensure API has these permissions:
#    ✅ Spot Trading
#    ✅ Margin Trading (if using leverage)
#    ✅ Futures Trading (for OKX perpetuals)
# 4. For OKX testnet: Must use separate testnet API key
# 5. For Binance testnet: Visit testnet.binance.vision
```

---

## Trading Issues

### Problem: No trades being executed (No orders placed)

**Cause**: Could be several reasons

**Debug Checklist**:

1. **Check Risk Limits**:
```bash
# View log to see why trades rejected
tail -f outputs/trading_*.log | grep -E "⛔|拒绝"

# Common reasons:
# ❌ Per-trade risk > 2%
# ❌ Monthly cumulative risk near -6%
# ❌ Insufficient margin
```

2. **Check AI Decisions**:
```bash
# Look for AI analysis in logs
tail -f outputs/trading_*.log | grep "AI 分析"

# If no BUY/SELL signals, AI might not be confident enough
```

3. **Verify Data Fetching**:
```bash
# Check if market data is being fetched
tail -f outputs/trading_*.log | grep "市场数据"

# If data fetch fails repeatedly, check:
# - Network connectivity
# - Exchange API limits (rate limiting)
# - Symbol availability
```

4. **Check Account Balance**:
```bash
# Verify sufficient funds in testnet account
python3 << 'EOF'
import ccxt
import json

with open('config.json') as f:
    config = json.load(f)

exchange = ccxt.okx({
    'apiKey': config['OKX_API_KEY'],
    'secret': config['OKX_SECRET_KEY'],
    'password': config['OKX_PASSPHRASE']
})
exchange.set_sandbox_mode(True)

balance = exchange.fetch_balance()
print(f"USDT Free: {balance['USDT']['free']}")
print(f"USDT Total: {balance['USDT']['total']}")
EOF
```

---

### Problem: "⛔ Risk exceeds single trade limit"

**Cause**: Trade risk is > 2% of account

**Example**:
```
Account: $10,000
Max risk: $200 (2%)
Proposed risk: $250
Result: ❌ REJECTED
```

**Solution**:
- Reduce position size
- Choose higher confidence entries only
- Wait for setup with better risk/reward

---

### Problem: "⛔ Monthly drawdown limit exceeded"

**Cause**: Cumulative monthly losses approaching -6%

**Example**:
```
Initial balance: $10,000
Current balance: $9,420
Cumulative loss: -$580 (-5.8%)
Remaining budget: $20 (-6% limit is $9,400)
Result: ❌ Trading stops to protect capital
```

**Solution**:
- Wait for next month (resets monthly limits)
- Or manually adjust trading_memory.json (not recommended)
- Review trading performance
- Optimize AI prompt or risk rules

---

## Performance Issues

### Problem: "Slow execution" or "High latency"

**Cause**: Network or API delays

**Metrics**:
```
Ideal cycle time: 5-10 seconds
- Data fetch: 200-500ms
- AI decision: 1-3s
- Order execution: 100-500ms
```

**Optimization**:
```python
# 1. Reduce polling frequency
trader.run(interval_minutes=10)  # Instead of 5

# 2. Check network connectivity
ping okx.com
ping openai.com  # Or Volcano Engine

# 3. Monitor API rate limits
# Most exchanges allow 10-100 requests/second
# Spread requests across time
```

---

### Problem: "High CPU usage" or "Memory leak"

**Cause**: Continuous polling without sleep

**Solution**:
```python
# Ensure sleep intervals are set
import time
time.sleep(60)  # Sleep between cycles

# Check for infinite loops in log generation
# Monitor memory usage
python3 -c "import psutil; print(psutil.Process().memory_info().rss / 1024 / 1024)"  # MB
```

---

## Data Issues

### Problem: "K线数据异常，已跳过" (Invalid data skipped)

**Cause**: Market data validation failed

**Reasons**:
- All values are 0
- Data is constant (not changing)
- Standard deviation too low
- Insufficient data points

**Solution**:
```bash
# 1. Check if symbol exists on exchange
python3 << 'EOF'
import ccxt
okx = ccxt.okx({'sandbox': True})
symbols = okx.fetch_markets()
btc_usdt = [s for s in symbols if s['symbol'] == 'BTC/USDT:USDT']
print(f"BTC/USDT found: {len(btc_usdt) > 0}")
EOF

# 2. Verify symbol format
# OKX: BTC/USDT:USDT (perpetual)
# OKX: BTC/USDT (spot fallback)
# Binance: BTC/USDT (spot)

# 3. Check if market is active (sufficient volume)
```

---

## Logging & Debugging

### View Real-time Logs

```bash
# Watch trading logs
tail -f outputs/trading_*.log

# Filter for specific events
tail -f outputs/trading_*.log | grep "✅"     # Successful trades
tail -f outputs/trading_*.log | grep "❌"     # Failed trades
tail -f outputs/trading_*.log | grep "⛔"     # Risk rejections
tail -f outputs/trading_*.log | grep "ERROR"  # Errors
```

### Analyze Trade History

```bash
# Pretty-print trading memory
python3 << 'EOF'
import json

with open('trading_memory.json') as f:
    data = json.load(f)

# Print month stats
print("Monthly Stats:")
print(f"Initial: ${data['month_stats']['initial_balance']}")
print(f"Trades: {len(data['month_stats'].get('trades', []))}")

# Print recent trades
print("\nRecent Trades:")
for trade in data['month_stats'].get('trades', [])[-5:]:
    print(f"  {trade.get('coin')}: {trade.get('signal')} @ ${trade.get('entry_price')}")
EOF
```

---

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Insufficient balance` | No margin | Deposit testnet funds |
| `Order rejected` | Risk too high | Check risk limits |
| `API rate limit` | Too many requests | Increase interval_minutes |
| `Network timeout` | Connection issue | Check internet, retry |
| `Invalid symbol` | Symbol not on exchange | Verify symbol format |
| `Leverage not allowed` | Exchange limit | Reduce leverage |
| `Maintenance` | Exchange downtime | Wait for service to resume |

---

## Getting Help

### Before Opening an Issue

1. ✅ Check this troubleshooting guide
2. ✅ Review logs in `outputs/trading_*.log`
3. ✅ Verify config.json is correct
4. ✅ Test API connection manually
5. ✅ Check exchange status page

### When Reporting Issues

Include:
- **Error message**: Full error text
- **Logs**: Relevant log excerpts
- **Environment**: Python version, OS
- **Config**: (without API keys!)
- **Steps to reproduce**: How to trigger the error

---

## Performance Optimization

### Recommended Settings

```json
{
  "interval_minutes": 5,           // Check every 5 minutes
  "duration_hours": 24,            // Run for 24 hours
  "max_symbols": 10,               // Monitor top 10 coins
  "timeout_seconds": 30            // API timeout
}
```

### Scaling Up

```python
# For higher frequency trading:
trader.run(interval_minutes=1)  # 1-minute cycles

# For stability:
trader.run(interval_minutes=15)  # 15-minute cycles

# Factors to consider:
# - Exchange rate limits
# - AI API latency
# - Your internet connection
```

---

## Still Stuck?

1. **Check [ARCHITECTURE.md](ARCHITECTURE.md)** - System design explanation
2. **Check [CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup
3. **Review [TRADING_SYSTEM_GUIDE.md](TRADING_SYSTEM_GUIDE.md)** - Detailed guide
4. **Open a GitHub Issue** - Provide detailed error info

---

**Happy Trading! 🚀**
