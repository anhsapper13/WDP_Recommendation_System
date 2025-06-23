# 🎯 CRAFFT/ASSIST Recommendation System

A comprehensive **FastAPI-based recommendation system** for drug prevention and addiction support, featuring both **content-based** and **collaborative filtering** algorithms.

## 🌟 Features

### 🧠 Machine Learning Recommendations
- **Content-Based Filtering**: TF-IDF vectorization with cosine similarity
- **Collaborative Filtering**: User-item matrix with similarity scoring
- **Hybrid Approach**: Combines both methods for optimal results
- **Risk-Level Mapping**: Recommendations based on CRAFFT/ASSIST assessment scores

### 📊 Data Processing
- **SQLAlchemy ORM**: Type-safe database operations
- **Pandas Integration**: Seamless data manipulation and analysis
- **Database Agnostic**: Works with PostgreSQL, SQLite, MySQL
- **Real-time Analytics**: Live data processing and insights

### 🔄 Recommendation Types
- **Course Recommendations**: Educational content based on risk level
- **Consultant Matching**: Professional counselors aligned with user needs
- **Behavioral Analysis**: Similar user pattern recognition
- **Risk Assessment**: Automated scoring and level determination

## 🏗️ Architecture

```
app/
├── main.py                 # FastAPI application entry point
├── database/
│   └── database.py        # Database connection and configuration
├── models/               # SQLAlchemy ORM models
│   ├── user.py
│   ├── course.py
│   ├── consultant.py
│   ├── appointment.py
│   └── ...
├── routes/              # API endpoints
│   └── recommendation_routes.py
└── service/            # Business logic
    └── recommendation_action.py
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/WDP_AI.git
cd WDP_AI
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration
Create a `.env` file:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=your_password
DB_DATABASE=drug_prevention
DB_SYNCHRONIZE=true
DB_LOGGING=true
```

### 4. Run the Application
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API
```bash
# Access API documentation
open http://localhost:8000/docs

# Test endpoints
curl http://localhost:8000/recommendations/data/user-surveys
curl http://localhost:8000/recommendations/demo/user123
```

## 📡 API Endpoints

### 🔍 Data Access
- `GET /recommendations/data/user-surveys` - All survey data
- `GET /recommendations/data/courses` - Course information
- `GET /recommendations/data/consultants` - Consultant profiles

### 🎯 Recommendations
- `GET /recommendations/{user_id}` - Full hybrid recommendations
- `GET /recommendations/{user_id}/courses` - Course recommendations only
- `GET /recommendations/{user_id}/consultants` - Consultant recommendations
- `GET /recommendations/{user_id}/collaborative` - Collaborative filtering results

### 📊 Analytics
- `GET /recommendations/{user_id}/risk-summary` - User risk assessment
- `GET /recommendations/{user_id}/recommendation-explanation` - Detailed explanations
- `GET /recommendations/demo/{user_id}` - Full system demonstration

## 🧪 Example Response

```json
{
  "courses": [
    {
      "course_id": "123",
      "title": "Substance Abuse Prevention",
      "description": "Comprehensive prevention strategies...",
      "score": 0.85,
      "recommendation_type": "hybrid"
    }
  ],
  "consultants": [
    {
      "consultant_id": "456",
      "name": "Dr. Jane Smith",
      "specialization": "Addiction Counseling",
      "score": 0.92,
      "recommendation_type": "content_based"
    }
  ],
  "user_risk_info": {
    "latest_risk_level": "MEDIUM",
    "latest_score": 15,
    "total_surveys_taken": 3
  },
  "status": "success"
}
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: PostgreSQL, SQLAlchemy ORM
- **ML/Analytics**: Pandas, Scikit-learn, NumPy
- **API Documentation**: Swagger/OpenAPI
- **Containerization**: Docker, Docker Compose

## 📋 Requirements

```txt
fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.0
psycopg2-binary>=2.9.0
pandas>=1.3.0
scikit-learn>=1.0.0
numpy>=1.21.0
python-dotenv>=0.19.0
pydantic>=1.8.0
```

## 🔬 Testing

```bash
# Run database connection test
python test_database_connection.py

# Test recommendation system
curl http://localhost:8000/recommendations/demo/user123
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Project Goals

- **Personalized Recommendations**: AI-driven suggestions for educational content and professional support
- **Evidence-Based**: Built on CRAFFT/ASSIST standardized assessment tools
- **Scalable Architecture**: Designed for production deployment
- **Real-time Processing**: Live recommendation updates based on user behavior

## 📧 Contact

- **Project Lead**: [Your Name]
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

---

**Built with ❤️ for drug prevention and addiction support**
