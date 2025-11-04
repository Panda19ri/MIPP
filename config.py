import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medical-insurance-prediction-secret-key-2024'
    
    # Database Configuration
    DATABASE_PATH = 'database.db'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Application Configuration
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Model Configuration
    MODEL_PATH = 'models/insurance_model.pkl'
    SCALER_PATH = 'models/scaler.pkl'
    
    # Admin Configuration
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'
    DEFAULT_ADMIN_EMAIL = 'admin@insurance.com'
