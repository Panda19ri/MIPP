from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database.db_manager import get_all_users, get_all_predictions, get_statistics
from functools import wraps

# admin_bp = Blueprint('admin', __name__)
admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get application statistics
    stats = get_statistics()
    
    # Get recent predictions (last 10)
    recent_predictions = get_all_predictions()[:10]
    
    return render_template('admin/admin_dashboard.html', 
                         stats=stats, 
                         recent_predictions=recent_predictions)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users page"""
    users = get_all_users()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/predictions')
@login_required
@admin_required
def view_predictions():
    """View all predictions"""
    predictions = get_all_predictions()
    
    # Debug: Print predictions count
    print(f"Admin viewing {len(predictions)} total predictions")
    
    return render_template('admin/predictions.html', predictions=predictions)

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard - Simple working version"""
    return render_template('admin/analytics.html')

@admin_bp.route('/api/analytics-data')
@login_required
@admin_required
def api_analytics_data():
    """Simple API endpoint for real analytics data"""
    try:
        from datetime import datetime
        from collections import defaultdict
        
        # Get real data from application
        predictions = get_all_predictions()
        users = get_all_users()
        
        # Initialize response structure
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'basic_stats': {
                'total_revenue': 0,
                'total_users': 0,
                'total_predictions': 0,
                'average_premium': 0
            },
            'premium_ranges': {},
            'age_distribution': {},
            'regional_data': {},
            'top_users': [],
            'insights': []
        }
        
        # Filter real users (exclude admins)
        real_users = [u for u in users if not u.get('is_admin', False)]
        response['basic_stats']['total_users'] = len(real_users)
        
        if not predictions:
            return jsonify(response)
        
        # Calculate basic stats from real predictions
        response['basic_stats']['total_predictions'] = len(predictions)
        
        premiums = []
        for p in predictions:
            try:
                premium = float(p['predicted_premium'])
                premiums.append(premium)
            except (ValueError, KeyError, TypeError):
                continue
        
        if premiums:
            response['basic_stats']['total_revenue'] = sum(premiums)
            response['basic_stats']['average_premium'] = sum(premiums) / len(premiums)
        
        # Premium ranges from real data
        premium_ranges = defaultdict(int)
        for premium in premiums:
            if premium < 5000:
                premium_ranges['Under $5K'] += 1
            elif premium < 10000:
                premium_ranges['$5K - $10K'] += 1
            elif premium < 15000:
                premium_ranges['$10K - $15K'] += 1
            elif premium < 20000:
                premium_ranges['$15K - $20K'] += 1
            else:
                premium_ranges['Over $20K'] += 1
        
        response['premium_ranges'] = dict(premium_ranges)
        
        # Age distribution from real data
        age_distribution = defaultdict(int)
        for p in predictions:
            try:
                age = int(p['age'])
                if age < 25:
                    age_distribution['18-24'] += 1
                elif age < 35:
                    age_distribution['25-34'] += 1
                elif age < 45:
                    age_distribution['35-44'] += 1
                elif age < 55:
                    age_distribution['45-54'] += 1
                else:
                    age_distribution['55+'] += 1
            except (ValueError, KeyError, TypeError):
                continue
        
        response['age_distribution'] = dict(age_distribution)
        
        # Top users from real data
        user_stats = defaultdict(lambda: {'count': 0, 'total': 0, 'username': 'Unknown'})
        
        for p in predictions:
            try:
                user_id = p.get('user_id', 0)
                username = p.get('username', f'User_{user_id}')
                premium = float(p['predicted_premium'])
                
                user_stats[user_id]['count'] += 1
                user_stats[user_id]['total'] += premium
                user_stats[user_id]['username'] = username
            except (ValueError, KeyError, TypeError):
                continue
        
        # Convert to list and sort
        top_users = []
        for user_id, stats in user_stats.items():
            if stats['count'] > 0:
                avg_premium = stats['total'] / stats['count']
                top_users.append({
                    'username': stats['username'],
                    'prediction_count': stats['count'],
                    'avg_premium': avg_premium,
                    'total_premium': stats['total']
                })
        
        # Sort by prediction count and take top 5
        top_users.sort(key=lambda x: x['prediction_count'], reverse=True)
        response['top_users'] = top_users[:5]
        
        # Generate simple insights
        insights = []
        
        if response['basic_stats']['total_predictions'] > 0:
            avg_premium = response['basic_stats']['average_premium']
            total_predictions = response['basic_stats']['total_predictions']
            
            # Premium insight
            if avg_premium > 12000:
                insights.append({
                    'type': 'warning',
                    'icon': 'fas fa-exclamation-triangle',
                    'title': 'High Average Premium',
                    'description': f'Average premium is ${avg_premium:,.0f}, indicating higher risk profiles'
                })
            elif avg_premium > 8000:
                insights.append({
                    'type': 'info',
                    'icon': 'fas fa-info-circle',
                    'title': 'Normal Premium Range',
                    'description': f'Average premium is ${avg_premium:,.0f}, within expected range'
                })
            else:
                insights.append({
                    'type': 'success',
                    'icon': 'fas fa-check-circle',
                    'title': 'Low Risk Portfolio',
                    'description': f'Average premium is ${avg_premium:,.0f}, showing lower risk users'
                })
            
            # Activity insight
            if total_predictions < 10:
                insights.append({
                    'type': 'info',
                    'icon': 'fas fa-rocket',
                    'title': 'Growing User Base',
                    'description': f'${total_predictions} predictions made. System is gaining traction!'
                })
            else:
                insights.append({
                    'type': 'success',
                    'icon': 'fas fa-chart-line',
                    'title': 'Active Platform',
                    'description': f'{total_predictions} total predictions show strong user engagement'
                })
            
            # User engagement insight
            active_users = len(top_users)
            if active_users > 0:
                insights.append({
                    'type': 'success',
                    'icon': 'fas fa-users',
                    'title': 'User Engagement',
                    'description': f'{active_users} users actively using the prediction system'
                })
        
        response['insights'] = insights
        return jsonify(response)
        
    except Exception as e:
        print(f"Analytics API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to load analytics data',
            'basic_stats': {
                'total_revenue': 0,
                'total_users': 0,
                'total_predictions': 0,
                'average_premium': 0
            },
            'premium_ranges': {},
            'age_distribution': {},
            'regional_data': {},
            'top_users': [],
            'insights': []
        })
        # Get real data from our application
        predictions = get_all_predictions()
        users = get_all_users()
        stats = get_statistics()
        
        # Calculate real analytics
        analytics = calculate_real_insurance_analytics(predictions, users, stats)
        
        # Generate time-series data from real predictions
        premium_trends = generate_real_premium_trends(predictions)
        
        # Calculate risk distribution from real data
        risk_distribution = calculate_real_risk_distribution(predictions)
        
        # Get top users by prediction count from real data
        top_users = get_real_top_users(predictions, users)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'basic_stats': {
                'total_revenue': analytics['total_revenue'],
                'total_users': analytics['total_users'],
                'total_predictions': analytics['total_predictions'],
                'average_premium': analytics['average_premium'],
                'active_users_count': analytics['active_users_count'],
                'high_risk_count': analytics['high_risk_count'],
                'smoking_rate': analytics['smoking_rate'],
                'avg_age': analytics['avg_age'],
                'avg_bmi': analytics['avg_bmi'],
                'recent_activity': analytics['recent_activity']
            },
            'premium_trends': premium_trends,
            'risk_distribution': risk_distribution,
            'regional_data': analytics['regional_breakdown'],
            'age_distribution': analytics['age_distribution'],
            'premium_ranges': analytics['premium_ranges'],
            'top_users': top_users,
            'insights': generate_real_insights(analytics, predictions)
        })
        
    except Exception as e:
        print(f"Analytics API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load analytics data',
            'basic_stats': {
                'total_revenue': 0,
                'total_users': 0,
                'total_predictions': 0,
                'average_premium': 0
            }
        }), 500

