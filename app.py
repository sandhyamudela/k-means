import os
import io
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from utils.preprocessing import load_dataset, validate_dataset, get_dataset_overview, preprocess_data
from utils.clustering import find_optimal_k, perform_kmeans, generate_cluster_summary, generate_business_insights

app = Flask(__name__)
app.config['SECRET_KEY'] = 'customer-segmentation-secret-key-2026'

# Global in-memory storage for current session dataset and clustered results
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Mall_Customers.csv')
CURRENT_DF = None
CLUSTERED_DF = None
KMEANS_MODEL = None

def init_default_dataset():
    global CURRENT_DF
    if os.path.exists(DATASET_PATH):
        df, err = load_dataset(DATASET_PATH)
        if df is not None:
            CURRENT_DF = df

init_default_dataset()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/dataset-overview', methods=['GET'])
def api_dataset_overview():
    global CURRENT_DF
    if CURRENT_DF is None:
        init_default_dataset()
    
    if CURRENT_DF is None:
        return jsonify({"error": "Dataset not loaded."}), 400
        
    overview = get_dataset_overview(CURRENT_DF)
    return jsonify(overview)

@app.route('/api/upload-dataset', methods=['POST'])
def api_upload_dataset():
    global CURRENT_DF, CLUSTERED_DF
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400
        
    df, err = load_dataset(file)
    if err:
        return jsonify({"error": err}), 400
        
    is_valid, msg = validate_dataset(df)
    if not is_valid:
        return jsonify({"error": msg}), 400
        
    CURRENT_DF = df
    CLUSTERED_DF = None
    
    overview = get_dataset_overview(CURRENT_DF)
    return jsonify({"message": "Dataset uploaded and validated successfully!", "overview": overview})

@app.route('/api/elbow', methods=['POST'])
def api_elbow():
    global CURRENT_DF
    if CURRENT_DF is None:
        init_default_dataset()
        
    if CURRENT_DF is None:
        return jsonify({"error": "Dataset unavailable."}), 400
        
    data = request.get_json() or {}
    selected_features = data.get('features', ['Age', 'Annual Income (k$)', 'Spending Score (1-100)'])
    
    is_valid, msg = validate_dataset(CURRENT_DF)
    if not is_valid:
        return jsonify({"error": msg}), 400
        
    df_clean, scaled_df, scaler, summary = preprocess_data(CURRENT_DF, selected_features)
    elbow_res = find_optimal_k(scaled_df, min_k=2, max_k=10)
    
    return jsonify(elbow_res)

@app.route('/api/cluster', methods=['POST'])
def api_cluster():
    global CURRENT_DF, CLUSTERED_DF, KMEANS_MODEL
    if CURRENT_DF is None:
        init_default_dataset()
        
    if CURRENT_DF is None:
        return jsonify({"error": "Dataset unavailable."}), 400
        
    data = request.get_json() or {}
    k = int(data.get('k', 5))
    selected_features = data.get('features', ['Age', 'Annual Income (k$)', 'Spending Score (1-100)'])
    
    if k < 2 or k > 10:
        return jsonify({"error": "K must be between 2 and 10."}), 400
        
    df_clean, scaled_df, scaler, preprocessing_summary = preprocess_data(CURRENT_DF, selected_features)
    df_clustered, model = perform_kmeans(df_clean, scaled_df, k=k, random_state=42)
    
    CLUSTERED_DF = df_clustered
    KMEANS_MODEL = model
    
    cluster_summary = generate_cluster_summary(df_clustered)
    insights = generate_business_insights(cluster_summary)
    
    # Prepare records for frontend charts and table
    records = df_clustered.to_dict(orient="records")
    
    return jsonify({
        "preprocessing_summary": preprocessing_summary,
        "k": k,
        "features": selected_features,
        "cluster_summary": cluster_summary,
        "insights": insights,
        "records": records
    })

@app.route('/api/search-customer', methods=['GET'])
def api_search_customer():
    global CLUSTERED_DF
    customer_id = request.args.get('id', '').strip()
    
    if CLUSTERED_DF is None:
        return jsonify({"error": "Run clustering first before searching customers."}), 400
        
    if not customer_id:
        return jsonify({"error": "Please provide a Customer ID."}), 400
        
    # Search by CustomerID if present or row index
    match = None
    if 'CustomerID' in CLUSTERED_DF.columns:
        res = CLUSTERED_DF[CLUSTERED_DF['CustomerID'].astype(str) == customer_id]
        if not res.empty:
            match = res.iloc[0].to_dict()
            
    if match is None and customer_id.isdigit():
        idx = int(customer_id)
        if 0 <= idx < len(CLUSTERED_DF):
            match = CLUSTERED_DF.iloc[idx].to_dict()
            
    if match is None:
        return jsonify({"error": f"Customer ID '{customer_id}' not found."}), 404
        
    # Get associated insight for cluster
    cluster_summary = generate_cluster_summary(CLUSTERED_DF)
    insights = generate_business_insights(cluster_summary)
    
    c_id = int(match.get('Cluster', 0))
    insight_for_c = next((i for i in insights if i['cluster'] == c_id), None)
    
    return jsonify({
        "customer": match,
        "insight": insight_for_c
    })

@app.route('/api/download-csv', methods=['GET'])
def api_download_csv():
    global CLUSTERED_DF, CURRENT_DF
    target_df = CLUSTERED_DF if CLUSTERED_DF is not None else CURRENT_DF
    
    if target_df is None:
        return jsonify({"error": "No data available for download."}), 400
        
    buffer = io.BytesIO()
    target_df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='customer_segments.csv'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='127.0.0.1', port=port)


