## FEATURE:

A comprehensive quantitative trading strategy that identifies undervalued stocks through fundamental fair value gap analysis and combines this with momentum detection to optimize entry timing. The system targets mid-cap ($2-10B market cap) companies in Technology and Healthcare/Biotech sectors.

### Core Strategy Overview

**Primary Objective**: Identify stocks trading below their intrinsic fair value (fundamental fair value gap) that also exhibit upward momentum, creating a systematic approach to value investing with timing optimization.

**Strategy Classification**: Technical Momentum Strategy with Fundamental Value Screening
- **Fair Value Gap Analysis**: Acts as the primary stock screening mechanism
- **Momentum Detection**: Serves as the entry timing and confirmation signal
- **Risk Management**: Position sizing and stop-loss based on volatility and fundamental confidence

### Target Universe Definition

**Sectors**: 
- **Technology**: Focus on SaaS, cloud computing, software, and tech hardware companies
- **Healthcare/Biotech**: Including established pharma, biotech, and medical device companies
- **Rationale**: These sectors provide complementary opportunity types:
  - Tech: Predictable revenue models, quarterly earnings cycles
  - Healthcare: Event-driven catalysts (FDA approvals, clinical trials), longer development cycles

**Market Capitalization**: Mid-cap companies ($2-10B market cap)
- **Reasoning**: Optimal balance between market inefficiency opportunities and data quality/liquidity
- **Tech Examples**: Snowflake, CrowdStrike, Datadog, Palantir
- **Healthcare Examples**: Moderna, Regeneron, Illumina, BioNTech

**Geographic Focus**: US-listed companies (NYSE, NASDAQ)
- **Initial Universe**: ~500-800 companies across both sectors
- **Screening Criteria**: Minimum daily volume, financial reporting standards, data availability

### Data Requirements & Sources

**Primary Data Sources**:
1. **Fundamental Data**: 
   - Financial statements (quarterly/annual): Income statements, balance sheets, cash flow statements
   - Key metrics: Revenue, earnings, debt, cash, book value, R&D spending
   - Provider: Alpha Vantage, Financial Modeling Prep, or Polygon.io ($50-200/month)

2. **Market Data**:
   - Daily OHLCV data (Open, High, Low, Close, Volume)
   - Market capitalization, shares outstanding
   - Provider: Yahoo Finance (free) or Alpha Vantage

3. **Institutional Fair Value Estimates**:
   - Morningstar fair value estimates
   - Analyst consensus targets
   - Provider: Refinitiv, Morningstar Direct, or Bloomberg (premium)

4. **Economic Data**:
   - Risk-free rates (10-year Treasury)
   - Sector-specific discount rates
   - Provider: FRED (Federal Reserve Economic Data)

**Healthcare-Specific Data**:
- FDA approval calendars and clinical trial databases
- Patent expiration schedules
- Drug pipeline information

### Fair Value Calculation Methodology

**Multi-Model Ensemble Approach**:

1. **Discounted Cash Flow (DCF) Model**:
   - **Tech Companies**: Focus on free cash flow sustainability and recurring revenue growth
   - **Healthcare Companies**: Risk-adjusted NPV of drug pipelines + current operations DCF
   - **Discount Rate**: Sector-specific WACC with risk adjustments

2. **Sector-Specific Valuation Models**:
   - **Tech**: Revenue multiples (P/S), adjusted for growth rates and margins
   - **Healthcare**: P/E ratios adjusted for pipeline value and patent cliffs
   - **Both**: Book value multiples where applicable

3. **Institutional Consensus Integration**:
   - Incorporate Morningstar fair value estimates
   - Weight institutional estimates based on historical accuracy
   - Create ensemble model combining internal DCF + institutional estimates

**Fair Value Gap Calculation**:
```
Fair Value Gap (%) = (Fair Value - Current Price) / Current Price
Minimum Gap Threshold = 15% (undervalued)
High Confidence Gap = 25%+ (strong buy signal)
```

