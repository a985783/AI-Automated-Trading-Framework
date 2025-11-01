"""
加密货币合约AI交易系统
- AI: DeepSeek-V3 (火山引擎 ARK)
- 交易所: OKX 模拟盘（仅保留模拟交易）
"""

import os
from openai import OpenAI
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional
import logging
from pathlib import Path
from risk_manager import MonthlyRiskManager

class CryptoAITrader:
    """
    加密货币AI交易系统
    - DeepSeek-V3 完全自主决策
    - OKX 模拟盘交易
    """
    
    def __init__(self):
        """初始化交易系统"""
        # 加载配置
        self.config = self._load_config()
        
        # 初始化 DeepSeek-V3 客户端 (通过火山引擎 ARK)
        self.ai_client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.config['ARK_API_KEY']
        )
        self.ai_model = self.config['ARK_MODEL']
        
        # 交易所类型（仅 OKX）
        self.exchange_type = 'okx'
        # 初始化交易所
        self.exchange = self._init_okx_testnet()

        # 初始化风险管理器（固定6%月度回撤）
        self.risk_manager = MonthlyRiskManager('trading_memory.json')

        # 交易状态
        self.positions = {}  # 当前持仓
        self.trade_history = []  # 交易历史
        self.initial_balance = None
        self.month_initialized = False  # 月度初始化标记
        
        # 监控的币种（市值前10）
        self.coin_list = ['BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'ADA', 'TRX', 'AVAX', 'LINK']
        self.symbols = [self._convert_symbol(f"{coin}/USDT") for coin in self.coin_list]
        
        # 设置日志
        self._setup_logging()
        
        # 创建输出目录
        Path('outputs').mkdir(exist_ok=True)
        
        self.logger.info("✅ 交易系统初始化完成")
    
    def _load_config(self) -> Dict:
        """加载配置"""
        config = {
            # 火山引擎 ARK API (DeepSeek-V3)
            'ARK_API_KEY': os.getenv('ARK_API_KEY', ''),
            'ARK_MODEL': 'deepseek-v3-1-terminus',
            # 交易所（仅 OKX）
            'EXCHANGE': 'okx',
            
            # OKX API（实盘）
            'OKX_API_KEY': os.getenv('OKX_API_KEY', ''),
            'OKX_SECRET_KEY': os.getenv('OKX_SECRET_KEY', ''),
            'OKX_PASSPHRASE': os.getenv('OKX_PASSPHRASE', ''),
            'OKX_DEMO': False,
        }

        # 尝试从 config.json 读取
        config_file = Path('config.json')
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)

        # 验证必需配置
        if not config['ARK_API_KEY']:
            raise ValueError("请设置 ARK_API_KEY")

        # 验证 OKX 配置
        if not config.get('OKX_API_KEY') or not config.get('OKX_SECRET_KEY') or not config.get('OKX_PASSPHRASE'):
            raise ValueError("请设置 OKX_API_KEY/OKX_SECRET_KEY/OKX_PASSPHRASE")

        # 实盘警告
        if not config.get('OKX_DEMO', False):
            print("\n⚠️  警告：您正在使用 OKX 实盘环境！")
            print("⚠️  这将使用真实资金进行交易！")
            print("⚠️  请确保已理解系统的交易逻辑和风险！\n")
        
        return config

    

    def _init_okx_testnet(self):
        """初始化 OKX 交易环境 (USDT 本位永续)"""
        exchange = ccxt.okx({
            'apiKey': self.config['OKX_API_KEY'],
            'secret': self.config['OKX_SECRET_KEY'],
            'password': self.config['OKX_PASSPHRASE'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # USDT 本位永续
                'recvWindow': 50000,
                'adjustForTimeDifference': True,
            }
        })

        # 根据配置选择模拟盘或实盘
        is_demo = self.config.get('OKX_DEMO', False)
        if is_demo:
            # 启用模拟盘
            try:
                exchange.set_sandbox_mode(True)
            except Exception:
                # 兼容旧版本：直接设置头部
                exchange.headers = exchange.headers or {}
                exchange.headers.update({'x-simulated-trading': '1'})
            print("✅ 已连接到 OKX 模拟盘")
        else:
            # 实盘模式
            print("✅ 已连接到 OKX 实盘")

        # 测试连接
        try:
            balance = exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            env_name = "模拟盘" if is_demo else "实盘"
            print(f"✅ OKX {env_name}连接成功")
            print(f"USDT 余额: {usdt_balance:.2f}")
        except Exception as e:
            env_name = "模拟盘" if is_demo else "实盘"
            raise ConnectionError(f"OKX {env_name}连接失败: {e}")

        return exchange

    def _convert_symbol(self, symbol: str) -> str:
        """OKX 永续合约格式: 'BTC/USDT:USDT'"""
        coin = symbol.split('/')[0] if '/' in symbol else symbol.replace('USDT', '').strip()
        return f"{coin}/USDT:USDT"

    def _setup_logging(self):
        """设置日志"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        file_handler = logging.FileHandler(
            f'outputs/trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        
        self.logger = logging.getLogger('CryptoAITrader')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    # ========== 数据获取 ==========
    
    def fetch_market_data(self) -> Dict:
        """获取所有币种的市场数据（带健壮回退）"""
        market_data = {}

        def is_series_invalid(closes: List[float]) -> bool:
            if not closes or len(closes) < 10:
                return True
            arr = np.array(closes, dtype=float)
            # 全为0或几乎恒定
            if np.allclose(arr, 0):
                return True
            unique = np.unique(np.round(arr, 4))
            if unique.size <= 2:
                return True
            # 低波动（过去100根标准差过低）
            if np.std(arr) < 1e-8:
                return True
            return False

        for symbol in self.symbols:
            # 从符号提取币种名称（OKX 格式）
            coin = symbol.split('/')[0] if '/' in symbol else symbol.replace('USDT', '').strip()
            self.logger.info(f"获取 {coin} 数据...")

            used_symbol = symbol
            data_note = ''
            funding_rate = 0.0001
            open_interest = 0.0

            try:
                # 交易周期：5m；趋势周期：20m（由5m聚合）
                ohlcv_5m = self.exchange.fetch_ohlcv(symbol, '5m', limit=200)
                ticker = self.exchange.fetch_ticker(symbol)

                # 仅合约有资金费率/未平仓量
                try:
                    funding = self.exchange.fetch_funding_rate(symbol)
                    funding_rate = float(funding.get('fundingRate', 0.0001) or 0.0001)
                except Exception:
                    funding_rate = 0.0001
                try:
                    oi = self.exchange.fetch_open_interest(symbol)
                    open_interest = float(oi.get('openInterestAmount') or 0)
                except Exception:
                    open_interest = 0.0

                # 5m 数据 + 20m 聚合
                df_5m = self._klines_to_df(ohlcv_5m[-120:])
                ohlcv_20m = self._aggregate_ohlcv_by_ms(ohlcv_5m, 20 * 60 * 1000)
                df_20m = self._klines_to_df(ohlcv_20m[-60:])

                # 如果数据明显异常，回退到现货对
                if is_series_invalid(df_5m['close'].tolist()) or is_series_invalid(df_20m['close'].tolist()):
                    spot_symbol = f"{coin}/USDT"

                    try:
                        spot_5m = self.exchange.fetch_ohlcv(spot_symbol, '5m', limit=200)
                        spot_ticker = self.exchange.fetch_ticker(spot_symbol)
                        df_5m = self._klines_to_df(spot_5m[-120:])
                        ohlcv_20m = self._aggregate_ohlcv_by_ms(spot_5m, 20 * 60 * 1000)
                        df_20m = self._klines_to_df(ohlcv_20m[-60:])
                        ticker = spot_ticker
                        used_symbol = spot_symbol
                        data_note = 'spot_fallback'
                    except Exception as _:
                        data_note = 'invalid_series'

                indicators_5m = self._calculate_indicators(df_5m)
                indicators_20m = self._calculate_indicators(df_20m)

                # 如果仍异常，跳过该币种
                if is_series_invalid(df_5m['close'].tolist()) or is_series_invalid(df_20m['close'].tolist()):
                    self.logger.warning(f"{coin} K线数据异常，已跳过 (source={used_symbol}, note={data_note})")
                    time.sleep(0.05)
                    continue

                market_data[coin] = {
                    'source_symbol': used_symbol,
                    'current_price': float(ticker['last']),
                    'current_ema_20': float(indicators_5m['ema_20'].iloc[-1]),
                    'current_macd': float(indicators_5m['macd_histogram'].iloc[-1]),
                    'current_rsi_7': float(indicators_5m['rsi_7'].iloc[-1]),
                    'open_interest': {
                        'latest': open_interest,
                        'average': open_interest
                    },
                    'funding_rate': funding_rate if used_symbol == symbol else 0.0,
                    'minute_series': {
                        'mid_price': [float(x) for x in df_5m['close'].tail(10).tolist()],
                        'ema_20': [float(x) for x in indicators_5m['ema_20'].tail(10).tolist()],
                        'macd': [float(x) for x in indicators_5m['macd_histogram'].tail(10).tolist()],
                        'rsi_7': [float(x) for x in indicators_5m['rsi_7'].tail(10).tolist()],
                        'rsi_14': [float(x) for x in indicators_5m['rsi_14'].tail(10).tolist()],
                    },
                    'trend_context': {
                        'ema_20': float(indicators_20m['ema_20'].iloc[-1]),
                        'ema_50': float(indicators_20m['ema_50'].iloc[-1]),
                        'atr_3': float(indicators_20m['atr_3'].iloc[-1]),
                        'atr_14': float(indicators_20m['atr_14'].iloc[-1]),
                        'current_volume': float(df_20m['volume'].iloc[-1]),
                        'average_volume': float(df_20m['volume'].mean()),
                        'macd_series': [float(x) for x in indicators_20m['macd_histogram'].tail(10).tolist()],
                        'rsi_14_series': [float(x) for x in indicators_20m['rsi_14'].tail(10).tolist()],
                    },
                    '24h_change_percent': float(ticker.get('percentage') or 0),
                    '24h_high': float(ticker.get('high') or 0),
                    '24h_low': float(ticker.get('low') or 0),
                    '24h_volume': float(ticker.get('quoteVolume') or ticker.get('baseVolume') or 0),
                    'data_note': data_note,
                }

                time.sleep(0.1)  # 避免限流

            except Exception as e:
                self.logger.error(f"获取 {symbol} 数据失败: {e}")
                continue

        return market_data
    
    def _klines_to_df(self, klines: List) -> pd.DataFrame:
        """K线转DataFrame"""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume'
        ])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df

    def _aggregate_ohlcv_by_ms(self, klines: List[List[float]], bucket_ms: int) -> List[List[float]]:
        """按时间桶聚合 OHLCV，open=首根open, high=max, low=min, close=末根close, volume=sum"""
        if not klines:
            return []
        buckets = {}
        for row in klines:
            if row is None or len(row) < 6:
                continue
            ts, o, h, l, c, v = row
            try:
                ts = int(ts)
                o = float(o); h = float(h); l = float(l); c = float(c); v = float(v)
            except Exception:
                continue
            b = (ts // bucket_ms) * bucket_ms
            bkt = buckets.get(b)
            if bkt is None:
                buckets[b] = {
                    'open': o,
                    'high': h,
                    'low': l,
                    'close': c,
                    'volume': v,
                    'ts_first': ts,
                    'ts_last': ts,
                }
            else:
                bkt['high'] = max(bkt['high'], h)
                bkt['low'] = min(bkt['low'], l)
                bkt['close'] = c
                bkt['volume'] = (bkt['volume'] or 0) + v
                bkt['ts_last'] = ts
        aggregated = []
        for b in sorted(buckets.keys()):
            x = buckets[b]
            aggregated.append([b, x['open'], x['high'], x['low'], x['close'], x['volume']])
        return aggregated

    # 删除通用时间框架聚合函数，恢复固定 5m/20m 逻辑
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        indicators = df.copy()
        
        # EMA
        indicators['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        indicators['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=7).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=7).mean()
        rs = gain / loss
        indicators['rsi_7'] = 100 - (100 / (1 + rs))
        
        gain14 = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss14 = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs14 = gain14 / loss14
        indicators['rsi_14'] = 100 - (100 / (1 + rs14))
        
        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        indicators['macd_histogram'] = macd_line - signal_line
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        indicators['atr_3'] = tr.rolling(window=3).mean()
        indicators['atr_14'] = tr.rolling(window=14).mean()
        
        return indicators

    def _fmt_price(self, p: float) -> str:
        """根据数量级格式化价格，避免小币种被四舍五入成0/1"""
        try:
            p = float(p)
        except Exception:
            return str(p)
        if p < 0:
            p = abs(p)
        if p < 1:
            return f"{p:.4f}"
        if p < 100:
            return f"{p:.2f}"
        return f"{p:.1f}"
    
    def get_account_info(self, market_data: Dict) -> Dict:
        """获取账户信息"""
        try:
            balance = self.exchange.fetch_balance()
            usdt_free = float(balance['USDT']['free'])
            usdt_total = float(balance['USDT']['total'])
        except Exception as e:
            self.logger.error(f"获取余额失败: {e}")
            usdt_free = 10000
            usdt_total = 10000
        
        if self.initial_balance is None:
            self.initial_balance = usdt_total
        
        # 获取持仓信息
        positions_detail = []
        total_unrealized_pnl = 0
        
        for symbol, pos in self.positions.items():
            coin = symbol.split('/')[0]
            if coin not in market_data:
                continue
            
            current_price = market_data[coin]['current_price']
            
            # 计算未实现盈亏
            if pos['side'] == 'long':
                unrealized_pnl = (current_price - pos['entry_price']) * pos['quantity']
            else:
                unrealized_pnl = (pos['entry_price'] - current_price) * pos['quantity']
            
            total_unrealized_pnl += unrealized_pnl
            
            # 计算清算价格
            if pos['side'] == 'long':
                liquidation = pos['entry_price'] * (1 - 1/pos['leverage'] * 0.9)
            else:
                liquidation = pos['entry_price'] * (1 + 1/pos['leverage'] * 0.9)
            
            positions_detail.append({
                'symbol': coin,
                'quantity': pos['quantity'],
                'entry_price': pos['entry_price'],
                'current_price': current_price,
                'liquidation_price': round(liquidation, 2),
                'unrealized_pnl': round(unrealized_pnl, 2),
                'leverage': pos['leverage'],
                'exit_plan': pos.get('exit_plan', {}),
                'confidence': pos.get('confidence', 0.65),
                'risk_usd': pos.get('risk_usd', 0),
                'notional_usd': round(current_price * pos['quantity'], 2),
            })
        
        total_value = usdt_total + total_unrealized_pnl
        total_return_pct = (total_value - self.initial_balance) / self.initial_balance * 100
        
        return {
            'total_return_pct': round(total_return_pct, 2),
            'available_cash': round(usdt_free, 2),
            'account_balance': round(usdt_total, 2),
            'positions': positions_detail,
            'sharpe_ratio': self._calculate_sharpe(),
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
        }
    
    def _calculate_sharpe(self) -> float:
        """计算夏普比率"""
        if len(self.trade_history) < 2:
            return 0.0
        returns = [t.get('pnl_pct', 0) for t in self.trade_history]
        if not returns:
            return 0.0
        return np.mean(returns) / (np.std(returns) + 1e-10)
    
    # ========== AI决策 (DeepSeek-V3) ==========
    
    def get_ai_decision(self, market_data: Dict, account_info: Dict) -> Dict:
        """获取 DeepSeek-V3 的交易决策"""
        prompt = self._build_prompt(market_data, account_info)
        
        try:
            self.logger.info("正在请求 DeepSeek-V3 决策...")
            
            response = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的加密货币合约交易AI系统。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4096,
            )
            
            raw_response = response.choices[0].message.content
            decision = self._parse_decision(raw_response)

            # 调试：打印原始响应（帮助诊断问题）
            if len(decision) < len(self.symbols):
                self.logger.warning(f"⚠️ AI 只决策了 {len(decision)} 个币种，预期 {len(self.symbols)} 个")
                self.logger.debug(f"AI 原始响应:\n{raw_response[:500]}")  # 打印前 500 字符
                self.logger.debug(f"解析后决策: {decision}")

            self.logger.info(f"✅ DeepSeek-V3 决策完成，涉及 {len(decision)} 个币种")

            return decision
            
        except Exception as e:
            self.logger.error(f"AI决策失败: {e}")
            return {}
    
    def _build_prompt(self, market_data: Dict, account_info: Dict) -> str:
        """构建提示词（支持严格/自由两种风格）"""

        # 获取历史交易和上一笔交易逻辑
        all_trades = self.risk_manager.get_all_trades()
        last_trade_logic = self.risk_manager.get_last_trade_logic()
        open_trades = self.risk_manager.get_open_trades()
        month_stats = self.risk_manager.get_month_stats()

        # 格式化交易历史（最近5笔）
        recent_trades_text = ""
        if all_trades:
            for trade in all_trades[-5:]:
                result = "✓" if trade.get('pnl', 0) > 0 else "✗"
                recent_trades_text += f"  {result} {trade['coin']}: {trade['signal']} @ {trade['entry_price']:.2f}, 止损:{trade['stop_loss']:.2f}, 结构:{trade.get('structure', 'N/A')}\n"
        else:
            recent_trades_text = "  (无历史交易)"

        # 格式化当前持仓
        open_trades_text = ""
        if open_trades:
            for trade in open_trades:
                open_trades_text += f"  {trade['coin']}: 入场{trade['entry_price']:.2f}, 止损{trade['stop_loss']:.2f}, 杠杆{trade['leverage']}x\n"
        else:
            open_trades_text = "  (无持仓)"

        # 格式化市场数据
        market_summary = []
        for coin, data in market_data.items():
            mid_series = [self._fmt_price(x) for x in data['minute_series']['mid_price'][-10:]]
            rsi7_series = [f"{float(x):.1f}" for x in data['minute_series']['rsi_7'][-10:]]
            summary = f"""
