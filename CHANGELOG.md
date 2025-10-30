# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-exchange support framework (OKX & Binance)
- Symbol format conversion system
- Advanced binance testnet integration

### Changed
- Updated symbol handling for cross-exchange compatibility

## [1.0.0] - 2025-10-30

### Added
- AI trading decision engine powered by DeepSeek-V3
- Dual-layer risk management system
  - Per-trade risk limit (2% max)
  - Monthly drawdown limit (6% max)
- Automated trade execution on OKX testnet
- Trade memory persistence (JSON-based)
- Real-time trading logs and statistics
- Technical indicator calculations (EMA, RSI, MACD, ATR)
- 20-minute trend + 5-minute execution framework
- Multi-timeframe market analysis

### Features
- Price action + order flow analysis
- Dynamic position sizing based on confidence
- Leverage management (1-20x)
- Stop loss and take profit automation
- Monthly performance tracking
- Trade history and statistics

### Documentation
- Comprehensive risk management guide
- Trading system user guide
- API configuration examples
- Troubleshooting guide

### Infrastructure
- One-click startup script (start.sh)
- Configurable environment setup
- Modular code architecture
- Extensive logging system

## Security Notes

- All API keys are properly isolated in config.json
- config.json is git-ignored to prevent credential leaks
- trading_memory.json is git-ignored for privacy
- Mock trading on simulated accounts only (default)
