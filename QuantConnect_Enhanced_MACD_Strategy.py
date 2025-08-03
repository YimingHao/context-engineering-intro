# region imports
from AlgorithmImports import *
import numpy as np
from scipy.optimize import minimize
from collections import deque
# endregion

class EnhancedMACDETFStrategy(QCAlgorithm):
    """
    Enhanced MACD Strategy for QuantConnect
    Trades on 8 major ETFs with dynamic parameter optimization and risk management
    
    Features:
    - Multi-ETF portfolio management
    - Dynamic MACD parameter optimization
    - Risk-based position sizing
    - Drawdown protection
    - Performance tracking and analytics
    """
    
    def Initialize(self):
        """Initialize the algorithm"""
        # Set backtest period
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)
        
        # Define ETF universe - 8 major sector and broad market ETFs
        self.etf_symbols = [
            "SPY",   # S&P 500 ETF
            "QQQ",   # NASDAQ 100 ETF
            "XLK",   # Technology Select Sector SPDR Fund
            "XLF",   # Financial Select Sector SPDR Fund
            "XLV",   # Health Care Select Sector SPDR Fund
            "XLE",   # Energy Select Sector SPDR Fund
            "XLI",   # Industrial Select Sector SPDR Fund
            "XLP"    # Consumer Staples Select Sector SPDR Fund
        ]
        
        # Add ETF data
        self.etfs = {}
        for symbol in self.etf_symbols:
            equity = self.AddEquity(symbol, Resolution.Daily)
            equity.SetDataNormalizationMode(DataNormalizationMode.Adjusted)
            self.etfs[symbol] = {
                'symbol': equity.Symbol,
                'macd': None,
                'ema_fast': None,
                'ema_slow': None,
                'signal_line': None,
                'position': 0,
                'last_signal': 0,
                'optimal_params': [12, 26, 9],  # Default MACD parameters
                'price_history': deque(maxlen=252),  # 1 year of daily prices
                'returns': deque(maxlen=252),
                'last_optimization': self.Time
            }
        
        # Strategy parameters
        self.fast_period = 12
        self.slow_period = 26
        self.signal_period = 9
        self.lookback_period = 200
        
        # Risk management parameters
        self.max_position_size = 0.125  # 12.5% per ETF (8 ETFs = 100% max)
        self.stop_loss_pct = 0.05       # 5% stop loss
        self.max_drawdown = 0.15        # 15% maximum drawdown
        self.volatility_window = 20      # Volatility calculation window
        
        # Portfolio management
        self.portfolio_heat = 0.0       # Current portfolio risk exposure
        self.max_portfolio_heat = 1.0   # Maximum allowed risk exposure
        self.rebalance_frequency = 5    # Rebalance every 5 days
        
        # Performance tracking
        self.daily_returns = deque(maxlen=252)
        self.benchmark_returns = deque(maxlen=252)
        self.peak_portfolio_value = self.Portfolio.TotalPortfolioValue
        self.drawdown = 0.0
        
        # Optimization settings
        self.optimization_frequency = 21  # Optimize parameters every 21 days
        self.min_history_for_optimization = 63  # Minimum 3 months of data
        
        # Schedule functions
        self.Schedule.On(
            self.DateRules.EveryDay("SPY"),
            self.TimeRules.AfterMarketOpen("SPY", 30),
            self.RebalancePortfolio
        )
        
        self.Schedule.On(
            self.DateRules.Every(DayOfWeek.Monday),
            self.TimeRules.AfterMarketOpen("SPY", 60),
            self.OptimizeParameters
        )
        
        # Set benchmark
        self.SetBenchmark("SPY")
        
        # Set warm-up period
        self.SetWarmUp(max(self.lookback_period, 100))

    def OnData(self, data):
        """Handle incoming data"""
        if self.IsWarmingUp:
            return
            
        # Update indicators and collect data for each ETF
        for symbol_str, etf_data in self.etfs.items():
            symbol = etf_data['symbol']
            
            if not data.ContainsKey(symbol):
                continue
                
            price = data[symbol].Close
            etf_data['price_history'].append(price)
            
            # Calculate returns
            if len(etf_data['price_history']) > 1:
                daily_return = (price / etf_data['price_history'][-2]) - 1
                etf_data['returns'].append(daily_return)
            
            # Update MACD indicators
            self.UpdateMACDIndicators(symbol_str, price)
        
        # Update portfolio metrics
        self.UpdatePortfolioMetrics()

    def UpdateMACDIndicators(self, symbol_str, price):
        """Update MACD indicators for a given ETF"""
        etf_data = self.etfs[symbol_str]
        params = etf_data['optimal_params']
        fast_period, slow_period, signal_period = params
        
        # Calculate EMAs manually for more control
        if len(etf_data['price_history']) >= slow_period:
            prices = list(etf_data['price_history'])
            
            # Calculate EMAs
            ema_fast = self.CalculateEMA(prices, fast_period)
            ema_slow = self.CalculateEMA(prices, slow_period)
            
            if ema_fast is not None and ema_slow is not None:
                # MACD Line
                macd_value = ema_fast - ema_slow
                etf_data['macd'] = macd_value
                etf_data['ema_fast'] = ema_fast
                etf_data['ema_slow'] = ema_slow
                
                # Signal Line (EMA of MACD)
                # For simplicity, we'll use a basic moving average of MACD values
                # In practice, you'd want to maintain a history of MACD values
                etf_data['signal_line'] = macd_value * 0.1 + (etf_data['signal_line'] or 0) * 0.9

    def CalculateEMA(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        multiplier = 2.0 / (period + 1.0)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema

    def RebalancePortfolio(self):
        """Main portfolio rebalancing logic"""
        if self.IsWarmingUp:
            return
        
        signals = {}
        
        # Generate signals for each ETF
        for symbol_str, etf_data in self.etfs.items():
            signal = self.GenerateSignal(symbol_str)
            signals[symbol_str] = signal
        
        # Apply risk management filters
        filtered_signals = self.ApplyRiskManagement(signals)
        
        # Execute trades based on filtered signals
        self.ExecuteTrades(filtered_signals)
        
        # Log portfolio status
        self.LogPortfolioStatus()

    def GenerateSignal(self, symbol_str):
        """Generate trading signal for a specific ETF"""
        etf_data = self.etfs[symbol_str]
        
        if etf_data['macd'] is None or etf_data['signal_line'] is None:
            return 0
        
        macd = etf_data['macd']
        signal_line = etf_data['signal_line']
        last_signal = etf_data['last_signal']
        
        # MACD crossover signals
        if macd > signal_line and last_signal <= 0:
            # Bullish crossover
            signal = 1
        elif macd < signal_line and last_signal >= 0:
            # Bearish crossover
            signal = -1
        else:
            # Hold current position
            signal = etf_data['position']
        
        # Additional filters
        signal = self.ApplyAdditionalFilters(symbol_str, signal)
        
        etf_data['last_signal'] = signal
        return signal

    def ApplyAdditionalFilters(self, symbol_str, signal):
        """Apply additional filters to improve signal quality"""
        etf_data = self.etfs[symbol_str]
        
        # Volatility filter
        if len(etf_data['returns']) >= self.volatility_window:
            recent_returns = list(etf_data['returns'])[-self.volatility_window:]
            volatility = np.std(recent_returns) * np.sqrt(252)
            
            # Reduce signal strength in high volatility environments
            if volatility > 0.3:  # 30% annual volatility threshold
                signal *= 0.5
        
        # Momentum filter
        if len(etf_data['price_history']) >= 20:
            current_price = etf_data['price_history'][-1]
            ma_20 = np.mean(list(etf_data['price_history'])[-20:])
            
            # Only trade in direction of medium-term trend
            if signal > 0 and current_price < ma_20 * 0.98:  # 2% below MA
                signal = 0
            elif signal < 0 and current_price > ma_20 * 1.02:  # 2% above MA
                signal = 0
        
        return signal

    def ApplyRiskManagement(self, signals):
        """Apply portfolio-level risk management"""
        filtered_signals = {}
        
        # Check overall portfolio drawdown
        if self.drawdown > self.max_drawdown:
            self.Log(f"Portfolio drawdown {self.drawdown:.2%} exceeds maximum {self.max_drawdown:.2%}")
            # Reduce all positions in high drawdown scenario
            for symbol_str in signals:
                if signals[symbol_str] > 0:
                    filtered_signals[symbol_str] = 0
                else:
                    filtered_signals[symbol_str] = signals[symbol_str]
            return filtered_signals
        
        # Calculate position sizes based on volatility
        for symbol_str, signal in signals.items():
            if signal != 0:
                position_size = self.CalculatePositionSize(symbol_str, signal)
                filtered_signals[symbol_str] = signal * position_size
            else:
                filtered_signals[symbol_str] = 0
        
        return filtered_signals

    def CalculatePositionSize(self, symbol_str, signal):
        """Calculate position size based on volatility and risk management"""
        etf_data = self.etfs[symbol_str]
        
        if len(etf_data['returns']) < self.volatility_window:
            return self.max_position_size
        
        # Calculate ETF volatility
        recent_returns = list(etf_data['returns'])[-self.volatility_window:]
        volatility = np.std(recent_returns) * np.sqrt(252)
        
        # Inverse volatility weighting
        base_vol = 0.15  # 15% base volatility
        vol_adjustment = min(base_vol / max(volatility, 0.05), 2.0)  # Cap at 2x
        
        # Calculate position size
        position_size = self.max_position_size * vol_adjustment
        position_size = min(position_size, self.max_position_size)
        
        return position_size

    def ExecuteTrades(self, signals):
        """Execute trades based on filtered signals"""
        for symbol_str, target_signal in signals.items():
            etf_data = self.etfs[symbol_str]
            symbol = etf_data['symbol']
            current_position = etf_data['position']
            
            # Calculate target weight
            target_weight = target_signal
            current_weight = current_position
            
            if abs(target_weight - current_weight) > 0.01:  # 1% threshold
                # Calculate number of shares to trade
                portfolio_value = self.Portfolio.TotalPortfolioValue
                target_value = portfolio_value * target_weight
                current_value = portfolio_value * current_weight
                trade_value = target_value - current_value
                
                if self.Securities.ContainsKey(symbol):
                    current_price = self.Securities[symbol].Price
                    if current_price > 0:
                        shares_to_trade = int(trade_value / current_price)
                        
                        if abs(shares_to_trade) > 0:
                            # Execute the trade
                            order_ticket = self.MarketOrder(symbol, shares_to_trade)
                            
                            if order_ticket.Status == OrderStatus.Filled:
                                etf_data['position'] = target_weight
                                self.Log(f"Traded {shares_to_trade} shares of {symbol_str}, "
                                       f"New position: {target_weight:.2%}")

    def OptimizeParameters(self):
        """Optimize MACD parameters for each ETF"""
        if self.IsWarmingUp:
            return
        
        for symbol_str, etf_data in self.etfs.items():
            # Check if enough data and time since last optimization
            if (len(etf_data['price_history']) >= self.min_history_for_optimization and
                (self.Time - etf_data['last_optimization']).days >= self.optimization_frequency):
                
                optimal_params = self.OptimizeETFParameters(symbol_str)
                if optimal_params:
                    etf_data['optimal_params'] = optimal_params
                    etf_data['last_optimization'] = self.Time
                    self.Log(f"Optimized {symbol_str} parameters: {optimal_params}")

    def OptimizeETFParameters(self, symbol_str):
        """Optimize MACD parameters for a specific ETF"""
        etf_data = self.etfs[symbol_str]
        prices = list(etf_data['price_history'])
        
        if len(prices) < self.min_history_for_optimization:
            return None
        
        # Define parameter bounds
        bounds = [(8, 20), (20, 40), (6, 15)]  # (fast, slow, signal)
        initial_guess = [12, 26, 9]
        
        def objective(params):
            fast, slow, signal = int(params[0]), int(params[1]), int(params[2])
            
            if fast >= slow:
                return -1000  # Invalid parameters
            
            # Calculate MACD strategy returns
            returns = self.CalculateStrategyReturns(prices, fast, slow, signal)
            
            if len(returns) == 0:
                return -1000
            
            # Calculate Sharpe ratio
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return == 0:
                return -1000
            
            sharpe_ratio = avg_return / std_return * np.sqrt(252)
            return -sharpe_ratio  # Negative because we minimize
        
        try:
            result = minimize(objective, initial_guess, bounds=bounds, method='L-BFGS-B')
            if result.success:
                return [int(result.x[0]), int(result.x[1]), int(result.x[2])]
        except:
            pass
        
        return None

    def CalculateStrategyReturns(self, prices, fast_period, slow_period, signal_period):
        """Calculate strategy returns for parameter optimization"""
        if len(prices) < slow_period + signal_period:
            return []
        
        # Calculate MACD
        macd_values = []
        signal_values = []
        
        for i in range(slow_period, len(prices)):
            # Get price window
            price_window = prices[max(0, i-slow_period):i+1]
            
            # Calculate EMAs
            ema_fast = self.CalculateEMA(price_window, fast_period)
            ema_slow = self.CalculateEMA(price_window, slow_period)
            
            if ema_fast and ema_slow:
                macd = ema_fast - ema_slow
                macd_values.append(macd)
                
                # Calculate signal line
                if len(macd_values) >= signal_period:
                    signal = np.mean(macd_values[-signal_period:])
                    signal_values.append(signal)
        
        # Generate trading signals
        positions = []
        for i in range(1, len(signal_values)):
            if macd_values[i] > signal_values[i] and macd_values[i-1] <= signal_values[i-1]:
                positions.append(1)  # Buy
            elif macd_values[i] < signal_values[i] and macd_values[i-1] >= signal_values[i-1]:
                positions.append(-1)  # Sell
            else:
                positions.append(positions[-1] if positions else 0)  # Hold
        
        # Calculate returns
        returns = []
        start_idx = slow_period + signal_period
        
        for i in range(len(positions)):
            if start_idx + i + 1 < len(prices):
                price_return = (prices[start_idx + i + 1] / prices[start_idx + i]) - 1
                strategy_return = positions[i] * price_return
                returns.append(strategy_return)
        
        return returns

    def UpdatePortfolioMetrics(self):
        """Update portfolio performance metrics"""
        current_value = self.Portfolio.TotalPortfolioValue
        
        # Update peak value and drawdown
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
        
        self.drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value
        
        # Calculate daily returns
        if hasattr(self, 'previous_portfolio_value'):
            daily_return = (current_value / self.previous_portfolio_value) - 1
            self.daily_returns.append(daily_return)
        
        self.previous_portfolio_value = current_value

    def LogPortfolioStatus(self):
        """Log current portfolio status"""
        if self.Time.day % 5 == 0:  # Log every 5 days
            total_positions = sum(abs(etf_data['position']) for etf_data in self.etfs.values())
            
            self.Log(f"Portfolio Status - Total Exposure: {total_positions:.2%}, "
                   f"Drawdown: {self.drawdown:.2%}, "
                   f"Value: ${self.Portfolio.TotalPortfolioValue:,.0f}")
            
            # Log individual positions
            for symbol_str, etf_data in self.etfs.items():
                if abs(etf_data['position']) > 0.01:
                    self.Log(f"{symbol_str}: {etf_data['position']:.2%} "
                           f"(Params: {etf_data['optimal_params']})")

    def OnEndOfAlgorithm(self):
        """Called at the end of the algorithm"""
        # Calculate final performance metrics
        if len(self.daily_returns) > 0:
            total_return = (self.Portfolio.TotalPortfolioValue / 100000) - 1
            annual_return = (1 + total_return) ** (252 / len(self.daily_returns)) - 1
            volatility = np.std(list(self.daily_returns)) * np.sqrt(252)
            sharpe_ratio = annual_return / volatility if volatility > 0 else 0
            
            self.Log(f"=== FINAL PERFORMANCE METRICS ===")
            self.Log(f"Total Return: {total_return:.2%}")
            self.Log(f"Annual Return: {annual_return:.2%}")
            self.Log(f"Volatility: {volatility:.2%}")
            self.Log(f"Sharpe Ratio: {sharpe_ratio:.3f}")
            self.Log(f"Max Drawdown: {self.drawdown:.2%}")
            
            # Log final ETF parameters
            self.Log(f"=== FINAL OPTIMIZED PARAMETERS ===")
            for symbol_str, etf_data in self.etfs.items():
                self.Log(f"{symbol_str}: {etf_data['optimal_params']}")