加密货币合约 AI 交易系统（OKX 模拟盘）

一个基于 DeepSeek-V3（火山引擎 ARK）的自主交易引擎：固定“20m 趋势 + 5m 执行”框架，内置双重硬风控（单笔 2%、月度 -6%），面向 OKX 模拟盘（USDT 本位永续）。不包含前端，仅日志输出与交易记忆持久化。

功能
- 深度提示词驱动的 AI 决策（价格行为 + 订单流 + 缠论）
- 20m 趋势判定 + 5m 执行周期
- 双重硬风控：单笔 2% 风险、月度 -6% 回撤即停
- 自动下单与持仓跟踪（OKX 模拟盘）
- 交易记忆与月度统计（`trading_memory.json`）
- 日志输出到 `outputs/trading_*.log`

快速开始
1) 准备环境（Python 3.9+）
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) 配置密钥
```
cp config.example.json config.json
# 编辑 config.json，填入 ARK 与 OKX 模拟盘 API 三件套
```

3) 运行
```
python3 crypto_trading_bot_enhanced.py
# 或
./start.sh
```

4) 查看日志
```
tail -f outputs/trading_*.log
```

目录结构
```
├── crypto_trading_bot_enhanced.py   # 主交易引擎
├── risk_manager.py                  # 月度风控/交易记忆
├── config.json                      # 本地密钥（git 忽略）
├── config.example.json              # 示例配置
├── outputs/                         # 日志与导出（git 忽略）
├── trading_memory.json              # 交易记忆（git 忽略）
├── start.sh                         # 一键启动脚本
├── RISK_MANAGEMENT_RULES.md         # 风险管理规则
└── TRADING_SYSTEM_GUIDE.md          # 系统使用说明
```

风险与声明
- 本代码仅用于研究与教育目的，不构成投资建议。
- 实盘交易存在本金损失风险。请务必理解并接受相关风险。
- 默认对接 OKX 模拟盘；若用于实盘请自行添加服务器端止损/止盈等保护。

依赖
- Python 3.9+
- openai（ARK SDK 兼容版）
- ccxt、pandas、numpy

常见问题
- 启动报错缺少密钥：请在 `config.json` 中填入 ARK 与 OKX 模拟盘 API。
- 连接失败：检查网络、时间同步（NTP）、API 权限与白名单。
- 没有下单：可能因风控限制（单笔 >2% 或接近月度 -6%）。查看日志了解原因。

———

如需添加前端仪表板或接入其他交易所，可在此基础上扩展（建议保持风控硬约束不变）。
