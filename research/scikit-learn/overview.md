# Scikit-Learn for Quantitative Finance

`scikit-learn` is the most popular machine learning library in Python. Its power lies in its simple, consistent API and its tools for building robust data processing and modeling workflows.

## 1. The Core Philosophy: A Consistent API

`scikit-learn` is built around a consistent interface for all its "objects":

-   **Estimator**: The base object. It learns from data.
    -   `estimator.fit(data, labels)`: The core training method.
-   **Predictor**: An estimator that can make predictions.
    -   `predictor.predict(new_data)`: Makes predictions on new data.
-   **Transformer**: An estimator that can preprocess data.
    -   `transformer.transform(new_data)`: Applies a learned transformation.
    -   `transformer.fit_transform(data, labels)`: A convenience method that calls `fit` then `transform`.

This consistency makes it easy to swap out different models and preprocessing steps.

## 2. The Golden Rule: Preventing Data Leakage

When building a predictive model, the single most important rule is to **never let your training process see the test (or validation) data.** When information from outside the training set influences the model, it's called **data leakage**.

This is especially dangerous during preprocessing.

### The Wrong Way: Leaking Information
Imagine you want to scale your features (e.g., stock returns) using `StandardScaler`, which centers the data by subtracting the mean and scaling by the standard deviation.

```python
# The WRONG way to do it
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Your features and labels
X, y = get_some_financial_data() 

# This is wrong! The scaler learns the mean/std from the ENTIRE dataset.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Now, when you split, the training set has already been influenced
# by the test set's statistical properties.
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y) 

# Your model's performance on X_test will be unrealistically good.
```
Your model will appear to perform better than it will in the real world because it was implicitly given hints about the data it was being tested on.

## 3. The Solution: `scikit-learn` Pipelines

A `Pipeline` is an object that chains together multiple steps (transformers and a final estimator). It ensures that data is transformed and fit correctly, especially during cross-validation, preventing leakage.

### The Right Way: Using a Pipeline
The pipeline ensures that `fit` is only ever called on the training data passed to it. The validation/test data is only ever passed to `transform`.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

X, y = get_some_financial_data()
X_train, X_test, y_train, y_test = train_test_split(X, y)

# 1. Define the steps in your workflow
pipeline = Pipeline([
    ('scaler', StandardScaler()),              # First, scale the data
    ('regressor', LinearRegression())          # Then, fit the model
])

# 2. Fit the ENTIRE pipeline on the training data
# This correctly calls scaler.fit_transform() on X_train
# and then regressor.fit() on the transformed training data.
pipeline.fit(X_train, y_train)

# 3. Evaluate on the test data
# This correctly calls scaler.transform() on X_test (NO re-fitting)
# and then regressor.predict() on the transformed test data.
score = pipeline.score(X_test, y_test)

print(f"Model R^2 score: {score:.4f}")
```
Using a `Pipeline` is not just a best practice; it is essential for sound machine learning research.

## 4. Common Models for Finance

While there are many models, a few are excellent starting points for financial prediction tasks.

-   **Linear Models**:
    -   `LinearRegression`: The simplest model. Good for a baseline.
    -   `Ridge`, `Lasso`, `ElasticNet`: These are regularized linear models that help prevent overfitting by penalizing large coefficients. `Lasso` is particularly useful as it can perform feature selection by forcing some coefficients to zero.

-   **Tree-Based Ensembles**:
    -   `RandomForestRegressor`/`RandomForestClassifier`: An ensemble of decision trees. They are robust, handle non-linear relationships well, and are less prone to overfitting than a single decision tree.
    -   `GradientBoostingRegressor`/`GradientBoostingClassifier`: Builds trees sequentially, where each new tree corrects the errors of the previous one. Often very high-performing, but can be more sensitive to parameter tuning.

When starting a project, it's often best to begin with a simple, interpretable model like `Ridge` or `Lasso` to establish a baseline before moving to more complex models like `RandomForest`. 