### Momentum Detection Framework

**Dual Momentum Approach**:

1. **Fundamental Momentum** (Primary Filter):
   - **Revenue Growth Acceleration**: Quarter-over-quarter improvement
   - **Earnings Momentum**: EPS growth trends and estimate revisions
   - **Margin Expansion**: Gross/operating margin improvements
   - **Sector-Specific Metrics**:
     - Tech: ARR growth, customer acquisition efficiency
     - Healthcare: Pipeline progression, regulatory milestones

2. **Price Momentum** (Entry Timing):
   - **Post-Earnings Momentum**: Price strength following earnings announcements
   - **Relative Strength**: Performance vs. sector and market indices
   - **Volume Confirmation**: Above-average volume supporting price moves
   - **Technical Indicators**: 
     - 20/50 day moving average crossovers
     - RSI momentum (30-70 range preferred)

**Momentum Scoring System**:
- Fundamental Momentum Score: 0-100 (based on metric improvements)
- Price Momentum Score: 0-100 (based on technical indicators)
- Combined Momentum Threshold: 60+ for entry consideration

### Strategy Execution Framework

**Portfolio Construction**:
- **Maximum Positions**: 20-30 stocks (diversification without over-diversification)
- **Sector Allocation**: 50% Tech, 50% Healthcare (rebalanced quarterly)
- **Position Sizing**: Based on conviction level and volatility
  - High conviction (FVG >25%, Momentum >80): 4-6% position
  - Medium conviction (FVG 15-25%, Momentum 60-80): 2-4% position

**Entry Criteria** (All must be met):
1. Fair Value Gap ≥ 15% (undervalued)
2. Fundamental Momentum Score ≥ 60
3. Price Momentum Score ≥ 60
4. Minimum daily volume $10M
5. Recent earnings announcement (<30 days) with positive reaction

**Exit Criteria**:
- **Profit Target**: Fair value gap closes to <5%
- **Stop Loss**: -15% from entry price
- **Time-Based**: Hold for maximum 12 months if no exit triggered
- **Fundamental Deterioration**: Momentum score drops below 40

**Rebalancing Schedule**:
- **Quarterly**: Full portfolio review aligned with earnings season
- **Monthly**: Momentum score updates and position adjustments
- **Event-Driven**: Immediate review for FDA approvals, major announcements

### Risk Management System

**Position-Level Risk Controls**:
- **Maximum Single Position**: 6% of portfolio
- **Sector Concentration**: Maximum 60% in any single sector
- **Volatility Adjustment**: Position size inversely related to 30-day volatility

**Portfolio-Level Risk Controls**:
- **Maximum Drawdown**: 20% portfolio-wide stop
- **Correlation Monitoring**: Limit positions in highly correlated stocks
- **Liquidity Requirements**: Minimum 10-day average volume for all positions

**Healthcare-Specific Risk Controls**:
- **Binary Event Risk**: Reduced position sizing before FDA decisions
- **Pipeline Concentration**: Maximum 30% in clinical-stage biotech
- **Regulatory Risk**: Monitoring of policy changes affecting drug pricing

### Performance Measurement & Backtesting

**Benchmark Comparisons**:
- **Primary**: S&P 500 Technology and Healthcare sector indices
- **Secondary**: Value factor ETFs (VTV, VBR)
- **Risk-Adjusted**: Sharpe ratio, Sortino ratio, maximum drawdown

**Key Performance Metrics**:
- **Annualized Return**: Target 12-15% (vs. 10% market average)
- **Win Rate**: Target 60%+ of positions profitable
- **Average Holding Period**: 3-6 months
- **Maximum Drawdown**: <15% (vs. 20% market typical)

**Backtesting Framework**:
- **Historical Period**: 5+ years of data
- **Out-of-Sample Testing**: Reserve 20% of data for validation
- **Walk-Forward Analysis**: Quarterly model retraining
- **Survivorship Bias Control**: Include delisted companies in analysis

