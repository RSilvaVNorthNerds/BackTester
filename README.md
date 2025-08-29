# BackTester: A Professional Quantitative Trading Backtesting Framework

A robust, production-ready backtesting engine designed for quantitative trading strategies. Built with clean architecture principles, this framework provides accurate simulation of trading strategies with realistic market conditions including fees, slippage, and proper signal alignment.

## 🏗️ Architecture Overview

The framework is built with a modular, layered architecture that separates concerns and promotes maintainability:

```
src/
├── data.py          # Data fetching and caching layer
├── indicators.py    # Technical indicators (SMA, Z-score)
├── strategies.py    # Signal generation logic
├── engine.py        # Core backtesting engine
├── metrics.py       # Performance analytics
└── plot.py          # Visualization utilities
```

### Why This Architecture?

**Separation of Concerns**: Each module has a single responsibility, making the code easier to test, debug, and extend.

**Data Flow**: The architecture follows a clear data flow: Data → Indicators → Strategies → Engine → Metrics → Visualization.

**Modularity**: You can easily swap out components (e.g., different data sources, new indicators, alternative strategies) without affecting other parts of the system.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd BackTester

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from src.data import get_price_data
from src.strategies import signal_sma_crossover, align_next_bar
from src.engine import run_backtest
from src.metrics import summarize_backtest_performance

# Get data
df = get_price_data(["AAPL"], "2022-01-01", "2022-12-31")
close = df[("AAPL", "Close")]

# Generate signals
signals = signal_sma_crossover(close, fast=20, slow=50)
signals = align_next_bar(signals)  # Critical: prevents look-ahead bias

# Run backtest
results = run_backtest(close, signals, initial_cash=100000, fee_bps=1)

# Analyze performance
summary = summarize_backtest_performance(results["equity"])
print(f"Total Return: {summary['total_return']:.2%}")
print(f"Sharpe Ratio: {summary['sharpe']:.2f}")
```

## 📊 Core Components

### 1. Data Layer (`src/data.py`)

**Purpose**: Handles data fetching, caching, and preprocessing.

**Key Features**:
- **Yahoo Finance Integration**: Uses `yfinance` for reliable market data
- **Smart Caching**: Local CSV caching to reduce API calls and improve performance
- **Data Cleaning**: Automatic index normalization and duplicate handling
- **Multi-ticker Support**: Efficient batch processing of multiple symbols

**Why This Approach?**
- **Reliability**: Yahoo Finance provides consistent, high-quality data
- **Performance**: Local caching eliminates repeated downloads
- **Flexibility**: Multi-level indexing allows easy access to different price types

```python
# Fetch multiple tickers efficiently
df = get_price_data(["AAPL", "MSFT", "GOOGL"], "2022-01-01", "2022-12-31")

# Access data with intuitive indexing
aapl_close = df[("AAPL", "Close")]
msft_open = df[("MSFT", "Open")]
```

### 2. Technical Indicators (`src/indicators.py`)

**Purpose**: Provides building blocks for strategy development.

**Available Indicators**:
- **Simple Moving Average (SMA)**: Trend-following indicator
- **Z-Score**: Mean reversion indicator for statistical arbitrage

**Why These Indicators?**
- **SMA**: Most fundamental trend indicator, widely used and understood
- **Z-Score**: Statistically sound mean reversion signal with clear entry/exit thresholds

```python
from src.indicators import simple_moving_average, zscore

# Calculate 20-day SMA
sma_20 = simple_moving_average(close, 20)

# Calculate Z-score for mean reversion
z_score = zscore(close, lookback=20)
```

### 3. Strategy Layer (`src/strategies.py`)

**Purpose**: Converts technical indicators into actionable trading signals.

**Available Strategies**:
- **SMA Crossover**: Classic trend-following strategy
- **Mean Reversion**: Statistical arbitrage based on Z-score extremes

**Signal Alignment**: The `align_next_bar()` function is **critical** - it prevents look-ahead bias by ensuring signals are executed on the next available bar.

**Why This Design?**
- **Realistic Execution**: Simulates actual trading conditions where signals are acted upon after market close
- **Bias Prevention**: Eliminates the most common backtesting mistake (using future information)
- **Strategy Independence**: Each strategy is a pure function that can be easily tested and modified

```python
from src.strategies import signal_sma_crossover, signal_mean_reversion, align_next_bar

# Generate raw signals
sma_signals = signal_sma_crossover(close, fast=20, slow=50)
mr_signals = signal_mean_reversion(close, lookback=20, entry=1.0, exit=0.2)

# Align to prevent look-ahead bias
sma_signals = align_next_bar(sma_signals)
mr_signals = align_next_bar(mr_signals)
```

### 4. Backtesting Engine (`src/engine.py`)

**Purpose**: Core simulation engine that executes strategies and tracks performance.

**Key Features**:
- **Realistic Execution**: Next-bar execution with configurable slippage
- **Fee Modeling**: Basis point-based transaction costs
- **Position Tracking**: Comprehensive trade and portfolio state monitoring
- **Cash Management**: Proper handling of available capital and position sizing

**Why This Implementation?**
- **Accuracy**: Simulates real-world trading constraints and costs
- **Transparency**: Full visibility into every trade execution
- **Flexibility**: Configurable parameters for different market conditions

```python
from src.engine import run_backtest

# Run backtest with realistic parameters
results = run_backtest(
    close=close,
    signal=signals,
    initial_cash=100000,
    fee_bps=1.0,        # 1 basis point = 0.01%
    slippage_bps=0.5     # 0.5 basis points slippage
)

