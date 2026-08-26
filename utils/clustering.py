import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def find_optimal_k(scaled_df, min_k=2, max_k=10):
    """
    Calculate WCSS / Inertia for K ranging from min_k to max_k to determine optimal clusters.
    """
    wcss = []
    k_values = list(range(min_k, max_k + 1))
    
    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_df)
        wcss.append(float(kmeans.inertia_))
        
    # Automatic recommendation using elbow detection (maximum angle / second derivative distance)
    # Differences between consecutive inertia reductions
    if len(wcss) >= 3:
        diffs = np.diff(wcss)
        diff_ratios = np.diff(diffs)
        # Recommended k corresponds to maximum bend (second derivative peak + offset)
        recommended_idx = np.argmax(diff_ratios) + 1
        recommended_k = k_values[min(recommended_idx, len(k_values) - 1)]
    else:
        recommended_k = 5

    return {
        "k_values": k_values,
        "wcss": [round(val, 2) for val in wcss],
        "recommended_k": int(recommended_k)
    }

def perform_kmeans(df_original, scaled_df, k=5, random_state=42):
    """
    Apply KMeans clustering on scaled features and attach cluster labels to original dataset.
    """
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_df)
    
    df_clustered = df_original.copy()
    df_clustered['Cluster'] = cluster_labels
    
    return df_clustered, kmeans

def generate_cluster_summary(df_clustered):
    """
    Calculate cluster-level aggregate statistics.
    """
    summary = []
    clusters = sorted(df_clustered['Cluster'].unique())
    
    for cluster_id in clusters:
        cluster_data = df_clustered[df_clustered['Cluster'] == cluster_id]
        
        avg_age = round(float(cluster_data['Age'].mean()), 1) if 'Age' in cluster_data.columns else 0
        avg_income = round(float(cluster_data['Annual Income (k$)'].mean()), 1) if 'Annual Income (k$)' in cluster_data.columns else 0
        avg_spending = round(float(cluster_data['Spending Score (1-100)'].mean()), 1) if 'Spending Score (1-100)' in cluster_data.columns else 0
        customer_count = int(len(cluster_data))
        percentage = round((customer_count / len(df_clustered)) * 100, 1)
        
        summary.append({
            "cluster": int(cluster_id),
            "count": customer_count,
            "percentage": percentage,
            "avg_age": avg_age,
            "avg_income": avg_income,
            "avg_spending": avg_spending
        })
        
    return summary

def generate_business_insights(cluster_summary):
    """
    Generate dynamic segment names, behavioral interpretations, and marketing strategies based on cluster stats.
    """
    insights = []
    
    # Calculate overall dataset means for context
    all_incomes = [s['avg_income'] for s in cluster_summary]
    all_spendings = [s['avg_spending'] for s in cluster_summary]
    
    mean_income = np.mean(all_incomes) if all_incomes else 50
    mean_spending = np.mean(all_spendings) if all_spendings else 50
    
    for item in cluster_summary:
        c_id = item['cluster']
        inc = item['avg_income']
        spn = item['avg_spending']
        age = item['avg_age']
        
        # Determine dynamic segment archetype based on income & spending profile
        if inc >= mean_income * 1.1 and spn >= mean_spending * 1.1:
            title = "High Income — High Spending (Target Premium)"
            archetype = "Loyal & Premium Shoppers"
            desc = "High purchasing power and high engagement. These are top-tier customers with strong brand loyalty."
            strategy = "Offer VIP memberships, early access to new collections, exclusive premium rewards, and high-touch customer support."
            badge_color = "success"
        elif inc >= mean_income * 1.1 and spn < mean_spending * 0.9:
            title = "High Income — Low Spending (Conservative High-Earners)"
            archetype = "Potential VIPs / Quality Seekers"
            desc = "High financial capacity but hesitant or picky spenders. They shop selectively."
            strategy = "Run targeted promotional campaigns, highlight luxury value props, provide personalized product recommendations and premium incentives."
            badge_color = "warning"
        elif inc < mean_income * 0.9 and spn >= mean_spending * 1.1:
            title = "Low Income — High Spending (Carefree Spenders)"
            archetype = "Trend-Driven & Impulse Buyers"
            desc = "Moderate or low income but disproportionately high enthusiasm for mall offerings."
            strategy = "Engage with flash sales, discount coupons, trend alert newsletters, flexible payment plans, and loyalty points."
            badge_color = "info"
        elif inc < mean_income * 0.9 and spn < mean_spending * 0.9:
            title = "Low Income — Low Spending (Budget Conscious)"
            archetype = "Frugal / Price-Sensitive"
            desc = "Cautious buyers with lower income and spending scores. Visit primarily for essential needs."
            strategy = "Focus on value promotions, essential product bundles, clearance discounts, and low-friction retention campaigns."
            badge_color = "secondary"
        else:
            title = "Average Income — Average Spending (Mainstream)"
            archetype = "Core Retail Shoppers"
            desc = "Balanced financial profile and steady spending behavior across standard retail categories."
            strategy = "Maintain baseline engagement through standard loyalty programs, seasonal sales, and cross-selling popular merchandise."
            badge_color = "primary"
            
        insights.append({
            "cluster": c_id,
            "title": title,
            "archetype": archetype,
            "description": desc,
            "strategy": strategy,
            "badge_color": badge_color,
            "metrics": item
        })
        
    return insights
