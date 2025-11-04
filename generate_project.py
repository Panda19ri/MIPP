#!/usr/bin/env python3
"""
Medical Insurance Premium Prediction Project Generator
Run this script to create all project files automatically.
"""

import os
import shutil

def create_directory_structure():
    """Create the complete directory structure."""
    directories = [
        'models',
        'database', 
        'routes',
        'templates',
        'templates/admin',
        'static',
        'static/css',
        'static/js', 
        'static/images',
        'data',
        'utils',
        'backups'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files
    init_files = ['models', 'database', 'routes', 'utils']
    for init_dir in init_files:
        init_path = os.path.join(init_dir, '__init__.py')
        with open(init_path, 'w') as f:
            f.write(f'# {init_dir} module\n')
        print(f"Created: {init_path}")

def create_requirements_txt():
    """Create requirements.txt file."""
    requirements = """Flask==2.3.3
Flask-Login==0.6.3
Werkzeug==2.3.7
scikit-learn==1.3.0
pandas==2.1.1
numpy==1.25.2
joblib==1.3.2"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("Created: requirements.txt")

def create_config_py():
    """Create config.py file."""
    config_content = '''import os
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
'''
    
    with open('config.py', 'w') as f:
        f.write(config_content)
    print("Created: config.py")

def create_app_py():
    """Create main app.py file."""
    app_content = '''from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from config import Config
from database.db_manager import init_database, get_user_by_username, create_admin_user
from models.ml_model import InsurancePremiumPredictor
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from database.db_manager import get_user_by_id
    return get_user_by_id(user_id)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

# Initialize ML model
predictor = InsurancePremiumPredictor()

@app.route('/')
def index():
    """Homepage route"""
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Prediction route"""
    if request.method == 'POST':
        try:
            # Get form data
            age = int(request.form['age'])
            gender = request.form['gender']
            bmi = float(request.form['bmi'])
            children = int(request.form['children'])
            smoker = request.form['smoker']
            region = request.form['region']
            
            # Make prediction
            prediction = predictor.predict(age, gender, bmi, children, smoker, region)
            
            # Save prediction to database
            from database.db_manager import save_prediction
            save_prediction(current_user.id, age, gender, bmi, children, smoker, region, prediction)
            
            flash(f'Predicted Insurance Premium: ${prediction:.2f}', 'success')
            return redirect(url_for('user.dashboard'))
            
        except ValueError as e:
            flash('Please enter valid values for all fields.', 'error')
        except Exception as e:
            flash('An error occurred during prediction. Please try again.', 'error')
    
    return render_template('predict.html')

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('base.html', error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('base.html', error_message='Internal server error'), 500

if __name__ == '__main__':
    # Initialize database and create admin user
    init_database()
    create_admin_user()
    
    # Train model if not exists
    if not os.path.exists(Config.MODEL_PATH):
        print("Training machine learning model...")
        predictor.train_model()
        print("Model training completed!")
    else:
        predictor.load_model()
    
    # Run the application
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
'''
    
    with open('app.py', 'w') as f:
        f.write(app_content)
    print("Created: app.py")

def create_basic_html_template():
    """Create a basic HTML template to get started."""
    basic_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Insurance Premium Prediction</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8 text-center">
                <h1 class="mb-4">Medical Insurance Premium Prediction</h1>
                <div class="alert alert-info">
                    <h4>Project Setup Complete!</h4>
                    <p>Your project structure has been created successfully.</p>
                    <p><strong>Next Steps:</strong></p>
                    <ol class="list-unstyled">
                        <li>1. Install dependencies: <code>pip install -r requirements.txt</code></li>
                        <li>2. Copy all the provided code files into their respective directories</li>
                        <li>3. Run the application: <code>python app.py</code></li>
                    </ol>
                    <p class="mt-3">
                        <strong>Admin Login:</strong> admin / admin123
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    with open('templates/index.html', 'w') as f:
        f.write(basic_html)
    print("Created: templates/index.html (basic template)")

def create_readme():
    """Create README.md file."""
    readme_content = '''# Medical Insurance Premium Prediction

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application:**
   ```bash
   python app.py
   ```

3. **Access Application:**
   - Open browser to `http://localhost:5000`
   - Admin Login: `admin` / `admin123`

## 📁 Project Structure

- `app.py` - Main Flask application
- `config.py` - Configuration settings
- `models/` - Machine learning model
- `database/` - Database management
- `routes/` - Web routes
- `templates/` - HTML templates
- `static/` - CSS, JS, images
- `data/` - Sample data
- `utils/` - Helper functions

## 🔧 Features

- ✅ User authentication
- ✅ AI-powered predictions
- ✅ Admin dashboard
- ✅ Responsive design
- ✅ Prediction history
- ✅ SQLite database

## 📊 Tech Stack

- **Backend:** Python Flask
- **Database:** SQLite
- **ML:** Scikit-learn
- **Frontend:** Bootstrap 5, JavaScript

## 🎯 Next Steps

After running the generator script:
1. Copy all provided code files to their respective directories
2. Install requirements: `pip install -r requirements.txt`
3. Run the app: `python app.py`

Enjoy your insurance prediction system! 🎉
'''
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("Created: README.md")

def main():
    """Main function to generate the complete project."""
    print("🚀 Medical Insurance Premium Prediction - Project Generator")
    print("=" * 60)
    
    # Create directory structure
    print("\\n📁 Creating directory structure...")
    create_directory_structure()
    
    # Create core files
    print("\\n📄 Creating core project files...")
    create_requirements_txt()
    create_config_py()
    create_app_py()
    create_basic_html_template()
    create_readme()
    
    print("\\n" + "=" * 60)
    print("✅ Project structure created successfully!")
    print("\\n📋 Next Steps:")
    print("1. Copy all the provided code files from the artifacts into their respective directories")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the application: python app.py")
    print("4. Access at: http://localhost:5000")
    print("5. Admin login: admin / admin123")
    
    print("\\n🎉 Happy coding!")

if __name__ == "__main__":
    main()