【{coin} 市场分析】
价格: {self._fmt_price(data['current_price'])} | 20日EMA: {self._fmt_price(data['current_ema_20'])} | RSI(7): {data['current_rsi_7']:.1f}

5分钟K线序列（最近10根）：
  价格: {mid_series}
  RSI-7: {rsi7_series}

20分钟周期背景（趋势判定）：
  EMA-20: {self._fmt_price(data['trend_context']['ema_20'])} vs EMA-50: {self._fmt_price(data['trend_context']['ema_50'])}
  波动率(ATR-3): {self._fmt_price(data['trend_context']['atr_3'])} | 资金费率: {data['funding_rate']:.6f}
"""
            market_summary.append(summary)
        prompt = f"""你是一个使用【价格行为 + 订单流 + 缠论】的专业交易AI。

================== 核心交易框架 ==================
1. 趋势周期(20分钟K线)：判断大方向，只顺应主趋势
2. 交易周期(5分钟K线)：执行信号，等待结构突破
3. 关键原则：顺大逆小，结构未破不重仓，亏损及时止损
4. 风险管理：【以损定仓】根据置信度和结构清晰度灵活选择 0.5%-2% 风险
   ⚠️ 【硬限制】单笔最高2%亏损 + 月度最高6%累积亏损（两个都不能突破）

