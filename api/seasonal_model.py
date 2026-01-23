from datetime import datetime, timedelta
import math

class SeasonalRevenueModel:
    def __init__(self):
        self.fitted_values = []
        self.metrics = {}
        self.day_profiles = {}  # Stores avg revenue per day of week (0=Mon, 6=Sun)
        self.global_trend = 0   # Slope of growth/decline
        
    def train(self, data):
        """
        Train using Day-Specific Moving Average
        data: list of dicts [{'date': date_obj, 'revenue': float}, ...]
        """
        if not data:
            raise ValueError("No training data provided")
            
        # 1. Sort data
        sorted_data = sorted(data, key=lambda x: x['date'])
        
        # 2. Calculate Day Profiles (Seasonality)
        # Group revenues by day of week (0=Monday, ..., 6=Sunday)
        day_buckets = {i: [] for i in range(7)}
        
        for entry in sorted_data:
            dow = entry['date'].weekday()
            day_buckets[dow].append(entry['revenue'])
            
        # Calculate weighted average for each day (Recent weeks get more weight)
        for dow, values in day_buckets.items():
            if not values:
                self.day_profiles[dow] = 0
                continue
                
            # Simple average for robustness against outliers
            # Or use weighted average if enough data
            if len(values) >= 4:
                # Give last 4 weeks 2x weight
                recent = values[-4:]
                older = values[:-4]
                weighted_sum = sum(recent) * 2 + sum(older)
                weighted_count = len(recent) * 2 + len(older)
                self.day_profiles[dow] = weighted_sum / weighted_count
            else:
                self.day_profiles[dow] = sum(values) / len(values)
                
        # 3. Calculate Trend (Linear slope over last 30 days)
        if len(sorted_data) > 1:
            recent_data = sorted_data[-30:] # Last 30 days
            n = len(recent_data)
            
            # Simple Linear Regression for Trend only
            # X = days from start, Y = revenue
            sum_x = sum(range(n))
            sum_y = sum(d['revenue'] for d in recent_data)
            sum_xy = sum(i * d['revenue'] for i, d in enumerate(recent_data))
            sum_xx = sum(i**2 for i in range(n))
            
            if n * sum_xx - sum_x**2 != 0:
                self.global_trend = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
            else:
                self.global_trend = 0
        else:
            self.global_trend = 0
            
        # 4. Generate Fitted Values (Simulate past to calculate accuracy)
        self.fitted_values = []
        squared_errors = []
        abs_errors = []
        abs_percent_errors = []
        
        start_date = sorted_data[0]['date']
        
        for i, entry in enumerate(sorted_data):
            actual = entry['revenue']
            
            # Prediction = Profile(Day) + (Trend * days_since_start)
            # We temper the trend effect to avoid explosion on long history
            dow = entry['date'].weekday()
            base = self.day_profiles.get(dow, 0)
            
            # Apply trend carefully (clamped)
            # Trend impact is relative to the "center of mass" of the training data or end
            # Here we apply trend relative to the simple average level
            trend_impact = self.global_trend * (i - len(sorted_data) + 15) # Centered roughly on recent
            
            predicted = max(0, base + trend_impact)
            
            self.fitted_values.append({
                'date': entry['date'],
                'actual_revenue': actual,
                'fitted_revenue': predicted
            })
            
            # Metrics
            err = actual - predicted
            squared_errors.append(err ** 2)
            abs_errors.append(abs(err))
            if actual > 0:
                abs_percent_errors.append(abs(err) / actual)
                
        # Calculate final metrics
        n = len(sorted_data)
        mae = sum(abs_errors) / n if n > 0 else 0
        rmse = math.sqrt(sum(squared_errors) / n) if n > 0 else 0
        mape = (sum(abs_percent_errors) / len(abs_percent_errors) * 100) if abs_percent_errors else 0
        
        self.metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2': 0 # Not calculated for custom model
        }
        
        return self.metrics

    def predict_future(self, days=30, last_date=None):
        """Generate future predictions"""
        predictions = []
        
        if last_date is None and self.fitted_values:
            last_date = self.fitted_values[-1]['date']
        elif last_date is None:
            last_date = datetime.now().date()
            
        total_predicted = 0
        
        for i in range(1, days + 1):
            next_date = last_date + timedelta(days=i)
            dow = next_date.weekday()
            
            # Base value from profile
            base = self.day_profiles.get(dow, 0)
            
            # Apply trend (continuing from end of training)
            trend_impact = self.global_trend * i
            
            # Prediction
            predicted_revenue = max(0, base + trend_impact)
            
            predictions.append({
                'date': next_date.isoformat(),
                'predicted_revenue': predicted_revenue
            })
            total_predicted += predicted_revenue
            
        return {
            'predictions': predictions,
            'total_predicted': total_predicted,
            'average_daily': total_predicted / days if days > 0 else 0
        }

    def get_fitted_values(self):
        return self.fitted_values
