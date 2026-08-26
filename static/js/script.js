/**
 * Customer Segmentation Dashboard JavaScript
 * Handles API calls, Plotly interactive chart rendering, UI state updates, search, and filtering.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Global state
    let globalOverview = null;
    let globalClusteringData = null;

    // Element references
    const kpiTotalCustomers = document.getElementById('kpiTotalCustomers');
    const kpiAvgAge = document.getElementById('kpiAvgAge');
    const kpiAvgIncome = document.getElementById('kpiAvgIncome');
    const kpiAvgSpending = document.getElementById('kpiAvgSpending');
    const kpiNumClusters = document.getElementById('kpiNumClusters');

    const metaRows = document.getElementById('metaRows');
    const metaCols = document.getElementById('metaCols');
    const metaMissing = document.getElementById('metaMissing');
    const metaColumnNames = document.getElementById('metaColumnNames');

    const prepOriginal = document.getElementById('prepOriginal');
    const prepMissing = document.getElementById('prepMissing');
    const prepDuplicates = document.getElementById('prepDuplicates');
    const prepRecords = document.getElementById('prepRecords');

    const fileUploadInput = document.getElementById('fileUploadInput');
    const uploadStatusMsg = document.getElementById('uploadStatusMsg');
    const runClusteringBtn = document.getElementById('runClusteringBtn');
    const runElbowBtn = document.getElementById('runElbowBtn');
    const kValueInput = document.getElementById('kValueInput');
    const recommendedKBadge = document.getElementById('recommendedKBadge');

    const filterClusterScatter = document.getElementById('filterClusterScatter');
    const filterClusterTable = document.getElementById('filterClusterTable');
    const searchCustomerIdInput = document.getElementById('searchCustomerIdInput');
    const searchCustomerBtn = document.getElementById('searchCustomerBtn');
    const searchResultCard = document.getElementById('searchResultCard');
    const dataTableBody = document.getElementById('dataTableBody');
    const insightsGrid = document.getElementById('insightsGrid');
    const toastContainer = document.getElementById('toastContainer');

    // Color palette for clusters
    const clusterColors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#06b6d4', '#8b5cf6', '#f43f5e', '#84cc16', '#3b82f6', '#d97706'];

    // Utility: Show Toast Notification
    function showToast(message, type = 'info') {
        if (!toastContainer) return;
        const toast = document.createElement('div');
        toast.className = 'toast';
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-exclamation-triangle';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    // Selected features helper
    function getSelectedFeatures() {
        const features = [];
        if (document.getElementById('chkAge')?.checked) features.push('Age');
        if (document.getElementById('chkIncome')?.checked) features.push('Annual Income (k$)');
        if (document.getElementById('chkSpending')?.checked) features.push('Spending Score (1-100)');
        return features;
    }

    // Initial Load: Dataset Overview
    async function loadDatasetOverview() {
        try {
            const res = await fetch('/api/dataset-overview');
            if (!res.ok) throw new Error('Failed to fetch dataset overview');
            const data = await res.json();
            globalOverview = data;

            // Update KPIs
            if (data.kpi) {
                kpiTotalCustomers.textContent = data.kpi.total_customers || 0;
                kpiAvgAge.textContent = data.kpi.avg_age || 0;
                kpiAvgIncome.textContent = `$${data.kpi.avg_income || 0}k`;
                kpiAvgSpending.textContent = data.kpi.avg_spending || 0;
            }

            // Update Metadata
            metaRows.textContent = data.num_rows || 0;
            metaCols.textContent = data.num_columns || 0;
            metaMissing.textContent = data.missing_values || 0;
            metaColumnNames.textContent = (data.column_names || []).join(', ');

            prepOriginal.textContent = data.num_rows || 0;

            // Run initial Elbow & Clustering automatically
            runElbowMethod();
            executeClustering();
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Execute Elbow Method API & Chart
    async function runElbowMethod() {
        try {
            const features = getSelectedFeatures();
            if (features.length < 2) {
                showToast('Please select at least 2 features for clustering.', 'error');
                return;
            }

            const res = await fetch('/api/elbow', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ features })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Elbow calculation failed');
            }

            const data = await res.json();
            recommendedKBadge.textContent = `Recommended K: ${data.recommended_k}`;
            kValueInput.value = data.recommended_k;

            // Render Plotly Elbow Chart
            const trace = {
                x: data.k_values,
                y: data.wcss,
                type: 'scatter',
                mode: 'lines+markers',
                marker: { size: 10, color: '#8b5cf6' },
                line: { shape: 'spline', color: '#6366f1', width: 3 }
            };

            const layout = {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                margin: { t: 30, r: 20, l: 50, b: 40 },
                xaxis: { title: 'Number of Clusters (K)', color: '#94a3b8', gridcolor: '#1e293b' },
                yaxis: { title: 'WCSS (Inertia)', color: '#94a3b8', gridcolor: '#1e293b' },
                font: { family: 'Inter', color: '#f8fafc' }
            };

            Plotly.newPlot('elbowChart', [trace], layout, { responsive: true, displayModeBar: false });
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Execute K-Means Clustering API
    async function executeClustering() {
        try {
            const k = parseInt(kValueInput.value, 10) || 5;
            const features = getSelectedFeatures();
            if (features.length < 2) {
                showToast('Please select at least 2 features for clustering.', 'error');
                return;
            }

            const res = await fetch('/api/cluster', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ k, features })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Clustering failed');
            }

            const data = await res.json();
            globalClusteringData = data;
            kpiNumClusters.textContent = data.k;

            // Update Preprocessing Banner
            if (data.preprocessing_summary) {
                prepOriginal.textContent = data.preprocessing_summary.original_records;
                prepMissing.textContent = data.preprocessing_summary.missing_values;
                prepDuplicates.textContent = data.preprocessing_summary.duplicates_removed;
                prepRecords.textContent = data.preprocessing_summary.records_used;
            }

            // Populate Filter Dropdowns
            populateFilterOptions(data.k);

            // Render Visualizations & Insights
            renderClusterScatterPlot(data.records);
            renderClusterDistChart(data.cluster_summary);
            renderClusterCompChart(data.cluster_summary);
            renderBusinessInsights(data.insights);
            renderDataTable(data.records);

            showToast(`K-Means clustering completed successfully for K=${data.k}!`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }

    // Populate Cluster Filter Dropdowns
    function populateFilterOptions(k) {
        filterClusterScatter.innerHTML = '<option value="ALL">All Clusters</option>';
        filterClusterTable.innerHTML = '<option value="ALL">Filter by Cluster (All)</option>';

        for (let i = 0; i < k; i++) {
            filterClusterScatter.innerHTML += `<option value="${i}">Cluster ${i}</option>`;
            filterClusterTable.innerHTML += `<option value="${i}">Cluster ${i}</option>`;
        }
    }

    // Render Scatter Plot: Annual Income vs Spending Score
    function renderClusterScatterPlot(records, filterCluster = 'ALL') {
        const filteredRecords = filterCluster === 'ALL'
            ? records
            : records.filter(r => r.Cluster === parseInt(filterCluster, 10));

        const clusters = [...new Set(filteredRecords.map(r => r.Cluster))].sort((a, b) => a - b);
        const traces = [];

        clusters.forEach(cId => {
            const clusterPoints = filteredRecords.filter(r => r.Cluster === cId);
            traces.push({
                x: clusterPoints.map(r => r['Annual Income (k$)'] || 0),
                y: clusterPoints.map(r => r['Spending Score (1-100)'] || 0),
                mode: 'markers',
                type: 'scatter',
                name: `Cluster ${cId}`,
                marker: {
                    size: 9,
                    color: clusterColors[cId % clusterColors.length],
                    opacity: 0.85
                },
                text: clusterPoints.map(r => `Customer ID: ${r.CustomerID || 'N/A'}<br>Age: ${r.Age || 'N/A'}`),
                hoverinfo: 'text+x+y'
            });
        });

        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            margin: { t: 30, r: 20, l: 50, b: 50 },
            xaxis: { title: 'Annual Income (k$)', color: '#94a3b8', gridcolor: '#1e293b' },
            yaxis: { title: 'Spending Score (1-100)', color: '#94a3b8', gridcolor: '#1e293b' },
            legend: { font: { color: '#f8fafc' }, orientation: 'h', y: -0.2 },
            font: { family: 'Inter', color: '#f8fafc' }
        };

        Plotly.newPlot('clusterScatterChart', traces, layout, { responsive: true, displayModeBar: false });
    }

    // Render Cluster Distribution Bar Chart
    function renderClusterDistChart(clusterSummary) {
        const trace = {
            x: clusterSummary.map(s => `Cluster ${s.cluster}`),
            y: clusterSummary.map(s => s.count),
            type: 'bar',
            marker: {
                color: clusterSummary.map(s => clusterColors[s.cluster % clusterColors.length]),
                border: { width: 0 }
            },
            text: clusterSummary.map(s => `${s.percentage}%`),
            textposition: 'auto'
        };

        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            margin: { t: 30, r: 20, l: 50, b: 40 },
            xaxis: { color: '#94a3b8', gridcolor: '#1e293b' },
            yaxis: { title: 'Customer Count', color: '#94a3b8', gridcolor: '#1e293b' },
            font: { family: 'Inter', color: '#f8fafc' }
        };

        Plotly.newPlot('clusterDistChart', [trace], layout, { responsive: true, displayModeBar: false });
    }

    // Render Cluster Comparison Chart (Grouped Bar Chart)
    function renderClusterCompChart(clusterSummary) {
        const xVals = clusterSummary.map(s => `Cluster ${s.cluster}`);

        const traceAge = {
            x: xVals,
            y: clusterSummary.map(s => s.avg_age),
            name: 'Avg Age',
            type: 'bar',
            marker: { color: '#38bdf8' }
        };

        const traceIncome = {
            x: xVals,
            y: clusterSummary.map(s => s.avg_income),
            name: 'Avg Income (k$)',
            type: 'bar',
            marker: { color: '#34d399' }
        };

        const traceSpending = {
            x: xVals,
            y: clusterSummary.map(s => s.avg_spending),
            name: 'Avg Spending Score',
            type: 'bar',
            marker: { color: '#fbbf24' }
        };

        const layout = {
            barmode: 'group',
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            margin: { t: 30, r: 20, l: 50, b: 50 },
            xaxis: { color: '#94a3b8', gridcolor: '#1e293b' },
            yaxis: { title: 'Average Value', color: '#94a3b8', gridcolor: '#1e293b' },
            legend: { font: { color: '#f8fafc' }, orientation: 'h', y: -0.2 },
            font: { family: 'Inter', color: '#f8fafc' }
        };

        Plotly.newPlot('clusterCompChart', [traceAge, traceIncome, traceSpending], layout, { responsive: true, displayModeBar: false });
    }

    // Render Business Insights Cards
    function renderBusinessInsights(insights) {
        if (!insightsGrid) return;
        insightsGrid.innerHTML = '';

        insights.forEach(item => {
            const card = document.createElement('div');
            card.className = 'glass-card';
            card.style.display = 'flex';
            card.style.flexDirection = 'column';
            card.style.justifySpaceBetween = 'space-between';

            card.innerHTML = `
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                        <h3 style="font-size: 1.25rem;">Cluster ${item.cluster}</h3>
                        <span class="segment-badge badge-${item.badge_color}">${item.archetype}</span>
                    </div>
                    <h4 style="font-size: 1.05rem; color: #a5b4fc; margin-bottom: 0.5rem;">${item.title}</h4>
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1rem;">${item.description}</p>
                    
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 0.75rem; border-radius: var(--radius-md); font-size: 0.85rem; margin-bottom: 1rem; display: grid; grid-template-columns: repeat(3, 1fr); text-align: center;">
                        <div><div style="color: var(--text-dim);">Count</div><strong>${item.metrics.count} (${item.metrics.percentage}%)</strong></div>
                        <div><div style="color: var(--text-dim);">Avg Inc</div><strong>$${item.metrics.avg_income}k</strong></div>
                        <div><div style="color: var(--text-dim);">Avg Score</div><strong>${item.metrics.avg_spending}</strong></div>
                    </div>
                </div>

                <div style="border-top: 1px solid var(--bg-card-border); padding-top: 0.75rem;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: var(--accent-amber); text-transform: uppercase; margin-bottom: 0.3rem;">
                        <i class="fa-solid fa-bullhorn"></i> Strategy Recommendation
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-main);">${item.strategy}</p>
                </div>
            `;
            insightsGrid.appendChild(card);
        });
    }

    // Render Data Table
    function renderDataTable(records, filterCluster = 'ALL') {
        if (!dataTableBody) return;
        dataTableBody.innerHTML = '';

        const filteredRecords = filterCluster === 'ALL'
            ? records
            : records.filter(r => r.Cluster === parseInt(filterCluster, 10));

        // Limit preview to first 50 rows for performance
        const displayRecords = filteredRecords.slice(0, 50);

        displayRecords.forEach(r => {
            const tr = document.createElement('tr');
            const cId = r.Cluster !== undefined ? r.Cluster : '--';
            const color = clusterColors[cId % clusterColors.length] || '#94a3b8';

            tr.innerHTML = `
                <td><strong>#${r.CustomerID || r.Customer_ID || 'N/A'}</strong></td>
                <td>${r.Gender || 'N/A'}</td>
                <td>${r.Age || 'N/A'}</td>
                <td>$${r['Annual Income (k$)'] || 0}k</td>
                <td>${r['Spending Score (1-100)'] || 0}</td>
                <td>
                    <span class="segment-badge" style="background: ${color}22; color: ${color}; border: 1px solid ${color}44;">
                        Cluster ${cId}
                    </span>
                </td>
            `;
            dataTableBody.appendChild(tr);
        });
    }

    // Search Customer Handler
    async function searchCustomer() {
        const query = searchCustomerIdInput.value.trim();
        if (!query) {
            showToast('Please enter a Customer ID to search.', 'error');
            return;
        }

        try {
            const res = await fetch(`/api/search-customer?id=${encodeURIComponent(query)}`);
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Customer search failed');
            }

            const data = await res.json();
            const cust = data.customer;
            const insight = data.insight;

            searchResultCard.style.display = 'block';
            searchResultCard.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <h3>Customer Search Result: #${cust.CustomerID || cust.Customer_ID}</h3>
                    <span class="segment-badge badge-${insight ? insight.badge_color : 'primary'}">
                        Cluster ${cust.Cluster}
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; font-size: 0.9rem; margin-bottom: 0.75rem;">
                    <div><strong>Gender:</strong> ${cust.Gender}</div>
                    <div><strong>Age:</strong> ${cust.Age}</div>
                    <div><strong>Income:</strong> $${cust['Annual Income (k$)']}k</div>
                    <div><strong>Spending Score:</strong> ${cust['Spending Score (1-100)']}</div>
                </div>
                ${insight ? `
                    <div style="font-size: 0.85rem; color: var(--text-muted); border-top: 1px dashed var(--bg-card-border); padding-top: 0.5rem;">
                        <strong>Segment Archetype:</strong> ${insight.title}<br>
                        <strong>Recommended Strategy:</strong> ${insight.strategy}
                    </div>
                ` : ''}
            `;
        } catch (err) {
            searchResultCard.style.display = 'none';
            showToast(err.message, 'error');
        }
    }

    // CSV File Upload Handler
    async function handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        uploadStatusMsg.innerHTML = '<span style="color: var(--accent-amber);"><i class="fa-solid fa-spinner fa-spin"></i> Uploading and validating CSV...</span>';

        try {
            const res = await fetch('/api/upload-dataset', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Upload failed');
            }

            const data = await res.json();
            uploadStatusMsg.innerHTML = `<span style="color: var(--accent-emerald);"><i class="fa-solid fa-check-circle"></i> ${data.message}</span>`;
            showToast(data.message, 'success');

            // Refresh overview & rerun clustering
            loadDatasetOverview();
        } catch (err) {
            uploadStatusMsg.innerHTML = `<span style="color: var(--accent-rose);"><i class="fa-solid fa-triangle-exclamation"></i> ${err.message}</span>`;
            showToast(err.message, 'error');
        }
    }

    // Event Listeners
    if (runClusteringBtn) runClusteringBtn.addEventListener('click', executeClustering);
    if (runElbowBtn) runElbowBtn.addEventListener('click', runElbowMethod);
    if (fileUploadInput) fileUploadInput.addEventListener('change', handleFileUpload);
    if (searchCustomerBtn) searchCustomerBtn.addEventListener('click', searchCustomer);

    if (filterClusterScatter) {
        filterClusterScatter.addEventListener('change', (e) => {
            if (globalClusteringData) {
                renderClusterScatterPlot(globalClusteringData.records, e.target.value);
            }
        });
    }

    if (filterClusterTable) {
        filterClusterTable.addEventListener('change', (e) => {
            if (globalClusteringData) {
                renderDataTable(globalClusteringData.records, e.target.value);
            }
        });
    }

    // Initial Execution
    loadDatasetOverview();
});
