import sqlite3
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from config import Config
from datetime import datetime

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with schema"""
    conn = get_db_connection()
    
    # Read and execute schema
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()

def create_admin_user():
    """Create default admin user if not exists"""
    conn = get_db_connection()
    
    # Check if admin user exists
    admin = conn.execute(
        'SELECT id FROM users WHERE username = ?',
        (Config.DEFAULT_ADMIN_USERNAME,)
    ).fetchone()
    
    if not admin:
        password_hash = generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD)
        conn.execute(
            'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            (Config.DEFAULT_ADMIN_USERNAME, Config.DEFAULT_ADMIN_EMAIL, password_hash, True)
        )
        conn.commit()
        print(f"Admin user created: {Config.DEFAULT_ADMIN_USERNAME}")
    
    conn.close()

def create_user(username, email, password):
    """Create a new user"""
    conn = get_db_connection()
    try:
        password_hash = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['email'], user['is_admin'])
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['email'], user['is_admin'])
    return None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ?',
        (email,)
    ).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['email'], user['is_admin'])
    return None

def verify_password(username, password):
    """Verify user password"""
    from werkzeug.security import check_password_hash
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT password_hash FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return True
    return False

def save_prediction(user_id, age, gender, bmi, children, smoker, region, premium):
    """Save prediction to database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO predictions 
               (user_id, age, gender, bmi, children, smoker, region, predicted_premium)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, age, gender, bmi, children, smoker, region, premium)
        )
        conn.commit()
        prediction_id = cursor.lastrowid
        print(f"Saved prediction {prediction_id} for user {user_id}: ${premium:.2f}")
        return prediction_id
    except Exception as e:
        print(f"Error saving prediction: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_user_predictions(user_id, limit=50):
    """Get user's prediction history"""
    conn = get_db_connection()
    try:
        predictions = conn.execute(
            '''SELECT * FROM predictions 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?''',
            (user_id, limit)
        ).fetchall()
        
        # Convert to list of dicts for easier handling
        result = []
        for pred in predictions:
            result.append({
                'id': pred['id'],
                'user_id': pred['user_id'],
                'age': pred['age'],
                'gender': pred['gender'],
                'bmi': pred['bmi'],
                'children': pred['children'],
                'smoker': pred['smoker'],
                'region': pred['region'],
                'predicted_premium': pred['predicted_premium'],
                'created_at': pred['created_at']
            })
        
        print(f"Retrieved {len(result)} predictions for user {user_id}")
        return result
    except Exception as e:
        print(f"Error getting user predictions: {e}")
        return []
    finally:
        conn.close()

def get_all_predictions():
    """Get all predictions (admin only)"""
    conn = get_db_connection()
    try:
        predictions = conn.execute(
            '''SELECT p.*, u.username 
               FROM predictions p
               JOIN users u ON p.user_id = u.id
               ORDER BY p.created_at DESC'''
        ).fetchall()
        
        # Convert to list of dicts
        result = []
        for pred in predictions:
            result.append({
                'id': pred['id'],
                'user_id': pred['user_id'],
                'username': pred['username'],
                'age': pred['age'],
                'gender': pred['gender'],
                'bmi': pred['bmi'],
                'children': pred['children'],
                'smoker': pred['smoker'],
                'region': pred['region'],
                'predicted_premium': pred['predicted_premium'],
                'created_at': pred['created_at']
            })
        
        print(f"Retrieved {len(result)} total predictions for admin")
        return result
    except Exception as e:
        print(f"Error getting all predictions: {e}")
        return []
    finally:
        conn.close()

def get_all_users():
    """Get all users (admin only)"""
    conn = get_db_connection()
    users = conn.execute(
        'SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return users

def get_statistics():
    """Get application statistics"""
    conn = get_db_connection()
    
    # Total users
    total_users = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0]
    
    # Total predictions
    total_predictions = conn.execute('SELECT COUNT(*) FROM predictions').fetchone()[0]
    
    # Average premium
    avg_premium = conn.execute('SELECT AVG(predicted_premium) FROM predictions').fetchone()[0] or 0
    
    # Recent predictions count (last 30 days)
    recent_predictions = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE created_at >= datetime('now', '-30 days')"
    ).fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_predictions': total_predictions,
        'average_premium': round(avg_premium, 2),
        'recent_predictions': recent_predictions
    }