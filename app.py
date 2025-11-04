from flask import Flask, render_template, request, redirect, url_for, flash, session
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
# login_manager.login_view = 'login'

# app.register_blueprint(admin_bp)



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
    # app.run(debug=True)
    
    # Train model if not exists
    if not os.path.exists(Config.MODEL_PATH):
        print("Training machine learning model...")
        predictor.train_model()
        print("Model training completed!")
    else:
        predictor.load_model()
    
    # Run the application
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
