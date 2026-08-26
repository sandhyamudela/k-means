import unittest
import json
import os
import io
from app import app, init_default_dataset

class CustomerSegmentationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_default_dataset()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer Segmentation using K-Means', response.data)

    def test_dashboard_route(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer Segmentation Dashboard', response.data)

    def test_dataset_overview_api(self):
        response = self.client.get('/api/dataset-overview')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['num_rows'], 200)
        self.assertEqual(data['num_columns'], 5)
        self.assertIn('CustomerID', data['column_names'])

    def test_elbow_api(self):
        payload = {"features": ["Age", "Annual Income (k$)", "Spending Score (1-100)"]}
        response = self.client.post('/api/elbow', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('k_values', data)
        self.assertIn('wcss', data)
        self.assertIn('recommended_k', data)
        self.assertEqual(len(data['wcss']), 9)

    def test_dynamic_k_transitions(self):
        """Test K=4 -> K=5 -> K=4 dynamic clustering sequence"""
        features = ["Age", "Annual Income (k$)", "Spending Score (1-100)"]

        # Step 1: K=4
        res4 = self.client.post('/api/cluster', data=json.dumps({"k": 4, "features": features}), content_type='application/json')
        self.assertEqual(res4.status_code, 200)
        d4 = json.loads(res4.data)
        self.assertEqual(d4['k'], 4)
        self.assertEqual(len(d4['cluster_summary']), 4)
        self.assertEqual(len(d4['insights']), 4)
        unique_clusters_4 = set(r['Cluster'] for r in d4['records'])
        self.assertEqual(len(unique_clusters_4), 4)
        self.assertEqual(unique_clusters_4, {0, 1, 2, 3})

        # Step 2: K=5
        res5 = self.client.post('/api/cluster', data=json.dumps({"k": 5, "features": features}), content_type='application/json')
        self.assertEqual(res5.status_code, 200)
        d5 = json.loads(res5.data)
        self.assertEqual(d5['k'], 5)
        self.assertEqual(len(d5['cluster_summary']), 5)
        self.assertEqual(len(d5['insights']), 5)
        unique_clusters_5 = set(r['Cluster'] for r in d5['records'])
        self.assertEqual(len(unique_clusters_5), 5)
        self.assertEqual(unique_clusters_5, {0, 1, 2, 3, 4})

        # Step 3: Switch back to K=4
        res4_back = self.client.post('/api/cluster', data=json.dumps({"k": 4, "features": features}), content_type='application/json')
        self.assertEqual(res4_back.status_code, 200)
        d4_back = json.loads(res4_back.data)
        self.assertEqual(d4_back['k'], 4)
        self.assertEqual(len(d4_back['cluster_summary']), 4)
        self.assertEqual(len(d4_back['insights']), 4)
        unique_clusters_4_back = set(r['Cluster'] for r in d4_back['records'])
        self.assertEqual(len(unique_clusters_4_back), 4)
        self.assertEqual(unique_clusters_4_back, {0, 1, 2, 3})

    def test_search_customer_api(self):
        # Run clustering first
        self.client.post('/api/cluster', data=json.dumps({"k": 5}), content_type='application/json')
        
        # Test valid search
        response = self.client.get('/api/search-customer?id=1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(int(data['customer']['CustomerID']), 1)
        self.assertIn('insight', data)

        # Test invalid search ID
        response_invalid = self.client.get('/api/search-customer?id=9999')
        self.assertEqual(response_invalid.status_code, 404)

    def test_download_csv_api(self):
        self.client.post('/api/cluster', data=json.dumps({"k": 5}), content_type='application/json')
        response = self.client.get('/api/download-csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'Cluster', response.data)

    def test_invalid_upload(self):
        data = {'file': (io.BytesIO(b"Invalid,CSV\n1,2"), 'test.txt')}
        response = self.client.post('/api/upload-dataset', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()

