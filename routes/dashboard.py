from flask import Blueprint, render_template, redirect, url_for, session

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard():
    if session.get('logged_in'):
        return render_template('dashboard.html')
    else:
        return redirect(url_for('dash.index'))