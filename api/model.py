import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta
from fetch_data import get_revenue_data

class RevenuePredictionModel:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
        self.training_data = None
        self.start_date = None
        
    def prepare_features(self, data):
        """
        Prepare features for training/prediction
        Data format: [{'date': date_obj, 'revenue': float}, ...]
        Features: day_of_week, day_of_month, month, day_number (sequential)
        """
        if not data or len(data) == 0:
            return None, None
        
        # Sort by date
        sorted_data = sorted(data, key=lambda x: x['date'])
        self.start_date = sorted_data[0]['date']
        
        X = []
        y = []
        
        for item in sorted_data:
            date = item['date']
            revenue = item['revenue']
            
            # Extract features
            day_of_week = date.weekday()  # 0=Monday, 6=Sunday
            day_of_month = date.day
            month = date.month
            day_number = (date - self.start_date).days
            
            X.append([day_of_week, day_of_month, month, day_number])
            y.append(revenue)
        
        return np.array(X), np.array(y)
    
    def calculate_mape(self, y_true, y_pred):
        """
        Calculate Mean Absolute Percentage Error (MAPE)
        """
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        return mape
    
    def train(self, data):
        """
        Train the model with historical data
        Data format: [{'date': date_obj, 'revenue': float}, ...]
        """
        # Store original data
        self.training_data = data
        
        X, y = self.prepare_features(data)
        
        if X is None or len(X) < 10:
            return {'error': 'Insufficient data for training. Need at least 10 days.'}
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate on test set
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = self.calculate_mape(y_test, y_pred)
        
        print("\n" + "="*50)
        print("Model Training Results (sklearn LinearRegression):")
        print(f"Features: 4 basic (day_of_week, day_of_month, month, day_number)")
        print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        print(f"Mean Absolute Error: Rp {mae:,.0f}")
        print(f"Root Mean Squared Error: Rp {rmse:,.0f}")
        print(f"R² Score: {r2:.4f}")
        print(f"MAPE: {mape:.2f}%")
        print("="*50)
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'mape': mape
        }
    
    def get_fitted_values(self):
        """
        Get fitted values (predictions on training data) for visualization
        Returns: list of dicts [{'date': date_obj, 'actual_revenue': float, 'fitted_revenue': float}]
        """
        if not self.is_trained or self.training_data is None:
            raise Exception("Model must be trained first!")
        
        X, y = self.prepare_features(self.training_data)
        fitted_values = self.model.predict(X)
        
        # Create result list
        result = []
        sorted_data = sorted(self.training_data, key=lambda x: x['date'])
        
        for i, item in enumerate(sorted_data):
            result.append({
                'date': item['date'],  # Keep as date object
                'actual_revenue': y[i],
                'fitted_revenue': max(0, fitted_values[i])  # No negative predictions
            })
        
        return result
    
    def predict_future(self, days=30):
        """
        Predict revenue for the next N days starting from the last training data date
        Returns: dict with 'predictions', 'total_predicted', 'average_daily'
        """
        if not self.is_trained:
            raise Exception("Model must be trained first!")
        
        # Get the last date from training data
        if self.training_data is not None and len(self.training_data) > 0:
            sorted_data = sorted(self.training_data, key=lambda x: x['date'])
            last_date = sorted_data[-1]['date']
        else:
            last_date = datetime.now().date()
        
        # Generate future dates starting from last_date + 1
        future_dates = [last_date + timedelta(days=i) for i in range(1, days+1)]
        
        # Prepare features for future dates
        X_future = []
        for date in future_dates:
            day_of_week = date.weekday()
            day_of_month = date.day
            month = date.month
            day_number = (date - self.start_date).days
            
            X_future.append([day_of_week, day_of_month, month, day_number])
        
        X_future = np.array(X_future)
        
        # Predict
        predictions = self.model.predict(X_future)
        
        # Ensure no negative predictions
        predictions = np.maximum(predictions, 0)
        
        # Create result
        future_predictions = []
        for i, date in enumerate(future_dates):
            future_predictions.append({
                'date': date.isoformat(),  # ISO format for JSON serialization
                'predicted_revenue': float(predictions[i])
            })
        
        total_predicted = float(np.sum(predictions))
        average_daily = total_predicted / days if days > 0 else 0
        
        return {
            'predictions': future_predictions,
            'total_predicted': total_predicted,
            'average_daily': average_daily
        }

def main():
    """
    Main function to train and test the model
    """
    print("Revenue Prediction Model Training (sklearn LinearRegression)\n")
    
    # Fetch data from Supabase
    print("Fetching data from Supabase...")
    data = get_revenue_data()
    
    if data is None or len(data) < 10:
        print("Insufficient data for training. Need at least 10 days of data.")
        return
    
    print(f"Loaded {len(data)} days of revenue data")
    print(f"Date range: {data[0]['date']} to {data[-1]['date']}")
    
    # Initialize and train model
    model = RevenuePredictionModel()
    metrics = model.train(data)
    
    if 'error' in metrics:
        print(f"Error: {metrics['error']}")
        return
    
    # Predict next 30 days
    print("\nPredicting revenue for next 30 days...")
    result = model.predict_future(days=30)
    
    predictions = result['predictions']
    print("\nPredicted Revenue (Next 5 Days):")
    for p in predictions[:5]:
        print(f"  {p['date']}: Rp {p['predicted_revenue']:,.0f}")
    
    print(f"\nTotal predicted revenue (30 days): Rp {result['total_predicted']:,.0f}")
    print(f"Average predicted daily revenue: Rp {result['average_daily']:,.0f}")
    
    return model, result

if __name__ == "__main__":
    model, predictions = main()
