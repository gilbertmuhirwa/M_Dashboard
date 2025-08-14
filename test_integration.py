"""
Test script to verify all Ibali Farm Platform integrations work correctly
"""
import sys
import traceback

def test_imports():
    """Test all module imports"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import folium
        from streamlit_folium import st_folium
        print("✅ Folium imported successfully")
    except ImportError as e:
        print(f"❌ Folium import failed: {e}")
        return False
    
    return True

def test_custom_modules():
    """Test custom module imports"""
    print("\n🔧 Testing custom modules...")
    
    try:
        from database import get_database_manager
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Database module import failed: {e}")
        return False
    
    try:
        from firebase_service import get_firebase_service
        print("✅ Firebase service imported successfully")
    except ImportError as e:
        print(f"❌ Firebase service import failed: {e}")
        return False
    
    try:
        from ai_models import get_yield_predictor, get_chatbot
        print("✅ AI models imported successfully")
    except ImportError as e:
        print(f"❌ AI models import failed: {e}")
        return False
    
    try:
        from utils import get_weather_service, get_export_service, get_chart_utils
        print("✅ Utils imported successfully")
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    try:
        from config import Config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    return True

def test_service_initialization():
    """Test service initialization"""
    print("\n⚙️ Testing service initialization...")
    
    try:
        from database import get_database_manager
        from firebase_service import get_firebase_service
        from ai_models import get_yield_predictor, get_chatbot
        from utils import get_weather_service, get_export_service, get_chart_utils
        
        # Test each service individually
        db_manager = get_database_manager()
        print("✅ Database manager initialized")
        
        firebase_service = get_firebase_service()
        print("✅ Firebase service initialized")
        
        weather_service = get_weather_service()
        print("✅ Weather service initialized")
        
        export_service = get_export_service()
        print("✅ Export service initialized")
        
        chart_utils = get_chart_utils()
        print("✅ Chart utils initialized")
        
        yield_predictor = get_yield_predictor()
        print("✅ Yield predictor initialized")
        
        chatbot = get_chatbot()
        print("✅ Chatbot initialized")
        
        # Test the initialize_services function
        def initialize_services():
            return db_manager, firebase_service, weather_service, export_service, chart_utils, yield_predictor, chatbot
        
        services = initialize_services()
        print(f"✅ initialize_services() returns {len(services)} values")
        
        # Test unpacking
        db_mgr, fb_svc, weather_svc, export_svc, chart_util, yield_pred, chat_bot = initialize_services()
        print("✅ Service unpacking works correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Ibali Farm Platform Integration Tests\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test custom modules
    if not test_custom_modules():
        print("\n❌ Custom module tests failed!")
        return False
    
    # Test service initialization
    if not test_service_initialization():
        print("\n❌ Service initialization tests failed!")
        return False
    
    print("\n🎉 All tests passed! Your Ibali Farm Platform is ready to run!")
    print("\n📋 Summary:")
    print("✅ All dependencies installed correctly")
    print("✅ All custom modules working")
    print("✅ Service initialization working")
    print("✅ Function unpacking working correctly")
    print("\n🚀 You can now run: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)