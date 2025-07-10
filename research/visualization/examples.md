# Visualizing Quantitative Strategy Performance

Visualizing the results of a backtest is just as important as the numerical metrics. A few key charts can provide immediate, intuitive insights into a strategy's performance and risk characteristics.

This document provides Python code snippets for generating the most essential plots using `matplotlib` and `pandas`.

## 1. The Equity Curve

The equity curve is the most fundamental chart. It plots the cumulative return or total value of your portfolio over time. It should (ideally) be a smooth, upward-sloping line.

### How to Plot It

First, you need a `pandas` Series of daily (or any frequency) returns for your strategy.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Generate Sample Data ---
# In a real scenario, this would be the output of your backtest.
days = 365 * 3 # 3 years of daily data
np.random.seed(42)
# Simulate returns: mean of 0.05% daily, std dev of 1%
daily_returns = np.random.normal(0.0005, 0.01, days)
# Add a couple of larger shocks
daily_returns[50] = -0.10
daily_returns[200] = 0.08

# Create a DatetimeIndex
index = pd.date_range('2021-01-01', periods=days, freq='D')
returns_series = pd.Series(daily_returns, index=index, name="Daily Returns")


# --- 2. Calculate the Equity Curve (Cumulative Returns) ---
# Start with an initial capital of 1
initial_capital = 1
# Calculate the cumulative product of daily returns (1 + r)
cumulative_returns = (1 + returns_series).cumprod()
equity_curve = initial_capital * cumulative_returns


# --- 3. Plot the Equity Curve ---
plt.style.use('seaborn-v0_8-darkgrid') # Use a nice style
fig, ax = plt.subplots(figsize=(12, 7))

ax.plot(equity_curve.index, equity_curve, color='blue', linewidth=2)

# Formatting
ax.set_title('Strategy Equity Curve', fontsize=16)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Portfolio Value', fontsize=12)
ax.grid(True)
plt.show()
```

This will produce a clear line chart showing the growth of $1 invested in the strategy.

## 2. The Drawdown Plot

A drawdown is the percentage decline from a previous peak in the portfolio's value. Visualizing drawdowns is crucial for understanding the risk and the "pain" a strategy can inflict.

### How to Calculate and Plot It

We'll use the equity curve we calculated above to find the drawdowns.

```python
# --- 1. Calculate Peaks ---
# A 'peak' is the highest value the equity curve has reached to date.
previous_peaks = equity_curve.cummax()

# --- 2. Calculate Drawdown ---
# The drawdown is the percentage drop from the previous peak.
drawdown = (equity_curve - previous_peaks) / previous_peaks

# --- 3. Plot the Drawdown ---
fig, ax = plt.subplots(figsize=(12, 7))

# Plot the drawdown series
ax.plot(drawdown.index, drawdown * 100, color='red', linewidth=2)
# Fill the area under the drawdown curve
ax.fill_between(drawdown.index, drawdown * 100, 0, color='red', alpha=0.3)

# Formatting
ax.set_title('Strategy Drawdowns', fontsize=16)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Drawdown (%)', fontsize=12)
ax.grid(True)
# Set y-axis to show percentages
ax.yaxis.set_major_formatter(plt.FuncFormatter('{:.0f}%'.format))
plt.show()
```
This plot immediately shows you the periods where the strategy was losing money and the magnitude of those losses.

## Combining the Plots

For a comprehensive view, you can plot both on the same figure using subplots.

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Plot Equity Curve on the first subplot
ax1.plot(equity_curve.index, equity_curve, color='blue', linewidth=2)
ax1.set_title('Equity Curve', fontsize=16)
ax1.set_ylabel('Portfolio Value', fontsize=12)
ax1.grid(True)

# Plot Drawdown on the second subplot
ax2.plot(drawdown.index, drawdown * 100, color='red', linewidth=2)
ax2.fill_between(drawdown.index, drawdown * 100, 0, color='red', alpha=0.3)
ax2.set_title('Drawdown', fontsize=16)
ax2.set_ylabel('Drawdown (%)', fontsize=12)
ax2.set_xlabel('Date', fontsize=12)
ax2.grid(True)
ax2.yaxis.set_major_formatter(plt.FuncFormatter('{:.0f}%'.format))

plt.suptitle('Strategy Performance Overview', fontsize=20, y=0.93)
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.show()
```
This combined view gives a powerful, at-a-glance summary of a strategy's historical performance and risk. 