# Results include comprehensive tracking
print(results.columns)
# ['position', 'shares', 'trade_shares', 'exec_px', 'cash', 'holdings', 'equity', 'fees']
```

### 5. Performance Analytics (`src/metrics.py`)

**Purpose**: Comprehensive performance measurement and risk analysis.

**Available Metrics**:
- **Returns**: Total return, CAGR, daily returns
- **Risk**: Volatility, maximum drawdown, drawdown duration
- **Risk-Adjusted Returns**: Sharpe ratio, Sortino ratio
- **Trade Analysis**: Win rate, profit factor, average win/loss

**Why These Metrics?**
- **Industry Standard**: Metrics that professional investors and risk managers use
- **Comprehensive**: Covers both return and risk aspects of performance
- **Actionable**: Provides insights for strategy improvement

```python
from src.metrics import summarize_backtest_performance, extract_trades, trade_stats

# Get comprehensive performance summary
summary = summarize_backtest_performance(results["equity"])

# Analyze individual trades
trades = extract_trades(results)
trade_analysis = trade_stats(trades)

print(f"Sharpe Ratio: {summary['sharpe']:.2f}")
print(f"Max Drawdown: {summary['max_drawdown']:.2%}")
print(f"Win Rate: {trade_analysis['win_rate']:.1%}")
```

### 6. Visualization (`src/plot.py`)

**Purpose**: Clear visual representation of strategy performance and signals.

**Available Plots**:
- **Equity Curves**: Portfolio value over time
- **Drawdown Analysis**: Risk visualization
- **Signal Visualization**: Entry/exit points on price charts

## 🔬 Advanced Examples

### Multi-Strategy Comparison

```python
import pandas as pd
from src.strategies import *
from src.engine import run_backtest
from src.metrics import summarize_backtest_performance

# Test multiple strategies on same data
strategies = {
    "SMA 20/50": lambda x: align_next_bar(signal_sma_crossover(x, 20, 50)),
    "SMA 10/30": lambda x: align_next_bar(signal_sma_crossover(x, 10, 30)),
    "Mean Reversion": lambda x: align_next_bar(signal_mean_reversion(x, 20, 1.0, 0.2))
}

# Compare performance
results = {}
for name, strategy in strategies.items():
    signals = strategy(close)
    bt = run_backtest(close, signals, initial_cash=100000, fee_bps=1)
    results[name] = summarize_backtest_performance(bt["equity"])

# Create comparison DataFrame
comparison = pd.DataFrame(results).T
print(comparison[["total_return", "sharpe", "max_drawdown"]])
```

### Portfolio Backtesting

```python
# Test strategy across multiple assets
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
df = get_price_data(tickers, "2022-01-01", "2022-12-31")

portfolio_results = []
for ticker in tickers:
    close = df[(ticker, "Close")]
    signals = align_next_bar(signal_sma_crossover(close, 20, 50))
    bt = run_backtest(close, signals, initial_cash=100000, fee_bps=1)
    
    summary = summarize_backtest_performance(bt["equity"])
    summary["ticker"] = ticker
    portfolio_results.append(summary)

portfolio_df = pd.DataFrame(portfolio_results)
print(portfolio_df.set_index("ticker"))
```

### Parameter Optimization

```python
import itertools

# Grid search for optimal parameters
fast_periods = [5, 10, 15, 20]
slow_periods = [30, 40, 50, 60]
results = []

for fast, slow in itertools.product(fast_periods, slow_periods):
    if fast >= slow:
        continue
        
    signals = align_next_bar(signal_sma_crossover(close, fast, slow))
    bt = run_backtest(close, signals, initial_cash=100000, fee_bps=1)
    summary = summarize_backtest_performance(bt["equity"])
    
    summary.update({"fast": fast, "slow": slow})
    results.append(summary)

# Find best parameters
results_df = pd.DataFrame(results)
best_params = results_df.loc[results_df["sharpe"].idxmax()]
print(f"Best parameters: Fast={best_params['fast']}, Slow={best_params['slow']}")
print(f"Best Sharpe: {best_params['sharpe']:.2f}")
```

## 🎯 Design Philosophy

### 1. Realistic Simulation

**Why**: Backtesting must accurately reflect real trading conditions to be useful.

**How**: 
- Next-bar execution prevents look-ahead bias
- Transaction costs and slippage modeling
- Proper signal alignment and timing

### 2. Modular Architecture

**Why**: Enables easy testing, modification, and extension of components.

**How**:
- Clear separation of concerns
- Pure functions with minimal side effects
- Standardized interfaces between modules

### 3. Performance Focus

**Why**: Quantitative analysis often involves large datasets and multiple iterations.

**How**:
- Efficient pandas operations
- Local data caching
- Vectorized calculations where possible

### 4. Professional Standards

**Why**: Results must be credible for investment decisions.

**How**:
- Industry-standard performance metrics
- Proper risk measurement
- Transparent trade execution tracking

## 🧪 Testing

The project includes comprehensive tests to ensure reliability:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_engine.py

# Run with coverage
pytest --cov=src tests/
```

## 📈 Future Enhancements

- **Risk Management**: Position sizing, stop-losses, portfolio-level risk controls
- **Advanced Execution**: Market impact modeling, VWAP execution
- **Machine Learning**: Integration with ML-based signal generation
- **Real-time Trading**: Live trading capabilities with broker APIs
- **Performance Attribution**: Factor analysis and risk decomposition

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style and architecture
- New features include appropriate tests
- Documentation is updated for new functionality

## 📄 License

Copyright (c) 2025 Rafael Silva-Vergara

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- NonCommercial — You may not use the material for commercial purposes.
- No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

Full license text: https://creativecommons.org/licenses/by-nc/4.0/

---

**Built with ❤️ for quantitative finance professionals who demand accuracy, transparency, and reliability in their backtesting frameworks.**
