"""
Firebase service for Ibali Farm Platform
Handles real-time data from Firebase Realtime Database and IoT sensor integration
"""
import firebase_admin
from firebase_admin import credentials, db, messaging, storage
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import threading
import time
from config import Config
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        self.app = None
        self.db_ref = None
        self.storage_bucket = None
        self._initialize_firebase()
        self.listeners = {}
        
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                # Initialize with service account credentials or config
                if hasattr(Config, 'FIREBASE_CREDENTIALS_PATH') and Config.FIREBASE_CREDENTIALS_PATH:
                    cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                elif hasattr(Config, 'FIREBASE_CONFIG'):
                    # Use the Firebase config from config.py
                    firebase_config = Config.FIREBASE_CONFIG
                    cred = credentials.ApplicationDefault()  # For production
                else:
                    # Use default credentials for cloud deployment
                    cred = credentials.ApplicationDefault()
                
                # Get database URL from config
                database_url = getattr(Config, 'FIREBASE_DATABASE_URL', None)
                if hasattr(Config, 'FIREBASE_CONFIG'):
                    database_url = Config.FIREBASE_CONFIG.get('databaseURL', database_url)
                
                # Get storage bucket from config
                storage_bucket = getattr(Config, 'FIREBASE_STORAGE_BUCKET', None)
                if hasattr(Config, 'FIREBASE_CONFIG'):
                    storage_bucket = Config.FIREBASE_CONFIG.get('storageBucket', storage_bucket)
                
                init_config = {}
                if database_url:
                    init_config['databaseURL'] = database_url
                if storage_bucket:
                    init_config['storageBucket'] = storage_bucket
                
                self.app = firebase_admin.initialize_app(cred, init_config)
            else:
                self.app = firebase_admin.get_app()
            
            self.db_ref = db.reference()
            
            # Initialize storage if bucket is available
            storage_bucket = getattr(Config, 'FIREBASE_STORAGE_BUCKET', None)
            if hasattr(Config, 'FIREBASE_CONFIG'):
                storage_bucket = Config.FIREBASE_CONFIG.get('storageBucket', storage_bucket)
            
            if storage_bucket:
                self.storage_bucket = storage.bucket()
            
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Firebase initialization error: {e}")
            # Don't show error in UI for Firebase issues
            logger.warning("Firebase connection failed. Real-time features may not work.")

    # Real-time Sensor Data Management
    def get_sensor_data(self, sensor_type=None, limit=100):
        """Get latest sensor readings"""
        try:
            if sensor_type:
                ref = self.db_ref.child('sensors').child(sensor_type)
            else:
                ref = self.db_ref.child('sensors')
            
            data = ref.order_by_key().limit_to_last(limit).get()
            
            if data:
                # Convert to DataFrame for easy processing
                records = []
                for sensor_id, readings in data.items():
                    if isinstance(readings, dict):
                        for timestamp, reading in readings.items():
                            if isinstance(reading, dict):
                                record = reading.copy()
                                record['sensor_id'] = sensor_id
                                record['timestamp'] = timestamp
                                records.append(record)
                
                return pd.DataFrame(records)
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            return pd.DataFrame()

    def add_sensor_reading(self, sensor_id, sensor_type, value, unit, location=None):
        """Add new sensor reading"""
        try:
            timestamp = datetime.now().isoformat()
            reading_data = {
                'value': value,
                'unit': unit,
                'timestamp': timestamp,
                'sensor_type': sensor_type,
                'location': location or {'lat': 0, 'lng': 0}
            }
            
            ref = self.db_ref.child('sensors').child(sensor_id).child(timestamp)
            ref.set(reading_data)
            
            # Check for alerts
            self._check_sensor_alerts(sensor_id, sensor_type, value)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding sensor reading: {e}")
            return False

    def _check_sensor_alerts(self, sensor_id, sensor_type, value):
        """Check if sensor reading triggers any alerts"""
        alert_thresholds = {
            'soil_moisture': {'min': 20, 'max': 80},
            'temperature': {'min': 5, 'max': 35},
            'humidity': {'min': 30, 'max': 90},
            'ph_level': {'min': 6.0, 'max': 7.5}
        }
        
        if sensor_type in alert_thresholds:
            thresholds = alert_thresholds[sensor_type]
            
            if value < thresholds['min']:
                self.create_alert(
                    f"Low {sensor_type.replace('_', ' ').title()}",
                    f"Sensor {sensor_id}: {sensor_type} is {value} (below minimum {thresholds['min']})",
                    'high',
                    sensor_id
                )
            elif value > thresholds['max']:
                self.create_alert(
                    f"High {sensor_type.replace('_', ' ').title()}",
                    f"Sensor {sensor_id}: {sensor_type} is {value} (above maximum {thresholds['max']})",
                    'high',
                    sensor_id
                )

    # Alert Management
    def create_alert(self, title, message, priority='medium', source=None):
        """Create a new alert"""
        try:
            alert_data = {
                'title': title,
                'message': message,
                'priority': priority,
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'read': False,
                'resolved': False
            }
            
            ref = self.db_ref.child('alerts').push(alert_data)
            
            # Send push notification if configured
            if priority == 'high':
                self._send_push_notification(title, message)
            
            return ref.key
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None

    def get_alerts(self, unread_only=False, limit=50):
        """Get alerts from Firebase"""
        try:
            ref = self.db_ref.child('alerts')
            
            if unread_only:
                alerts = ref.order_by_child('read').equal_to(False).limit_to_last(limit).get()
            else:
                alerts = ref.order_by_key().limit_to_last(limit).get()
            
            if alerts:
                alert_list = []
                for alert_id, alert_data in alerts.items():
                    alert_data['id'] = alert_id
                    alert_list.append(alert_data)
                
                return sorted(alert_list, key=lambda x: x['timestamp'], reverse=True)
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []

    def mark_alert_read(self, alert_id):
        """Mark alert as read"""
        try:
            ref = self.db_ref.child('alerts').child(alert_id)
            ref.update({'read': True})
            return True
        except Exception as e:
            logger.error(f"Error marking alert as read: {e}")
            return False

    def resolve_alert(self, alert_id, resolution_note=None):
        """Resolve an alert"""
        try:
            ref = self.db_ref.child('alerts').child(alert_id)
            update_data = {
                'resolved': True,
                'resolved_at': datetime.now().isoformat(),
                'read': True
            }
            if resolution_note:
                update_data['resolution_note'] = resolution_note
            
            ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False

    # Equipment and Asset Tracking
    def track_equipment_status(self, equipment_id, status, location=None, operator=None):
        """Track equipment status and location"""
        try:
            status_data = {
                'status': status,  # 'active', 'idle', 'maintenance', 'broken'
                'location': location or {'lat': 0, 'lng': 0},
                'operator': operator,
                'timestamp': datetime.now().isoformat()
            }
            
            ref = self.db_ref.child('equipment').child(equipment_id).child('current_status')
            ref.set(status_data)
            
            # Also add to history
            history_ref = self.db_ref.child('equipment').child(equipment_id).child('history')
            history_ref.push(status_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking equipment: {e}")
            return False

    def get_equipment_status(self, equipment_id=None):
        """Get current equipment status"""
        try:
            if equipment_id:
                ref = self.db_ref.child('equipment').child(equipment_id).child('current_status')
                return ref.get()
            else:
                ref = self.db_ref.child('equipment')
                equipment_data = ref.get()
                
                if equipment_data:
                    status_list = []
                    for eq_id, eq_data in equipment_data.items():
                        if 'current_status' in eq_data:
                            status = eq_data['current_status']
                            status['equipment_id'] = eq_id
                            status_list.append(status)
                    return status_list
                
                return []
                
        except Exception as e:
            logger.error(f"Error getting equipment status: {e}")
            return [] if not equipment_id else None

    # Weather Station Integration
    def log_weather_data(self, station_id, weather_data):
        """Log weather station data"""
        try:
            timestamp = datetime.now().isoformat()
            weather_entry = {
                'temperature': weather_data.get('temperature'),
                'humidity': weather_data.get('humidity'),
                'pressure': weather_data.get('pressure'),
                'wind_speed': weather_data.get('wind_speed'),
                'wind_direction': weather_data.get('wind_direction'),
                'rainfall': weather_data.get('rainfall', 0),
                'timestamp': timestamp
            }
            
            ref = self.db_ref.child('weather_stations').child(station_id).child(timestamp)
            ref.set(weather_entry)
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging weather data: {e}")
            return False

    def get_weather_history(self, station_id, hours=24):
        """Get weather history from station"""
        try:
            ref = self.db_ref.child('weather_stations').child(station_id)
            
            # Get data from last N hours
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            data = ref.order_by_key().start_at(cutoff_time).get()
            
            if data:
                weather_records = []
                for timestamp, record in data.items():
                    record['timestamp'] = timestamp
                    weather_records.append(record)
                
                return pd.DataFrame(weather_records)
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting weather history: {e}")
            return pd.DataFrame()

    # File Storage for Images and Documents
    def upload_image(self, file_path, destination_path):
        """Upload image to Firebase Storage"""
        try:
            if not self.storage_bucket:
                return None
            
            blob = self.storage_bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None

    def upload_file_from_bytes(self, file_bytes, destination_path, content_type='image/jpeg'):
        """Upload file from bytes to Firebase Storage"""
        try:
            if not self.storage_bucket:
                return None
            
            blob = self.storage_bucket.blob(destination_path)
            blob.upload_from_string(file_bytes, content_type=content_type)
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading file from bytes: {e}")
            return None

    # Push Notifications
    def _send_push_notification(self, title, body, topic='farm_alerts'):
        """Send push notification"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                topic=topic
            )
            
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")

    # Real-time Data Streaming
    def start_real_time_listener(self, path, callback):
        """Start real-time listener for data changes"""
        try:
            def listener(event):
                callback(event.data, event.path)
            
            ref = self.db_ref.child(path)
            self.listeners[path] = ref.listen(listener)
            
            logger.info(f"Started real-time listener for {path}")
            
        except Exception as e:
            logger.error(f"Error starting listener: {e}")

    def stop_real_time_listener(self, path):
        """Stop real-time listener"""
        try:
            if path in self.listeners:
                self.listeners[path].close()
                del self.listeners[path]
                logger.info(f"Stopped real-time listener for {path}")
        except Exception as e:
            logger.error(f"Error stopping listener: {e}")

    def cleanup(self):
        """Clean up all listeners and connections"""
        for path in list(self.listeners.keys()):
            self.stop_real_time_listener(path)

# Global Firebase service instance
@st.cache_resource
def get_firebase_service():
    return FirebaseService()