================== 账户状态 ==================
账户余额: ${account_info['account_balance']:.2f}
可用资金: ${account_info['available_cash']:.2f}
月度初始资金: ${month_stats.get('initial_balance', 0):.2f}
月度回撤硬止损: ${month_stats.get('drawdown_limit', 0):.2f}
当月已交易: {month_stats.get('total_trades', 0)}笔 (胜率: {month_stats.get('win_rate', 0):.1f}%)
当月已亏: ${month_stats.get('initial_balance', 0) - account_info['account_balance']:.2f} (离6%限额还有 ${month_stats.get('drawdown_limit', 0) - account_info['account_balance']:.2f})

当前持仓:
{open_trades_text}

================== 上一笔交易逻辑（记忆中） ==================
{f"币种: {last_trade_logic.get('coin')}, 信号: {last_trade_logic.get('signal')}, 结构: {last_trade_logic.get('structure', 'N/A')}, 置信度: {last_trade_logic.get('confidence', 0)}, 风险: {last_trade_logic.get('risk_usd', 0):.0f}USD" if last_trade_logic else "(首笔交易)"}

================== 市场数据 ==================
{''.join(market_summary)}

================== 你的决策任务 ==================

【决策步骤】
1. 识别20分钟趋势（多头/空头/无方向）- 检查EMA关系和结构突破
2. 在5分钟级别找结构突破或回测点 - 等待最佳进场机会
3. 识别止损点 - 围绕近期高低点/关键结构位设置
4. 【以损定仓】根据以下原则自主决定风险金额：
   - 高置信度 (>80%) + 结构清晰 → 可用 1.5%-2% 风险
   - 中置信度 (60%-80%) + 结构中等 → 用 0.8%-1.5% 风险
   - 低置信度 (<60%) 或结构不清 → 用 0.5%-1% 风险，甚至 HOLD 观望
   - 月度已亏接近6%限额 → 自动降低到 0.5%-1% 范围
