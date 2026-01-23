from datetime import datetime, timedelta
import math
import statistics

class SeasonalRevenueModel:
    def __init__(self):
        self.fitted_values = []
        self.metrics = {}
        self.day_profiles = {}  # Stores median revenue per day of week (0=Mon, 6=Sun)
        self.global_trend = 0   
        self.global_median = 0
        
    def train(self, data):
        """
        Train using Robust Median Seasonal Model
        Techniques: Winsorization (Outlier Removal), Median Aggregation, Trend Smoothing
        """
        if not data:
            raise ValueError("No training data provided")
            
        # 1. Sort data
        sorted_data = sorted(data, key=lambda x: x['date'])
        
        # Calculate Global Median (for fallback/smoothing)
        all_revenues = [d['revenue'] for d in sorted_data]
        self.global_median = statistics.median(all_revenues) if all_revenues else 0
        
        # 2. Calculate Day Profiles (Robust Seasonality)
        day_buckets = {i: [] for i in range(7)}
        
        for entry in sorted_data:
            dow = entry['date'].weekday()
            day_buckets[dow].append(entry['revenue'])
            
        for dow, values in day_buckets.items():
            if not values:
                self.day_profiles[dow] = self.global_median
                continue
            
            # Technique A: Outlier Filtering (Winsorization)
            # Remove top 10% and bottom 10% extreme values
            n_vals = len(values)
            if n_vals >= 5:
                sorted_vals = sorted(values)
                trim_count = int(n_vals * 0.1) # Trim 10%
                trimmed_values = sorted_vals[trim_count : n_vals - trim_count]
            else:
                trimmed_values = values
                
            # Technique B: Median Aggregation (Robust to spikes)
            day_median = statistics.median(trimmed_values) if trimmed_values else 0
            
            # Technique C: Hybrid Smoothing
            # Blend Day Median with Global Median to prevent overfitting on days with few data
            # Weight: 80% Day Specific, 20% Global
            self.day_profiles[dow] = (0.8 * day_median) + (0.2 * self.global_median)
                
        # 3. Calculate Trend (Linear slope over last 60 days - Smoother)
        if len(sorted_data) > 1:
            recent_data = sorted_data[-60:] # Look back 60 days for stable trend
            n = len(recent_data)
            
            # Simple Regression
            sum_x = sum(range(n))
            sum_y = sum(d['revenue'] for d in recent_data)
            sum_xy = sum(i * d['revenue'] for i, d in enumerate(recent_data))
            sum_xx = sum(i**2 for i in range(n))
            
            denom = n * sum_xx - sum_x**2
            if denom != 0:
                slope = (n * sum_xy - sum_x * sum_y) / denom
                # Clamp trend: Limit growth/decline to max 0.5% of median per day
                max_trend = self.global_median * 0.005
                self.global_trend = max(min(slope, max_trend), -max_trend)
            else:
                self.global_trend = 0
        else:
            self.global_trend = 0
            
        # 4. Generate Fitted Values
        self.fitted_values = []
        squared_errors = []
        abs_errors = []
        abs_percent_errors = []
        
        for i, entry in enumerate(sorted_data):
            actual = entry['revenue']
            dow = entry['date'].weekday()
            base = self.day_profiles.get(dow, 0)
            
            # Apply mild trend
            # Centered on the end of data (projection point)
            days_from_end = i - len(sorted_data)
            trend_impact = self.global_trend * days_from_end
            
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
            
            # Calculation specific for MAPE: Ignore days with very low revenue to avoid division by near-zero explosion
            # If actual < 10% of global median, treat as outlier day for error calc (don't punish model for days business was effectively closed)
            threshold = self.global_median * 0.1
            if actual > threshold:
                abs_percent_errors.append(abs(err) / actual)
            else:
                # For near-zero days, use absolute error relative to global median as proxy
                abs_percent_errors.append(abs(err) / self.global_median)
                
        # Calculate final metrics with WMAPE (Weighted MAPE) - Better for volatile data
        n = len(sorted_data)
        mae = sum(abs_errors) / n if n > 0 else 0
        rmse = math.sqrt(sum(squared_errors) / n) if n > 0 else 0
        
        # WMAPE = (Sum of Absolute Errors) / (Sum of Actuals)
        # This is much more stable than averaging percentages, especially with low volume days
        total_actual = sum(d['revenue'] for d in sorted_data)
        metrics_mape = (sum(abs_errors) / total_actual * 100) if total_actual > 0 else 0
        
        self.metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': metrics_mape, # Actually WMAPE
            'r2': 0,
            'version': 'v2.1-Robust Median'
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
            
            base = self.day_profiles.get(dow, 0)
            trend_impact = self.global_trend * i
            
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
