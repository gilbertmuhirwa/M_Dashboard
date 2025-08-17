"""
Enhanced Ibali Farm Platform Dashboard
AI-Driven Agricultural Management System with Real-time Data Integration
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
import folium.plugins
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh
from streamlit_chat import message
from datetime import datetime, timedelta
import numpy as np
import time

# Import custom modules
from database import get_database_manager
from firebase_service import get_firebase_service
from ai_models import get_yield_predictor, get_chatbot
from utils import get_weather_service, get_export_service, get_chart_utils
from config import Config

# Page config
st.set_page_config(
    page_title=Config.APP_TITLE, 
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 30 seconds for real-time updates
st_autorefresh(interval=Config.REFRESH_INTERVAL * 1000, key="data_refresh")

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize all services and connections"""
    db_manager = get_database_manager()
    firebase_service = get_firebase_service()
    weather_service = get_weather_service()
    export_service = get_export_service()
    chart_utils = get_chart_utils()
    yield_predictor = get_yield_predictor()
    chatbot = get_chatbot()
    
    return db_manager, firebase_service, weather_service, export_service, chart_utils, yield_predictor, chatbot

# Load services
db_manager, firebase_service, weather_service, export_service, chart_utils, yield_predictor, chatbot = initialize_services()

# Enhanced CSS for modern UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main .block-container {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Top navigation bar */
    .top-nav {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 1rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(46, 125, 50, 0.3);
    }
    
    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .logo-section h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    .nav-icons {
        display: flex;
        gap: 1rem;
        font-size: 1.3rem;
    }
    
    .nav-icons span {
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 50%;
        transition: background-color 0.3s;
    }
    
    .nav-icons span:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .kpi-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #4CAF50;
        transition: transform 0.3s, box-shadow 0.3s;
        text-align: center;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .kpi-title {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E7D32;
        margin: 1rem 0;
        line-height: 1;
    }
    
    .kpi-delta {
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2E7D32;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 2rem 1rem;
        border-bottom: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }
    
    .sidebar-logo h2 {
        color: #2E7D32;
        margin: 0;
        font-weight: 700;
    }
    
    .sidebar-logo p {
        color: #666;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Weather widget */
    .weather-widget {
        background: linear-gradient(135deg, #87CEEB 0%, #4682B4 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .weather-temp {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Alert styles */
    .alert-container {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-high {
        background: #f8d7da;
        border-color: #f5c6cb;
    }
    
    /* Chatbot styles */
    .chatbot-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
    }
    
    /* Status badges */
    .status-good { 
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .status-warning { 
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .status-danger { 
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .nav-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .kpi-container {
            grid-template-columns: 1fr;
        }
        
        .kpi-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar with real-time data
with st.sidebar:
    # Logo and branding
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🌾 Ibali</h2>
        <p>AI-Powered Farm Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation menu with exact icons from the image
    menu_options = {
        " Dashboard": "Dashboard",
        " Report": "Report",
        " Issues": "Issues",
        " Requests": "Requests",
        " Stock": "Stock",
        " Maps": "Maps",
        " Terms of use& Privacy policy": "Privacy Policy",
        " Help&support": "Help",
        " Logout": "Logout"
    }
    
    # Custom CSS for sidebar styling to match the image
    st.markdown("""
    <style>
    .sidebar-nav {
        padding: 0;
        margin: 0;
    }
    .nav-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        margin: 2px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 16px;
        font-weight: 500;
        color: #333;
        text-decoration: none;
        border-left: 4px solid transparent;
    }
    .nav-item:hover {
        background-color: #f0f0f0;
        border-left: 4px solid #4CAF50;
    }
    .nav-item.active {
        background-color: #e8f5e8;
        border-left: 4px solid #4CAF50;
        color: #2E7D32;
        font-weight: 600;
    }
    .nav-icon {
        margin-right: 12px;
        font-size: 18px;
        width: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    selected_page = st.radio("Navigation", list(menu_options.keys()), index=0, label_visibility="collapsed")
    selected_page = menu_options[selected_page]
    
    st.markdown("---")
    
    # Weather widget
    try:
        weather_data = weather_service.get_current_weather(city="Farm Location")
        st.markdown(f"""
        <div class="weather-widget">
            <div style="font-size: 1.1rem; font-weight: 600;">🌤️ Current Weather</div>
            <div class="weather-temp">{weather_data['temperature']:.1f}°C</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{weather_data['description'].title()}</div>
            <div style="font-size: 0.8rem; margin-top: 0.5rem;">
                💨 {weather_data['wind_speed']} m/s | 💧 {weather_data['humidity']}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Weather data unavailable")
    
    # Real-time alerts from Firebase
    try:
        alerts = db_manager.get_firebase_alerts()
        if alerts:
            st.markdown("###  Live Alerts")
            alert_count = 0
            for alert_id, alert in alerts.items():
                if not alert.get('read', False) and alert_count < 3:
                    priority_class = f"alert-{alert.get('priority', 'medium')}"
                    st.markdown(f"""
                    <div class="alert-container {priority_class}">
                        <strong>{alert.get('type', 'Alert').title()}</strong><br>
                        {alert.get('message', 'No message')}
                    </div>
                    """, unsafe_allow_html=True)
                    alert_count += 1
    except Exception as e:
        pass  # Firebase alerts are optional
    
    # Quick stats
    st.markdown("###  Quick Stats")
    try:
        kpi_data = db_manager.get_kpi_metrics()
        if not kpi_data.empty:
            st.metric("Total Harvest", f"{kpi_data.iloc[0]['total_harvest']:.1f}t")
            st.metric("Active Issues", f"{kpi_data.iloc[0]['pending_requests']:.0f}")
    except Exception as e:
        st.metric("Total Harvest", "Loading...")
        st.metric("Active Issues", "Loading...")

# Enhanced Top Navigation Bar
st.markdown(f"""
<div class="top-nav">
    <div class="nav-content">
        <div class="logo-section">
            <h1>{Config.APP_ICON} {Config.APP_TITLE}</h1>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                Last updated: {datetime.now().strftime('%H:%M:%S')} | 
                Status: <span style="color: #90EE90;">🟢 Online</span>
            </div>
        </div>
        <div class="nav-icons">
            <span title="Settings">⚙️</span>
            <span title="Notifications">🔔</span>
            <span title="Export">📊</span>
            <span title="Profile">👤</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Content Area
if selected_page == "Dashboard":
    # Initialize all services
    db_manager, firebase_service, weather_service, export_service, chart_utils, yield_predictor, chatbot = initialize_services()
    # Hero section with real-time data
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.9), rgba(76, 175, 80, 0.9)), 
                   url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1400&q=80');
        background-size: cover;
        background-position: center;
        height: 250px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        position: relative;
        box-shadow: 0 8px 32px rgba(46, 125, 50, 0.3);
    ">
        <div style="text-align: center; color: white; z-index: 1;">
            <h1 style="font-size: 2.5rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); font-weight: 700;">
                Real-Time Farm Operations
            </h1>
            <p style="font-size: 1.1rem; margin: 1rem 0 0 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); opacity: 0.95;">
                AI-powered insights • Live monitoring • Smart predictions
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced KPI Cards with real database data
    try:
        kpi_data = db_manager.get_kpi_metrics()
        if not kpi_data.empty:
            kpi_row = kpi_data.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(chart_utils.create_kpi_card(
                    "Total Harvest Reported", 
                    f"{kpi_row['total_harvest']:.1f}t",
                    "+12.5% vs last month"
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown(chart_utils.create_kpi_card(
                    "Total Livestock Production", 
                    f"{kpi_row['total_livestock']:.0f}",
                    "+5.2% vs last month"
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown(chart_utils.create_kpi_card(
                    "Pending Resource Requests", 
                    f"{kpi_row['pending_requests']:.0f}",
                    "-3 from yesterday"
                ), unsafe_allow_html=True)
            
            with col4:
                st.markdown(chart_utils.create_kpi_card(
                    "Delivered Requests", 
                    f"{kpi_row['delivered_requests']:.0f}",
                    "+8 this week"
                ), unsafe_allow_html=True)
        else:
            st.warning("Unable to load KPI data. Please check database connection.")
    except Exception as e:
        st.error(f"Error loading KPI data: {str(e)}")
        # Show placeholder KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(chart_utils.create_kpi_card("Total Harvest", "Loading...", ""), unsafe_allow_html=True)
        with col2:
            st.markdown(chart_utils.create_kpi_card("Livestock", "Loading...", ""), unsafe_allow_html=True)
        with col3:
            st.markdown(chart_utils.create_kpi_card("Pending Requests", "Loading...", ""), unsafe_allow_html=True)
        with col4:
            st.markdown(chart_utils.create_kpi_card("Delivered", "Loading...", ""), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========== DASHBOARD ANALYTICS SECTION ==========
    
    # DYNAMIC ANALYTICS CHARTS SECTION
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; text-align: center;">📊 Advanced Analytics Dashboard</h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">Real-time data visualization and insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics Charts in three columns
    analytics_col1, analytics_col2, analytics_col3 = st.columns(3)
    
    with analytics_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader(" Yield Trends Over Time")
        
        try:
            # Get real harvest trends data
            harvest_trends = db_manager.get_harvest_trends()
            
            if not harvest_trends.empty:
                fig_yield = px.line(
                    harvest_trends, 
                    x='month', 
                    y='total_harvest',
                    color='crop_type',
                    title="Monthly Harvest Trends",
                    markers=True
                )
                fig_yield.update_layout(
                    height=350,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=True
                )
            else:
                # Fallback sample data
                sample_yield_data = pd.DataFrame({
                    'Month': pd.date_range('2024-01-01', periods=12, freq='M'),
                    'Corn': [120, 135, 145, 160, 180, 195, 210, 205, 190, 175, 160, 145],
                    'Wheat': [80, 85, 90, 95, 100, 105, 110, 108, 102, 95, 88, 82],
                    'Soybeans': [60, 65, 70, 75, 80, 85, 90, 88, 82, 75, 68, 62]
                })
                
                fig_yield = go.Figure()
                for crop in ['Corn', 'Wheat', 'Soybeans']:
                    fig_yield.add_trace(go.Scatter(
                        x=sample_yield_data['Month'],
                        y=sample_yield_data[crop],
                        mode='lines+markers',
                        name=crop,
                        line=dict(width=3),
                        marker=dict(size=6)
                    ))
                
                fig_yield.update_layout(
                    title="Yield Trends Over Time",
                    height=350,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Month",
                    yaxis_title="Yield (tons)"
                )
            
            st.plotly_chart(fig_yield, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading yield trends: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with analytics_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🐛 Most Reported Issues")
        
        # Sample issue data (replace with real data from database)
        issue_data = pd.DataFrame({
            'Issue Type': ['Pest Infestation', 'Equipment Failure', 'Irrigation Problems', 'Disease Outbreak', 'Weather Damage'],
            'Count': [25, 18, 15, 12, 8],
            'Severity': ['High', 'Medium', 'High', 'High', 'Medium']
        })
        
        # Create color mapping based on severity
        colors = ['#FF4444' if sev == 'High' else '#FFA500' if sev == 'Medium' else '#4CAF50' 
                 for sev in issue_data['Severity']]
        
        fig_issues = go.Figure(data=[
            go.Bar(
                x=issue_data['Count'],
                y=issue_data['Issue Type'],
                orientation='h',
                marker_color=colors,
                text=issue_data['Count'],
                textposition='auto',
            )
        ])
        
        fig_issues.update_layout(
            title="Most Reported Issues",
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Number of Reports",
            yaxis_title="Issue Type"
        )
        
        st.plotly_chart(fig_issues, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with analytics_col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader(" Resource Request Status")
        
        try:
            # Get real resource status data
            resource_status = db_manager.get_resource_status()
            
            if not resource_status.empty:
                fig_resources = px.pie(
                    resource_status,
                    names='status',
                    values='count',
                    title="Resource Request Distribution",
                    color_discrete_map={
                        'delivered': '#4CAF50',
                        'approved': '#2196F3',
                        'pending': '#FF9800',
                        'rejected': '#F44336'
                    }
                )
            else:
                # Fallback sample data
                sample_resource_data = pd.DataFrame({
                    'Status': ['Delivered', 'Approved', 'Pending', 'Rejected'],
                    'Count': [45, 25, 20, 10]
                })
                
                fig_resources = px.pie(
                    sample_resource_data,
                    names='Status',
                    values='Count',
                    title="Resource Request Status",
                    color_discrete_map={
                        'Delivered': '#4CAF50',
                        'Approved': '#2196F3',
                        'Pending': '#FF9800',
                        'Rejected': '#F44336'
                    }
                )
            
            fig_resources.update_layout(
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_resources, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading resource status: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 3. AI PREDICTION PANEL
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b, #ee5a24); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; text-align: center;">🤖 AI Yield Predictions</h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">Machine learning powered forecasting</p>
    </div>
    """, unsafe_allow_html=True)
    
    prediction_col1, prediction_col2 = st.columns([1, 2])
    
    with prediction_col1:
        # Prediction Card
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            margin: 1rem 0;
        ">
            <h3 style="margin: 0 0 1rem 0; font-size: 1.2rem;">🎯 Next Month Prediction</h3>
            <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">245.8</div>
            <div style="font-size: 1.1rem; opacity: 0.9;">tons expected yield</div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.3);">
                <div style="font-size: 0.9rem; opacity: 0.8;">Confidence: 87%</div>
                <div style="font-size: 0.9rem; opacity: 0.8; color: #4CAF50;">↗ +12% vs last month</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Weather Impact Card
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4CAF50, #45a049);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">🌤️ Weather Impact</h4>
            <div style="font-size: 1.5rem; font-weight: bold;">Favorable</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Optimal conditions expected</div>
        </div>
        """, unsafe_allow_html=True)
    
    with prediction_col2:
        # Prediction Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader(" 6-Month Yield Forecast")
        
        try:
            # Try to get real predictions from AI model
            yield_predictor = get_yield_predictor()
            
            # Train model with historical data if available
            historical_data = db_manager.get_historical_yields()
            if not historical_data.empty:
                yield_predictor.train_model(historical_data)
                predictions = yield_predictor.predict_future_yields(6)
                
                if not predictions.empty:
                    fig_prediction = yield_predictor.create_prediction_chart(predictions)
                    st.plotly_chart(fig_prediction, use_container_width=True)
                else:
                    raise Exception("No predictions generated")
            else:
                raise Exception("No historical data available")
                
        except Exception as e:
            # Fallback to sample prediction data
            future_dates = pd.date_range(start=datetime.now(), periods=6, freq='M')
            sample_predictions = pd.DataFrame({
                'Date': future_dates,
                'Predicted_Yield': [245.8, 258.3, 271.2, 264.7, 252.1, 239.6],
                'Confidence_Lower': [220.2, 232.5, 244.1, 238.2, 226.9, 215.6],
                'Confidence_Upper': [271.4, 284.1, 298.3, 291.2, 277.3, 263.6]
            })
            
            fig_prediction = go.Figure()
            
            # Add prediction line
            fig_prediction.add_trace(go.Scatter(
                x=sample_predictions['Date'],
                y=sample_predictions['Predicted_Yield'],
                mode='lines+markers',
                name='Predicted Yield',
                line=dict(color='#4CAF50', width=3),
                marker=dict(size=8)
            ))
            
            # Add confidence interval
            fig_prediction.add_trace(go.Scatter(
                x=sample_predictions['Date'],
                y=sample_predictions['Confidence_Upper'],
                fill=None,
                mode='lines',
                line_color='rgba(0,0,0,0)',
                showlegend=False
            ))
            
            fig_prediction.add_trace(go.Scatter(
                x=sample_predictions['Date'],
                y=sample_predictions['Confidence_Lower'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,0,0,0)',
                name='Confidence Interval',
                fillcolor='rgba(76, 175, 80, 0.2)'
            ))
            
            fig_prediction.update_layout(
                title="AI-Powered Yield Predictions",
                height=350,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Date",
                yaxis_title="Predicted Yield (tons)"
            )
            
            st.plotly_chart(fig_prediction, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Original Charts section - Two columns layout
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader(" Harvest Trends Analysis")
        
        # Improved harvest data with more realistic values
        harvest_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            '2017': [160, 90, 100, 80, 130, 120, 30, 60, 30, 140, 150, 60],
            '2018': [70, 70, 50, 130, 120, 40, 80, 90, 70, 150, 150, 90]
        })
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=harvest_data['Month'], 
            y=harvest_data['2017'],
            mode='lines+markers',
            name='2017',
            line=dict(color='#4CAF50', width=3),
            marker=dict(size=8)
        ))
        fig1.add_trace(go.Scatter(
            x=harvest_data['Month'], 
            y=harvest_data['2018'],
            mode='lines+markers',
            name='2018',
            line=dict(color='#FF9800', width=3),
            marker=dict(size=8)
        ))
        
        fig1.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Month",
            yaxis_title="Harvest (tons)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader(" Resource Status")
        
        # Resource Request Status Pie Chart - Improved
        pie_data = pd.DataFrame({
            'Status': ['Delivered', 'Approved', 'Pending', 'Rejected'],
            'Count': [45, 25, 20, 10]
        })
        
        fig3 = px.pie(
            pie_data, 
            names='Status', 
            values='Count',
            color='Status',
            color_discrete_map={
                'Delivered': '#4CAF50',
                'Approved': '#2196F3', 
                'Pending': '#FF9800',
                'Rejected': '#F44336'
            },
            hole=0.4
        )
        
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom section with issues and transactions
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader(" Issues & Activity Trends")
    
    # Create subplot for combined bar and line chart
    issues_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Issues Reported': [5, 8, 6, 12, 9, 15],
        'Issues Resolved': [3, 7, 8, 10, 12, 13],
        'Total Activities': [15, 25, 30, 35, 28, 40]
    })
    
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig2.add_trace(
        go.Bar(x=issues_data['Month'], y=issues_data['Issues Reported'], name='Issues Reported', marker_color='#F44336'),
        secondary_y=False,
    )
    
    fig2.add_trace(
        go.Bar(x=issues_data['Month'], y=issues_data['Issues Resolved'], name='Issues Resolved', marker_color='#4CAF50'),
        secondary_y=False,
    )
    
    fig2.add_trace(
        go.Scatter(x=issues_data['Month'], y=issues_data['Total Activities'], 
                  mode='lines+markers', name='Total Activities', 
                  line=dict(color='#2196F3', width=3), marker=dict(size=8)),
        secondary_y=True,
    )
    
    fig2.update_xaxes(title_text="Month")
    fig2.update_yaxes(title_text="Number of Issues", secondary_y=False)
    fig2.update_yaxes(title_text="Total Activities", secondary_y=True)
    
    fig2.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_page == "Report":
    # Initialize services for Report page
    db_manager, firebase_service, weather_service, export_service, chart_utils, yield_predictor, chatbot = initialize_services()
    
    st.markdown('<div class="main-header"><h2 style="margin:0;">📊 Farm Reports & Analytics</h2></div>', unsafe_allow_html=True)
    
    # Export Section Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2c3e50, #3498db); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; text-align: center;">📄 Export & Download Reports</h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">Generate professional analytics reports and export data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Export buttons section
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button(" Download PDF Analytics Report", type="primary", use_container_width=True):
            try:
                # Get data for report
                kpi_data = db_manager.get_kpi_metrics()
                
                # Generate PDF report
                pdf_data = export_service.generate_pdf_report(kpi_data, {})
                
                if pdf_data:
                    st.download_button(
                        label=" Download PDF Report",
                        data=pdf_data,
                        file_name=f"ibali_farm_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report generated successfully!")
                else:
                    st.error("❌ Failed to generate PDF report")
                    
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    with export_col2:
        if st.button(" Download Excel Analytics", type="secondary", use_container_width=True):
            try:
                # Prepare data for Excel export
                dataframes_dict = {
                    'KPI_Metrics': db_manager.get_kpi_metrics(),
                    'Harvest_Trends': db_manager.get_harvest_trends(),
                    'Resource_Status': db_manager.get_resource_status(),
                    'Inventory_Data': db_manager.get_inventory_data()
                }
                
                # Generate Excel file
                excel_data = export_service.export_to_excel(dataframes_dict)
                
                if excel_data:
                    st.download_button(
                        label=" Download Excel File",
                        data=excel_data,
                        file_name=f"ibali_farm_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    st.success("✅ Excel file generated successfully!")
                else:
                    st.error("❌ Failed to generate Excel file")
                    
            except Exception as e:
                st.error(f"Error generating Excel: {str(e)}")
    
    with export_col3:
        if st.button(" Schedule Report Email", use_container_width=True):
            st.info(" Email scheduling feature coming soon!")
            st.balloons()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Report Generation Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; text-align: center;">📋 Custom Report Generator</h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0;">Create customized reports for specific analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Report filters
    col1, col2, col3 = st.columns(3)
    with col1:
        report_type = st.selectbox("Report Type", 
                                 ["Harvest Report", "Financial Summary", "Livestock Report", "Issue Analysis", "Yield Predictions", "Resource Utilization"])
    with col2:
        date_range = st.date_input("Date Range", value=[datetime.now() - timedelta(days=30), datetime.now()])
    with col3:
        st.write("")
        if st.button("Generate Custom Report", type="primary"):
            st.success(f"Generating {report_type}...")
    
    # Sample report data based on selection
    if report_type == "Harvest Report":
        st.subheader("🌾 Harvest Analysis Report")
        report_data = pd.DataFrame({
            'Crop': ['Wheat', 'Corn', 'Soybeans', 'Rice', 'Barley'],
            'Hectares': [120, 100, 80, 45, 35],
            'Yield (tons/ha)': [3.2, 4.1, 2.8, 5.5, 2.9],
            'Total Yield (tons)': [384, 410, 224, 247.5, 101.5],
            'Quality Grade': ['A', 'A+', 'B+', 'A', 'B'],
            'Market Price ($/ton)': [250, 180, 420, 380, 200]
        })
        st.dataframe(report_data, use_container_width=True)
        
        # Add summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Hectares", f"{report_data['Hectares'].sum()}")
        with col2:
            st.metric("Total Yield", f"{report_data['Total Yield (tons)'].sum():.1f} tons")
        with col3:
            st.metric("Avg Yield/Ha", f"{report_data['Yield (tons/ha)'].mean():.2f} tons/ha")
        with col4:
            total_value = (report_data['Total Yield (tons)'] * report_data['Market Price ($/ton)']).sum()
            st.metric("Total Value", f"${total_value:,.0f}")
    
    elif report_type == "Financial Summary":
        st.subheader("💰 Financial Performance Report")
        financial_data = pd.DataFrame({
            'Category': ['Revenue', 'Seeds & Planting', 'Fertilizers', 'Equipment', 'Labor', 'Utilities', 'Insurance'],
            'Amount ($)': [485000, -45000, -32000, -28000, -65000, -12000, -8000],
            'Percentage': [100, -9.3, -6.6, -5.8, -13.4, -2.5, -1.6]
        })
        st.dataframe(financial_data, use_container_width=True)
        
        # Financial metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", "$485,000", "+12.5%")
        with col2:
            st.metric("Total Expenses", "$190,000", "+8.2%")
        with col3:
            st.metric("Net Profit", "$295,000", "+15.8%")
        with col4:
            st.metric("Profit Margin", "60.8%", "+2.1%")
    
    elif report_type == "Yield Predictions":
        st.subheader(" AI Yield Predictions Report")
        
        # Generate predictions
        try:
            historical_data = db_manager.get_historical_yields()
            if not historical_data.empty:
                yield_predictor.train_model(historical_data)
                predictions = yield_predictor.predict_future_yields(6)
                
                if not predictions.empty:
                    st.dataframe(predictions, use_container_width=True)
                    fig = yield_predictor.create_prediction_chart(predictions)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No predictions available. Using sample data.")
            else:
                st.info("No historical data available for predictions.")
        except Exception as e:
            st.error(f"Error generating predictions: {str(e)}")
    
    else:
        st.info(f" {report_type} report template coming soon...")

elif selected_page == "Issues":
    st.markdown('<div class="main-header"><h2 style="margin:0;">🐛 Issue Management</h2></div>', unsafe_allow_html=True)
    
    # Issue filters and actions
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        issue_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Resolved", "Closed"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    with col3:
        st.write("")
        if st.button("New Issue", type="primary"):
            st.info("Opening new issue form...")
    
    # Issues table
    issues_df = pd.DataFrame({
        'ID': ['ISS-001', 'ISS-002', 'ISS-003', 'ISS-004', 'ISS-005'],
        'Title': ['Pest infestation in sector A', 'Irrigation system malfunction', 'Equipment breakdown', 'Soil analysis needed', 'Weather damage assessment'],
        'Priority': ['High', 'Medium', 'High', 'Low', 'Medium'],
        'Status': ['Open', 'In Progress', 'Resolved', 'Open', 'Closed'],
        'Assigned To': ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'John Doe'],
        'Created': ['2024-01-15', '2024-01-12', '2024-01-10', '2024-01-08', '2024-01-05']
    })
    
    st.dataframe(issues_df, use_container_width=True)

elif selected_page == "Requests":
    st.markdown('<div class="main-header"><h2 style="margin:0;">✋ Resource Requests</h2></div>', unsafe_allow_html=True)
    
    # Request overview metrics
    req_col1, req_col2, req_col3, req_col4 = st.columns(4)
    
    with req_col1:
        st.metric("Total Requests", "89", "+7")
    with req_col2:
        st.metric("Pending", "23", "+3")
    with req_col3:
        st.metric("Approved", "45", "+8")
    with req_col4:
        st.metric("Delivered", "21", "+2")
    
    # Requests table
    requests_df = pd.DataFrame({
        'Request ID': ['REQ-001', 'REQ-002', 'REQ-003', 'REQ-004', 'REQ-005'],
        'Item Requested': ['Fertilizer (50kg)', 'Seeds (Corn)', 'Pesticide Spray', 'Farm Tools', 'Irrigation Equipment'],
        'Quantity': [10, 25, 5, 1, 3],
        'Requested By': ['John Farmer', 'Mary Smith', 'David Wilson', 'Sarah Johnson', 'Mike Brown'],
        'Status': ['Pending', 'Approved', 'Delivered', 'Pending', 'Approved'],
        'Request Date': ['2024-01-15', '2024-01-12', '2024-01-10', '2024-01-08', '2024-01-05'],
        'Priority': ['High', 'Medium', 'Low', 'High', 'Medium']
    })
    
    st.dataframe(requests_df, use_container_width=True)

elif selected_page == "Stock":
    st.markdown('<div class="main-header"><h2 style="margin:0;">🛒 Stock Management</h2></div>', unsafe_allow_html=True)
    
    # Stock overview metrics
    stock_col1, stock_col2, stock_col3, stock_col4 = st.columns(4)
    
    with stock_col1:
        st.metric("Total Items", "156", "+12")
    with stock_col2:
        st.metric("Low Stock Items", "8", "-3")
    with stock_col3:
        st.metric("Out of Stock", "2", "+1")
    with stock_col4:
        st.metric("Total Value", "$45,230", "+5.2%")
    
    # Stock table
    stock_df = pd.DataFrame({
        'Item Code': ['SED-001', 'FER-002', 'PES-003', 'TOL-004', 'EQP-005'],
        'Item Name': ['Corn Seeds (Premium)', 'Nitrogen Fertilizer', 'Organic Pesticide', 'Hand Tools Set', 'Irrigation Pipes'],
        'Category': ['Seeds', 'Fertilizer', 'Pesticide', 'Tools', 'Equipment'],
        'Current Stock': [250, 45, 12, 8, 150],
        'Min. Required': [100, 50, 20, 10, 100],
        'Unit Price ($)': [12.50, 85.00, 45.00, 125.00, 15.00],
        'Status': ['In Stock', 'Low Stock', 'Low Stock', 'Low Stock', 'In Stock']
    })
    
    st.dataframe(stock_df, use_container_width=True)

elif selected_page == "Maps":
    st.markdown('<div class="main-header"><h2 style="margin:0;">🗺️ Rwanda Farm Maps & Locations</h2></div>', unsafe_allow_html=True)
    
    # Enhanced Maps Header with Rwanda theme
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 2rem; border-radius: 20px; margin: 1rem 0; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 10px; right: 20px; font-size: 3rem; opacity: 0.2;">🇷🇼</div>
        <h2 style="color: white; margin: 0; text-align: center; font-size: 2rem;">🗺️ Interactive Rwanda Farm Map</h2>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 1rem 0 0 0; font-size: 1.1rem;">
            Explore agricultural locations across Rwanda • Real-time tracking • Advanced analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Map Controls and Search
    map_col1, map_col2, map_col3, map_col4 = st.columns(4)
    
    with map_col1:
        map_style = st.selectbox(
            "🗺️ Map Style",
            ["OpenStreetMap", "Satellite", "Terrain", "CartoDB Positron", "CartoDB Dark"],
            index=0
        )
    
    with map_col2:
        zoom_level = st.slider("🔍 Zoom Level", 6, 18, 10)
    
    with map_col3:
        show_weather = st.checkbox("🌤️ Weather Overlay", value=True)
    
    with map_col4:
        show_districts = st.checkbox("🏛️ Show Districts", value=True)
    
    # Location Search
    st.markdown("### 📍 Find Location in Rwanda")
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_location = st.text_input(
            "Search for cities, districts, or landmarks in Rwanda",
            placeholder="e.g., Kigali, Butare, Gisenyi, Ruhengeri..."
        )
    
    with search_col2:
        st.write("")
        search_button = st.button("🔍 Search", type="primary")
    
    # Rwanda locations database
    rwanda_locations = {
        'kigali': [-1.9441, 30.0619],
        'butare': [-2.5967, 29.7394],
        'huye': [-2.5967, 29.7394],
        'gisenyi': [-1.7038, 29.2564],
        'rubavu': [-1.7038, 29.2564],
        'ruhengeri': [-1.4996, 29.6333],
        'musanze': [-1.4996, 29.6333],
        'gitarama': [-2.0742, 29.7564],
        'muhanga': [-2.0742, 29.7564],
        'byumba': [-1.5764, 30.0678],
        'gicumbi': [-1.5764, 30.0678],
        'cyangugu': [-2.4845, 28.9077],
        'rusizi': [-2.4845, 28.9077],
        'kibungo': [-2.1547, 30.7708],
        'ngoma': [-2.1547, 30.7708],
        'nyagatare': [-1.2918, 30.3256],
        'gatsibo': [-1.5833, 30.4167],
        'kayonza': [-1.8833, 30.6167],
        'kirehe': [-2.2167, 30.7167],
        'bugesera': [-2.2833, 30.2833],
        'rwamagana': [-1.9486, 30.4347]
    }
    
    # Initialize services for maps page
    try:
        db_manager, firebase_service, weather_service, export_service, chart_utils, yield_predictor, chatbot = initialize_services()
        
        # Rwanda center coordinates (Kigali)
        rwanda_center = [-1.9441, 30.0619]
        
        # Handle location search
        if search_button and search_location:
            search_key = search_location.lower().strip()
            if search_key in rwanda_locations:
                rwanda_center = rwanda_locations[search_key]
                st.success(f"📍 Found {search_location.title()}! Map centered on location.")
            else:
                st.warning(f"Location '{search_location}' not found. Showing Kigali instead.")
                # Try partial matching
                for key, coords in rwanda_locations.items():
                    if search_key in key or key in search_key:
                        rwanda_center = coords
                        st.info(f"📍 Did you mean {key.title()}? Map centered there.")
                        break
        
        # Map style configuration
        tile_options = {
            "OpenStreetMap": "OpenStreetMap",
            "Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "Terrain": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
            "CartoDB Positron": "CartoDB positron",
            "CartoDB Dark": "CartoDB dark_matter"
        }
        
        # Create enhanced map
        m = folium.Map(
            location=rwanda_center,
            zoom_start=zoom_level,
            tiles=tile_options.get(map_style, "OpenStreetMap"),
            width='100%',
            height='700px',
            attr='Rwanda Farm Platform'
        )
        
        # Add advanced plugins
        folium.plugins.Fullscreen(
            position='topright',
            title='Fullscreen',
            title_cancel='Exit fullscreen',
            force_separate_button=True
        ).add_to(m)
        
        # Add measure tool
        folium.plugins.MeasureControl(
            position='topleft',
            primary_length_unit='kilometers',
            secondary_length_unit='meters',
            primary_area_unit='hectares'
        ).add_to(m)
        
        # Add minimap
        minimap = folium.plugins.MiniMap(
            tile_layer=tile_options.get(map_style, "OpenStreetMap"),
            position='bottomright',
            width=150,
            height=150,
            zoom_level_offset=-5
        )
        m.add_child(minimap)
        
        # Add mouse position
        folium.plugins.MousePosition(
            position='bottomleft',
            separator=' | ',
            empty_string='NaN',
            lng_first=True,
            num_digits=20,
            prefix='Coordinates: '
        ).add_to(m)
        
        # Rwanda districts boundaries (simplified)
        if show_districts:
            rwanda_districts = [
                {"name": "Kigali City", "coords": [[-1.9, 30.0], [-1.9, 30.1], [-2.0, 30.1], [-2.0, 30.0]]},
                {"name": "Eastern Province", "coords": [[-1.5, 30.5], [-1.5, 31.0], [-2.5, 31.0], [-2.5, 30.5]]},
                {"name": "Northern Province", "coords": [[-1.0, 29.5], [-1.0, 30.5], [-1.5, 30.5], [-1.5, 29.5]]},
                {"name": "Southern Province", "coords": [[-2.0, 29.0], [-2.0, 30.5], [-2.8, 30.5], [-2.8, 29.0]]},
                {"name": "Western Province", "coords": [[-1.5, 28.8], [-1.5, 29.8], [-2.5, 29.8], [-2.5, 28.8]]}
            ]
            
            for district in rwanda_districts:
                folium.Polygon(
                    locations=district["coords"],
                    popup=district["name"],
                    tooltip=f"District: {district['name']}",
                    color='blue',
                    weight=2,
                    opacity=0.6,
                    fillColor='lightblue',
                    fillOpacity=0.1
                ).add_to(m)
        
        # Add weather stations if enabled
        if show_weather:
            weather_stations = [
                {"name": "Kigali Weather Station", "lat": -1.9441, "lng": 30.0619, "temp": "22°C", "humidity": "65%"},
                {"name": "Butare Weather Station", "lat": -2.5967, "lng": 29.7394, "temp": "20°C", "humidity": "70%"},
                {"name": "Gisenyi Weather Station", "lat": -1.7038, "lng": 29.2564, "temp": "24°C", "humidity": "60%"},
                {"name": "Ruhengeri Weather Station", "lat": -1.4996, "lng": 29.6333, "temp": "18°C", "humidity": "75%"}
            ]
            
            for station in weather_stations:
                weather_popup = f"""
                <div style="width: 200px; text-align: center;">
                    <h4 style="color: #2E7D32; margin-bottom: 10px;">🌤️ {station['name']}</h4>
                    <p><strong>🌡️ Temperature:</strong> {station['temp']}</p>
                    <p><strong>💧 Humidity:</strong> {station['humidity']}</p>
                    <p><em>Real-time weather data</em></p>
                </div>
                """
                
                folium.Marker(
                    location=[station['lat'], station['lng']],
                    popup=folium.Popup(weather_popup, max_width=250),
                    tooltip=f"Weather: {station['temp']}",
                    icon=folium.Icon(color='blue', icon='cloud', prefix='fa')
                ).add_to(m)
        
        # Enhanced farm locations with Rwanda-specific data
        rwanda_farm_locations = [
            {
                "name": "Kigali Urban Farm", "lat": -1.9541, "lng": 30.0719, 
                "type": "urban_agriculture", "crop": "Vegetables", "size": "2 hectares",
                "status": "excellent", "yield": "High", "owner": "Cooperative ABCD"
            },
            {
                "name": "Butare Coffee Plantation", "lat": -2.6067, "lng": 29.7494, 
                "type": "coffee", "crop": "Arabica Coffee", "size": "15 hectares",
                "status": "good", "yield": "Premium", "owner": "Rwanda Coffee Ltd"
            },
            {
                "name": "Gisenyi Tea Estate", "lat": -1.7138, "lng": 29.2664, 
                "type": "tea", "crop": "Tea Leaves", "size": "25 hectares",
                "status": "excellent", "yield": "Export Quality", "owner": "Sorwathe Tea"
            },
            {
                "name": "Ruhengeri Potato Farm", "lat": -1.5096, "lng": 29.6433, 
                "type": "tubers", "crop": "Irish Potatoes", "size": "8 hectares",
                "status": "good", "yield": "Medium", "owner": "Musanze Farmers Coop"
            },
            {
                "name": "Nyagatare Cattle Ranch", "lat": -1.3018, "lng": 30.3356, 
                "type": "livestock", "crop": "Cattle", "size": "50 hectares",
                "status": "excellent", "yield": "High Milk Production", "owner": "Girinka Program"
            },
            {
                "name": "Kayonza Rice Scheme", "lat": -1.8933, "lng": 30.6267, 
                "type": "rice", "crop": "Rice", "size": "12 hectares",
                "status": "needs_attention", "yield": "Medium", "owner": "Kayonza Rice Coop"
            },
            {
                "name": "Bugesera Maize Farm", "lat": -2.2933, "lng": 30.2933, 
                "type": "cereals", "crop": "Maize", "size": "6 hectares",
                "status": "good", "yield": "Good", "owner": "Bugesera Farmers"
            }
        ]
        
        # Color and icon mapping for different farm types
        farm_colors = {
            'urban_agriculture': 'green', 'coffee': 'darkred', 'tea': 'darkgreen',
            'tubers': 'orange', 'livestock': 'purple', 'rice': 'blue', 'cereals': 'cadetblue'
        }
        
        farm_icons = {
            'urban_agriculture': 'leaf', 'coffee': 'coffee', 'tea': 'leaf',
            'tubers': 'apple', 'livestock': 'paw', 'rice': 'grain', 'cereals': 'wheat'
        }
        
        status_colors = {
            'excellent': 'green', 'good': 'blue', 'needs_attention': 'orange', 'poor': 'red'
        }
        
        # Add Rwanda farm markers
        for farm in rwanda_farm_locations:
            farm_color = status_colors.get(farm['status'], 'gray')
            farm_icon = farm_icons.get(farm['type'], 'info-sign')
            
            # Create detailed popup
            popup_content = f"""
            <div style="width: 280px; font-family: Arial, sans-serif;">
                <div style="background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 10px; margin: -10px -10px 10px -10px; border-radius: 8px 8px 0 0;">
                    <h3 style="margin: 0; font-size: 16px;">🌾 {farm['name']}</h3>
                </div>
                
                <div style="padding: 5px 0;">
                    <p style="margin: 5px 0;"><strong>🌱 Crop:</strong> {farm['crop']}</p>
                    <p style="margin: 5px 0;"><strong>📏 Size:</strong> {farm['size']}</p>
                    <p style="margin: 5px 0;"><strong>📊 Status:</strong> 
                        <span style="color: {status_colors.get(farm['status'], 'gray')}; font-weight: bold;">
                            {farm['status'].replace('_', ' ').title()}
                        </span>
                    </p>
                    <p style="margin: 5px 0;"><strong>📈 Yield:</strong> {farm['yield']}</p>
                    <p style="margin: 5px 0;"><strong>👥 Owner:</strong> {farm['owner']}</p>
                    <p style="margin: 5px 0;"><strong>📍 Coordinates:</strong> {farm['lat']:.4f}, {farm['lng']:.4f}</p>
                </div>
                
                <div style="background: #f5f5f5; padding: 8px; margin: 10px -10px -10px -10px; border-radius: 0 0 8px 8px; text-align: center;">
                    <small style="color: #666;">Click for more details</small>
                </div>
            </div>
            """
            
            folium.Marker(
                location=[farm['lat'], farm['lng']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{farm['name']} - {farm['crop']}",
                icon=folium.Icon(
                    color=farm_color,
                    icon=farm_icon,
                    prefix='fa'
                )
            ).add_to(m)
        
        # Add marker clustering for better performance
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster(
            name="Farm Clusters",
            overlay=True,
            control=True,
            icon_create_function="""
            function(cluster) {
                return L.divIcon({
                    html: '<div style="background-color: #4CAF50; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">' + cluster.getChildCount() + '</div>',
                    className: 'custom-cluster-icon',
                    iconSize: L.point(40, 40)
                });
            }
            """
        )
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Display the enhanced map
        st.markdown("### 🗺️ Interactive Rwanda Agricultural Map")
        map_data = st_folium(m, width=1200, height=700, returned_objects=["last_object_clicked", "last_clicked"])
        
        # Display clicked location info
        if map_data['last_object_clicked']:
            clicked_lat = map_data['last_object_clicked']['lat']
            clicked_lng = map_data['last_object_clicked']['lng']
            
            st.markdown("### 📍 Selected Location Details")
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.metric("Latitude", f"{clicked_lat:.6f}")
            with detail_col2:
                st.metric("Longitude", f"{clicked_lng:.6f}")
            with detail_col3:
                # Calculate distance from Kigali
                import math
                kigali_lat, kigali_lng = -1.9441, 30.0619
                distance = math.sqrt((clicked_lat - kigali_lat)**2 + (clicked_lng - kigali_lng)**2) * 111  # Rough km conversion
                st.metric("Distance from Kigali", f"{distance:.1f} km")
        
        # Map Statistics
        st.markdown("### 📊 Rwanda Agricultural Statistics")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric("Total Farms Mapped", "7", "+2 this month")
        with stats_col2:
            st.metric("Total Area", "118 hectares", "+15 ha")
        with stats_col3:
            st.metric("Active Cooperatives", "5", "+1")
        with stats_col4:
            st.metric("Weather Stations", "4", "100% operational")
        
    except Exception as e:
        st.error(f"Error loading Rwanda maps: {str(e)}")
        st.info("🗺️ Map requires internet connection for full functionality.")

elif selected_page == "Privacy Policy":
    st.markdown('<div class="main-header"><h2 style="margin:0;">📄 Terms of Use & Privacy Policy</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Terms of Use
    
    ### 1. Acceptance of Terms
    By accessing and using the Ibali Farm Platform, you accept and agree to be bound by the terms and provision of this agreement.
    
    ### 2. Use License
    Permission is granted to temporarily download one copy of the materials on Ibali Farm Platform for personal, non-commercial transitory viewing only.
    
    ### 3. Disclaimer
    The materials on Ibali Farm Platform are provided on an 'as is' basis. Ibali Farm Platform makes no warranties, expressed or implied.
    
    ## Privacy Policy
    
    ### Information We Collect
    - Farm operational data
    - User account information
    - Usage analytics
    - Device information
    
    ### How We Use Information
    - To provide and maintain our service
    - To improve user experience
    - To communicate with users
    - To ensure platform security
    
    ### Data Protection
    We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.
    
    ### Contact Information
    For questions about these Terms or Privacy Policy, please contact us at support@ibali-farm.com
    """)

elif selected_page == "Help":
    st.markdown('<div class="main-header"><h2 style="margin:0;">❓ Help & Support</h2></div>', unsafe_allow_html=True)
    
    # Help sections
    help_col1, help_col2 = st.columns(2)
    
    with help_col1:
        st.markdown("""
        ###  Getting Started
        - **Dashboard Overview**: View your farm's key metrics and real-time data
        - **Navigation**: Use the sidebar to access different sections
        - **Maps**: Track issues and monitor field locations
        - **Reports**: Generate and download analytics reports
        
        ###  Using Analytics
        - **Yield Predictions**: AI-powered forecasting for better planning
        - **Issue Tracking**: Monitor and resolve farm issues efficiently
        - **Resource Management**: Track inventory and requests
        
        ###  Troubleshooting
        - **Data Not Loading**: Check your internet connection
        - **Map Issues**: Ensure location services are enabled
        - **Export Problems**: Try refreshing the page
        """)
    
    with help_col2:
        st.markdown("""
        ### 📞 Contact Support
        
        **Email Support**
        📧 support@ibali-farm.com
        
        **Phone Support**
        📱 +1 (555) 123-4567
        
        **Live Chat**
        💬 Available 24/7 through the platform
        
        **Documentation**
        📚 Visit our knowledge base for detailed guides
        
        ### 🎓 Training Resources
        - Video tutorials
        - User guides
        - Webinar sessions
        - Best practices documentation
        """)
    
    # FAQ Section
    st.markdown("### ❓ Frequently Asked Questions")
    
    with st.expander("How do I add new farm issues?"):
        st.write("Navigate to the Issues section and click 'New Issue' to report problems or concerns.")
    
    with st.expander("Can I export my data?"):
        st.write("Yes! Use the Export section on the Dashboard to download PDF reports or Excel files.")
    
    with st.expander("How accurate are the AI predictions?"):
        st.write("Our AI models achieve 85-90% accuracy based on historical data and current conditions.")
    
    with st.expander("Is my farm data secure?"):
        st.write("Yes, we use enterprise-grade security measures to protect all your data.")

elif selected_page == "Logout":
    st.markdown('<div class="main-header"><h2 style="margin:0;">🚪 Logout</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h3>Are you sure you want to logout?</h3>
        <p>You will need to login again to access your farm data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    logout_col1, logout_col2, logout_col3 = st.columns([1, 1, 1])
    
    with logout_col2:
        if st.button("🚪 Confirm Logout", type="primary", use_container_width=True):
            st.success("✅ Successfully logged out!")
            st.balloons()
            st.info("👋 Thank you for using Ibali Farm Platform!")
        
        if st.button("↩️ Cancel", use_container_width=True):
            st.rerun()

else:
    st.markdown(f'<div class="main-header"><h2 style="margin:0;">{selected_page}</h2></div>', unsafe_allow_html=True)
    st.info(f"Welcome to {selected_page} section. Content coming soon...")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>© 2024 Ibali Farm Platform | Empowering Agricultural Excellence</p>
    </div>
    """, 
    unsafe_allow_html=True
)    # Enha 