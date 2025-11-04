from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from database.db_manager import create_user, get_user_by_username, verify_password, get_user_by_email
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = get_user_by_username(username)
        
        if user and verify_password(username, password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on user role
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))  # Redirect admin to admin dashboard


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if username or email already exists
        if get_user_by_username(username):
            errors.append('Username already exists.')
        
        if get_user_by_email(email):
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create user
        if create_user(username, email, password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')
