"""
Utility functions for Ibali Farm Agri-Platform
Handles weather API, export functions, and other utilities
"""
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import streamlit as st
import io
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_current_weather(_self, lat=0, lon=0, city=""):
        """Get current weather data"""
        try:
            if not _self.api_key:
                return _self._get_mock_weather()
            
            if city:
                url = f"{_self.base_url}/weather?q={city}&appid={_self.api_key}&units=metric"
            else:
                url = f"{_self.base_url}/weather?lat={lat}&lon={lon}&appid={_self.api_key}&units=metric"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed'],
                    'pressure': data['main']['pressure']
                }
            else:
                return _self._get_mock_weather()
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return _self._get_mock_weather()
    
    def _get_mock_weather(self):
        """Return mock weather data when API is not available"""
        return {
            'temperature': 22.5,
            'humidity': 65,
            'description': 'partly cloudy',
            'wind_speed': 3.2,
            'pressure': 1013
        }

class ExportService:
    @staticmethod
    def export_to_excel(dataframes_dict, filename="farm_report.xlsx"):
        """Export multiple dataframes to Excel"""
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in dataframes_dict.items():
                    if not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Excel export error: {e}")
            return None
    
    @staticmethod
    def generate_pdf_report(kpi_data, charts_data, filename="farm_report.pdf"):
        """Generate PDF report"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.HexColor('#2E7D32')
            )
            story.append(Paragraph("Ibali Farm Platform Report", title_style))
            story.append(Spacer(1, 20))
            
            # Date
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # KPI Section
            story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
            if not kpi_data.empty:
                kpi_table_data = [
                    ['Metric', 'Value'],
                    ['Total Harvest', f"{kpi_data.iloc[0]['total_harvest']:.1f} tons"],
                    ['Total Livestock', f"{kpi_data.iloc[0]['total_livestock']:.0f}"],
                    ['Pending Requests', f"{kpi_data.iloc[0]['pending_requests']:.0f}"],
                    ['Delivered Requests', f"{kpi_data.iloc[0]['delivered_requests']:.0f}"]
                ]
                
                kpi_table = Table(kpi_table_data)
                kpi_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(kpi_table)
            
            story.append(Spacer(1, 30))
            
            # Summary
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(
                "This report provides an overview of current farm operations, including harvest data, "
                "livestock counts, and resource request status. The data is automatically generated "
                "from the Ibali Farm Platform database.",
                styles['Normal']
            ))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            return None

class ChartUtils:
    @staticmethod
    def create_kpi_card(title, value, delta=None, delta_color="normal"):
        """Create a styled KPI card"""
        delta_html = ""
        if delta is not None:
            color = "#28a745" if delta_color == "normal" else "#dc3545" if delta_color == "inverse" else "#6c757d"
            delta_html = f'<div style="color: {color}; font-size: 0.9rem; margin-top: 5px;">{delta}</div>'
        
        return f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #4CAF50;
            text-align: center;
            margin: 0.5rem 0;
        ">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{title}</div>
            <div style="font-size: 2rem; font-weight: bold; color: #2E7D32; margin: 0.5rem 0;">{value}</div>
            {delta_html}
        </div>
        """
    
    @staticmethod
    def create_status_badge(status):
        """Create a status badge"""
        status_colors = {
            'good': {'bg': '#d4edda', 'color': '#155724'},
            'warning': {'bg': '#fff3cd', 'color': '#856404'},
            'danger': {'bg': '#f8d7da', 'color': '#721c24'},
            'info': {'bg': '#d1ecf1', 'color': '#0c5460'}
        }
        
        color_scheme = status_colors.get(status.lower(), status_colors['info'])
        
        return f"""
        <span style="
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            background-color: {color_scheme['bg']};
            color: {color_scheme['color']};
        ">{status.title()}</span>
        """

# Global service instances
@st.cache_resource
def get_weather_service():
    return WeatherService()

@st.cache_resource
def get_export_service():
    return ExportService()

@st.cache_resource
def get_chart_utils():
    return ChartUtils()