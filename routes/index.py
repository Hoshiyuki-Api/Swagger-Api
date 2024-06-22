from flask import Blueprint, render_template

index_app = Blueprint('index', __name__, url_prefix='/')

@index_app.route('/')
def index():
    # Render the HTML template located in the 'templates' directory
     return render_template('index.html')
