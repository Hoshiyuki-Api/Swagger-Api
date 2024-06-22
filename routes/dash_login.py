from flask import Blueprint, render_template

dash_app = Blueprint('dash', __name__, url_prefix='/login')

@dash_app.route('/')
def index():
    # Render the HTML template located in the 'templates' directory
     return render_template('index_login.html')
