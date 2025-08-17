"""
Configuration module for Ibali Farm Platform
Handles environment variables and database connections
"""
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

class Config:
    # Database configurations
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'ibali_farm')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
    

    
    # Firebase configuration
    FIREBASE_CONFIG = {
        "apiKey": "AIzaSyBqOryWBR3c902UU0fmI3wLMIfSqlS5_5I",
        "authDomain": "ibabi-b75d0.firebaseapp.com",
        "projectId": "ibabi-b75d0",
        "storageBucket": "ibabi-b75d0.firebasestorage.app",
        "messagingSenderId": "479417617288",
        "appId": "1:479417617288:web:c721b8f256120fea3d083d",
        "measurementId": "G-SQ8MWTC4V4",
        "databaseURL": "https://ibabi-b75d0-default-rtdb.firebaseio.com/"
    }
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
    FIREBASE_DATABASE_URL = FIREBASE_CONFIG.get("databaseURL", "")
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN', '')
    
    # App settings
    APP_TITLE = "Ibali Farm Platform"
    APP_ICON = "🌾"
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '30'))  # seconds

# Streamlit secrets fallback
def get_secret(key, default=''):
    """Get secret key from environment or Streamlit secrets"""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)
    