### Technology Stack & Implementation

**Core Technologies**:
- **Language**: Python 3.9+
- **Data Processing**: pandas, numpy (as documented in /research)
- **Machine Learning**: scikit-learn for momentum modeling
- **Backtesting**: Custom framework with vectorized operations
- **Visualization**: matplotlib, seaborn for performance charts


**Data Pipeline Architecture**:
1. **Data Ingestion**: Automated daily/quarterly data collection
2. **Data Validation**: Pydantic models for schema enforcement
3. **Feature Engineering**: Automated calculation of all momentum metrics
4. **Model Scoring**: Real-time fair value and momentum scoring
5. **Signal Generation**: Automated buy/sell signal creation
6. **Portfolio Management**: Position sizing and risk monitoring

**Deployment Considerations**:
- **Environment**: Local development → Cloud deployment (AWS/GCP)
- **Scheduling**: Daily model updates, quarterly rebalancing
- **Monitoring**: Real-time performance tracking and alerting
- **Compliance**: Audit trail for all trading decisions

### Success Metrics & Milestones

**Phase 1 - Foundation (Months 1-2)**:
- Complete data pipeline implementation
- Basic DCF and momentum models operational
- Historical backtesting framework complete
- Target: 5-year backtest with >12% annual returns

**Phase 2 - Enhancement (Months 3-4)**:
- Institutional fair value integration
- Advanced momentum models with ML
- Risk management system implementation
- Target: Sharpe ratio >1.0, max drawdown <15%

**Phase 3 - Production (Months 5-6)**:
- Live paper trading implementation
- Performance monitoring dashboard
- Automated rebalancing system
- Target: Ready for live capital deployment

**Long-term Success Criteria**:
- **3-Year Performance**: Outperform benchmarks by 200+ basis points annually
- **Risk Management**: Maintain maximum drawdown <15%
- **Consistency**: Positive returns in 70%+ of quarters
- **Scalability**: Handle $1M+ in capital efficiently

This comprehensive strategy combines rigorous fundamental analysis with systematic momentum detection, creating a robust framework for identifying and capitalizing on market inefficiencies in high-growth sectors.

## EXAMPLES:

To provide a real-world model for our project's structure and implementation, we will reference the following open-source quantitative trading framework. Instead of a single strategy, this example provides a comprehensive, production-grade architecture that aligns with our goals.

### Primary Real-World Example: `pfund` Framework

