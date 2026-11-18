# FlowMind AI 🚀
### Sales Intelligence & Revenue Forecasting Platform

**FlowMind AI** is a data-driven application designed to help businesses understand their sales performance, analyze retail transactions, and forecast future revenue using Machine Learning.

The platform combines data processing, business analytics, database management, and predictive modeling in one application.

---

## 🎯 Project Objectives

The main objectives of FlowMind AI are to:

- Transform raw sales data into meaningful business insights.
- Monitor sales performance through key performance indicators (KPIs).
- Analyze retail transactions and customer purchasing patterns.
- Identify business trends and product performance.
- Predict future revenue using Machine Learning.
- Support data-driven business decision-making.

## ✨ Key Features

### 1. Sales Data Management
- Import sales data from CSV files.
- Store and manage sales records.
- Integrate sales data with a PostgreSQL database.

### 2. Sales Analytics
- Calculate total sales and revenue.
- Analyze average sales.
- Identify best-selling products.
- Monitor business performance using analytical indicators.

### 3. Retail Analytics
- Analyze retail transaction data.
- Explore product and country-level performance.
- Identify sales trends and purchasing patterns.
- Extract useful information from historical transactions.

### 4. Revenue Forecasting
- Apply Machine Learning techniques to historical sales data.
- Predict future revenue.
- Evaluate forecasting performance using Mean Absolute Error (MAE).
- Compare predictive models with a baseline approach.

### 5. Interactive Dashboard
- Visualize business performance.
- Explore sales indicators and analytical results.
- Present insights in an accessible interface.

---

## 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend & Dashboard | Streamlit |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Processing | Pandas |
| Machine Learning | Scikit-learn |
| Data Validation | Pydantic |
| Database Configuration | Python-dotenv |
| API Server | Uvicorn |

---

## 🏗️ Project Architecture

FlowMind AI follows a modular architecture separating the backend, data processing, database operations, and dashboard.

```text
FlowMind-AI/
│
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── analytics.py
│       ├── csv_service.py
│       ├── database.py
│       ├── forecasting.py
│       ├── init_db.py
│       ├── main.py
│       ├── models.py
│       ├── schemas.py
│       └── test_db.py
│
├── frontend.py
├── import_retail_data.py
├── prepare_data.py
├── .gitignore
└── README.md
```

### Main Components

- **main.py:** Defines the FastAPI application and API endpoints.
- **database.py:** Manages the PostgreSQL connection and database sessions.
- **models.py:** Defines database models.
- **schemas.py:** Defines data validation schemas.
- **analytics.py:** Contains sales analytics and KPI calculations.
- **csv_service.py:** Handles CSV data import.
- **forecasting.py:** Contains revenue forecasting logic.
- **init_db.py:** Initializes database tables.
- **frontend.py:** Provides the interactive Streamlit dashboard.
- **prepare_data.py:** Handles data preparation.
- **import_retail_data.py:** Handles retail dataset import.

---

## 📊 Dataset

The project uses historical retail sales data, including the **UCI Online Retail Dataset**.

The dataset contains information such as:

- Invoice numbers
- Product descriptions
- Quantities
- Invoice dates
- Unit prices
- Customer identifiers
- Countries

The data is prepared and processed before being stored and analyzed.

---

## ⚙️ Installation and Setup

### Prerequisites

Make sure you have installed:

- Python 3.10 or later
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd FlowMind-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

If a `requirements.txt` file is provided:

```bash
pip install -r requirements.txt
```

### 5. Configure PostgreSQL

Create a PostgreSQL database named:

```sql
CREATE DATABASE flowmind_db;
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=flowmind_db
DB_USER=postgres
DB_PASSWORD=YOUR_DATABASE_PASSWORD
```

**Important:** Never upload your `.env` file or database credentials to GitHub.

### 7. Initialize the Database

```bash
python -m backend.app.init_db
```

---

## ▶️ Running the Application

### Start the FastAPI Backend

```bash
uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### Access the API Documentation

FastAPI automatically generates interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit Dashboard

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run frontend.py
```

---

## 🔮 Machine Learning & Revenue Forecasting

FlowMind AI integrates Machine Learning to analyze historical revenue and generate future predictions.

The forecasting process includes:

1. Data preparation and cleaning.
2. Aggregation of sales into daily revenue.
3. Feature preparation for predictive modeling.
4. Model training and evaluation.
5. Revenue prediction for future periods.

**Evaluation Metric:**

Mean Absolute Error (MAE) is used to measure the average absolute difference between actual and predicted revenue.

\[
MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i-\hat{y}_i|
\]

A lower MAE indicates better predictive accuracy.

---

## 🔐 Security and Configuration

- Database credentials are stored in environment variables.
- Sensitive configuration files are excluded from version control.
- Database access is managed through SQLAlchemy.
- Input data is processed before being stored.

---

## 🚀 Future Improvements

Potential future developments include:

- Advanced sales forecasting models.
- Customer segmentation.
- Customer behavior analysis.
- Sales anomaly detection.
- More interactive visualizations.
- Automated business reports.
- Deployment to a cloud platform.

---

## 👩‍💻 Author

**Khadija Aglagal**

Engineering Student in Data Science, Big Data & Artificial Intelligence.

**Project:** FlowMind AI

---

## 📌 Project Status

Developed as a practical Data Science and AI project combining backend development, data analytics, database management, and Machine Learning.

