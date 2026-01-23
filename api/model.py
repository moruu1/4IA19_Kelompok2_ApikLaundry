import math
from datetime import datetime, timedelta
from fetch_data import get_revenue_data

class SimpleLinearRegression:
    def __init__(self):
        self.slope = 0
        self.intercept = 0
        self.is_trained = False
        self.training_data = None
        
    def fit(self, x_values, y_values):
        """
        Fit the model using Least Squares Mean
        """
        n = len(x_values)
        if n < 2:
            raise ValueError("Insufficient data points")
            
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_xx = sum(x * x for x in x_values)
        
        # Calculate slope (m) and intercept (c)
        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            self.slope = 0
            self.intercept = sum_y / n
        else:
            self.slope = (n * sum_xy - sum_x * sum_y) / denominator
            self.intercept = (sum_y - self.slope * sum_x) / n
            
        self.is_trained = True
        
    def predict(self, x):
        if not self.is_trained:
            raise Exception("Model not trained")
        
        # Handle both single value and list
        if isinstance(x, (list, tuple)):
            return [self.slope * val + self.intercept for val in x]
        return self.slope * x + self.intercept

class RevenuePredictionModel:
    def __init__(self):
        self.model = SimpleLinearRegression()
        self.is_trained = False
        self.training_data = []  
        self.start_date = None
        
    def prepare_data(self, data):
        """
        Prepare/Extract features (x=day_number) and target (y=revenue)
        """
        if not data:
            return [], []
        
        # Sort just in case
        sorted_data = sorted(data, key=lambda x: x['date'])
        self.start_date = sorted_data[0]['date']
        
        x = [] # day number
        y = [] # revenue
        
        for item in sorted_data:
            delta = item['date'] - self.start_date
            x.append(delta.days)
            y.append(item['revenue'])
            
        return x, y
        
    def get_fitted_values(self):
        """
        Get fitted values (predictions on training data) for visualization
        Returns: list of dicts
        """
        if not self.is_trained:
            raise Exception("Model must be trained first!")
            
        x, y = self.prepare_data(self.training_data)
        predictions = self.model.predict(x)
        
        result = []
        for i, (day_num, actual, pred) in enumerate(zip(x, y, predictions)):
            date_val = self.start_date + timedelta(days=day_num)
            result.append({
                'date': date_val, # Keep as object, format in predict.py
                'actual_revenue': actual,
                'fitted_revenue': max(0, pred)
            })
            
        return result
    
    def train(self, data):
        """
        Train the model
        """
        self.training_data = data
        x, y = self.prepare_data(data)
        
        if len(x) < 2:
            return {'error': 'Insufficient data'}
            
        # Train model
        self.model.fit(x, y)
        self.is_trained = True
        
        # Calculate basic metrics (MAE, RMSE) on training data
        predictions = self.model.predict(x)
        errors = [p - actual for p, actual in zip(predictions, y)]
        
        mae = sum(abs(e) for e in errors) / len(errors)
        rmse = math.sqrt(sum(e*e for e in errors) / len(errors))
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        # Avoid division by zero
        mape_sum = 0
        count = 0
        for actual, pred in zip(y, predictions):
            if actual != 0:
                mape_sum += abs((actual - pred) / actual)
                count += 1
        mape = (mape_sum / count * 100) if count > 0 else 0
        
        # Calculate R2 (Coefficient of Determination)
        mean_y = sum(y) / len(y)
        ss_tot = sum((val - mean_y)**2 for val in y)
        ss_res = sum(e*e for e in errors)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'slope': self.model.slope
        }
    
    def predict_future(self, days=30):
        """
        Predict revenue for the next N days
        Returns: list of dicts [{'date': date_obj, 'predicted_revenue': float}]
        """
        if not self.is_trained:
            raise Exception("Model must be trained first!")
        
        # Find the last day number from training data
        x_train, _ = self.prepare_data(self.training_data)
        last_day_num = x_train[-1] if x_train else 0
        
        future_predictions = []
        
        # Predict for next 'days' days
        for i in range(1, days + 1):
            future_day_num = last_day_num + i
            pred_revenue = self.model.predict(future_day_num)
            
            # Ensure no negative predictions
            pred_revenue = max(0, pred_revenue)
            
            future_date = self.start_date + timedelta(days=future_day_num)
            
            future_predictions.append({
                'date': future_date.isoformat(), # Return string for JSON serialization
                'predicted_revenue': pred_revenue
            })
            
        return {
            'predictions': future_predictions,
            'total_predicted': sum(p['predicted_revenue'] for p in future_predictions),
            'average_daily': sum(p['predicted_revenue'] for p in future_predictions) / days
        }

def main():
    """
    Main function to train and test the model
    """
    print("Revenue Prediction Model Training (Lightweight)\n")
    
    # Fetch data
    print("Fetching data from Supabase...")
    data = get_revenue_data()
    
    if not data or len(data) < 5:
        print("Insufficient data for training. Need at least 5 days of data.")
        return
    
    # Initialize and train model
    model = RevenuePredictionModel()
    metrics = model.train(data)
    
    # Predict next 30 days
    print("\nPredicting revenue for next 30 days...")
    result = model.predict_future(days=30)
    
    predictions = result['predictions']
    print("\nPredicted Revenue (Next 5 Days):")
    for p in predictions[:5]:
        print(f"Date: {p['date']}, Revenue: Rp {p['predicted_revenue']:,.0f}")
        
    print(f"\nTotal predicted revenue (30 days): Rp {result['total_predicted']:,.0f}")
    
    return model, result

if __name__ == "__main__":
    main()
