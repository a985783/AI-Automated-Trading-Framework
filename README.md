# 🤖 Crypto AI Trading Bot

![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Trading Engine](https://img.shields.io/badge/Engine-DeepSeek%20V3-orange)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

**An autonomous AI-powered cryptocurrency trading engine using DeepSeek-V3 with dual-layer risk management for OKX testnet.**

> 🚀 **20-minute trend confirmation + 5-minute execution** framework with hardened risk controls

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Decision Engine** | Deep-prompt-driven decisions using price action + order flow analysis |
| 📊 **Multi-timeframe** | 20m trend confirmation + 5m execution framework |
| 🛡️ **Risk Management** | Dual hardcoded limits: 2% per-trade max, 6% monthly drawdown max |
| 📈 **Auto Trading** | Fully automated order execution with position tracking |
| 💾 **Trade Memory** | Persistent trading history and monthly statistics |
| 📝 **Detailed Logs** | Real-time trading journal with performance metrics |
| 🔄 **Multi-Exchange** | Support for OKX (default) & Binance testnet |

---

## 🎯 Core Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Market Data Feed                           │
│              (OHLCV + Technical Indicators)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            DeepSeek-V3 Decision Engine (ARK API)            │
│  • Price Action Analysis      • Order Flow                  │
│  • Technical Indicators       • Confidence Scoring          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Risk Management System                         │
│  ├─ Per-Trade Limit: 2% of account balance                  │
│  ├─ Monthly Limit: -6% drawdown max                         │
│  └─ Position Sizing: Dynamic based on confidence            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            OKX/Binance Trade Execution                      │
│  ├─ Leverage Control (1-20x)    ├─ Stop Loss                │
│  ├─ Margin Management            └─ Take Profit             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Trade Memory & Statistics Tracking                  │
│              (JSON Persistence Layer)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1️⃣ Prerequisites

```bash
# Python 3.9 or higher
python3 --version

# Virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2️⃣ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/crypto-ai-trading-bot.git
cd crypto-ai-trading-bot

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Configuration

```bash
# Copy example config
cp config.example.json config.json

# Edit with your credentials (using your preferred editor)
nano config.json
# or
open config.json  # macOS

# Required fields:
# - ARK_API_KEY: DeepSeek-V3 API key (from Volcano Engine)
# - EXCHANGE: "okx" (default) or "binance"
# - OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE (if using OKX)
```

### 4️⃣ Run the Bot

```bash
# Method 1: Direct execution
python3 crypto_trading_bot_enhanced.py

# Method 2: Using startup script
chmod +x start.sh
./start.sh
```

### 5️⃣ Monitor Performance

```bash
# Watch live logs
tail -f outputs/trading_*.log

# Check trading history
cat trading_memory.json | python3 -m json.tool

# View trading stats
# (Stats printed to logs in real-time)
```

---

## 📁 Project Structure

```
crypto-ai-trading-bot/
├── crypto_trading_bot_enhanced.py   # Main trading engine
├── risk_manager.py                  # Risk management & trade memory
├── config.example.json              # Configuration template
├── config.json                      # Local config (git-ignored)
├── requirements.txt                 # Python dependencies
├── start.sh                         # One-click startup
│
├── outputs/                         # Trading logs (git-ignored)
│   └── trading_YYYYMMDD_HHMMSS.log
├── trading_memory.json              # Trade history (git-ignored)
│
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
├── CONTRIBUTING.md                  # Contribution guidelines
├── LICENSE                          # MIT License
├── TRADING_SYSTEM_GUIDE.md          # Detailed usage guide
├── RISK_MANAGEMENT_RULES.md         # Risk management documentation
└── GITHUB_READY_CHECKLIST.md        # Project improvement checklist
```

---

## ⚙️ Configuration Examples

### OKX Testnet (Default)
```json
{
  "EXCHANGE": "okx",
  "ARK_API_KEY": "your-deepseek-v3-key",
  "OKX_API_KEY": "your-okx-api-key",
  "OKX_SECRET_KEY": "your-okx-secret-key",
  "OKX_PASSPHRASE": "your-okx-passphrase"
}
```

### Binance Testnet
```json
{
  "EXCHANGE": "binance",
  "ARK_API_KEY": "your-deepseek-v3-key",
  "BINANCE_API_KEY": "your-binance-api-key",
  "BINANCE_SECRET_KEY": "your-binance-secret-key",
  "BINANCE_TESTNET": true
}
```

---

## 📊 Performance Metrics

The bot tracks and reports:

- **Per-Trade Metrics**: Entry price, exit price, P&L, P&L%, hold duration
- **Risk Metrics**: Risk per trade, leverage used, liquidation price
- **Monthly Stats**: Total trades, win rate, max drawdown, ROI
- **AI Metrics**: Decision confidence, signal accuracy, execution time

Example output:
```
===============================================================================
第 1 轮 - 2025-10-30 14:30:00
===============================================================================

🎯 市场数据: BTC: $42,500.00 (↑2.3%) | ETH: $2,450.00 (↑1.8%) | ...

💭 AI 分析:
BTC: 强势上升趋势，5m有小回调机会 → 买入信号
  信心度: 0.75 | 杠杆: 5x | 风险: $150.00 | 目标: $43,200

✅ 执行: BTC 买入 1.2 BTC @ $42,500
📊 月度统计: 总交易 8 笔 | 胜率 62.5% | 月度P&L: +$1,250
```

---

## 🛡️ Risk Management

### Hardcoded Limits

```
Per-Trade Maximum:  2% of account balance
Monthly Drawdown:   -6% hard stop-loss
Leverage Range:     1-20x (configurable per trade)
```

### Example Scenario

Starting balance: $10,000
- Max risk per trade: $200 (2%)
- Monthly stop loss level: $9,400 (6% drawdown)

If a trade risks $200 and loses, account becomes $9,800.
If cumulative losses reach -$600, system stops trading.

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [TRADING_SYSTEM_GUIDE.md](TRADING_SYSTEM_GUIDE.md) | Detailed system explanation & trading logic |
| [RISK_MANAGEMENT_RULES.md](RISK_MANAGEMENT_RULES.md) | Risk framework & hardened constraints |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute & development setup |
| [CHANGELOG.md](CHANGELOG.md) | Version history & feature releases |

---

## 🚨 Risk Disclosure

**⚠️ IMPORTANT - Please Read Before Using**

- 🔴 **This is experimental software**: Use at your own risk
- 📚 **Educational purposes only**: Not financial advice
- 💸 **Live trading risk**: Can result in loss of capital
- 🧪 **Thoroughly test on testnet first**: Before any real trading
- 🔐 **Secure your API keys**: Never commit credentials
- 📞 **Implement safeguards**: Add server-side stop-losses for production

---

## 🔧 Installation Issues?

### Common Problems

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: openai` | Run `pip install -r requirements.txt` |
| `Invalid API Key` | Check `config.json` credentials |
| `Connection refused` | Check internet & API endpoint availability |
| `InsufficientBalance` | Testnet account needs minimum balance |

👉 See [TRADING_SYSTEM_GUIDE.md](TRADING_SYSTEM_GUIDE.md) for more troubleshooting

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report bugs
- Feature request process
- Development guidelines
- Pull request procedures

---

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **DeepSeek-V3**: AI decision engine (via Volcano Engine ARK API)
- **CCXT**: Cryptocurrency exchange abstraction library
- **OKX & Binance**: Testnet environments for safe trading practice

---

## 📧 Support

- 📖 Read the documentation
- 🔍 Search existing issues
- 💬 Open a discussion
- 🐛 Report a bug

---

**Happy Trading! 🚀📈**

*Remember: Past performance doesn't guarantee future results. Trade wisely.*
