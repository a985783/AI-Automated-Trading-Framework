# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Crypto AI Trading Bot                        │
│                  System Architecture v1.0                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 1. DATA LAYER                                                    │
│ ├─ Market Data Fetcher (OHLCV)                                   │
│ ├─ Technical Indicator Calculator (EMA, RSI, MACD, ATR)          │
│ └─ Data Validation & Fallback System                             │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. AI DECISION ENGINE                                            │
│ ├─ Deep-Prompt Engineering                                       │
│ ├─ Price Action Analysis                                         │
│ ├─ Order Flow Interpretation                                     │
│ ├─ Confidence Scoring (0-1.0)                                    │
│ └─ Signal Generation (BUY/SELL/HOLD)                             │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. RISK MANAGEMENT LAYER                                         │
│ ├─ Per-Trade Risk Check (2% max)                                 │
│ ├─ Monthly Drawdown Check (6% max)                               │
│ ├─ Position Sizing Calculator                                    │
│ ├─ Leverage Determiner (1-20x)                                   │
│ └─ Trade Validation & Approval                                   │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. EXECUTION LAYER                                               │
│ ├─ OKX/Binance Exchange Connectors (via CCXT)                    │
│ ├─ Order Placement (Market Orders)                               │
│ ├─ Position Tracking                                             │
│ ├─ Stop Loss / Take Profit Management                            │
│ └─ Leverage & Margin Control                                     │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. PERSISTENCE LAYER                                             │
│ ├─ Trade Memory (JSON)                                           │
│ ├─ Monthly Statistics                                            │
│ ├─ Performance Tracking                                          │
│ └─ Logging & Audit Trail                                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Data Layer

**File**: `crypto_trading_bot_enhanced.py` (methods: `fetch_market_data`, `_calculate_indicators`)

**Responsibilities**:
- Fetch OHLCV data from exchange (1m, 4h)
- Calculate technical indicators
- Validate data integrity
- Fallback to spot trading if perpetual fails

**Key Indicators**:
```python
- EMA (20, 50)       # Trend confirmation
- RSI (7, 14)        # Momentum & overbought/oversold
- MACD               # Trend & momentum crossover
- ATR (3, 14)        # Volatility & range
- Funding Rate       # Perpetual contract health
- Open Interest      # Market sentiment
```

**Data Validation**:
- Checks for zero/constant values
- Validates minimum data points (≥10 samples)
- Implements fallback mechanism

---

### 2. AI Decision Engine

**File**: `crypto_trading_bot_enhanced.py` (method: `query_ai_for_decision`)

**Input**:
- Market data (prices, indicators)
- Technical structure analysis
- Account information

**AI Prompt Structure**:
```
系统提示:
├─ 角色定义 (交易员/分析师)
├─ 任务 (生成交易决策)
├─ 风险约束 (2% max, 6% monthly)
│
用户提示:
├─ 市场数据分析
├─ 技术面 (EMA, RSI, MACD, ATR)
├─ 基本面 (资金费率, OI)
├─ 账户状态 (余额, 风险使用)
│
要求输出:
├─ 信号 (BUY/SELL/HOLD)
├─ 信心度 (0-1.0)
├─ 风险金额 ($)
├─ 杠杆倍数 (1-20x)
├─ 目标价格
├─ 止损价格
└─ 理由
```

**Output Format** (JSON):
```json
{
  "signal": "buy",
  "confidence": 0.75,
  "risk_usd": 150,
  "leverage": 5,
  "profit_target": 43200,
  "stop_loss": 41800,
  "justification": "..."
}
```

---

### 3. Risk Management Layer

**File**: `risk_manager.py` + `crypto_trading_bot_enhanced.py`

**Hardcoded Rules**:

