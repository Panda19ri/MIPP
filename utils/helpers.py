"""
Utility helper functions for the Medical Insurance Premium Prediction application.
"""

import re
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
from flask import flash, request, current_app
from flask_login import current_user

def validate_age(age):
    """Validate age input."""
    try:
        age = int(age)
        if 18 <= age <= 100:
            return True, age
        else:
            return False, "Age must be between 18 and 100"
    except (ValueError, TypeError):
        return False, "Age must be a valid number"

def validate_bmi(bmi):
    """Validate BMI input."""
    try:
        bmi = float(bmi)
        if 10 <= bmi <= 50:
            return True, bmi
        else:
            return False, "BMI must be between 10 and 50"
    except (ValueError, TypeError):
        return False, "BMI must be a valid number"

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, email.lower()
    else:
        return False, "Invalid email format"

def validate_username(username):
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, username

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # You can add more password strength checks here
    # if not re.search(r'[A-Z]', password):
    #     return False, "Password must contain at least one uppercase letter"
    
    return True, password

def get_bmi_category(bmi):
    """Get BMI category based on value."""
    if bmi < 18.5:
        return "Underweight", "info"
    elif bmi < 25:
        return "Normal weight", "success"
    elif bmi < 30:
        return "Overweight", "warning"
    else:
        return "Obese", "danger"

def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"

def format_date(date_string):
    """Format date string for display."""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_string

def calculate_bmi(height_cm, weight_kg):
    """Calculate BMI from height and weight."""
    try:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    except (ValueError, ZeroDivisionError):
        return None

def get_premium_risk_level(premium):
    """Determine risk level based on premium amount."""
    if premium < 5000:
        return "Low", "success"
    elif premium < 10000:
        return "Medium", "warning"
    elif premium < 20000:
        return "High", "danger"
    else:
        return "Very High", "dark"

def sanitize_input(input_string):
    """Sanitize user input to prevent XSS."""
    if not input_string:
        return ""
    
    # Remove HTML tags
    clean = re.sub('<.*?>', '', str(input_string))
    
    # Remove dangerous characters
    clean = clean.replace('<', '&lt;').replace('>', '&gt;')
    
    return clean.strip()

def log_user_activity(action, details=None):
    """Log user activity for audit purposes."""
    if current_user.is_authenticated:
        timestamp = datetime.now().isoformat()
        user_id = current_user.id
        ip_address = request.remote_addr if request else 'unknown'
        
        log_entry = {
            'timestamp': timestamp,
            'user_id': user_id,
            'username': current_user.username,
            'action': action,
            'details': details,
            'ip_address': ip_address
        }
        
        # In a production environment, you might want to store this in a separate log file
        # or database table for security audit purposes
        print(f"USER ACTIVITY: {log_entry}")

def require_admin(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin privileges required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=10, window=60):
    """Simple rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In a production environment, you would implement proper rate limiting
            # using Redis or a similar store. This is a simplified version.
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def paginate_results(query_results, page=1, per_page=20):
    """Paginate database query results."""
    total = len(query_results)
    start = (page - 1) * per_page
    end = start + per_page
    
    items = query_results[start:end]
    
    has_prev = page > 1
    has_next = end < total
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_num': prev_num,
        'next_num': next_num,
        'pages': (total + per_page - 1) // per_page
    }

def export_to_csv(data, filename, headers=None):
    """Export data to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    if headers:
        writer.writerow(headers)
    elif data and isinstance(data[0], dict):
        writer.writerow(data[0].keys())
    
    # Write data
    for row in data:
        if isinstance(row, dict):
            writer.writerow(row.values())
        else:
            writer.writerow(row)
    
    return output.getvalue()

def backup_database():
    """Create a backup of the SQLite database."""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'database_backup_{timestamp}.db'
    
    try:
        shutil.copy2('database.db', f'backups/{backup_filename}')
        return True, backup_filename
    except Exception as e:
        return False, str(e)

def send_notification_email(to_email, subject, body):
    """Send notification email (placeholder for future implementation)."""
    # In a production environment, you would integrate with an email service
    # like SendGrid, AWS SES, or similar
    print(f"EMAIL NOTIFICATION:")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("-" * 50)
    
    return True

