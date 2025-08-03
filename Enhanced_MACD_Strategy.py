#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced MACD Strategy with Parameter Optimization and Risk Management
Based on je-suis-tm/quant-trading repository
Enhanced for YimingHao's fork with:
- Dynamic parameter optimization
- Transaction cost modeling
- Improved risk management
- Walk-forward analysis
- Performance metrics

Author: YimingHao (Enhanced version)
Original: je-suis-tm
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class EnhancedMACDStrategy:
    """
    Enhanced MACD Strategy with optimization and risk management
    """
    
    def __init__(self, symbol='AAPL', start_date='2015-01-01', end_date='2023-01-01'):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.data = None
        self.signals = None
        self.results = None
        
    def fetch_data(self):
        """Fetch historical price data"""
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(start=self.start_date, end=self.end_date)
            if self.data.empty:
                raise ValueError(f"No data found for {self.symbol}")
            print(f"Successfully fetched {len(self.data)} days of data for {self.symbol}")
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False
        return True
    
    def calculate_macd(self, data, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate MACD indicator with customizable parameters
        """
        signals = data.copy()
        
        # Calculate exponential moving averages
        ema_fast = signals['Close'].ewm(span=fast_period).mean()
        ema_slow = signals['Close'].ewm(span=slow_period).mean()
        
        # MACD line
        signals['macd'] = ema_fast - ema_slow
        
        # Signal line
        signals['signal'] = signals['macd'].ewm(span=signal_period).mean()
        
        # Histogram
        signals['histogram'] = signals['macd'] - signals['signal']
        
        return signals
    
    def generate_signals(self, data, fast_period=12, slow_period=26, signal_period=9):
        """
        Generate trading signals based on MACD crossovers
        """
        signals = self.calculate_macd(data, fast_period, slow_period, signal_period)
        
        # Initialize positions
        signals['position'] = 0
        signals['signal_trigger'] = 0
        
        # Generate signals when MACD crosses above/below signal line
        for i in range(1, len(signals)):
            if (signals['macd'].iloc[i] > signals['signal'].iloc[i] and 
                signals['macd'].iloc[i-1] <= signals['signal'].iloc[i-1]):
                signals['signal_trigger'].iloc[i] = 1  # Buy signal
            elif (signals['macd'].iloc[i] < signals['signal'].iloc[i] and 
                  signals['macd'].iloc[i-1] >= signals['signal'].iloc[i-1]):
                signals['signal_trigger'].iloc[i] = -1  # Sell signal
        
        # Calculate positions (cumulative signals)
        signals['position'] = signals['signal_trigger'].cumsum()
        signals['position'] = signals['position'].clip(-1, 1)  # Limit to -1, 0, 1
        
        return signals
    
    def calculate_returns(self, signals, transaction_cost=0.001):
        """
        Calculate strategy returns with transaction costs
        """
        results = signals.copy()
        
        # Calculate daily returns
        results['market_return'] = results['Close'].pct_change()
        
        # Calculate position changes (trades)
        results['position_change'] = results['position'].diff().abs()
        
        # Apply transaction costs
        results['transaction_costs'] = results['position_change'] * transaction_cost
        
        # Calculate strategy returns
        results['strategy_return'] = (results['position'].shift(1) * 
                                    results['market_return'] - 
                                    results['transaction_costs'])
        
        # Calculate cumulative returns
        results['market_cumulative'] = (1 + results['market_return']).cumprod()
        results['strategy_cumulative'] = (1 + results['strategy_return']).cumprod()
        
        return results
    
    def calculate_metrics(self, returns):
        """
        Calculate performance metrics
        """
        strategy_returns = returns['strategy_return'].dropna()
        market_returns = returns['market_return'].dropna()
        
        metrics = {}
        
        # Return metrics
        metrics['total_return'] = returns['strategy_cumulative'].iloc[-1] - 1
        metrics['market_return'] = returns['market_cumulative'].iloc[-1] - 1
        metrics['annual_return'] = (1 + metrics['total_return']) ** (252 / len(strategy_returns)) - 1
        
        # Risk metrics
        metrics['volatility'] = strategy_returns.std() * np.sqrt(252)
        metrics['sharpe_ratio'] = metrics['annual_return'] / metrics['volatility'] if metrics['volatility'] > 0 else 0
        
        # Drawdown
        running_max = returns['strategy_cumulative'].expanding().max()
        drawdown = (returns['strategy_cumulative'] - running_max) / running_max
        metrics['max_drawdown'] = drawdown.min()
        
        # Win rate
        winning_trades = strategy_returns[strategy_returns > 0]
        metrics['win_rate'] = len(winning_trades) / len(strategy_returns) if len(strategy_returns) > 0 else 0
        
        # Beta (relative to market)
        if len(market_returns) > 0 and market_returns.std() > 0:
            covariance = np.cov(strategy_returns, market_returns)[0, 1]
            market_variance = market_returns.var()
            metrics['beta'] = covariance / market_variance
        else:
            metrics['beta'] = 0
        
        return metrics
    
    def objective_function(self, params, data):
        """
        Objective function for parameter optimization
        """
        fast_period, slow_period, signal_period = int(params[0]), int(params[1]), int(params[2])
        
        # Ensure parameters are valid
        if fast_period >= slow_period or fast_period < 1 or signal_period < 1:
            return -np.inf
        
        try:
            signals = self.generate_signals(data, fast_period, slow_period, signal_period)
            results = self.calculate_returns(signals)
            metrics = self.calculate_metrics(results)
            
            # Optimize for risk-adjusted returns (Sharpe ratio)
            return -metrics['sharpe_ratio']  # Negative because minimize function
        except:
            return np.inf
    
    def optimize_parameters(self, optimization_window=252):
        """
        Optimize MACD parameters using historical data
        """
        if self.data is None:
            print("No data available. Please fetch data first.")
            return None
        
        # Use only a portion of data for optimization
        opt_data = self.data.head(optimization_window)
        
        # Parameter bounds: (fast_period, slow_period, signal_period)
        bounds = [(5, 20), (20, 50), (5, 15)]
        initial_guess = [12, 26, 9]  # Standard MACD parameters
        
        print("Optimizing parameters...")
        result = minimize(
            self.objective_function,
            initial_guess,
            args=(opt_data,),
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        if result.success:
            optimal_params = result.x
            print(f"Optimal parameters found:")
            print(f"Fast period: {int(optimal_params[0])}")
            print(f"Slow period: {int(optimal_params[1])}")
            print(f"Signal period: {int(optimal_params[2])}")
            return [int(p) for p in optimal_params]
        else:
            print("Optimization failed. Using default parameters.")
            return [12, 26, 9]
    
    def walk_forward_analysis(self, optimization_window=252, test_window=63):
        """
        Perform walk-forward analysis
        """
        if self.data is None:
            print("No data available. Please fetch data first.")
            return None
        
        results_list = []
        
        for start_idx in range(0, len(self.data) - optimization_window - test_window, test_window):
            # Optimization period
            opt_start = start_idx
            opt_end = start_idx + optimization_window
            opt_data = self.data.iloc[opt_start:opt_end]
            
            # Test period
            test_start = opt_end
            test_end = min(opt_end + test_window, len(self.data))
            test_data = self.data.iloc[test_start:test_end]
            
            # Optimize parameters on optimization data
            temp_strategy = EnhancedMACDStrategy()
            temp_strategy.data = opt_data
            optimal_params = temp_strategy.optimize_parameters()
            
            # Test on out-of-sample data
            if optimal_params:
                signals = self.generate_signals(test_data, *optimal_params)
                results = self.calculate_returns(signals)
                
                period_results = {
                    'start_date': test_data.index[0],
                    'end_date': test_data.index[-1],
                    'parameters': optimal_params,
                    'return': results['strategy_cumulative'].iloc[-1] - 1,
                    'sharpe': self.calculate_metrics(results)['sharpe_ratio']
                }
                results_list.append(period_results)
        
        return pd.DataFrame(results_list)
    
    def backtest(self, fast_period=12, slow_period=26, signal_period=9, 
                 transaction_cost=0.001, plot_results=True):
        """
        Run complete backtest
        """
        if self.data is None:
            if not self.fetch_data():
                return None
        
        # Generate signals
        self.signals = self.generate_signals(self.data, fast_period, slow_period, signal_period)
        
        # Calculate returns
        self.results = self.calculate_returns(self.signals, transaction_cost)
        
        # Calculate metrics
        metrics = self.calculate_metrics(self.results)
        
        # Print results
        print(f"\n=== Enhanced MACD Strategy Results for {self.symbol} ===")
        print(f"Strategy Total Return: {metrics['total_return']:.2%}")
        print(f"Market Total Return: {metrics['market_return']:.2%}")
        print(f"Annualized Return: {metrics['annual_return']:.2%}")
        print(f"Volatility: {metrics['volatility']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
        print(f"Maximum Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"Win Rate: {metrics['win_rate']:.2%}")
        print(f"Beta: {metrics['beta']:.3f}")
        
        if plot_results:
            self.plot_results()
        
        return metrics
    
    def plot_results(self):
        """
        Plot backtest results
        """
        if self.results is None:
            print("No results to plot. Run backtest first.")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Price and signals
        ax1.plot(self.results.index, self.results['Close'], label='Close Price', alpha=0.7)
        buy_signals = self.results[self.results['signal_trigger'] == 1]
        sell_signals = self.results[self.results['signal_trigger'] == -1]
        ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', s=50, label='Buy Signal')
        ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', s=50, label='Sell Signal')
        ax1.set_title(f'{self.symbol} Price and Trading Signals')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # MACD
        ax2.plot(self.results.index, self.results['macd'], label='MACD', color='blue')
        ax2.plot(self.results.index, self.results['signal'], label='Signal', color='red')
        ax2.bar(self.results.index, self.results['histogram'], label='Histogram', alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.set_title('MACD Indicator')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Cumulative returns
        ax3.plot(self.results.index, self.results['strategy_cumulative'], label='Strategy', linewidth=2)
        ax3.plot(self.results.index, self.results['market_cumulative'], label='Market', linewidth=2)
        ax3.set_title('Cumulative Returns Comparison')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylabel('Cumulative Return')
        
        # Drawdown
        running_max = self.results['strategy_cumulative'].expanding().max()
        drawdown = (self.results['strategy_cumulative'] - running_max) / running_max
        ax4.fill_between(self.results.index, drawdown, 0, alpha=0.3, color='red')
        ax4.set_title('Strategy Drawdown')
        ax4.set_ylabel('Drawdown')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def main():
    """
    Example usage of Enhanced MACD Strategy
    """
    # Initialize strategy
    strategy = EnhancedMACDStrategy(symbol='AAPL', start_date='2020-01-01', end_date='2024-01-01')
    
    # Run backtest with default parameters
    print("Running backtest with default parameters...")
    metrics_default = strategy.backtest()
    
    # Optimize parameters
    print("\nOptimizing parameters...")
    optimal_params = strategy.optimize_parameters()
    
    if optimal_params:
        print(f"\nRunning backtest with optimized parameters: {optimal_params}")
        metrics_optimized = strategy.backtest(*optimal_params)
        
        print(f"\nImprovement in Sharpe Ratio: {metrics_optimized['sharpe_ratio'] - metrics_default['sharpe_ratio']:.3f}")
    
    # Walk-forward analysis
    print("\nPerforming walk-forward analysis...")
    wf_results = strategy.walk_forward_analysis()
    if wf_results is not None and not wf_results.empty:
        print(f"Average out-of-sample Sharpe ratio: {wf_results['sharpe'].mean():.3f}")
        print(f"Win rate (positive periods): {(wf_results['return'] > 0).mean():.2%}")

if __name__ == "__main__":
    main()