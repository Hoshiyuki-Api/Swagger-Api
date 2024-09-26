import os
from flask import Flask, render_template
from flask_restx import Api
# Index
from routes.index import index_app
# Login/Register
from routes.dash_login import dash_app
from routes.auth import auth_bp
from routes.dash_check import check_bp
from routes.dash_regis import regis_app
from routes.dashboard import dashboard_bp
# Routes Downloader
from routes.downloader import tiktok_bp, igdl_bp, twitter_bp, tiktokdlrek as tiktok_ns, instagramdlrek as igdl_ns, twitterdlrek as twitter_ns
from routes.downloader import facebook_bp, mediafire_bp, pinterestvid_bp, laheludl_bp, ytdl_bp, facebookdlrek as fbdl_ns, mediafiredlrek as mdf_ns, pinterestviddlrek as pinvid_ns, laheludlrek as lahelu_ns,  ytdlrek as ytdl_ns
# Routes Tools
from routes.tools import igstalk_bp, remove_bp, cuaca_bp, stalkigrek as stalkig_ns, removebgrek as removebg_ns, cuacagrek as cuaca_ns
# Routes api
from routes.useragent import useragent_bp, api as useragent_ns
# Routes Checker
from routes.dash_check import check_bp, api as check_ns
# Routes AI
from routes.ai import blackbox_bp, deepai_bp, simi_bp, osmage_bp, blackboxrek as blackbox_ns, deepairek as deepai_ns, simirek as simi_ns, osmagerek as osmage_ns
from routes.ai import textti_bp, animediff_bp, bingimg_bp, imgtotext_bp, texttirek as textti_ns, animediff as animediff_ns, bingimg as bingimg_ns, imgtotext as imgtotext_ns

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Index
app.register_blueprint(index_app)
# 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
# Login, Register, Dash
app.register_blueprint(regis_app)
app.register_blueprint(dash_app)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(dashboard_bp)
# Register Blueprints
app.register_blueprint(useragent_bp, url_prefix='/api')
app.register_blueprint(check_bp, url_prefix='/api')
# Register Downloader
app.register_blueprint(tiktok_bp, url_prefix='/api')
app.register_blueprint(igdl_bp, url_prefix='/api')
app.register_blueprint(twitter_bp, url_prefix='/api')
app.register_blueprint(facebook_bp, url_prefix='/api/fbdl')
app.register_blueprint(mediafire_bp, url_path='/api/mediafire')
app.register_blueprint(pinterestvid_bp, url_path='/api/pinvid')
app.register_blueprint(laheludl_bp, url_prefix='/api/laheludl')
app.register_blueprint(ytdl_bp, url_prefix='/api/ytdl')
# Register tools
app.register_blueprint(igstalk_bp, url_prefix='/api/stalkig')
app.register_blueprint(remove_bp, url_prefix='/api/removebg')
app.register_blueprint(cuaca_bp, url_prefix='/api/cuaca')
# Register Ai
app.register_blueprint(blackbox_bp, url_prefix='/api/blackbox')
app.register_blueprint(deepai_bp, url_prefix='/api/deepai')
app.register_blueprint(simi_bp, url_prefix='/api/simi')
app.register_blueprint(osmage_bp, url_prefix='/api/osmage')
app.register_blueprint(textti_bp, url_prefix='/api/texttoimg')
app.register_blueprint(animediff_bp, url_prefix='/api/animediff')
app.register_blueprint(bingimg_bp, url_prefix='/api/bingimg')
app.register_blueprint(imgtotext_bp, url_prefix='/api/imgtotext')

# Initialize Flask-RESTX
api = Api(app, version='1.0.21', title='Hoshiyuki-API',
          description='A Simple Documentation API Created Using Flask-RestX\nThx For Xenzi-XN1 & YukiSmall',
          doc='/playground')

# Add namespaces
api.add_namespace(useragent_ns, path='/user-agent')
api.add_namespace(check_ns, path='/check/apikey')
# NameSpace Downloader
api.add_namespace(tiktok_ns, path='/api/tiktok')  # Namespace untuk TikTok
api.add_namespace(igdl_ns, path='/api/igdl')      # Namespace untuk Instagram
api.add_namespace(twitter_ns, path='/api/twdl')   # Namespace untuk Twitter
api.add_namespace(fbdl_ns, path='/api/fbdl')      # NameSpace Untuk Facebook
api.add_namespace(mdf_ns, path='/api/mediafire')  # NameSpace Untuk Mediafire
api.add_namespace(pinvid_ns, path='/api/pinvid')  # NameSpace Untuk Pinterest Video
api.add_namespace(lahelu_ns, path='/api/lahelu')  # NameSpace Untuk Lahelu
api.add_namespace(ytdl_ns, path='/api/ytdl')
# NameSpace Tools
api.add_namespace(stalkig_ns, path='/api/stalkig')
api.add_namespace(removebg_ns, path='/api/removebg')
api.add_namespace(cuaca_ns, path='/api/cuaca')
# NameSpace AI
api.add_namespace(blackbox_ns, path='/api/blackbox')
api.add_namespace(deepai_ns, path='/api/deepai')
api.add_namespace(simi_ns, path='/api/simi')
api.add_namespace(osmage_ns, path='/api/osmage')
api.add_namespace(textti_ns, path='/api/texttoimg')
api.add_namespace(animediff_ns, path='/api/animediff')
api.add_namespace(bingimg_ns, path='/api/bingimg')
api.add_namespace(imgtotext_ns, path='/api/imgtotext')

if __name__ == '__main__':
    app.run(debug=True)
