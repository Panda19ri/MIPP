from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database.db_manager import get_user_predictions, save_prediction
from models.ml_model import InsurancePremiumPredictor

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Get recent predictions
    predictions = get_user_predictions(current_user.id, limit=5)
    
    return render_template('dashboard.html', predictions=predictions)

@user_bp.route('/history')
@login_required
def history():
    """User prediction history"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Get all predictions for the user (increased limit)
    predictions = get_user_predictions(current_user.id, limit=100)
    
    # Debug: Print predictions to console
    print(f"User {current_user.id} has {len(predictions)} predictions")
    for pred in predictions[:3]:  # Print first 3 for debugging
        print(f"Prediction: {dict(pred)}")
    
    return render_template('history.html', predictions=predictions)

@user_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Make insurance premium prediction"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            age = int(request.form['age'])
            gender = request.form['gender']
            bmi = float(request.form['bmi'])
            children = int(request.form['children'])
            smoker = request.form['smoker']
            region = request.form['region']
            
            # Validate inputs
            if not (18 <= age <= 100):
                flash('Age must be between 18 and 100.', 'error')
                return render_template('predict.html')
            
            if not (10 <= bmi <= 50):
                flash('BMI must be between 10 and 50.', 'error')
                return render_template('predict.html')
            
            if not (0 <= children <= 10):
                flash('Number of children must be between 0 and 10.', 'error')
                return render_template('predict.html')
            
            if gender not in ['male', 'female']:
                flash('Please select a valid gender.', 'error')
                return render_template('predict.html')
            
            if smoker not in ['yes', 'no']:
                flash('Please select smoking status.', 'error')
                return render_template('predict.html')
            
            if region not in ['northeast', 'southeast', 'southwest', 'northwest']:
                flash('Please select a valid region.', 'error')
                return render_template('predict.html')
            
            # Make prediction
            predictor = InsurancePremiumPredictor()
            prediction = predictor.predict(age, gender, bmi, children, smoker, region)
            
            # Save prediction to database
            save_prediction(current_user.id, age, gender, bmi, children, smoker, region, prediction)
            
            flash(f'Predicted Insurance Premium: ${prediction:,.2f}', 'success')
            return redirect(url_for('user.dashboard'))
            
        except ValueError as e:
            flash('Please enter valid numerical values.', 'error')
        except Exception as e:
            flash('An error occurred during prediction. Please try again.', 'error')
            print(f"Prediction error: {e}")  # For debugging
    
    return render_template('predict.html')

@user_bp.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """API endpoint for prediction (AJAX)"""
    if current_user.is_admin:
        return jsonify({'error': 'Admin users cannot make predictions'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['age', 'gender', 'bmi', 'children', 'smoker', 'region']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Make prediction
        predictor = InsurancePremiumPredictor()
        prediction = predictor.predict(
            data['age'], data['gender'], data['bmi'],
            data['children'], data['smoker'], data['region']
        )
        
        # Save prediction to database
        save_prediction(
            current_user.id, data['age'], data['gender'], data['bmi'],
            data['children'], data['smoker'], data['region'], prediction
        )
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'formatted_prediction': f'${prediction:,.2f}'
        })
        
    except Exception as e:
        print(f"API Prediction error: {e}")
        return jsonify({'error': 'Prediction failed'}), 500

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Get user statistics
    predictions = get_user_predictions(current_user.id, limit=1000)  # Get all predictions
    
    stats = {
        'total_predictions': len(predictions),
        'avg_premium': sum([p['predicted_premium'] for p in predictions]) / len(predictions) if predictions else 0,
        'latest_prediction': predictions[0] if predictions else None
    }
    
    return render_template('profile.html', stats=stats)

# ✅ New Chatbot API
@user_bp.route('/chatbot_api', methods=['POST'])
@login_required
def chatbot_api():
    """Simple chatbot API endpoint"""
    if current_user.is_admin:
        return jsonify({'error': 'Admin users cannot use chatbot'}), 403

    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a valid message."}), 400

        # 🔹 Simple mock chatbot response (can be extended later)
        reply = f"You said: {user_message}"

        return jsonify({"reply": reply})
    
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({"error": "Something went wrong"}), 500
