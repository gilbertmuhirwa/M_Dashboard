"""
Database connection and query module for Ibali Farm Platform
Handles PostgreSQL and Firebase connections
"""
import psycopg2
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import streamlit as st
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.postgres_conn = None
        self.firebase_app = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize all database connections"""
        try:
            self._connect_postgres()
            self._connect_firebase()
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            self.postgres_conn = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                sslmode='prefer'
            )
            logger.info("PostgreSQL connected successfully")
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            st.error("Failed to connect to PostgreSQL database")
    

    
    def _connect_firebase(self):
        """Connect to Firebase"""
        try:
            if not firebase_admin._apps:
                # Try service account first, fallback to config
                try:
                    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                except:
                    # Use application default credentials or initialize without credentials for public data
                    cred = credentials.ApplicationDefault()
                
                self.firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': Config.FIREBASE_DATABASE_URL,
                    'projectId': Config.FIREBASE_CONFIG['projectId']
                })
            logger.info("Firebase connected successfully")
        except Exception as e:
            logger.error(f"Firebase connection error: {e}")
            # Firebase is optional, don't show error to user
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_kpi_metrics(_self):
        """Get KPI metrics from PostgreSQL"""
        try:
            query = """
            SELECT 
                COALESCE(SUM(harvest_amount), 0) as total_harvest,
                COALESCE(SUM(livestock_count), 0) as total_livestock,
                COALESCE(COUNT(CASE WHEN request_status = 'pending' THEN 1 END), 0) as pending_requests,
                COALESCE(COUNT(CASE WHEN request_status = 'delivered' THEN 1 END), 0) as delivered_requests
            FROM (
                SELECT harvest_amount, 0 as livestock_count, NULL as request_status FROM harvests
                UNION ALL
                SELECT 0, livestock_count, NULL FROM livestock
                UNION ALL
                SELECT 0, 0, request_status FROM resource_requests
            ) combined_data;
            """
            return pd.read_sql(query, _self.postgres_conn)
        except Exception as e:
            logger.error(f"KPI metrics query error: {e}")
            # Return default values if query fails
            return pd.DataFrame({
                'total_harvest': [0],
                'total_livestock': [0], 
                'pending_requests': [0],
                'delivered_requests': [0]
            })
    
    @st.cache_data(ttl=300)
    def get_harvest_trends(_self):
        """Get harvest trends data from PostgreSQL"""
        try:
            query = """
            SELECT 
                DATE_TRUNC('month', harvest_date) as month,
                SUM(harvest_amount) as total_harvest,
                AVG(harvest_amount) as avg_harvest,
                crop_type
            FROM harvests 
            WHERE harvest_date >= CURRENT_DATE - INTERVAL '24 months'
            GROUP BY DATE_TRUNC('month', harvest_date), crop_type
            ORDER BY month DESC;
            """
            return pd.read_sql(query, _self.postgres_conn)
        except Exception as e:
            logger.error(f"Harvest trends query error: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def get_issue_locations(_self):
        """Get issue locations with coordinates from PostgreSQL"""
        try:
            query = """
            SELECT 
                issue_id,
                issue_title,
                issue_type,
                priority,
                status,
                latitude,
                longitude,
                created_date,
                assigned_to,
                image_url
            FROM farm_issues 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ORDER BY created_date DESC;
            """
            return pd.read_sql(query, _self.postgres_conn)
        except Exception as e:
            logger.error(f"Issue locations query error: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def get_resource_status(_self):
        """Get resource request status from PostgreSQL"""
        try:
            query = """
            SELECT 
                request_status as status,
                COUNT(*) as count
            FROM resource_requests
            GROUP BY request_status;
            """
            return pd.read_sql(query, _self.postgres_conn)
        except Exception as e:
            logger.error(f"Resource status query error: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_historical_yields(_self):
        """Get historical yield data for ML predictions from PostgreSQL"""
        try:
            query = """
            SELECT 
                harvest_date as ds,
                harvest_amount as y,
                crop_type,
                weather_condition,
                soil_quality_score
            FROM historical_harvests 
            WHERE harvest_date >= CURRENT_DATE - INTERVAL '3 years'
            ORDER BY harvest_date;
            """
            return pd.read_sql(query, _self.postgres_conn)
        except Exception as e:
            logger.error(f"Historical yields query error: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)
    def get_inventory_data(_self):
        """Get inventory data from PostgreSQL"""
        try:
            query = """
            SELECT 
                item_code,
                item_name,
                category,
                current_stock,
                min_required,
                unit_price,
                CASE 
                    WHEN current_stock <= min_required THEN 'Low Stock'
                    WHEN current_stock = 0 THEN 'Out of Stock'
                    ELSE 'In Stock'
                END as status
            FROM inventory
            ORDER BY item_name;
            """
            return pd.read_sql(query, _self.postgres_conn)
        except Exception as e:
            logger.error(f"Inventory query error: {e}")
            return pd.DataFrame()
    
    def get_firebase_alerts(self):
        """Get real-time alerts from Firebase"""
        try:
            ref = db.reference('alerts')
            alerts = ref.get()
            return alerts if alerts else {}
        except Exception as e:
            logger.error(f"Firebase alerts error: {e}")
            return {}
    
    def add_firebase_alert(self, alert_type, message, priority='medium'):
        """Add alert to Firebase"""
        try:
            ref = db.reference('alerts')
            new_alert = {
                'type': alert_type,
                'message': message,
                'priority': priority,
                'timestamp': pd.Timestamp.now().isoformat(),
                'read': False
            }
            ref.push(new_alert)
            return True
        except Exception as e:
            logger.error(f"Firebase add alert error: {e}")
            return False
    
    def close_connections(self):
        """Close all database connections"""
        try:
            if self.postgres_conn:
                self.postgres_conn.close()
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

# Global database manager instance
@st.cache_resource
def get_database_manager():
    return DatabaseManager()