**- Repository**: [https://github.com/PFund-Software-Ltd/pfund](https://github.com/PFund-Software-Ltd/pfund)
**- Description**: `pfund` is a modern, all-in-one algo-trading framework built in Python. It is designed to natively support machine learning models and data engineering best practices. It cleanly separates the components of a trading system, from data handling to strategy execution.

**- Why it is a good example for us**:
    1.  **Comprehensive Structure**: It provides a clear blueprint for building a system that handles backtesting, paper trading, and live trading. This directly maps to our three-phase development plan.
    2.  **Separation of Concerns**: The framework logically divides tasks into a `BacktestEngine` or `TradeEngine`, `Strategy` objects, and `Data` sources. This is a robust architecture we should emulate to keep our code modular and maintainable.
    3.  **Machine Learning Ready**: It is designed from the ground up to integrate machine learning models, which is a core requirement for our strategy's future enhancements (e.g., using ML for momentum scoring).
    4.  **Best Practices**: It demonstrates professional software engineering practices, such as using environment files for configuration (`.env`) and clear, object-oriented design.

**- How we will use it as a reference**:
    - We will model our project's directory structure based on `pfund`'s separation of data, strategies, and core engine logic.
    - We will adopt its object-oriented approach, creating classes for our `Strategy`, `Portfolio`, and `ExecutionHandler`.
    - We will study its backtesting engine to understand how to process historical data, calculate metrics, and avoid common pitfalls like lookahead bias.
    - We will use its `engine.add_strategy(...)` and `strategy.add_data(...)` patterns as inspiration for our own system's API.

By studying and adapting the architectural patterns from `pfund`, we can build a more robust, scalable, and professional-grade system than if we were to start from a simple script.

## DOCUMENTATION

This section provides links to the official documentation for the core technologies and data sources for this project. The AI should refer to these links as the primary source of truth.

### Core Python Libraries

- **Pandas (Data Manipulation and Analysis)**: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
  - *Key Areas*: Time-series functionality, DataFrame manipulation, reading/writing data.
- **NumPy (Numerical Computing)**: [https://numpy.org/doc/](https://numpy.org/doc/)
  - *Key Areas*: Array creation, vectorization, and mathematical operations.
- **Scikit-Learn (Machine Learning)**: [https://scikit-learn.org/stable/documentation.html](https://scikit-learn.org/stable/documentation.html)
  - *Key Areas*: `Pipeline` object, cross-validation, and model APIs (Regression, Classification).
- **Matplotlib (Data Visualization)**: [https://matplotlib.org/stable/contents.html](https://matplotlib.org/stable/contents.html)
  - *Key Areas*: Pyplot interface for creating equity curves, drawdown charts, and performance histograms.
- **Qlib (AI-Oriented Quant Platform)**: [https://qlib.readthedocs.io/en/latest/](https://qlib.readthedocs.io/en/latest/)
  - *Key Areas*: This will be our core framework. We will use its data management, expression engine, and backtesting components.

### Potential Data Providers & APIs

- **Alpha Vantage (Equities & Fundamentals)**: [https://www.alphavantage.co/documentation/](https://www.alphavantage.co/documentation/)
  - *Use For*: Core source for daily market data and quarterly/annual fundamental data.
- **Financial Modeling Prep (Fundamentals & Estimates)**: [https://site.financialmodelingprep.com/developer/docs](https://site.financialmodelingprep.com/developer/docs)
  - *Use For*: Alternative source for fundamentals, analyst estimates, and DCF values.
- **Polygon.io (Real-Time & Historical Data)**: [https://polygon.io/docs](https://polygon.io/docs)
  - *Use For*: High-quality, real-time and historical market data if higher resolution is needed.
- **FRED (Federal Reserve Economic Data)**: [https://fred.stlouisfed.org/docs/api/fred/](https://fred.stlouisfed.org/docs/api/fred/)
  - *Use For*: Fetching economic data such as risk-free interest rates.


## OTHER CONSIDERATIONS:

- **Environment Management**: This project will use a `requirements.txt` file to manage Python dependencies. API keys and other secrets must be stored in a `.env` file and loaded using a library like `python-dotenv`, never hard-coded.
- **Coding Standards**: All Python code should adhere to PEP 8 standards. Use type hints for function signatures to improve code clarity and maintainability.
- **Project Structure**: Never create files directly in the project's root folder. All new code, notebooks, or documentation must be placed in the appropriate sub-directory (e.g., `research/`, `src/`, `notebooks/`).
- **Code Reusability and Refactoring**: Before creating new scripts or functions, always review existing code to identify opportunities for reuse or refactoring. Avoid creating redundant scripts. Prefer modifying and extending existing components to maintain a clean and DRY (Don't Repeat Yourself) codebase.
- **Modularity**: The system should be built in a modular way, separating data sourcing, strategy logic, portfolio construction, and execution into different components or classes, as inspired by the `pfund` framework.
- **Research-Driven Development**: Every component of the strategy (e.g., the specific formula for the momentum score) should be backed by research documented in the `/research` folder. This ensures our development is evidence-based.
- **Adherence to `CLAUDE.md`**: The guiding principles outlined in `CLAUDE.md` must be followed for all development, particularly concerning data validation with `pydantic` and phased, iterative development.
- **No Frontend Required**: Unlike the original template, this project is purely for quantitative research and trading. No HTML/CSS/JS frontend is necessary. The primary interface will be through scripts, logs, and generated plot files.
