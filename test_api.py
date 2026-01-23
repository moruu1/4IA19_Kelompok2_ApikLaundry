"""
Test script for API endpoints
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

print("Testing API endpoints...\n")

# Test 1: Historical Data
try:
    from fetch_data import get_revenue_data
    data = get_revenue_data()
    print(f"✓ Historical API: {len(data) if data else 0} records")
except Exception as e:
    print(f"✗ Historical API failed: {e}")

# Test 2: Inventory Prediction
try:
    from inventory import InventoryPredictor
    predictor = InventoryPredictor()
    result = predictor.get_prediction()
    count = len(result) if isinstance(result, list) else 0
    print(f"✓ Inventory API: {count} items")
except Exception as e:
    print(f"✗ Inventory API failed: {e}")

# Test 3: Revenue Prediction
try:
    from predict import train_and_predict
    pred = train_and_predict(30)
    status = "success" if pred.get("success") else "failed"
    print(f"✓ Predict API: {status}, {len(pred.get('predictions', []))} days")
except Exception as e:
    print(f"✗ Predict API failed: {e}")

print("\nAll API endpoint tests completed!")
