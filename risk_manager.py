"""
月度风险管理系统
- 初始资金记录
- 月度回撤底线（-6%）
- 交易历史记录
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class MonthlyRiskManager:
    """月度风险管理"""

    def __init__(self, data_file: str = 'trading_memory.json'):
        self.data_file = Path(data_file)
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """加载交易数据"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            'month_start_date': None,
            'month_initial_balance': None,
            'month_drawdown_limit': None,
            'all_trades': [],
            'current_positions': {},
            'last_trade_logic': None
        }

    def _save_data(self):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def initialize_month(self, current_balance: float):
        """
        初始化月度（在月初或第一笔交易时调用）

        Args:
            current_balance: 当前账户余额
        """
        current_date = datetime.now()
        month_start = current_date.strftime('%Y-%m')

        # 检查是否需要重置月度数据
        if self.data['month_start_date'] != month_start:
            self.data['month_start_date'] = month_start
            self.data['month_initial_balance'] = current_balance
            # 固定月度回撤底线为 6%
            self.data['month_drawdown_limit'] = current_balance * 0.94
            self.data['all_trades'] = []
            self._save_data()

            return True, f"新月度初始化: {month_start}, 初始资金: ${current_balance:.2f}, 回撤底线: ${self.data['month_drawdown_limit']:.2f}"

        return False, "已在当月数据中"

    def check_monthly_stop(self, current_balance: float) -> tuple:
        """
        检查是否触发月度硬止损

        Args:
            current_balance: 当前账户余额

        Returns:
            (触发?, 消息)
        """
        if self.data['month_drawdown_limit'] is None:
            return False, "未初始化月度数据"

        if current_balance <= self.data['month_drawdown_limit']:
            return True, f"⛔ 触发月度硬止损！当前: ${current_balance:.2f}, 限额: ${self.data['month_drawdown_limit']:.2f}"

        remaining = current_balance - self.data['month_drawdown_limit']
        remaining_pct = (remaining / self.data['month_initial_balance']) * 100

        return False, f"✅ 月度风险正常，还可亏损: ${remaining:.2f} ({remaining_pct:.2f}%)"

    def record_trade(self, trade_info: Dict):
        """
        记录一笔交易

        Args:
            trade_info: {
                'timestamp': '2025-10-30 01:05:00',
                'coin': 'BTC',
                'signal': 'buy/sell/hold',
                'entry_price': 95000,
                'quantity': 1.5,
                'leverage': 5,
                'stop_loss': 92000,
                'profit_target': 100000,
                'entry_logic': '价格行为描述...',
                'structure': '多转空/空转多/...',
                'confidence': 0.8,
                ...
            }
        """
        trade_record = {
            'id': len(self.data['all_trades']) + 1,
            'timestamp': trade_info.get('timestamp', datetime.now().isoformat()),
            'coin': trade_info.get('coin'),
            'signal': trade_info.get('signal'),
            'entry_price': trade_info.get('entry_price'),
            'quantity': trade_info.get('quantity'),
            'leverage': trade_info.get('leverage'),
            'stop_loss': trade_info.get('stop_loss'),
            'profit_target': trade_info.get('profit_target'),
            'entry_logic': trade_info.get('entry_logic'),
            'structure': trade_info.get('structure'),
            'confidence': trade_info.get('confidence'),
            'status': 'open'  # open/closed
        }

        self.data['all_trades'].append(trade_record)
        self.data['last_trade_logic'] = trade_record
        self._save_data()

        return trade_record

    def close_trade(self, trade_id: int, exit_price: float, exit_logic: str):
        """
        平仓一笔交易

        Args:
            trade_id: 交易ID
            exit_price: 平仓价格
            exit_logic: 平仓理由
        """
        for trade in self.data['all_trades']:
            if trade['id'] == trade_id:
                trade['status'] = 'closed'
                trade['exit_price'] = exit_price
                trade['exit_logic'] = exit_logic

                # 计算盈亏
                if trade['signal'] == 'buy':
                    pnl = (exit_price - trade['entry_price']) * trade['quantity'] * trade['leverage']
                else:
                    pnl = (trade['entry_price'] - exit_price) * trade['quantity'] * trade['leverage']

                trade['pnl'] = pnl
                trade['pnl_pct'] = (pnl / (trade['entry_price'] * trade['quantity'])) * 100 if trade['quantity'] > 0 else 0

                self._save_data()
                return trade

        return None

    def get_all_trades(self) -> List[Dict]:
        """获取所有交易"""
        return self.data['all_trades']

    def get_last_trade_logic(self) -> Dict:
        """获取上一笔交易的逻辑"""
        return self.data.get('last_trade_logic', {})

    def get_open_trades(self) -> List[Dict]:
        """获取开仓中的交易"""
        return [t for t in self.data['all_trades'] if t['status'] == 'open']

    def get_month_stats(self) -> Dict:
        """获取月度统计"""
        trades = self.data['all_trades']
        closed_trades = [t for t in trades if t['status'] == 'closed' and 'pnl' in t]

        total_pnl = sum(t.get('pnl', 0) for t in closed_trades)
        win_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        lose_trades = [t for t in closed_trades if t.get('pnl', 0) < 0]

        return {
            'month': self.data['month_start_date'],
            'initial_balance': self.data['month_initial_balance'],
            'drawdown_limit': self.data['month_drawdown_limit'],
            'total_trades': len(trades),
            'closed_trades': len(closed_trades),
            'open_trades': len([t for t in trades if t['status'] == 'open']),
            'total_pnl': total_pnl,
            'win_rate': len(win_trades) / len(closed_trades) * 100 if closed_trades else 0,
            'win_count': len(win_trades),
            'lose_count': len(lose_trades)
        }