5. 根据止损距离 → 计算杠杆和仓位 (公式: quantity = risk_usd / (entry_price × stop_loss_distance_pct))

【硬性约束 - 必须遵守】
⛔ 单笔亏损不能超过 ${account_info['account_balance'] * 0.02:.2f}（账户2%）
⛔ 月度累积亏损不能超过 ${month_stats.get('drawdown_limit', 0):.2f}（月初资金的6%）
⛔ 结构未破，不操作
⛔ 无明显趋势，不操作

【灵活范围 - AI自主选择】
✅ 杠杆：1-20倍（根据波动率和确定性自主选择）
✅ 风险金额：0.5%-2% 之间灵活选择（根据以损定仓原则）
✅ 进场时机：完全自主（基于结构和信号）
✅ 是否操作：可以 HOLD 观望，不是必须交易

【返回格式 - JSON（不要markdown，必须返回所有币种；严格：返回单个 JSON 对象，非数组）】
为监控的所有币种都返回决策（包括 BTC, ETH, XRP, BNB, SOL, DOGE, ADA, TRX, AVAX, LINK）：

{{
    "BTC": {{
        "signal": "buy/sell/hold",
        "structure": "空转多/多转空/回测/继续/观望",
        "trend_20m": "上升/下降/无方向",
        ...详细字段...
    }},
    "ETH": {{
        "signal": "hold",
        "structure": "观望",
        "trend_20m": "无方向",
        "confidence": 0.3,
        "justification": "结构不清，继续观望"
    }},
    ... 其他币种 ...
}}

