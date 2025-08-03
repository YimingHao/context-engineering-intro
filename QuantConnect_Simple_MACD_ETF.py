# region imports
from AlgorithmImports import *
# endregion

class SimplifiedMACDETFStrategy(QCAlgorithm):
    """
    Simplified Enhanced MACD Strategy for QuantConnect
    Trades on 8 major ETFs with built-in indicators and risk management
    
    Features:
    - Multi-ETF portfolio using built-in MACD indicators
    - Volatility-based position sizing
    - Drawdown protection
    - Regular rebalancing
    - Performance tracking
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
        
        # Add ETF data and create indicators
        self.etfs = {}
        for symbol in self.etf_symbols:
            equity = self.AddEquity(symbol, Resolution.Daily)
            equity.SetDataNormalizationMode(DataNormalizationMode.Adjusted)
            
            # Create MACD indicator
            macd = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily)
            
            # Create additional indicators
            sma_20 = self.SMA(symbol, 20, Resolution.Daily)
            rsi = self.RSI(symbol, 14, Resolution.Daily)
            
            self.etfs[symbol] = {
                'symbol': equity.Symbol,
                'macd': macd,
                'sma_20': sma_20,
                'rsi': rsi,
                'position': 0,
                'last_signal': 0,
                'returns': RollingWindow[float](252),  # Store daily returns
                'prices': RollingWindow[float](252)    # Store daily prices
            }
        
        # Strategy parameters
        self.max_position_size = 0.125  # 12.5% per ETF (8 ETFs = 100% max)
        self.max_drawdown = 0.15        # 15% maximum drawdown
        self.volatility_window = 20     # Volatility calculation window
        self.rebalance_frequency = 5    # Rebalance every 5 days
        
        # Performance tracking
        self.peak_portfolio_value = self.Portfolio.TotalPortfolioValue
        self.drawdown = 0.0
        self.last_rebalance = self.Time
        
        # Schedule rebalancing
        self.Schedule.On(
            self.DateRules.EveryDay("SPY"),
            self.TimeRules.AfterMarketOpen("SPY", 30),
            self.RebalancePortfolio
        )
        
        # Set benchmark
        self.SetBenchmark("SPY")
        
        # Set warm-up period for indicators
        self.SetWarmUp(30)

    def OnData(self, data):
        """Handle incoming data"""
        if self.IsWarmingUp:
            return
            
        # Update price and return data for each ETF
        for symbol_str, etf_data in self.etfs.items():
            symbol = etf_data['symbol']
            
            if data.ContainsKey(symbol) and data[symbol] is not None:
                price = data[symbol].Close
                etf_data['prices'].Add(price)
                
                # Calculate daily returns
                if etf_data['prices'].Count > 1:
                    daily_return = (price / etf_data['prices'][1]) - 1
                    etf_data['returns'].Add(daily_return)
        
        # Update portfolio metrics
        self.UpdatePortfolioMetrics()

    def RebalancePortfolio(self):
        """Main portfolio rebalancing logic"""
        if self.IsWarmingUp:
            return
        
        # Only rebalance every few days to reduce transaction costs
        if (self.Time - self.last_rebalance).days < self.rebalance_frequency:
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
        
        # Update last rebalance time
        self.last_rebalance = self.Time
        
        # Log portfolio status
        self.LogPortfolioStatus()

    def GenerateSignal(self, symbol_str):
        """Generate trading signal for a specific ETF"""
        etf_data = self.etfs[symbol_str]
        macd = etf_data['macd']
        sma_20 = etf_data['sma_20']
        rsi = etf_data['rsi']
        
        # Ensure indicators are ready
        if not macd.IsReady or not sma_20.IsReady or not rsi.IsReady:
            return 0
        
        signal = 0
        current_price = self.Securities[symbol_str].Price
        
        # MACD crossover signals
        macd_line = macd.Current.Value
        signal_line = macd.Signal.Current.Value
        histogram = macd.Histogram.Current.Value
        
        # Primary MACD signal
        if macd_line > signal_line and histogram > 0:
            signal = 1  # Bullish
        elif macd_line < signal_line and histogram < 0:
            signal = -1  # Bearish
        else:
            signal = 0  # Neutral
        
        # Additional filters
        signal = self.ApplyFilters(symbol_str, signal, current_price)
        
        return signal

    def ApplyFilters(self, symbol_str, signal, current_price):
        """Apply additional filters to improve signal quality"""
        etf_data = self.etfs[symbol_str]
        sma_20 = etf_data['sma_20']
        rsi = etf_data['rsi']
        
        # Trend filter - only trade in direction of medium-term trend
        if signal > 0 and current_price < sma_20.Current.Value * 0.98:
            signal = 0  # Don't buy if price is significantly below SMA
        elif signal < 0 and current_price > sma_20.Current.Value * 1.02:
            signal = 0  # Don't sell if price is significantly above SMA
        
        # RSI filter - avoid extreme conditions
        rsi_value = rsi.Current.Value
        if signal > 0 and rsi_value > 70:
            signal = 0  # Don't buy when overbought
        elif signal < 0 and rsi_value < 30:
            signal = 0  # Don't sell when oversold
        
        # Volatility filter
        if etf_data['returns'].Count >= self.volatility_window:
            recent_returns = [etf_data['returns'][i] for i in range(min(self.volatility_window, etf_data['returns'].Count))]
            volatility = np.std(recent_returns) * np.sqrt(252)
            
            # Reduce position size in high volatility environments
            if volatility > 0.35:  # 35% annual volatility threshold
                signal *= 0.5
        
        return signal

    def ApplyRiskManagement(self, signals):
        """Apply portfolio-level risk management"""
        filtered_signals = {}
        
        # Check overall portfolio drawdown
        if self.drawdown > self.max_drawdown:
            self.Log(f"Portfolio drawdown {self.drawdown:.2%} exceeds maximum {self.max_drawdown:.2%}")
            # In high drawdown, only allow closing positions or going to cash
            for symbol_str in signals:
                if signals[symbol_str] > 0:
                    filtered_signals[symbol_str] = 0  # No new long positions
                else:
                    filtered_signals[symbol_str] = signals[symbol_str]
            return filtered_signals
        
        # Calculate position sizes based on volatility and equal weighting
        total_signals = sum(abs(s) for s in signals.values() if s != 0)
        
        if total_signals == 0:
            # No signals, go to cash
            for symbol_str in signals:
                filtered_signals[symbol_str] = 0
        else:
            # Distribute capital among active signals
            for symbol_str, signal in signals.items():
                if signal != 0:
                    # Base position size
                    position_size = self.max_position_size
                    
                    # Adjust for volatility
                    position_size = self.AdjustForVolatility(symbol_str, position_size)
                    
                    # Apply signal direction and size
                    filtered_signals[symbol_str] = signal * position_size
                else:
                    filtered_signals[symbol_str] = 0
        
        return filtered_signals

    def AdjustForVolatility(self, symbol_str, base_size):
        """Adjust position size based on volatility"""
        etf_data = self.etfs[symbol_str]
        
        if etf_data['returns'].Count < self.volatility_window:
            return base_size
        
        # Calculate volatility
        recent_returns = [etf_data['returns'][i] for i in range(min(self.volatility_window, etf_data['returns'].Count))]
        volatility = np.std(recent_returns) * np.sqrt(252)
        
        # Inverse volatility weighting
        base_vol = 0.15  # 15% base volatility
        vol_adjustment = min(base_vol / max(volatility, 0.05), 2.0)  # Cap at 2x
        
        adjusted_size = base_size * vol_adjustment
        return min(adjusted_size, self.max_position_size)

    def ExecuteTrades(self, signals):
        """Execute trades based on filtered signals"""
        for symbol_str, target_weight in signals.items():
            etf_data = self.etfs[symbol_str]
            symbol = etf_data['symbol']
            
            # Get current holdings
            current_quantity = self.Portfolio[symbol].Quantity
            current_value = self.Portfolio[symbol].HoldingsValue
            portfolio_value = self.Portfolio.TotalPortfolioValue
            current_weight = current_value / portfolio_value if portfolio_value > 0 else 0
            
            # Calculate target position
            weight_difference = target_weight - current_weight
            
            if abs(weight_difference) > 0.02:  # 2% threshold to avoid excessive trading
                # Calculate target dollar amount
                target_value = portfolio_value * target_weight
                
                # Use CalculateOrderQuantity for precise position sizing
                quantity = self.CalculateOrderQuantity(symbol, target_weight)
                
                if quantity != 0:
                    # Execute the trade
                    ticket = self.MarketOrder(symbol, quantity)
                    
                    if ticket.Status == OrderStatus.Filled:
                        etf_data['position'] = target_weight
                        self.Log(f"Rebalanced {symbol_str}: {quantity} shares, target weight: {target_weight:.2%}")

    def UpdatePortfolioMetrics(self):
        """Update portfolio performance metrics"""
        current_value = self.Portfolio.TotalPortfolioValue
        
        # Update peak value and drawdown
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
        
        self.drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value

    def LogPortfolioStatus(self):
        """Log current portfolio status"""
        total_invested = sum(abs(self.Portfolio[etf_data['symbol']].HoldingsValue) 
                           for etf_data in self.etfs.values())
        portfolio_value = self.Portfolio.TotalPortfolioValue
        cash_percentage = self.Portfolio.CashBook["USD"].Amount / portfolio_value
        
        self.Log(f"Portfolio: ${portfolio_value:,.0f}, Cash: {cash_percentage:.1%}, "
               f"Invested: {total_invested/portfolio_value:.1%}, Drawdown: {self.drawdown:.2%}")
        
        # Log individual positions
        for symbol_str, etf_data in self.etfs.items():
            holdings_value = self.Portfolio[etf_data['symbol']].HoldingsValue
            weight = holdings_value / portfolio_value if portfolio_value > 0 else 0
            if abs(weight) > 0.01:  # Only log positions > 1%
                macd_signal = "N/A"
                if etf_data['macd'].IsReady:
                    macd_line = etf_data['macd'].Current.Value
                    signal_line = etf_data['macd'].Signal.Current.Value
                    macd_signal = "+" if macd_line > signal_line else "-"
                
                self.Log(f"  {symbol_str}: {weight:.1%} (MACD: {macd_signal})")

    def OnEndOfAlgorithm(self):
        """Called at the end of the algorithm"""
        # Calculate final performance metrics
        total_return = (self.Portfolio.TotalPortfolioValue / 100000) - 1
        
        # Get benchmark performance for comparison
        spy_history = self.History(["SPY"], self.StartDate, self.EndDate, Resolution.Daily)
        if not spy_history.empty:
            spy_start = spy_history.iloc[0]['close']
            spy_end = spy_history.iloc[-1]['close']
            benchmark_return = (spy_end / spy_start) - 1
        else:
            benchmark_return = 0
        
        self.Log(f"=== FINAL PERFORMANCE METRICS ===")
        self.Log(f"Strategy Total Return: {total_return:.2%}")
        self.Log(f"SPY Benchmark Return: {benchmark_return:.2%}")
        self.Log(f"Excess Return: {(total_return - benchmark_return):.2%}")
        self.Log(f"Maximum Drawdown: {self.drawdown:.2%}")
        self.Log(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:,.0f}")
        
        # Log final allocations
        self.Log(f"=== FINAL ALLOCATIONS ===")
        portfolio_value = self.Portfolio.TotalPortfolioValue
        for symbol_str, etf_data in self.etfs.items():
            holdings_value = self.Portfolio[etf_data['symbol']].HoldingsValue
            weight = holdings_value / portfolio_value if portfolio_value > 0 else 0
            if abs(weight) > 0.005:  # Log positions > 0.5%
                self.Log(f"{symbol_str}: {weight:.2%}")