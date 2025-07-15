# A Comprehensive Guide to Using Qlib for Quantitative Trading

This document provides a comprehensive overview and practical guide for using the `qlib` framework, tailored to our project's needs. It synthesizes information from the official documentation, GitHub repositories, and community tutorials.

## 1. Core Philosophy & Why We Are Using It

`Qlib` is an end-to-end, AI-oriented quantitative investment platform from Microsoft. We have chosen to pivot our project to build upon `qlib` for several key reasons:

-   **Accelerated Development**: It provides a robust, pre-built infrastructure for data management, backtesting, and analysis, saving us from reinventing the wheel.
-   **Focus on Alpha**: We can concentrate on what makes our strategy unique—defining our specific fair value and momentum factors—rather than on building and debugging infrastructure.
-   **Production-Ready**: It is an industry-tested, standardized platform designed for quant research, which is more robust and scalable than a custom-built script.
-   **AI-Oriented**: It is designed from the ground up to integrate machine learning models, aligning with the long-term vision of our strategy.

## 2. Phase 1: Installation and Data Preparation

Our first phase is to set up the environment and prepare all necessary data.

### Installation

`Qlib` can be installed via pip. It is highly recommended to do this within a dedicated virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install qlib
pip install pyqlib
```

### Data Preparation: The `qlib` Way

`Qlib` relies on a highly efficient, proprietary binary format for storing data. All data, whether it's pricing or fundamental, must be converted to this format before it can be used.

**A. Downloading Default Market Data:**

`Qlib` provides a script to download daily market data (from Yahoo Finance) for US and Chinese markets.

```bash
# Make sure you are in the project root directory before running
# This script downloads data to `~/.qlib/qlib_data/` by default.
python -m qlib.run.get_data qlib_data --target_dir ~/.qlib/qlib_data/us_data --region us
```
*Note: We will need to decide on a centralized location for this data within our project structure later.*

**B. Integrating Custom Fundamental Data (Crucial for our Strategy):**

This is the most critical step for our value-based strategy. We need to load fundamental data (e.g., Book Value, Revenue, Earnings from Alpha Vantage) into `qlib`.

The process involves two steps:
1.  **Format the data into a specific CSV structure.**
2.  **Use `qlib`'s script to "dump" the CSVs into its binary format.**

**Step B.1: Formatting the CSV Data**

We must create a CSV file for *each* fundamental factor. For example, to add `BookValue` and `Revenue`, we would create `book_value.csv` and `revenue.csv`.

Each file must have the following format:
-   No header row.
-   Column 1: `datetime` (e.g., `2023-01-01`)
-   Column 2: `instrument` (e.g., `AAPL`)
-   Column 3: `value` (the actual book value or revenue figure)

**Example `revenue.csv`:**
```
2022-12-31,AAPL,117154000000
2022-12-31,MSFT,52747000000
2023-03-31,AAPL,94836000000
2023-03-31,MSFT,52857000000
...
```

**Step B.2: Dumping the Data into Qlib Format**

Once the CSVs are prepared, we use the `dump_bin.py` script provided in the `qlib` library's scripts folder. We will need to create a script in our project to automate this.

**Conceptual Script (`scripts/load_fundamentals.py`):**
```python
import pandas as pd
from qlib.data.dump_bin import DumpData

# Assume we have a function to get fundamental data from Alpha Vantage
# and it returns a DataFrame in the format: ['date', 'ticker', 'revenue', 'book_value']
fundamental_df = get_data_from_alpha_vantage() 

# Directory where qlib expects the CSVs
csv_path = 'path/to/fundamental_csvs' 

# Directory to store the final qlib binary data
qlib_dir = 'path/to/custom_qlib_data/features' 

# Create separate CSVs for each factor
for factor in ['revenue', 'book_value']:
    factor_df = fundamental_df[['date', 'ticker', factor]].copy()
    factor_df.to_csv(f"{csv_path}/{factor.lower()}.csv", index=False, header=False)