完整字段示例（当 signal 为 buy/sell 时）：
{{
    "BTC": {{
        "signal": "buy/sell/hold",
        "structure": "空转多/多转空/回测/继续/观望",
        "trend_20m": "上升/下降/无方向",
        "entry_price": 你认为合理的进场价格,
        "stop_loss": 止损价格,
        "profit_target": 止盈目标,
        "risk_usd": 你根据置信度和结构决定的风险金额(0.5%-2%),
        "risk_pct": 风险占账户百分比,
        "leverage": 建议的杠杆倍数(1-20),
        "quantity": 计算的持仓数量,
        "confidence": 0-1,
        "structure_clarity": "清晰/中等/模糊",
        "invalidation": "结构失效条件（如价格重新跌破XXX）",
        "justification": "详细分析：(1)趋势判定 (2)结构状态 (3)为什么选择这个风险金额 (4)杠杆和仓位计算"
    }}
}}

【重要提醒】
- 必须返回所有币种的决策，即使都是 HOLD
- 如果行情复杂或结构不清或置信度过低，返回 signal: "hold" + 简短说明即可
- 宁可少赚也不要乱干，这是生存的第一原则
"""

        return prompt
    
    def _parse_decision(self, response: str) -> Dict:
        """解析AI决策"""
        try:
            response = response.strip()
            if '```' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                response = response[start:end]
            
            decisions = json.loads(response)

            # 兼容返回为 [ {"BTC": {...}}, {"ETH": {...}}, ... ] 的数组格式
            if isinstance(decisions, list):
                merged: Dict[str, Dict] = {}
                for item in decisions:
                    if isinstance(item, dict):
                        for coin, entry in item.items():
                            if isinstance(entry, dict):
                                merged[coin] = entry
                decisions = merged

            # 若仍不是 dict，则抛错
            if not isinstance(decisions, dict):
                raise ValueError("AI 响应不是单个 JSON 对象")
            
            # 验证格式
            for coin, decision in list(decisions.items()):
                if 'signal' not in decision:
                    self.logger.warning(f"{coin} 决策格式不完整，移除")
                    del decisions[coin]
            
            return decisions
            
        except Exception as e:
            self.logger.error(f"解析决策失败: {e}\n响应: {response[:500]}")
            return {}
    
    # ========== 交易执行 ==========
    
    def execute_decisions(self, decisions: Dict, market_data: Dict, account_info: Dict):
        """执行交易决策"""
        self.logger.info("\n" + "="*60)
        self.logger.info("开始执行交易决策")
        self.logger.info("="*60)
        
        for coin, decision in decisions.items():
            try:
                signal = decision.get('signal', 'hold')
                
                self.logger.info(f"\n{coin}: {signal.upper()}")
                self.logger.info(f"置信度: {decision.get('confidence', 0)*100:.0f}%")
                self.logger.info(f"理由: {decision.get('justification', 'N/A')[:100]}")
                
                if signal == 'hold':
                    self._check_existing_position(coin, decision, market_data)
                elif signal == 'buy':
                    self._execute_buy(coin, decision, market_data, account_info)
                elif signal == 'sell':
                    self._execute_sell(coin, decision, market_data)
                
                time.sleep(0.2)
                
            except Exception as e:
                self.logger.error(f"执行 {coin} 决策失败: {e}")
    
    def _execute_buy(self, coin: str, decision: Dict, market_data: Dict, account_info: Dict):
        """执行买入（OKX 模拟盘）"""
        # 根据交易所类型转换符号
        symbol = self._convert_symbol(f"{coin}/USDT")

        if symbol in self.positions:
            self.logger.info(f"已持有 {coin}，跳过")
            return

        try:
            current_price = market_data[coin]['current_price']
            leverage = decision.get('leverage', 3)
            quantity = decision.get('quantity', 0)
            risk_usd = decision.get('risk_usd', 0)

            if quantity <= 0:
                self.logger.warning(f"{coin} 数量无效: {quantity}")
                return

            # 【硬限制检查 1】单笔风险不能超过账户 2%
            max_risk_per_trade = account_info['account_balance'] * 0.02
            if risk_usd > max_risk_per_trade:
                self.logger.warning(f"⛔ {coin} 风险 ${risk_usd:.2f} 超过单笔限制 ${max_risk_per_trade:.2f}，拒绝执行")
                return

            # 【硬限制检查 2】月度累积亏损 + 本笔风险 不能超过月度限额
            month_stats = self.risk_manager.get_month_stats()
            current_month_loss = month_stats.get('initial_balance', account_info['account_balance']) - account_info['account_balance']
            remaining_loss_budget = month_stats.get('drawdown_limit', account_info['account_balance'] * 0.94) - account_info['account_balance'] + current_month_loss

            if risk_usd > remaining_loss_budget:
                self.logger.warning(f"⛔ {coin} 风险 ${risk_usd:.2f} 超过月度剩余预算 ${remaining_loss_budget:.2f}，拒绝执行")
                return

            # 资金与杠杆（合约：保证金 = 名义价值 / 杠杆）
            notional_value = current_price * quantity
            margin_required = notional_value / max(leverage, 1)
            if margin_required > account_info['available_cash'] * 0.98:
                self.logger.warning(f"{coin} 保证金不足: 需要${margin_required:.2f}，可用${account_info['available_cash']:.2f}")
                return

            # 设置杠杆与逐仓
            try:
                if self.exchange_type == 'okx':
                    self.exchange.set_leverage(leverage, symbol, params={'marginMode': 'isolated', 'posSide': 'long'})
                else:
                    self.exchange.set_leverage(leverage, symbol)
                    self.exchange.set_margin_type('isolated', symbol)
            except Exception as e:
                self.logger.warning(f"设置杠杆或保证金模式失败: {e}")

            # 下市价单
            params = {}
            if self.exchange_type == 'okx':
                params = {'tdMode': 'isolated', 'posSide': 'long'}
            order = self.exchange.create_market_buy_order(symbol, quantity, params=params)
            
            self.logger.info(f"✅ 买入成功: {quantity} {coin} @ ${current_price:.2f}")
            
            # 记录持仓
            self.positions[symbol] = {
                'coin': coin,
                'side': 'long',
                'quantity': quantity,
                'entry_price': current_price,
                'leverage': leverage,
                'risk_usd': decision.get('risk_usd', 0),
                'confidence': decision.get('confidence', 0.65),
                'exit_plan': {
                    'profit_target': decision.get('profit_target'),
                    'stop_loss': decision.get('stop_loss'),
                    'invalidation_condition': decision.get('invalidation_condition')
                },
                'entry_time': datetime.now(),
                'entry_order_id': order['id'],
            }

            # 【关键】记录交易到风险管理器（保存交易历史和逻辑）
            self.risk_manager.record_trade({
                'timestamp': datetime.now().isoformat(),
                'coin': coin,
                'signal': 'buy',
                'entry_price': current_price,
                'quantity': quantity,
                'leverage': leverage,
                'stop_loss': decision.get('stop_loss'),
                'profit_target': decision.get('profit_target'),
                'entry_logic': decision.get('justification', ''),
                'structure': decision.get('structure', 'N/A'),
                'confidence': decision.get('confidence', 0.65),
                'risk_usd': decision.get('risk_usd', 0)
            })

            # 服务器端止损/止盈（若提供）
            self._set_stop_orders(symbol, decision, quantity)
            
        except Exception as e:
            self.logger.error(f"买入 {coin} 失败: {e}")
    
    def _execute_sell(self, coin: str, decision: Dict, market_data: Dict):
        """执行卖出/平仓（OKX 模拟盘）"""
        symbol = self._convert_symbol(f"{coin}/USDT")

        if symbol not in self.positions:
            self.logger.info(f"未持有 {coin}，无需卖出")
            return

        try:
            position = self.positions[symbol]
            current_price = market_data[coin]['current_price']

            # 平仓（reduceOnly）
            params = {'reduceOnly': True}
            if self.exchange_type == 'okx':
                params.update({'tdMode': 'isolated', 'posSide': 'long'})
            order = self.exchange.create_market_sell_order(symbol, position['quantity'], params=params)
            
            # 计算盈亏
            pnl = (current_price - position['entry_price']) * position['quantity']
            pnl_pct = (current_price / position['entry_price'] - 1) * 100 * position['leverage']
            
            self.logger.info(f"✅ 卖出成功: {position['quantity']} {coin} @ ${current_price:.2f}")
            self.logger.info(f"   盈亏: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            
            # 记录交易历史
            self.trade_history.append({
                'coin': coin,
                'side': 'close_long',
                'quantity': position['quantity'],
                'entry_price': position['entry_price'],
                'exit_price': current_price,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'hold_hours': (datetime.now() - position['entry_time']).total_seconds() / 3600,
                'reason': decision.get('justification', ''),
                'timestamp': datetime.now()
            })
            
            # 取消服务器端止损/止盈单
            self._cancel_stop_orders(symbol)
            
            # 删除持仓
            del self.positions[symbol]
            
        except Exception as e:
            self.logger.error(f"卖出 {coin} 失败: {e}")
    
    def _check_existing_position(self, coin: str, decision: Dict, market_data: Dict):
        """检查现有持仓"""
        symbol = self._convert_symbol(f"{coin}/USDT")

        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        current_price = market_data[coin]['current_price']

        # 检查止损
        if position['exit_plan'].get('stop_loss'):
            if current_price <= position['exit_plan']['stop_loss']:
                self.logger.warning(f"⚠️ {coin} 触发止损!")
                self._execute_sell(coin, {'justification': '触发止损'}, market_data)
                return

        # 检查止盈
        if position['exit_plan'].get('profit_target'):
            if current_price >= position['exit_plan']['profit_target']:
                self.logger.info(f"🎯 {coin} 触发止盈!")
                self._execute_sell(coin, {'justification': '触发止盈'}, market_data)
                return
    
    def _set_stop_orders(self, symbol: str, decision: Dict, quantity: float):
        """OKX 模拟盘：记录止损/止盈，由本地风控处理"""
        try:
            stop_loss = decision.get('stop_loss')
            profit_target = decision.get('profit_target')
            if stop_loss or profit_target:
                self.logger.info("   已记录止损/止盈，OKX 模拟盘跳过服务器端委托")
        except Exception as e:
            self.logger.warning(f"设置止损止盈失败: {e}")

    def _cancel_stop_orders(self, symbol: str):
        """取消该合约下所有未成交的条件单（通用）"""
        try:
            open_orders = self.exchange.fetch_open_orders(symbol)
            for order in open_orders:
                try:
                    self.exchange.cancel_order(order['id'], symbol)
                except Exception:
                    pass
        except Exception as e:
            self.logger.warning(f"取消订单失败: {e}")
    
    # ========== 主循环 ==========
    
    def run(self, interval_minutes: int = 5, duration_hours: int = 24):
        """运行交易系统"""
        self.logger.info("\n" + "="*70)
        self.logger.info("🚀 加密货币AI交易系统启动")
        self.logger.info("="*70)
        self.logger.info(f"AI模型: DeepSeek-V3 (火山引擎 ARK)")
        self.logger.info(f"交易所: OKX 模拟盘")
        # 从币种列表提取币种名称（OKX 格式）
        coin_names = [s.split('/')[0] if '/' in s else s.replace('USDT', '').strip() for s in self.symbols]
        self.logger.info(f"监控币种: {coin_names}")
        self.logger.info(f"检查间隔: {interval_minutes} 分钟")
        self.logger.info(f"运行时长: {duration_hours} 小时")
        self.logger.info("="*70 + "\n")

        end_time = datetime.now() + timedelta(hours=duration_hours)
        iteration = 0

        try:
            while datetime.now() < end_time:
                iteration += 1
                self.logger.info(f"\n{'='*70}")
                self.logger.info(f"第 {iteration} 轮 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.logger.info(f"{'='*70}")

                # 获取市场数据
                market_data = self.fetch_market_data()
                if not market_data:
                    self.logger.warning("数据获取失败，跳过本轮")
                    time.sleep(60)
                    continue

                # 获取账户信息
                account_info = self.get_account_info(market_data)

                # 【关键】月度初始化 - 只在第一次运行时初始化
                if not self.month_initialized:
                    is_new_month, msg = self.risk_manager.initialize_month(account_info['account_balance'])
                    self.logger.info(f"📅 {msg}")
                    self.month_initialized = True

                # 【关键】检查月度硬止损
                should_stop, stop_msg = self.risk_manager.check_monthly_stop(account_info['account_balance'])
                self.logger.info(stop_msg)
                if should_stop:
                    self.logger.error("⛔ 触发月度硬止损，系统停止！")
                    break

                # 打印状态
                self._print_status(account_info)
                
                # AI决策
                decisions = self.get_ai_decision(market_data, account_info)
                
                # 执行交易
                if decisions:
                    self.execute_decisions(decisions, market_data, account_info)
                
                # 保存检查点
                if iteration % 12 == 0:
                    self._save_checkpoint()
                
                # 等待
                self.logger.info(f"\n⏳ 等待 {interval_minutes} 分钟...\n")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info("\n⚠️ 用户中断")
        except Exception as e:
            self.logger.error(f"系统错误: {e}", exc_info=True)
        finally:
            self._generate_report()
    
    def _print_status(self, account_info: Dict):
        """打印状态"""
        self.logger.info("\n📊 账户状态")
        self.logger.info("-" * 60)
        self.logger.info(f"余额: ${account_info['account_balance']:.2f}")
        self.logger.info(f"可用: ${account_info['available_cash']:.2f}")
        self.logger.info(f"回报率: {account_info['total_return_pct']:+.2f}%")
        
        if account_info['positions']:
            self.logger.info(f"\n持仓 ({len(account_info['positions'])} 个):")
            for pos in account_info['positions']:
                emoji = "🟢" if pos['unrealized_pnl'] > 0 else "🔴"
                self.logger.info(
                    f"{emoji} {pos['symbol']}: ${pos['current_price']:.2f} | "
                    f"盈亏: ${pos['unrealized_pnl']:+.2f} | {pos['leverage']}x"
                )
    
    def _save_checkpoint(self):
        """保存检查点"""
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'positions': len(self.positions),
            'trades': len(self.trade_history),
        }
        with open('outputs/checkpoint.json', 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False, default=str)
        self.logger.info("💾 检查点已保存")
    
    def _generate_report(self):
        """生成报告"""
        self.logger.info("\n" + "="*70)
        self.logger.info("📈 最终报告")
        self.logger.info("="*70)
        
        if self.trade_history:
            df = pd.DataFrame(self.trade_history)
            
            total_trades = len(df)
            winning = len(df[df['pnl'] > 0])
            win_rate = winning / total_trades * 100
            total_pnl = df['pnl'].sum()
            
            self.logger.info(f"交易次数: {total_trades}")
            self.logger.info(f"胜率: {win_rate:.1f}% ({winning}胜/{total_trades-winning}负)")
            self.logger.info(f"总盈亏: ${total_pnl:+.2f}")
            
            df.to_csv('outputs/trade_history.csv', index=False, encoding='utf-8-sig')
            self.logger.info("\n📁 交易历史已保存到 outputs/trade_history.csv")
        else:
            self.logger.info("无交易记录")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     加密货币AI交易系统                                        ║
║     AI: DeepSeek-V3 (火山引擎 ARK)                          ║
║     交易所: OKX 模拟盘                                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        trader = CryptoAITrader()
        trader.run(interval_minutes=5, duration_hours=24)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n请检查:")
        print("1. config.json 是否配置正确")
        print("2. API密钥是否有效")
        print("3. 网络连接是否正常")


if __name__ == "__main__":
    main()
