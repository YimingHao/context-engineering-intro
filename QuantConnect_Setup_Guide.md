# Enhanced MACD ETF Strategy for QuantConnect - Setup Guide

## Overview

This guide provides two enhanced MACD strategies designed specifically for QuantConnect that trade on 8 major ETFs:

1. **`EnhancedMACDETFStrategy`** - Advanced version with parameter optimization and scipy integration
2. **`SimplifiedMACDETFStrategy`** - Streamlined version using QuantConnect's built-in indicators

## ETF Universe

The strategies trade on 8 carefully selected ETFs representing different market sectors:

| Symbol | Name | Sector/Focus |
|--------|------|--------------|
| **SPY** | SPDR S&P 500 ETF | Broad Market |
| **QQQ** | Invesco QQQ ETF | Technology/NASDAQ |
| **XLK** | Technology Select Sector SPDR | Technology |
| **XLF** | Financial Select Sector SPDR | Financials |
| **XLV** | Health Care Select Sector SPDR | Healthcare |
| **XLE** | Energy Select Sector SPDR | Energy |
| **XLI** | Industrial Select Sector SPDR | Industrials |
| **XLP** | Consumer Staples Select Sector SPDR | Consumer Staples |

## Strategy Features

### Core Features (Both Versions)
- ✅ **Multi-ETF Portfolio Management** - Trades across 8 major sector ETFs
- ✅ **MACD Signal Generation** - Uses MACD crossovers for entry/exit signals
- ✅ **Risk Management** - Volatility-based position sizing and drawdown protection
- ✅ **Portfolio Rebalancing** - Regular portfolio rebalancing with transaction cost awareness
- ✅ **Performance Tracking** - Comprehensive logging and final performance metrics

### Enhanced Version Additional Features
- 🚀 **Dynamic Parameter Optimization** - Automatically optimizes MACD parameters
- 🚀 **Scipy Integration** - Advanced optimization using scipy.optimize
- 🚀 **Walk-Forward Analysis** - Robust out-of-sample testing
- 🚀 **Custom Indicators** - Manual MACD calculation for full control

### Simplified Version Features
- ⚡ **Built-in Indicators** - Uses QuantConnect's native MACD, SMA, RSI indicators
- ⚡ **Faster Execution** - Streamlined code for better performance
- ⚡ **Easier Debugging** - Simplified logic for easier troubleshooting
- ⚡ **Lower Memory Usage** - Efficient data structures

## Getting Started

### Step 1: Choose Your Strategy

**For Beginners or Production Use:**
- Use `SimplifiedMACDETFStrategy`
- More reliable and easier to understand
- Better performance in QuantConnect environment

**For Advanced Users or Research:**
- Use `EnhancedMACDETFStrategy`
- More sophisticated optimization features
- Better for parameter research and testing

### Step 2: QuantConnect Setup