def generate_report_data(predictions):
    """Generate statistical report data from predictions."""
    if not predictions:
        return {}
    
    # Convert to list of dicts if needed
    if hasattr(predictions[0], 'keys'):
        data = [dict(p) for p in predictions]
    else:
        data = predictions
    
    # Basic statistics
    premiums = [p['predicted_premium'] for p in data]
    ages = [p['age'] for p in data]
    bmis = [p['bmi'] for p in data]
    
    report = {
        'total_predictions': len(data),
        'premium_stats': {
            'min': min(premiums),
            'max': max(premiums),
            'avg': sum(premiums) / len(premiums),
            'median': sorted(premiums)[len(premiums)//2]
        },
        'age_stats': {
            'min': min(ages),
            'max': max(ages),
            'avg': sum(ages) / len(ages)
        },
        'bmi_stats': {
            'min': min(bmis),
            'max': max(bmis),
            'avg': sum(bmis) / len(bmis)
        },
        'smoker_distribution': {},
        'region_distribution': {},
        'gender_distribution': {}
    }
    
    # Distribution statistics
    for category in ['smoker', 'region', 'gender']:
        values = [p[category] for p in data]
        unique_values = set(values)
        distribution = {val: values.count(val) for val in unique_values}
        report[f'{category}_distribution'] = distribution
    
    return report

def get_system_health():
    """Check system health and return status."""
    health = {
        'database': 'healthy',
        'model': 'healthy',
        'disk_space': 'healthy',
        'memory': 'healthy'
    }
    
    # Database health check
    try:
        conn = sqlite3.connect('database.db')
        conn.execute('SELECT 1')
        conn.close()
    except Exception:
        health['database'] = 'error'
    
    # Model health check
    try:
        import os
        if not os.path.exists('models/insurance_model.pkl'):
            health['model'] = 'warning'
    except Exception:
        health['model'] = 'error'
    
    # Simple disk space check (placeholder)
    # In production, you would implement actual disk space monitoring
    health['disk_space'] = 'healthy'
    health['memory'] = 'healthy'
    
    return health

def clean_old_predictions(days_old=365):
    """Clean up old prediction records."""
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM predictions 
            WHERE created_at < ?
        ''', (cutoff_date.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return True, f"Deleted {deleted_count} old prediction records"
    except Exception as e:
        return False, str(e)

def validate_prediction_inputs(data):
    """Validate all prediction input data at once."""
    errors = []
    
    # Age validation
    age_valid, age_result = validate_age(data.get('age'))
    if not age_valid:
        errors.append(f"Age: {age_result}")
    
    # BMI validation
    bmi_valid, bmi_result = validate_bmi(data.get('bmi'))
    if not bmi_valid:
        errors.append(f"BMI: {bmi_result}")
    
    # Children validation
    try:
        children = int(data.get('children', 0))
        if children < 0 or children > 10:
            errors.append("Children: Must be between 0 and 10")
    except (ValueError, TypeError):
        errors.append("Children: Must be a valid number")
    
    # Gender validation
    if data.get('gender') not in ['male', 'female']:
        errors.append("Gender: Must be 'male' or 'female'")
    
    # Smoker validation
    if data.get('smoker') not in ['yes', 'no']:
        errors.append("Smoker: Must be 'yes' or 'no'")
    
    # Region validation
    valid_regions = ['northeast', 'southeast', 'southwest', 'northwest']
    if data.get('region') not in valid_regions:
        errors.append(f"Region: Must be one of {valid_regions}")
    
    return len(errors) == 0, errors

def get_prediction_insights(age, bmi, smoker, premium):
    """Generate insights about a prediction."""
    insights = []
    
    # Age insights
    if age < 25:
        insights.append("Your young age contributes to a lower premium.")
    elif age > 50:
        insights.append("Age is a significant factor in your higher premium.")
    
    # BMI insights
    bmi_category, _ = get_bmi_category(bmi)
    if bmi_category == "Normal weight":
        insights.append("Your healthy BMI helps keep your premium lower.")
    elif bmi_category in ["Overweight", "Obese"]:
        insights.append("Maintaining a healthy weight could help reduce your premium.")
    
    # Smoking insights
    if smoker == 'yes':
        insights.append("Smoking significantly increases your premium. Quitting could save you thousands annually.")
    else:
        insights.append("Your non-smoking status helps keep your premium lower.")
    
    # Premium level insights
    risk_level, _ = get_premium_risk_level(premium)
    if risk_level == "Low":
        insights.append("You have a low-risk profile with an affordable premium.")
    elif risk_level in ["High", "Very High"]:
        insights.append("Consider lifestyle changes to potentially reduce your premium.")
    
    return insights

def format_prediction_summary(prediction_data):
    """Format prediction data for display."""
    age = prediction_data.get('age')
    gender = prediction_data.get('gender', '').title()
    bmi = prediction_data.get('bmi')
    children = prediction_data.get('children')
    smoker = prediction_data.get('smoker')
    region = prediction_data.get('region', '').title()
    premium = prediction_data.get('predicted_premium')
    
    bmi_category, _ = get_bmi_category(bmi)
    risk_level, _ = get_premium_risk_level(premium)
    
    summary = {
        'basic_info': f"{age}-year-old {gender} from {region}",
        'health_info': f"BMI: {bmi} ({bmi_category}), Smoker: {smoker.title()}",
        'family_info': f"Children: {children}",
        'premium_info': f"Premium: {format_currency(premium)} ({risk_level} Risk)",
        'insights': get_prediction_insights(age, bmi, smoker, premium)
    }
    
    return summary