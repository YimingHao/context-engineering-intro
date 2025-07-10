### 📝 Guiding Principles for a Solo Quant Project

This document outlines the best practices and conventions for building a quantitative analysis project. As a solo developer, these guidelines will help maintain code quality, ensure reproducibility, and streamline the development process.

### 🔄 Project Awareness & Context

- **Documentation is a source of truth**: Your knowledge may be out of date. Always refer to the latest documentation for any third-party APIs or libraries. Use provided documentation as the source of truth.
- **Iterative Development**: Structure work into phases like `prototype` and `production-ready`. Start with a simple, working model and progressively add complexity and features.
- **Use `pydantic` for data validation**: Ensure that data coming from external sources conforms to expected schemas.
- **Use `python_dotenv` and `load_env()`** for environment variables, especially for API keys and database credentials.
- **Refer to the `/research/` directory**: Before implementing any feature that uses a third-party API or a complex library, check the relevant documents in the `/research/` directory.

### 🧱 Code Structure & Modularity

- **Keep files focused**: Aim for smaller, more focused files. If a file grows too large (e.g., over 500 lines), consider refactoring and splitting it into smaller modules.
- **Organize code logically**: Group code by feature or responsibility (e.g., `data_sourcing`, `feature_engineering`, `modeling`, `backtesting`).
- **Use clear, consistent imports**: Prefer absolute imports for clarity.
- **Configuration Management**: Store configuration (e.g., model parameters, data paths) in a separate, easily accessible format (e.g., YAML, JSON, or a dedicated Python file).

### 📈 Quantitative Development & Data

- **Leverage core libraries**: Use `numpy` and `pandas` for numerical operations and data manipulation. Prioritize vectorized operations for performance.
- **Data is paramount**:
    - **Sourcing**: Clearly document and script the process of obtaining data.
    - **Validation**: Implement checks to ensure data quality (e.g., checking for NaNs, outliers, correct data types).
    - **Storage**: Use appropriate storage for your data (e.g., CSV, Parquet, a database).
- **Modeling**:
    - Clearly separate feature engineering from modeling logic.
    - Document model assumptions and parameters.

### 📜 Backtesting & Validation

- **Implement a robust backtesting engine**: This is crucial for evaluating strategy performance. It should handle historical data, simulate trading, and calculate performance metrics.
- **Avoid lookahead bias**: Ensure your backtesting logic does not use future information.
- **Key Metrics**: Track standard performance metrics like Sharpe ratio, Sortino ratio, max drawdown, and CAGR.
- **Walk-forward analysis**: Use walk-forward validation or other out-of-sample testing methods to avoid overfitting.

### 📊 Visualization

- **Visualize your results**: Use libraries like `matplotlib`, `seaborn`, or `plotly` to plot results.
- **Standard plots**: Create standard visualizations for your analysis, such as equity curves, return distributions, and performance metric tables.

### 🧪 Testing & Reliability

- **Write unit tests**: Use `pytest` to write unit tests for your functions, especially for data transformations, feature calculations, and modeling logic.
- **Test coverage**:
    - Test for expected use cases.
    - Test edge cases (e.g., empty dataframes, unexpected values).
    - Test for failure cases (e.g., invalid inputs).
- **Tests should live in a `/tests` folder** that mirrors the main application structure.

### ✅ Task Management

- **Use `TASK.md`**: Keep a `TASK.md` file to track your to-do list, completed tasks, and ideas. This helps maintain focus and track progress.

### 📎 Style & Conventions

- **Use Python**: The primary language for this project is Python.
- **Follow PEP8**: Use a linter and formatter like `black` or `ruff` to maintain a consistent style.
- **Type Hinting**: Use type hints for all function signatures.
- **Docstrings**: Write Google-style docstrings for every function to explain its purpose, arguments, and return values.
  ```python
  def example_function(param1: int) -> str:
      """A brief summary of the function.

      Args:
          param1: A description of the parameter.

      Returns:
          A description of the return value.
      """
  ```

### 🧠 AI Behavior Rules

- **Never assume missing context**: Ask for clarification if a request is ambiguous.
- **Verify before using**: Do not hallucinate libraries or functions. Confirm that packages are installed and that functions exist.
- **Check file paths**: Always confirm that file paths and module names are correct before referencing them.

### 🎨 Design & UI

- If a UI or dashboard is needed (e.g., using Streamlit, Dash, or FastAPI), refer to `designsystem.md` for a consistent look and feel. The goal is a clean, functional interface for displaying results.