def generate_real_premium_trends(predictions):
    """Generate premium trends from real prediction data"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    if not predictions:
        return {'labels': [], 'data': []}
    
    # Group predictions by date
    daily_data = defaultdict(list)
    
    for p in predictions:
        try:
            pred_date = datetime.fromisoformat(p['created_at'].replace('Z', '+00:00'))
            date_str = pred_date.strftime('%Y-%m-%d')
            daily_data[date_str].append(p['predicted_premium'])
        except:
            continue
    
    # Get last 7 days with data
    sorted_dates = sorted(daily_data.keys())[-7:]  # Last 7 days with data
    
    labels = []
    data = []
    
    for date_str in sorted_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        labels.append(date_obj.strftime('%m/%d'))
        avg_premium = sum(daily_data[date_str]) / len(daily_data[date_str])
        data.append(round(avg_premium, 2))
    
    # If we have less than 7 days, fill with zeros
    while len(labels) < 7:
        labels.insert(0, 'No Data')
        data.insert(0, 0)
    
    return {'labels': labels, 'data': data}

def calculate_real_risk_distribution(predictions):
    """Calculate risk distribution from real predictions"""
    if not predictions:
        return {'low': 0, 'medium': 0, 'high': 0}
    
    low = medium = high = 0
    
    for p in predictions:
        premium = p['predicted_premium']
        if premium < 8000:
            low += 1
        elif premium < 16000:
            medium += 1
        else:
            high += 1
    
    return {'low': low, 'medium': medium, 'high': high}

def get_real_top_users(predictions, users):
    """Get top users by prediction count from real data"""
    from collections import defaultdict
    
    if not predictions:
        return []
    
    # Count predictions per user
    user_stats = defaultdict(lambda: {'count': 0, 'total_premium': 0, 'username': 'Unknown'})
    
    for p in predictions:
        user_id = p.get('user_id', 0)
        username = p.get('username', f'User_{user_id}')
        
        user_stats[user_id]['count'] += 1
        user_stats[user_id]['total_premium'] += p['predicted_premium']
        user_stats[user_id]['username'] = username
    
    # Calculate averages and sort by prediction count
    top_users = []
    for user_id, stats in user_stats.items():
        if stats['count'] > 0:
            avg_premium = stats['total_premium'] / stats['count']
            top_users.append({
                'username': stats['username'],
                'prediction_count': stats['count'],
                'avg_premium': round(avg_premium, 2),
                'total_premium': round(stats['total_premium'], 2)
            })
    
    # Sort by prediction count and return top 5
    return sorted(top_users, key=lambda x: x['prediction_count'], reverse=True)[:5]

def generate_real_insights(analytics, predictions):
    """Generate insights from real application data"""
    insights = []
    
    # Premium trend insight
    avg_premium = analytics.get('average_premium', 0)
    if avg_premium > 12000:
        insights.append({
            'type': 'warning',
            'icon': 'fas fa-exclamation-triangle',
            'title': 'High Average Premium',
            'description': f'Average premium is ${avg_premium:,.2f}, indicating higher risk profiles'
        })
    elif avg_premium > 8000:
        insights.append({
            'type': 'info',
            'icon': 'fas fa-info-circle',
            'title': 'Moderate Premium Range',
            'description': f'Average premium is ${avg_premium:,.2f}, within normal range'
        })
    else:
        insights.append({
            'type': 'success',
            'icon': 'fas fa-check-circle',
            'title': 'Low Average Premium',
            'description': f'Average premium is ${avg_premium:,.2f}, indicating lower risk profiles'
        })
    
    # User engagement insight
    total_users = analytics.get('total_users', 0)
    active_users = analytics.get('active_users_count', 0)
    if total_users > 0:
        engagement_rate = (active_users / total_users) * 100
        if engagement_rate > 70:
            insights.append({
                'type': 'success',
                'icon': 'fas fa-users',
                'title': 'High User Engagement',
                'description': f'{engagement_rate:.1f}% of users are active in the last 30 days'
            })
        else:
            insights.append({
                'type': 'warning',
                'icon': 'fas fa-users',
                'title': 'Low User Engagement',
                'description': f'Only {engagement_rate:.1f}% of users are active in the last 30 days'
            })
    
    # Smoking rate insight
    smoking_rate = analytics.get('smoking_rate', 0)
    if smoking_rate > 30:
        insights.append({
            'type': 'danger',
            'icon': 'fas fa-smoking',
            'title': 'High Smoking Rate',
            'description': f'{smoking_rate:.1f}% of users are smokers, affecting premium costs'
        })
    elif smoking_rate > 15:
        insights.append({
            'type': 'warning',
            'icon': 'fas fa-smoking',
            'title': 'Moderate Smoking Rate',
            'description': f'{smoking_rate:.1f}% of users are smokers'
        })
    else:
        insights.append({
            'type': 'success',
            'icon': 'fas fa-heart',
            'title': 'Low Smoking Rate',
            'description': f'Only {smoking_rate:.1f}% of users are smokers, promoting healthier profiles'
        })
    
    # Age demographic insight
    avg_age = analytics.get('avg_age', 0)
    if avg_age > 45:
        insights.append({
            'type': 'info',
            'icon': 'fas fa-calendar-alt',
            'title': 'Mature User Base',
            'description': f'Average user age is {avg_age:.1f} years, indicating mature demographic'
        })
    elif avg_age < 30:
        insights.append({
            'type': 'success',
            'icon': 'fas fa-calendar-alt',
            'title': 'Young User Base',
            'description': f'Average user age is {avg_age:.1f} years, indicating younger demographic'
        })
    else:
        insights.append({
            'type': 'info',
            'icon': 'fas fa-calendar-alt',
            'title': 'Balanced Age Demographics',
            'description': f'Average user age is {avg_age:.1f} years, showing balanced demographics'
        })
    
    return insights[:4]  # Return top 4 insights level categorization
    risk_levels = {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
    
    for premium in premiums:
        if premium < 5000:
            risk_levels['low'] += 1
        elif premium < 10000:
            risk_levels['medium'] += 1
        elif premium < 20000:
            risk_levels['high'] += 1
        else:
            risk_levels['very_high'] += 1
    
    # Gender analysis
    gender_stats = defaultdict(int)
    gender_premiums = defaultdict(list)
    
    for p in predictions:
        gender_stats[p['gender']] += 1
        gender_premiums[p['gender']].append(p['predicted_premium'])
    
    # Calculate trends (simulated)
    premium_trend = 12.5  # Percentage increase
    user_trend = 8.3     # Percentage increase
    prediction_trend = 0  # No change
    risk_trend = -2.1    # Decrease in average risk
    
    return {
        'basic_stats': {
            'total_predictions': total_predictions,
            'total_users': total_users,
            'recent_predictions': len(recent_predictions),
            'avg_premium': avg_premium,
            'max_premium': max_premium,
            'min_premium': min_premium,
            'avg_age': avg_age,
            'avg_bmi': avg_bmi,
            'smoking_rate': smoking_rate
        },
        'trends': {
            'premium_trend': premium_trend,
            'user_trend': user_trend,
            'prediction_trend': prediction_trend,
            'risk_trend': risk_trend
        },
        'regional': {
            'counts': dict(regions),
            'avg_premiums': regional_avg_premiums
        },
        'risk_levels': risk_levels,
        'gender_stats': {
            'counts': dict(gender_stats),
            'avg_premiums': {k: sum(v)/len(v) if v else 0 for k, v in gender_premiums.items()}
        },
        'time_analysis': {
            'daily': len(recent_predictions),
            'weekly': len(weekly_predictions),
            'monthly': len(monthly_predictions)
        }
    }

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard statistics"""
    stats = get_statistics()
    return jsonify(stats)

