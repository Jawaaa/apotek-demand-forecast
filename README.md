# Pharmacy Demand Forecast

**A weekly medicine demand forecasting system using LSTM** — an end-to-end application built with FastAPI, SQLite, and Streamlit to forecast medicine demand by therapeutic category and provide restocking recommendations.

## Background

Pharmacies face two major inventory challenges: **stockouts**, which can lead to lost sales, and **overstocking**, which ties up capital and increases the risk of medicine expiration.

This project aims to answer a key operational question:

**"Which medicines should be restocked next week, and how much stock is needed?"**

## Dataset

- **Source:** Indonesian pharmacy transaction data (`sales.sql`)
- **Period:** January 1, 2015 – December 31, 2015
- **Cleaned dataset:** 410,536 transaction records covering 2,162 unique medicines
- **Categorization:** Medicines grouped into 12 therapeutic categories
- **Aggregation:** Weekly demand, from Monday to Sunday, with sales summed for each category
- **Time series:** 53 weeks per category, with no weeks dropped
- **Partial weeks:** Two partial weeks at the end of the dataset were retained and flagged accordingly

## Methodology

The dataset was split chronologically into training, validation, and test sets. The validation set covered 8 weeks, while the test set covered 13 weeks.

Hyperparameter tuning was performed using a grid search across 24 configurations. The test set was reserved exclusively for final model evaluation.

**Best LSTM configuration:**

```python
{
    'lookback': 8,
    'units': 32,
    'lr': 0.005,
    'dropout': 0.2
}
```

## Model Performance

The following results were obtained on the test set.

| Model | RMSE | MAPE (%) |
|---|---:|---:|
| Naive (Previous Week) | 1090.30 | 16.44 |
| Moving Average (Window = 2, Initial) | 903.80 | 14.40 |
| Moving Average (Window = 4, Best) | 910.20 | 13.80 |
| Linear Regression (Lag = 2) | 1079.30 | 13.79 |
| LSTM (Before Tuning) | 856.40 | 13.12 |
| LSTM (After Tuning) | 1168.60 | 15.92 |

### Key Findings

- **LSTM before tuning achieved the best overall MAPE** of 13.12% among the evaluated models.
- The performance difference between the untuned LSTM and the best Moving Average baseline was **-2.12 percentage points in MAPE**, with a 95% bootstrap confidence interval of [-3.74, -0.21].
- LSTM outperformed the Moving Average baseline in 5 out of 12 therapeutic categories.
- The average week-to-week autocorrelation was 0.45.
- The reference MAPE for a constant-level prediction baseline was 11.6%, indicating that the dataset's limited temporal information presents a forecasting challenge.
- Hyperparameter tuning did not improve test performance, highlighting the importance of validation strategies and careful model selection.

**Note:** The dataset covers only approximately one year, limiting the model's ability to learn longer-term seasonal patterns.

## Key Features

| Feature | Description |
|---|---|
| Dashboard | Overview of restocking recommendations across all therapeutic categories |
| Forecasting | LSTM-based demand predictions for each category |
| Model Performance | Model evaluation metrics and comparisons against baseline models |
| Inventory Analysis | Upload sales data and analyze potential stockout risks |
| Prediction History | Store and review historical predictions from the database |

## Tech Stack

- **Programming Language:** Python 3.11
- **Machine Learning:** TensorFlow / Keras (LSTM)
- **Backend API:** FastAPI, Uvicorn
- **Database:** SQLite, SQLAlchemy
- **Frontend Dashboard:** Streamlit, Plotly
- **Testing:** Pytest
- **CI/CD:** GitHub Actions

## Getting Started

### Prerequisites

- Python 3.11
- Git

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Jawaaa/apotek-demand-forecast.git
   cd apotek-demand-forecast
   ```

2. Create and activate a virtual environment:

   **Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS / Linux:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the FastAPI backend in Terminal 1:

```bash
uvicorn api.main:app --reload --port 8000
```

Start the Streamlit dashboard in Terminal 2:

```bash
streamlit run ui/app.py
```

### Running Tests

Run the API tests with Pytest:

```bash
pytest tests/test_api.py -v
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health status |
| GET | `/categories` | Retrieve the list of 12 therapeutic categories |
| POST | `/predict` | Generate demand forecasts and restocking recommendations |
| GET | `/history` | Retrieve historical prediction records |

## Limitations

1. **Limited historical data:** The dataset covers only 53 weeks, or approximately one year.
2. **Symmetric error assumptions:** MAPE treats overestimation and underestimation symmetrically, although their business costs may differ.
3. **Keyword-based categorization:** Medicine categories are assigned using keyword-based rules, which may introduce classification errors.
4. **No actual inventory integration:** Restocking recommendations are not yet connected to real-time inventory levels.

## Future Improvements

- Incorporate 2–3 years of historical data to capture seasonal patterns.
- Add calendar features, including holidays and other relevant demand drivers.
- Integrate real-time inventory data to improve restocking recommendations.
- Implement authentication and access control.
- Deploy the application to a cloud platform.
- Containerize the application using Docker.
- Add model and application monitoring to track forecasting performance over time.

## Author

**Zahwa Rizzi Ani**

Final Project — Data Science & AI Machine Learning Bootcamp, Dibimbing (Batch 42)

GitHub: [Jawaaa](https://github.com/Jawaaa)