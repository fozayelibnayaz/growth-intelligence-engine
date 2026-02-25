"""
Eagle 3D Intelligence Platform - Predictive Growth Engine
ML-based upload growth predictions
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PredictiveGrowthEngine:
    def __init__(self):
        self.model = None
        self.model_version = "v1.0"
    
    def prepare_training_data(self, df):
        """Prepare data for ML model"""
        if len(df) < 30:
            return None, None, None
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('date')
        
        # Features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['rolling_mean_7'] = df['opportunity_score'].rolling(window=7).mean()
        df['rolling_mean_30'] = df['opportunity_score'].rolling(window=30).mean()
        
        df = df.dropna()
        
        if len(df) < 20:
            return None, None, None
        
        feature_cols = ['day_of_week', 'month', 'is_weekend', 
                       'rolling_mean_7', 'rolling_mean_30']
        
        X = df[feature_cols]
        y = df['opportunity_score']
        
        return X, y, feature_cols
    
    def train_model(self, df):
        """Train prediction model"""
        X, y, feature_cols = self.prepare_training_data(df)
        
        if X is None:
            return False, "Insufficient data (need 30+ records)"
        
        try:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            self.model.fit(X, y)
            return True, "Model trained successfully"
        except Exception as e:
            try:
                self.model = LinearRegression()
                self.model.fit(X, y)
                return True, "Model trained (Linear)"
            except:
                return False, f"Training failed: {str(e)}"
    
    def predict_next_30_days(self, df):
        """Predict growth for next 30 days"""
        if self.model is None:
            trained, msg = self.train_model(df)
            if not trained:
                return None, msg
        
        predictions = []
        dates = []
        current_date = datetime.now()
        recent_df = df.tail(30).copy()
        
        for i in range(30):
            future_date = current_date + timedelta(days=i+1)
            
            features = {
                'day_of_week': future_date.weekday(),
                'month': future_date.month,
                'is_weekend': 1 if future_date.weekday() >= 5 else 0,
                'rolling_mean_7': recent_df['opportunity_score'].tail(7).mean(),
                'rolling_mean_30': recent_df['opportunity_score'].tail(30).mean()
            }
            
            for key, value in features.items():
                if pd.isna(value):
                    features[key] = 50
            
            X_pred = pd.DataFrame([features])
            pred = self.model.predict(X_pred)[0]
            
            predictions.append(max(0, pred))
            dates.append(future_date.strftime('%Y-%m-%d'))
            
            recent_df = pd.concat([recent_df, pd.DataFrame([{
                'date': future_date,
                'opportunity_score': pred
            }])], ignore_index=True)
        
        return pd.DataFrame({'date': dates, 'predicted_score': predictions}), "Prediction complete"
    
    def calculate_growth_metrics(self, df):
        """Calculate growth metrics"""
        if len(df) < 7:
            return {'trend': 'Insufficient data', 'growth_rate': 0, 'volatility': 0, 'confidence': 'Low'}
        
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('date')
        
        recent_7 = df.tail(7)['opportunity_score'].mean()
        older_7 = df.head(7)['opportunity_score'].mean() if len(df) > 14 else recent_7
        
        growth_rate = ((recent_7 - older_7) / older_7 * 100) if older_7 > 0 else 0
        volatility = df['opportunity_score'].std()
        
        if growth_rate > 20:
            trend = '📈 Strong Growth'
            confidence = 'High'
        elif growth_rate > 5:
            trend = '📈 Moderate Growth'
            confidence = 'Medium'
        elif growth_rate > -5:
            trend = '➡️ Stable'
            confidence = 'Medium'
        else:
            trend = '📉 Decline'
            confidence = 'Medium'
        
        return {
            'trend': trend,
            'growth_rate': round(growth_rate, 2),
            'volatility': round(volatility, 2),
            'confidence': confidence
        }
    
    def get_upload_predictions(self, df):
        """Get complete upload predictions"""
        metrics = self.calculate_growth_metrics(df)
        predictions, msg = self.predict_next_30_days(df)
        
        if predictions is None:
            return {'metrics': metrics, 'predictions': None, 'message': msg}
        
        return {
            'metrics': metrics,
            'predictions': predictions,
            'summary': {
                'avg_30_day': round(predictions['predicted_score'].mean(), 2),
                'max_30_day': round(predictions['predicted_score'].max(), 2),
                'min_30_day': round(predictions['predicted_score'].min(), 2),
                'total_opportunities': round(predictions['predicted_score'].sum(), 2)
            },
            'message': 'Predictions generated'
        }