import pandas as pd
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
        self.training_df = None  
        
    def prepare_features(self, df):
        """
        Prepare features for training/prediction
        Features: day_of_week, day_of_month, month, day_number (sequential)
        """
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract time-based features
        df['day_of_week'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['day_number'] = (df['date'] - df['date'].min()).dt.days  # Sequential day number
        
        # Create feature matrix
        X = df[['day_of_week', 'day_of_month', 'month', 'day_number']].values
        y = df['revenue'].values
        
        return X, y, df
    
    def calculate_mape(self, y_true, y_pred):
        """
        Calculate Mean Absolute Percentage Error (MAPE)
        """
       
        mask = y_true != 0
        if not np.any(mask):
            return 0.0
        
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        return mape
    
    def train(self, df):
        """
        Train the model with historical data and store training data
        """
        # Store original data for fitted values
        self.training_df = df.copy()
        
        X, y, processed_df = self.prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = self.calculate_mape(y_test, y_pred)
        
        print("\n" + "="*50)
        print("Model Training Results (Linear Regression):")
        print(f"Features: 4 basic (day_of_week, day_of_month, month, day_number)")
        print(f"Mean Absolute Error: Rp {mae:,.0f}")
        print(f"Root Mean Squared Error: Rp {rmse:,.0f}")
        print(f"R² Score: {r2:.4f}")
        print(f"MAPE (Mean Absolute Percentage Error): {mape:.2f}%")
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
        """
        if not self.is_trained or self.training_df is None:
            raise Exception("Model must be trained first!")
        
        X, y, processed_df = self.prepare_features(self.training_df)
        fitted_values = self.model.predict(X)
        
        # Create result DataFrame with dates and fitted values
        result_df = pd.DataFrame({
            'date': processed_df['date'],
            'actual_revenue': y,
            'fitted_revenue': np.maximum(fitted_values, 0)  # No negative predictions
        })
        
        return result_df
    
    def predict_future(self, days=30):
        """
        Predict revenue for the next N days starting from the last training data date
        """
        if not self.is_trained:
            raise Exception("Model must be trained first!")
        
        # Get the last date from training data
        if self.training_df is not None and len(self.training_df) > 0:
            last_date = pd.to_datetime(self.training_df['date']).max().date()
        else:
            # Fallback to today if no training data
            last_date = datetime.now().date()
        
        # Generate future dates starting from last_date + 1
        future_dates = [last_date + timedelta(days=i) for i in range(1, days+1)]
        
        # Prepare features for future dates
        future_df = pd.DataFrame({
            'date': future_dates,
            'day_of_week': [d.weekday() for d in future_dates],
            'day_of_month': [d.day for d in future_dates],
            'month': [d.month for d in future_dates],
            'day_number': [i for i in range(1, days+1)]
        })
        
        X_future = future_df[['day_of_week', 'day_of_month', 'month', 'day_number']].values
        
        # Predict
        predictions = self.model.predict(X_future)
        
        # Ensure no negative predictions
        predictions = np.maximum(predictions, 0)
        
        # Create result DataFrame
        result_df = pd.DataFrame({
            'date': future_dates,
            'predicted_revenue': predictions
        })
        
        return result_df

def main():
    """
    Main function to train and test the model
    """
    print("Revenue Prediction Model Training\n")
    
    # Fetch data from Supabase
    print("Fetching data from Supabase...")
    df = get_revenue_data()
    
    if df is None or len(df) < 10:
        print("Insufficient data for training. Need at least 10 days of data.")
        return
    
    # Initialize and train model
    model = RevenuePredictionModel()
    metrics = model.train(df)
    
    # Predict next 30 days
    print("\nPredicting revenue for next 30 days...")
    predictions = model.predict_future(days=30)
    
    print("\nPredicted Revenue (Next 30 Days):")
    print(predictions.head(10))
    print(f"\nTotal predicted revenue (30 days): Rp {predictions['predicted_revenue'].sum():,.0f}")
    print(f"Average predicted daily revenue: Rp {predictions['predicted_revenue'].mean():,.0f}")
    
    return model, predictions

if __name__ == "__main__":
    model, predictions = main()
