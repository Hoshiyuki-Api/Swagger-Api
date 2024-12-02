from flask import Blueprint, render_template

docs_app = Blueprint('docs', __name__, url_prefix='/')

@docs_app.route('/docs')
def docs():
    # Render the HTML template located in the 'templates' directory
     return render_template('api-docs.html')
