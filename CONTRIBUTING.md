# Contributing to Crypto AI Trading Bot

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We're building a community focused on learning and improvement.

## Ways to Contribute

### 1. Report Bugs
- Check if the bug has already been reported in Issues
- If not, create a new issue with:
  - Clear title describing the bug
  - Detailed steps to reproduce
  - Expected vs actual behavior
  - Your environment (OS, Python version, etc.)
  - Relevant logs from `outputs/trading_*.log`

### 2. Suggest Features
- Describe the feature and why it would be useful
- Provide use cases and examples
- Consider if it aligns with the project's goals
- Check if something similar exists

### 3. Submit Code Changes

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-ai-trading-bot.git
cd crypto-ai-trading-bot

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pylint flake8 black pytest
```

#### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes:
   - Follow PEP 8 style guidelines
   - Add docstrings to functions
   - Add type hints where applicable
   - Keep commits atomic and meaningful

3. Test your changes:
   ```bash
   python3 -m pytest tests/
   pylint crypto_trading_bot_enhanced.py
   flake8 crypto_trading_bot_enhanced.py
   ```

4. Commit with clear messages:
   ```bash
   git commit -m "feat: add new feature description"
   # or
   git commit -m "fix: correct bug in trading logic"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request with:
   - Clear title and description
   - Reference to any related issues
   - Explanation of changes
   - Testing notes

### 4. Improve Documentation
- Fix typos and grammar
- Clarify confusing sections
- Add examples
- Translate documentation

## Development Guidelines

### Code Style

We follow [PEP 8](https://pep8.org/) with some preferences:

```python
# ✅ Good
def fetch_market_data(self) -> Dict[str, Any]:
    """Fetch OHLCV data for all monitored symbols.

    Returns:
        Dict containing market data for each symbol
    """
    market_data = {}
    for symbol in self.symbols:
        try:
            data = self.exchange.fetch_ohlcv(symbol, '1m', limit=100)
            # Process data
        except Exception as e:
            self.logger.error(f"Failed to fetch {symbol}: {e}")
    return market_data

# ❌ Avoid
def fetch_market_data(self):
    # fetch data
    data={}
    for s in self.symbols:
        d = self.exchange.fetch_ohlcv(s, '1m', limit=100)
    return data
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Build, dependencies, etc.

Examples:
```
feat(ai): implement new decision logic using sentiment analysis
fix(risk): correct monthly drawdown calculation
docs: add architecture documentation
test: add unit tests for RiskManager
```

### Testing

- Add tests for new features
- Ensure existing tests pass
- Aim for >80% code coverage

```python
# tests/test_risk_manager.py
import unittest
from risk_manager import MonthlyRiskManager

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        self.rm = MonthlyRiskManager('test_memory.json')

    def test_single_trade_limit(self):
        """Test per-trade risk limit"""
        max_risk = self.rm.get_max_risk_per_trade(10000)
        self.assertEqual(max_risk, 200)  # 2% of 10000
```

## Areas Where We Need Help

1. **Tests**: Adding comprehensive test coverage
2. **Documentation**: Improving clarity and adding examples
3. **Performance**: Optimizing data fetching and calculations
4. **Features**: Support for additional exchanges
5. **UI/Dashboard**: Building a web interface for monitoring
6. **Backtest Engine**: Historical performance analysis

## Questions or Need Help?

- Check existing issues and discussions
- Create a new discussion for questions
- Email: (your contact info)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making this project better! 🙏**
