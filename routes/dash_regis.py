from flask import Blueprint, render_template

regis_app = Blueprint('regis', __name__, url_prefix='/register')

@regis_app.route('/')
def index():
    # Render the HTML template located in the 'templates' directory
     return render_template('index_register.html') 