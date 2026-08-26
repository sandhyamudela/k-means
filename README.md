# Customer Segmentation using K-Means Clustering

> **Task 02: Retail Customer Behavioral Segmentation using Unsupervised Machine Learning**

An end-to-end, production-ready machine learning web application built with **Flask**, **Scikit-Learn**, **Pandas**, and **Plotly.js**. Designed for portfolio demonstrations, college project evaluations, and technical interviews.

---

## 📌 Problem Statement

In retail and e-commerce, understanding customer purchasing behavior is critical for personalized marketing, churn reduction, and maximizing Customer Lifetime Value (CLV). Traditional broad marketing campaigns waste budget by treating all customers equally. 

**Customer Segmentation** uses unsupervised machine learning to group customers with similar financial profiles and shopping habits, enabling data-driven retail strategies.

---

## 🎯 Key Objectives

- Perform exploratory data analysis and data preprocessing on the **Mall Customer Dataset**.
- Standardize features using `StandardScaler` to ensure unbiased distance metrics.
- Implement the **Elbow Method** (WCSS / Inertia calculation) to identify optimal cluster count ($K$).
- Train a **K-Means Clustering** model using `scikit-learn`.
- Visualize 2D and grouped cluster distributions dynamically using interactive **Plotly.js** charts.
- Generate automated **Business Insights & Marketing Strategies** based on cluster statistics.
- Provide interactive features: CSV upload validation, customer search by ID, cluster filtering, and CSV report downloads.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript (ES6+), Plotly.js |
| **Backend** | Python 3.14+, Flask Web Framework |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, StandardScaler, KMeans |
| **Data Format** | CSV (`Mall_Customers.csv`) |
| **Notebook** | Jupyter Notebook (`customer_segmentation.ipynb`) |

---

## 📊 Dataset Overview (`Mall_Customers.csv`)

The dataset contains 200 records of mall shoppers with 5 key features:

1. `CustomerID`: Unique identifier for each customer.
2. `Gender`: Categorical variable (`Male` / `Female`).
3. `Age`: Customer age in years.
4. `Annual Income (k$)`: Customer annual income in thousands of dollars.
5. `Spending Score (1-100)`: Score assigned by the mall based on customer behavior and purchase history.

---

## 🔄 Machine Learning Workflow / Methodology

```
Data Collection (Mall_Customers.csv)
       ↓
Data Preprocessing & Audit (Duplicates & Missing Values)
       ↓
Feature Selection & Standard Scaling (StandardScaler)
       ↓
Elbow Method Analysis (WCSS / Inertia across K=2..10)
       ↓
K-Means Clustering Execution (Scikit-Learn KMeans)
       ↓
Dynamic Cluster Assignment & Statistics
       ↓
Interactive Visualization (Plotly Scatter & Bar Plots)
       ↓
Automated Business Insights & Marketing Strategies
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Clone / Open Project Directory
```bash
cd /Users/sandhya/Desktop/k-means
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Flask Web Application
```bash
python app.py
```

### 5. Access Local Web Application
Open your browser and navigate to:
```
http://127.0.0.1:5001
```

---

## 💡 Customer Segments & Business Insights

When trained with $K=5$, the algorithm automatically identifies 5 distinct customer profiles:

1. **Target / Premium Shoppers** (High Income — High Spending Score):
   - *Strategy*: VIP rewards, exclusive previews, luxury product upsells.
2. **Conservative High-Earners** (High Income — Low Spending Score):
   - *Strategy*: Targeted campaigns, premium incentives, luxury value propositions.
3. **Carefree / Impulse Spenders** (Low Income — High Spending Score):
   - *Strategy*: Flash sales, trend alerts, affordable loyalty programs.
4. **Budget Conscious** (Low Income — Low Spending Score):
   - *Strategy*: Value discounts, essential product bundles, clearance offers.
5. **Mainstream Shoppers** (Average Income — Average Spending Score):
   - *Strategy*: General seasonal promotions, cross-selling popular inventory.

---

## 🚀 Future Enhancements

- Integration of **RFM Analysis** (Recency, Frequency, Monetary value).
- Implementation of **DBSCAN** & **Hierarchical Agglomerative Clustering** for comparison.
- Real-time customer recommendation engine.
- Customer Lifetime Value (CLV) predictive modeling.

---

## 📜 License & Acknowledgments

Built for SkillCraft Technology Task 02 & Educational Machine Learning Demonstrations.
