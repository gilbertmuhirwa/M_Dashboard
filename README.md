# 🌾 Ibali Farm Platform - AI-Driven Agricultural Management System

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)

## 🇷🇼 Overview

**Ibali Farm Platform** is a comprehensive, AI-powered agricultural management system specifically designed for Rwanda's farming sector. The platform combines real-time IoT monitoring, machine learning predictions, interactive mapping, and professional reporting to empower farmers and agricultural organizations across Rwanda.

### ✨ Key Features

- 🗺️ **Interactive Rwanda Maps** - Real-time farm location tracking with weather overlays
- 🤖 **AI Yield Predictions** - Machine learning-powered crop forecasting
- 📊 **Advanced Analytics** - Dynamic charts and real-time data visualization
- 🔥 **Firebase Integration** - Real-time alerts and IoT sensor monitoring
- 📄 **Professional Reports** - PDF and Excel export capabilities
- 🌤️ **Weather Integration** - Live weather data for informed decision-making
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices

## 🚀 Live Demo

Visit the live application: [Ibali Farm Platform](https://your-streamlit-app-url.com)

## 📸 Screenshots

### Dashboard Overview
![Dashboard](screenshots/dashboard.png)

### Rwanda Interactive Maps
![Maps](screenshots/maps.png)

### AI Predictions
![Predictions](screenshots/predictions.png)

## 🛠️ Technology Stack

### Backend
- **Python 3.13+** - Core application language
- **Streamlit** - Web application framework
- **PostgreSQL** - Primary database for operational data
- **Firebase** - Real-time database and authentication

### AI & Analytics
- **scikit-learn** - Machine learning models
- **Plotly** - Interactive data visualization
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing

### Mapping & Visualization
- **Folium** - Interactive maps
- **OpenStreetMap** - Map tiles and geographic data
- **Streamlit-Folium** - Streamlit-Folium integration

### Export & Reporting
- **ReportLab** - PDF generation
- **OpenPyXL** - Excel file creation
- **Matplotlib** - Static chart generation

## 📦 Installation

### Prerequisites
- Python 3.13 or higher
- PostgreSQL database
- Firebase account (optional, for real-time features)

### 1. Clone the Repository
```bash
git clone https://github.com/muhirwa23/Dahboard.git
cd Dahboard
```

### 2. Create Virtual Environment
```bash
python -m venv myvenv
# Windows
myvenv\Scripts\activate
# macOS/Linux
source myvenv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ibali_farm
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# API Keys (Optional)
OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY=your_weather_api_key
MAPBOX_TOKEN=your_mapbox_token

# Firebase Configuration (Optional)
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
```

### 5. Database Setup
```sql
-- Create PostgreSQL database
CREATE DATABASE ibali_farm;

-- Create sample tables (run the SQL scripts in /database folder)
```

### 6. Run the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🗺️ Rwanda-Specific Features

### Supported Locations
The platform includes comprehensive support for major Rwandan locations:

- **Kigali** - Capital city and urban agriculture
- **Butare (Huye)** - Coffee plantations
- **Gisenyi (Rubavu)** - Tea estates
- **Ruhengeri (Musanze)** - Potato farming
- **Nyagatare** - Livestock ranching
- **Kayonza** - Rice schemes
- **Bugesera** - Maize production

### Agricultural Data
- **7 Real farm locations** with authentic coordinates
- **Weather stations** in major agricultural regions
- **District boundaries** and administrative divisions
- **Crop-specific insights** for Rwanda's main agricultural products

## 🤖 AI Features

### Yield Prediction Model
- **Random Forest Regressor** for crop yield forecasting
- **6-month ahead predictions** with confidence intervals
- **Weather impact analysis** on crop performance
- **Historical data training** for improved accuracy

### Intelligent Chatbot
- **OpenAI GPT-3.5 integration** for farming advice
- **Local knowledge base** for common agricultural questions
- **Context-aware responses** using real farm data
- **Multilingual support** (English, Kinyarwanda planned)

## 📊 Analytics & Reporting

### Real-Time Dashboards
- **KPI metrics** with live updates
- **Interactive charts** using Plotly
- **Issue tracking** with priority management
- **Resource request monitoring**

### Export Capabilities
- **PDF reports** with professional styling
- **Excel spreadsheets** with multiple data sheets
- **Automated report scheduling** (planned)
- **Email delivery** (planned)

## 🔧 Configuration

### Firebase Setup (Optional)
1. Create a Firebase project
2. Enable Realtime Database
3. Download service account credentials
4. Update `config.py` with your Firebase configuration

### Database Schema
The platform uses PostgreSQL with the following main tables:
- `harvests` - Crop harvest data
- `farm_issues` - Issue tracking with GPS coordinates
- `resource_requests` - Resource request management
- `inventory` - Stock and inventory management
- `historical_harvests` - Data for ML training

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect to Streamlit Cloud
3. Add environment variables in Streamlit secrets
4. Deploy automatically

### Docker Deployment
```bash
# Build Docker image
docker build -t ibali-farm-platform .

# Run container
docker run -p 8501:8501 ibali-farm-platform
```

### Heroku Deployment
```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
```

## 🧪 Testing

Run the integration tests:
```bash
python test_integration.py
```

This will verify:
- ✅ All dependencies are installed
- ✅ Custom modules are working
- ✅ Service initialization is correct
- ✅ Database connections are functional

## 📈 Performance

### Optimization Features
- **Streamlit caching** for database queries
- **Lazy loading** for large datasets
- **Connection pooling** for database efficiency
- **Marker clustering** for map performance

### Scalability
- **Microservices architecture** ready
- **API-first design** for external integrations
- **Cloud deployment** optimized
- **Multi-tenant** support planned

## 🤝 Contributing

We welcome contributions to improve the Ibali Farm Platform!

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python test_integration.py`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions
- Include type hints where appropriate

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rwanda Ministry of Agriculture** for agricultural data insights
- **OpenStreetMap** contributors for mapping data
- **Streamlit** team for the amazing framework
- **Firebase** for real-time database capabilities
- **Rwanda ICT Chamber** for supporting AgTech innovation

## 📞 Support

For support and questions:

- **Email**: support@ibali-farm.com
- **GitHub Issues**: [Create an issue](https://github.com/muhirwa23/Dahboard/issues)
- **Documentation**: [Wiki](https://github.com/muhirwa23/Dahboard/wiki)

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core dashboard functionality
- ✅ Rwanda maps integration
- ✅ AI yield predictions
- ✅ Real-time monitoring

### Phase 2 (Planned)
- 🔄 Mobile application
- 🔄 SMS notifications
- 🔄 Kinyarwanda language support
- 🔄 Offline functionality

### Phase 3 (Future)
- 📅 IoT sensor integration
- 📅 Blockchain traceability
- 📅 Marketplace integration
- 📅 Financial services integration

---

**Made with ❤️ for Rwanda's agricultural sector**

*Empowering farmers through technology and data-driven insights*# M_Dashboard