# Use DumpData to convert all CSVs in that folder to qlib format
# The 'include' pattern tells it which files to process.
dumper = DumpData(csv_path=csv_path, qlib_dir=qlib_dir, include_fields=r'revenue,book_value')
dumper.dump()
```

This process creates binary files for our custom factors in the specified `qlib_dir`, making them available to the entire framework.

## 3. Phase 2: Strategy Implementation

With our data prepared, we can now implement our strategy logic.

### `qlib.init()`

Every script or notebook must start by initializing `qlib` and telling it where to find the data.

```python
import qlib
from qlib.constant import REG_US

# Point qlib to the directories containing BOTH the market data and our custom features
qlib.init(
    provider_uri='path/to/market_qlib_data',  # The default data
    expression_provider={
        "class": "LocalExpressionProvider",
        "kwargs": {
            "qlib_dir": "path/to/custom_qlib_data"  # Our fundamental data
        }
    },
    region=REG_US
)
```

### The Expression Engine: Defining Factors

This is the core of `qlib`'s power. We don't write procedural code to calculate factors; we define them as text-based expressions. `qlib`'s engine compiles and executes these very efficiently.

`$` indicates a factor (a column in the data). `$` followed by a name is a built-in factor (e.g., `$close`, `$volume`). `$` followed by a custom name in lowercase refers to our custom fundamental factors (e.g., `$revenue`, `$bookvalue`).

**Example Factors for Our Strategy:**

-   **Price Momentum (6-month return)**: `(Ref($close, -126) / $close) - 1`
-   **Book-to-Price Ratio (Value Factor)**: `$bookvalue / ($close * $sharesout)` (assuming we add shares outstanding as a custom factor)
-   **A more complex factor (e.g., 20-day moving average of close)**: `Mean($close, 20)`

### The Workflow: `workflow_config.yaml`

`qlib` automates the entire research pipeline (data processing -> model training -> backtesting -> evaluation) using a single YAML configuration file.

A typical `workflow_config.yaml` has three main sections:

1.  **`qlib_init`**: The same parameters we used in the `qlib.init()` call.
2.  **`market`**: Defines the stock universe (e.g., `csi300`, or a custom list).
3.  **`data_handler`**: This is where we define our features (`factors`) and the prediction target (`label`).
4.  **`task`**: Defines the model to use (e.g., `LightGBM`) and the backtesting settings.

**Simplified Example `workflow_config.yaml`:**
```yaml
qlib_init:
    provider_uri: ...
    expression_provider: ...
    region: REG_US

market: csi300 # Or a custom market definition

data_handler:
    class: DataHandlerLP
    kwargs:
        instruments: market
        start_time: 2010-01-01
        end_time: 2020-12-31
        data_loader:
            class: QlibDataLoader
            kwargs:
                config:
                    # Define our factors here!
                    feature:
                        - "(Ref($close, -126) / $close) - 1"  # Momentum
                        - "$bookvalue / ($close * $sharesout)" # Value
                        - "Mean($close, 20)"
                # Define our prediction target (e.g., return over the next 5 days)
                label:
                    - "(Ref($close, -5) / $close) - 1"

task:
    model:
        class: LightGBM
        module_path: qlib.contrib.model.gbdt
    dataset:
        class: DatasetH
        module_path: qlib.data.dataset
    record:
        - class: SignalRecord
          module_path: qlib.workflow.record_temp
        - class: PortAnaRecord
          module_path: qlib.workflow.record_temp
```

### Running a Backtest

Once the config file is ready, running the entire workflow is a single command:

```bash
qrun /path/to/our/workflow_config.yaml
```

`qlib` will then:
1.  Load the data.
2.  Calculate all the factors we defined.
3.  Train the LightGBM model to predict the label based on our factors.
4.  Generate predictions for each stock on each day.
5.  Create a portfolio based on these predictions (e.g., long the top 10%, short the bottom 10%).
6.  Calculate and print detailed performance metrics (Sharpe ratio, max drawdown, etc.).
``` 