```
Rule 1: Per-Trade Maximum
├─ Limit: Account Balance × 2%
├─ Example: $10,000 account = $200 max risk per trade
└─ Enforcement: Risk amount in USD must be ≤ limit

Rule 2: Monthly Drawdown
├─ Initial Balance: Recorded at first trade of month
├─ Limit: Initial Balance × 6% (hard stop)
├─ Example: Month starts at $10,000 → stop at $9,400
├─ Mechanism: Check before every trade
└─ Effect: System stops trading if breach imminent

Rule 3: Position Sizing
├─ Formula: Position Size = Risk Amount / (Entry Price - Stop Loss)
├─ Confidence-Based: Risk scales with AI confidence (0.5% - 2%)
└─ Dynamic: Adjusted based on account equity
```

**Check Sequence**:
```python
def _execute_buy():
    1. Check per-trade limit ❌ REJECT if risk > 2%
    2. Check monthly limit  ❌ REJECT if remaining budget < risk
    3. Check margin         ❌ REJECT if insufficient funds
    4. Set leverage         ✅ Apply leverage
    5. Place order          ✅ Execute trade
    6. Record trade         ✅ Log to memory
```

---

### 4. Execution Layer

**Exchange Abstraction** (CCXT):

```
CCXT Library
├─ OKX Connector
│  ├─ Perpetual Swaps (USDT-M)
│  ├─ Spot Trading (Fallback)
│  └─ Testnet Mode
│
└─ Binance Connector
   ├─ Futures (USDT-M)
   ├─ Spot Trading (Fallback)
   └─ Testnet Mode (testnet.binance.vision)
```

**Order Flow**:

```python
1. Create Market Order
   ├─ Symbol: BTC/USDT:USDT (OKX) or BTC/USDT (Binance)
   ├─ Type: Market Buy/Sell
   ├─ Quantity: Calculated from position sizing
   └─ Params: OKX-specific (tdMode, posSide) or Binance defaults

2. Set Leverage
   ├─ For OKX: exchange.set_leverage(5, symbol, params={'mgnMode': 'isolated'})
   └─ For Binance: exchange.set_leverage(5, symbol)

3. Place Stop Loss & Take Profit
   ├─ Type: Conditional orders
   ├─ OKX: Uses ordType='conditional' with triggerPx
   └─ Binance: Native stop loss orders

4. Track Position
   ├─ Entry Price: Record at execution
   ├─ Entry Time: Timestamp
   ├─ Entry Order ID: For reference
   ├─ Leverage: For risk calculation
   └─ Confidence: From AI decision
```

---

### 5. Persistence Layer

**Trade Memory** (`trading_memory.json`):

```json
{
  "current_month": "2025-10",
  "month_stats": {
    "initial_balance": 10000,
    "trades": [
      {
        "timestamp": "2025-10-30T14:30:00",
        "coin": "BTC",
        "signal": "buy",
        "entry_price": 42500,
        "quantity": 1.2,
        "leverage": 5,
        "stop_loss": 41800,
        "profit_target": 43200,
        "entry_logic": "Strong uptrend on 20m, pullback on 5m",
        "confidence": 0.75,
        "risk_usd": 150
      },
      {
        "timestamp": "2025-10-30T15:45:00",
        "coin": "BTC",
        "signal": "sell",
        "exit_price": 43100,
        "pnl": 720,
        "pnl_pct": 3.6
      }
    ]
  }
}
```

**Logging** (`outputs/trading_*.log`):

```
2025-10-30 14:30:00 - INFO - ✅ BTC 买入成功: 1.2 @ $42,500
2025-10-30 14:30:01 - INFO - 目标: $43,200 | 止损: $41,800
2025-10-30 15:45:00 - INFO - 🎯 BTC 触发止盈!
2025-10-30 15:45:01 - INFO - ✅ 卖出成功: 1.2 @ $43,100
2025-10-30 15:45:02 - INFO - 盈亏: $720 (+3.6%)
```

---

## Data Flow Example

### Scenario: Trade Execution