@admin_bp.route('/api/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    import sqlite3
    
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    try:
        conn = sqlite3.connect('database.db')
        
        # Check if user exists and is not admin
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user[0]:  # is_admin
            return jsonify({'error': 'Cannot delete admin users'}), 400
        
        # Delete user (cascade will handle predictions)
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete user'}), 500

@admin_bp.route('/api/user_activity/<int:user_id>')
@login_required
@admin_required
def user_activity(user_id):
    """Get user activity data"""
    import sqlite3
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    
    # Get user predictions
    predictions = conn.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 50
    ''', (user_id,)).fetchall()
    
    conn.close()
    
    activity_data = []
    for pred in predictions:
        activity_data.append({
            'date': pred['created_at'],
            'premium': pred['predicted_premium'],
            'age': pred['age'],
            'bmi': pred['bmi'],
            'smoker': pred['smoker'],
            'region': pred['region']
        })
    
    return jsonify(activity_data)


# new data added

@admin_bp.route('/analytics-dashboard')
@login_required
@admin_required
def analytics_dashboard():
    """Show real analytics charts from database"""
    import sqlite3, json
    import pandas as pd

    try:
        # Connect to your database
        conn = sqlite3.connect('database.db')
        df = pd.read_sql_query("SELECT * FROM predictions", conn)
        conn.close()

        if df.empty:
            return render_template('admin/analytics.html', message="No prediction data found.")

        # Calculate analytics
        region_counts = df['region'].value_counts().to_dict()
        smoker_counts = df['smoker'].value_counts().to_dict()
        avg_premium = df['predicted_premium'].mean()
        age_groups = df['age'].value_counts(bins=[0, 25, 35, 45, 55, 100]).to_dict()

        # Pass to frontend as JSON
        return render_template(
            'admin/analytics.html',
            region_data=json.dumps(region_counts),
            smoker_data=json.dumps(smoker_counts),
            avg_premium=round(avg_premium, 2),
            age_data=json.dumps(age_groups)
        )
    except Exception as e:
        print("Analytics error:", e)
        return render_template('admin/analytics.html', message="Error loading analytics.")
    
# another newly added one

@admin_bp.route('/api/analytics-data')
def api_analytics_data_route():  # <-- new unique name
    # @admin_bp.route('/api/analytics-data')
# def api_analytics_data():
    # --- SAMPLE STATIC DATA (for testing only) ---
    data = {
        "basic_stats": {
            "total_users": 120,
            "total_predictions": 340,
            "total_revenue": 78500.50,
            "average_premium": 2307.35
        },
        "premium_ranges": {
            "₹0 - ₹1000": 45,
            "₹1001 - ₹3000": 120,
            "₹3001 - ₹6000": 95,
            "₹6001 - ₹10000": 60,
            "₹10000+": 20
        },
        "age_distribution": {
            "18-25": 40,
            "26-35": 90,
            "36-45": 75,
            "46-55": 55,
            "56+": 30
        },
        "top_users": [
            {"username": "Pandarikaksha", "prediction_count": 45, "avg_premium": 2900.75},
            {"username": "Manideep", "prediction_count": 32, "avg_premium": 3100.20},
            {"username": "Shivasai", "prediction_count": 29, "avg_premium": 2500.10},
            {"username": "Abhi", "prediction_count": 25, "avg_premium": 2800.60}
        ],
        "insights": [
            {
                "type": "success",
                "icon": "bi bi-graph-up-arrow",
                "title": "Premium Growth",
                "description": "Users between 26–35 years have the highest average premium rate."
            },
            {
                "type": "info",
                "icon": "bi bi-person-check",
                "title": "Top Predictor",
                "description": "Pandarikaksha has made the most predictions this week!"
            },
            {
                "type": "warning",
                "icon": "bi bi-currency-rupee",
                "title": "Revenue Dip",
                "description": "Revenue from users above 50 years decreased slightly last month."
            }
        ]
    }
    return jsonify(data)
