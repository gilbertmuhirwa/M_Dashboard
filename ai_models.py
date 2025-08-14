"""
AI and Machine Learning models for Ibali Farm Platform
Handles yield predictions and chatbot functionality
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import openai
from config import Config
import logging

logger = logging.getLogger(__name__)

class YieldPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.feature_columns = ['month', 'crop_type_encoded', 'weather_score', 'soil_quality_score']
    
    def prepare_features(self, df):
        """Prepare features for ML model"""
        if df.empty:
            return pd.DataFrame()
        
        # Convert date to datetime if it's not already
        df['ds'] = pd.to_datetime(df['ds'])
        df['month'] = df['ds'].dt.month
        
        # Encode crop types
        crop_types = df['crop_type'].unique()
        crop_mapping = {crop: idx for idx, crop in enumerate(crop_types)}
        df['crop_type_encoded'] = df['crop_type'].map(crop_mapping)
        
        # Create weather score from weather condition
        weather_mapping = {
            'sunny': 0.9, 'partly_cloudy': 0.7, 'cloudy': 0.5,
            'rainy': 0.3, 'stormy': 0.1, 'drought': 0.1
        }
        df['weather_score'] = df['weather_condition'].map(weather_mapping).fillna(0.5)
        
        # Fill missing soil quality scores
        df['soil_quality_score'] = df['soil_quality_score'].fillna(df['soil_quality_score'].mean())
        
        return df
    
    def train_model(self, historical_data):
        """Train the yield prediction model"""
        try:
            if historical_data.empty:
                logger.warning("No historical data available for training")
                return False
            
            # Prepare features
            df = self.prepare_features(historical_data.copy())
            
            if df.empty or len(df) < 10:
                logger.warning("Insufficient data for training")
                return False
            
            # Prepare training data
            X = df[self.feature_columns].fillna(0)
            y = df['y'].fillna(0)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            
            self.is_trained = True
            logger.info(f"Model trained successfully. MAE: {mae:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return False
    
    def predict_future_yields(self, months_ahead=6):
        """Predict future yields"""
        if not self.is_trained:
            return pd.DataFrame()
        
        try:
            # Generate future dates
            future_dates = []
            current_date = datetime.now()
            
            for i in range(1, months_ahead + 1):
                future_date = current_date + timedelta(days=30 * i)
                future_dates.append(future_date)
            
            # Create prediction features (using average values)
            predictions = []
            for date in future_dates:
                features = np.array([[
                    date.month,  # month
                    0,  # crop_type_encoded (default)
                    0.7,  # weather_score (average)
                    0.75  # soil_quality_score (average)
                ]])
                
                pred = self.model.predict(features)[0]
                predictions.append({
                    'date': date,
                    'predicted_yield': max(0, pred),  # Ensure non-negative
                    'confidence': 0.8  # Placeholder confidence
                })
            
            return pd.DataFrame(predictions)
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return pd.DataFrame()
    
    def create_prediction_chart(self, predictions_df):
        """Create prediction visualization"""
        if predictions_df.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=predictions_df['date'],
            y=predictions_df['predicted_yield'],
            mode='lines+markers',
            name='Predicted Yield',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Yield Predictions (Next 6 Months)',
            xaxis_title='Date',
            yaxis_title='Predicted Yield (tons)',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

class FarmChatbot:
    def __init__(self):
        self.client = None
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        self.knowledge_base = {
            "crop_care": {
                "corn": "Corn requires well-drained soil, regular watering, and nitrogen-rich fertilizer. Plant after last frost.",
                "wheat": "Wheat grows best in cool, moist conditions. Requires good drainage and moderate fertilization.",
                "soybeans": "Soybeans fix their own nitrogen. Need warm soil and moderate water. Avoid overwatering."
            },
            "livestock": {
                "cattle": "Cattle need fresh water, quality pasture, and regular health checks. Rotate grazing areas.",
                "chickens": "Chickens need secure housing, balanced feed, and clean water. Collect eggs daily.",
                "pigs": "Pigs require shelter, balanced diet, and clean environment. Monitor for diseases."
            },
            "pest_control": {
                "aphids": "Use ladybugs, neem oil, or insecticidal soap. Remove affected leaves.",
                "caterpillars": "Hand-pick or use Bt (Bacillus thuringiensis) spray. Check plants regularly.",
                "fungal_diseases": "Improve air circulation, avoid overhead watering, use fungicides if needed."
            }
        }
    
    def get_response(self, user_message, context_data=None):
        """Generate chatbot response"""
        try:
            # Check knowledge base first
            local_response = self._check_knowledge_base(user_message.lower())
            if local_response:
                return local_response
            
            # Use OpenAI if available
            if self.client:
                return self._get_ai_response(user_message, context_data)
            else:
                return self._get_fallback_response(user_message)
                
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."
    
    def _check_knowledge_base(self, message):
        """Check local knowledge base for responses"""
        for category, items in self.knowledge_base.items():
            for key, response in items.items():
                if key in message or any(word in message for word in key.split()):
                    return f"**{key.title()} Care Tips:**\n\n{response}"
        return None
    
    def _get_ai_response(self, message, context_data):
        """Get response from OpenAI"""
        try:
            context = "You are an agricultural expert assistant for the Ibali Farm Platform. "
            context += "Provide helpful, practical advice about farming, livestock, and agricultural management. "
            
            if context_data:
                context += f"Current farm data: {context_data}. "
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message):
        """Fallback response when AI is not available"""
        responses = [
            "That's a great question about farming! I'd recommend checking with your local agricultural extension office for specific advice.",
            "For detailed farming guidance, consider consulting agricultural experts in your area or checking reputable farming resources online.",
            "I understand you're looking for farming advice. The dashboard data might have relevant insights, or you could consult with agricultural specialists.",
        ]
        return np.random.choice(responses)

# Global instances
@st.cache_resource
def get_yield_predictor():
    return YieldPredictor()

@st.cache_resource  
def get_chatbot():
    return FarmChatbot()