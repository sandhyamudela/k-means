import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

REQUIRED_COLUMNS = ['Age', 'Annual Income (k$)', 'Spending Score (1-100)']

def load_dataset(filepath_or_buffer):
    """
    Load dataset from CSV file or buffer.
    """
    try:
        df = pd.read_csv(filepath_or_buffer)
        return df, None
    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}"

def validate_dataset(df):
    """
    Validate that dataset contains required numerical features for clustering.
    """
    if df is None or df.empty:
        return False, "Dataset is empty."
    
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        return False, f"Missing required column(s): {', '.join(missing_cols)}"
    
    return True, "Dataset structure is valid."

def get_dataset_overview(df):
    """
    Generate dataset summary metrics and preview rows.
    """
    if df is None or df.empty:
        return {}
    
    overview = {
        "num_rows": int(len(df)),
        "num_columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "missing_per_column": df.isnull().sum().to_dict(),
        "preview_rows": df.head(10).to_dict(orient="records"),
        "kpi": {
            "total_customers": int(len(df)),
            "avg_age": round(float(df['Age'].mean()), 1) if 'Age' in df.columns else 0,
            "avg_income": round(float(df['Annual Income (k$)'].mean()), 1) if 'Annual Income (k$)' in df.columns else 0,
            "avg_spending": round(float(df['Spending Score (1-100)'].mean()), 1) if 'Spending Score (1-100)' in df.columns else 0
        }
    }
    return overview

def preprocess_data(df, selected_features=None):
    """
    Clean dataset, encode categorical variables, and scale selected features.
    """
    if selected_features is None:
        selected_features = REQUIRED_COLUMNS
    
    # Copy dataset
    df_clean = df.copy()
    
    # Original stats
    original_records = len(df_clean)
    missing_before = df_clean[selected_features].isnull().sum().sum()
    
    # Drop duplicates
    df_clean = df_clean.drop_duplicates()
    duplicates_removed = original_records - len(df_clean)
    
    # Fill missing values if any
    for col in selected_features:
        if col in df_clean.columns and df_clean[col].isnull().sum() > 0:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            
    # Standardize numerical features
    scaler = StandardScaler()
    scaled_matrix = scaler.fit_transform(df_clean[selected_features])
    scaled_df = pd.DataFrame(scaled_matrix, columns=selected_features, index=df_clean.index)
    
    summary = {
        "original_records": original_records,
        "missing_values": int(missing_before),
        "duplicates_removed": duplicates_removed,
        "features_selected": selected_features,
        "records_used": len(df_clean)
    }
    
    return df_clean, scaled_df, scaler, summary