```
[Every 5 minutes]
     │
     ▼
1. fetch_market_data()
   ├─ BTC: $42,500 (current price)
   ├─ EMA20: $42,450 (bullish)
   ├─ RSI7: 65 (momentum)
   └─ MACD: Positive (trend)

     │
     ▼
2. query_ai_for_decision()
   ├─ Input: Market data above
   ├─ AI Analysis: "Strong uptrend, good entry opportunity"
   └─ Output: {signal: "buy", confidence: 0.75, risk: $150, ...}

     │
     ▼
3. Risk Management Checks
   ├─ Per-trade: $150 < $200 (2% of $10k) ✅
   ├─ Monthly: Cumulative risk OK ✅
   └─ Margin: Sufficient balance ✅

     │
     ▼
4. _execute_buy()
   ├─ Set leverage: 5x
   ├─ Calculate quantity: $150 / ($42,500 - $41,800) = 1.2 BTC
   ├─ Create market order: Buy 1.2 BTC
   ├─ Set SL/TP: $41,800 / $43,200
   └─ Record trade: Save to trading_memory.json

     │
     ▼
5. Position Tracking
   ├─ Entry: $42,500 ✓
   ├─ Current P&L: Calculated each cycle
   ├─ Check SL: If price ≤ $41,800 → execute_sell()
   └─ Check TP: If price ≥ $43,200 → execute_sell()

     │
     ▼
6. Trade Completion
   ├─ Executed at $43,100
   ├─ P&L: $720 (3.6%)
   └─ Recorded: Monthly stats updated
```

---

## Configuration & Modes

### Testnet Mode (Default)

```json
{
  "EXCHANGE": "okx",
  "OKX_API_KEY": "demo-key",
  "OKX_SECRET_KEY": "demo-secret",
  "OKX_PASSPHRASE": "demo-passphrase"
}
```

- ✅ Safe: Play money only
- ✅ Realistic: Real market data
- ❌ Limited: Testnet volumes
- ❌ Latency: May differ from production

### Live Mode (Production)

```json
{
  "EXCHANGE": "okx",
  "OKX_API_KEY": "real-key",
  "OKX_SECRET_KEY": "real-secret",
  "OKX_PASSPHRASE": "real-passphrase"
}
```

- 🔴 **WARNING**: Real money at risk
- ✅ Pros: Live slippage, fees, market conditions
- ❌ Cons: Can lose capital, requires expertise

---

## Extension Points

### Adding a New Exchange

1. **Implement Initialization**:
```python
def _init_newexchange_testnet(self):
    exchange = ccxt.newexchange({
        'apiKey': self.config['NEWEX_API_KEY'],
        'secret': self.config['NEWEX_SECRET_KEY'],
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    return exchange
```

2. **Update Symbol Converter**:
```python
def _convert_symbol(self, symbol, to_exchange=None):
    # Add case for 'newexchange'
    if exchange == 'newexchange':
        return f"{coin}/USDT"  # Your format
```

3. **Test Connection**:
```bash
python3 -c "from crypto_trading_bot_enhanced import CryptoAITrader; CryptoAITrader()"
```

---

## Performance Characteristics

| Component | Latency | Bottleneck | Notes |
|-----------|---------|-----------|-------|
| Data Fetch | 200-500ms | Exchange API | Rate limited |
| AI Decision | 1-3s | OpenAI API | Network dependent |
| Order Execution | 100-500ms | Exchange API | Network latency |
| **Total Cycle** | **5+ seconds** | AI Processing | 5m minimum interval |

---

## Security Considerations

```
┌─────────────────────────────────────────────────┐
│         Security Layers                         │
├─────────────────────────────────────────────────┤
│ 1. API Key Protection                           │
│    ├─ Stored in config.json (git-ignored)       │
│    ├─ Never logged or displayed                 │
│    └─ Use API key with minimal permissions      │
│                                                  │
│ 2. Trade Validation                             │
│    ├─ Risk checks before execution              │
│    ├─ Monthly drawdown safeguard                │
│    └─ Manual review possible (extend code)      │
│                                                  │
│ 3. Data Integrity                               │
│    ├─ Data validation in fetch_market_data()    │
│    ├─ Fallback mechanisms for failures          │
│    └─ Logging for audit trail                   │
└─────────────────────────────────────────────────┘
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