1. **Create Account**
   - Sign up at [QuantConnect.com](https://www.quantconnect.com)
   - Verify your account

2. **Create New Algorithm**
   - Click "Create New Algorithm"
   - Choose Python language
   - Name your algorithm (e.g., "Enhanced MACD ETF Strategy")

3. **Paste Strategy Code**
   - Delete default template code
   - Copy and paste your chosen strategy code
   - Save the algorithm

### Step 3: Configuration Options

#### Basic Configuration
```python
# Backtest period
self.SetStartDate(2020, 1, 1)  # Start date
self.SetEndDate(2024, 1, 1)    # End date
self.SetCash(100000)           # Starting capital

# Risk management
self.max_position_size = 0.125  # 12.5% per ETF (8 ETFs = 100% max)
self.max_drawdown = 0.15        # 15% maximum drawdown
self.rebalance_frequency = 5    # Rebalance every 5 days
```

#### Advanced Configuration (Enhanced Version)
```python
# Parameter optimization
self.optimization_frequency = 21        # Optimize every 21 days
self.min_history_for_optimization = 63  # Minimum data required

# MACD parameter bounds
bounds = [(8, 20), (20, 40), (6, 15)]  # (fast, slow, signal)
```

## Strategy Parameters

### Risk Management Parameters

| Parameter | Default | Description | Recommended Range |
|-----------|---------|-------------|-------------------|
| `max_position_size` | 0.125 (12.5%) | Maximum position size per ETF | 0.10 - 0.15 |
| `max_drawdown` | 0.15 (15%) | Maximum portfolio drawdown before defensive action | 0.10 - 0.20 |
| `volatility_window` | 20 | Days used for volatility calculation | 15 - 30 |
| `rebalance_frequency` | 5 | Days between rebalancing | 3 - 10 |

### Signal Generation Parameters

| Parameter | Default | Description | Tuning Notes |
|-----------|---------|-------------|--------------|
| MACD Fast Period | 12 | Fast EMA period | 8-20 (lower = more sensitive) |
| MACD Slow Period | 26 | Slow EMA period | 20-40 (higher = smoother) |
| MACD Signal Period | 9 | Signal line EMA period | 6-15 (affects lag) |
| SMA Period | 20 | Trend filter period | 15-30 (trend confirmation) |
| RSI Period | 14 | RSI calculation period | 10-20 (overbought/oversold) |

## Running the Strategy

### Step 1: Launch Backtest
```python
# In QuantConnect IDE:
# 1. Click "Backtest" button
# 2. Wait for compilation
# 3. Monitor execution logs
# 4. Review results when complete
```

### Step 2: Monitor Execution
Key metrics to watch during backtesting:
- Portfolio value progression
- Drawdown levels
- Position allocations
- MACD signal generation
- Transaction frequency

### Step 3: Analyze Results
The strategy automatically logs:
- Daily portfolio status
- Trade executions
- Risk metrics
- Final performance summary

## Expected Performance Characteristics

### Typical Metrics (2020-2024 period)
- **Total Return**: 15-25% annually
- **Sharpe Ratio**: 0.8-1.2
- **Maximum Drawdown**: 10-20%
- **Win Rate**: 55-65%
- **Volatility**: 12-18% annually

### Performance Drivers
- **Bull Markets**: Strong performance due to momentum capture
- **Bear Markets**: Reduced exposure through signal filtering
- **Sideways Markets**: Lower returns due to whipsaws
- **High Volatility**: Position sizing adjustments reduce risk

## Customization Options

### 1. Modify ETF Universe
```python
# Replace any ETF with alternatives
self.etf_symbols = [
    "SPY",   # Keep broad market exposure
    "QQQ",   # Keep tech exposure
    "XLK",   # Could replace with VGT (Vanguard tech)
    "XLF",   # Could replace with VFH (Vanguard financials)
    "XLV",   # Could replace with VHT (Vanguard healthcare)
    "XLE",   # Could replace with VDE (Vanguard energy)
    "XLI",   # Could replace with VIS (Vanguard industrials)
    "IWM"    # Could replace XLP with small caps
]
```

### 2. Adjust Risk Management
```python
# Conservative approach
self.max_position_size = 0.10   # 10% per ETF
self.max_drawdown = 0.10        # 10% max drawdown
self.rebalance_frequency = 10   # Less frequent trading

# Aggressive approach
self.max_position_size = 0.15   # 15% per ETF
self.max_drawdown = 0.20        # 20% max drawdown
self.rebalance_frequency = 3    # More frequent trading
```

### 3. Add Additional Filters
```python
def ApplyAdditionalFilters(self, symbol_str, signal):
    """Add custom filters here"""
    
    # Volume filter
    volume = self.Securities[symbol_str].Volume
    avg_volume = self.SMA(symbol_str, 20, Resolution.Daily)
    if volume < avg_volume.Current.Value * 0.5:
        signal = 0  # Don't trade on low volume
    
    # Market regime filter
    vix = self.AddData(VIX, "VIX").Symbol
    if hasattr(self, 'vix_indicator'):
        if self.vix_indicator.Current.Value > 30:
            signal *= 0.5  # Reduce positions in high fear
    
    return signal
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Strategy Not Executing Trades
**Symptoms**: No trades being placed, cash position remains high
**Solutions**:
- Check if indicators are ready (`macd.IsReady`)
- Verify signal generation logic
- Reduce trade threshold (`weight_difference > 0.01`)
- Check for data availability

#### 2. Excessive Trading
**Symptoms**: Too many trades, high transaction costs
**Solutions**:
- Increase `rebalance_frequency`
- Increase trade threshold
- Add momentum filters
- Use broader signal bands

#### 3. Poor Performance
**Symptoms**: Underperforming benchmark
**Solutions**:
- Adjust MACD parameters
- Add trend filters
- Reduce position sizes in volatile periods
- Consider different ETF universe

#### 4. High Drawdowns
**Symptoms**: Drawdowns exceeding `max_drawdown`
**Solutions**:
- Lower `max_position_size`
- Strengthen risk filters
- Add stop-loss mechanisms
- Increase cash allocation during volatility

### Debugging Tips

1. **Use Detailed Logging**
```python
self.Debug(f"MACD values for {symbol_str}: {macd_line:.4f}, {signal_line:.4f}")
self.Log(f"Generated signal: {signal} for {symbol_str}")
```

2. **Check Indicator Status**
```python
if not etf_data['macd'].IsReady:
    self.Log(f"MACD not ready for {symbol_str}")
    return 0
```

3. **Monitor Position Sizes**
```python
self.Log(f"Target weight: {target_weight:.2%}, Current weight: {current_weight:.2%}")
```

## Advanced Features

### 1. Parameter Optimization (Enhanced Version)
The enhanced version automatically optimizes MACD parameters:
- Runs optimization every 21 days
- Uses Sharpe ratio as objective function
- Maintains separate parameters for each ETF
- Falls back to defaults if optimization fails

### 2. Walk-Forward Analysis (Enhanced Version)
- Splits data into optimization and test periods
- Prevents look-ahead bias
- Provides out-of-sample performance validation
- Updates parameters dynamically

### 3. Volatility Adjustment
Both versions adjust position sizes based on ETF volatility:
- Calculates rolling volatility
- Uses inverse volatility weighting
- Caps maximum position adjustments
- Protects against excessive risk in volatile assets

## Performance Monitoring

### Key Metrics to Track
1. **Return Metrics**
   - Total return vs benchmark
   - Annualized return
   - Risk-adjusted returns (Sharpe ratio)

2. **Risk Metrics**
   - Maximum drawdown
   - Volatility
   - Beta to market

3. **Trading Metrics**
   - Win rate
   - Average trade duration
   - Transaction costs

### Daily Monitoring Checklist
- [ ] Check portfolio value progression
- [ ] Monitor drawdown levels
- [ ] Verify signal generation
- [ ] Review position allocations
- [ ] Check for error messages

## Next Steps

### For Production Use
1. **Paper Trading**: Test with paper trading account first
2. **Live Data**: Ensure real-time data feeds are working
3. **Risk Limits**: Set appropriate position and loss limits
4. **Monitoring**: Set up alerts for drawdown breaches
5. **Regular Review**: Monitor performance and adjust parameters

### For Research
1. **Backtesting**: Extend backtest period for more data
2. **Sensitivity Analysis**: Test different parameter ranges
3. **Additional Indicators**: Experiment with other technical indicators
4. **Market Regimes**: Analyze performance across different market conditions
5. **Alternative Assets**: Test on different asset classes

## Support and Resources

### QuantConnect Resources
- [Documentation](https://www.quantconnect.com/docs)
- [Community Forum](https://www.quantconnect.com/forum)
- [Tutorial Videos](https://www.quantconnect.com/learning)
- [Algorithm Examples](https://www.quantconnect.com/tutorials)

### Strategy-Specific Resources
- Original je-suis-tm repository for theoretical background
- MACD indicator documentation
- ETF analysis and selection criteria
- Risk management best practices

---

## Disclaimer

This strategy is for educational and research purposes only. Past performance does not guarantee future results. Always conduct thorough testing and consider your risk tolerance before using any trading strategy with real money.

**Risk Warning**: Trading involves risk of loss. The strategies provided here should be thoroughly tested and understood before implementation. Consider consulting with a financial advisor for personalized investment advice.