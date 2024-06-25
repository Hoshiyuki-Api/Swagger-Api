from flask import Flask
from flask_restx import Api
# Index
from routes.index import index_app
# Routes Downloader
from routes.downloader import tiktok_bp, igdl_bp, twitter_bp, tiktokdlrek as tiktok_ns, instagramdlrek as igdl_ns, twitterdlrek as twitter_ns
from routes.downloader import facebook_bp, mediafire_bp, pinterestvid_bp, laheludl_bp, ytdl_bp, facebookdlrek as fbdl_ns, mediafiredlrek as mdf_ns, pinterestviddlrek as pinvid_ns, laheludlrek as lahelu_ns,  ytdlrek as ytdl_ns
from routes.tools import igstalk_bp, stalkigrek as stalkig_ns
# Routes api
from routes.useragent import useragent_bp, api as useragent_ns
# Routes Tools
from routes.dash_check import check_bp, api as check_ns
# Routes AI
from routes.ai import blackbox_bp, blackboxrek as blackbox_ns

app = Flask(__name__)

# Index
app.register_blueprint(index_app)
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
# Register Tools
app.register_blueprint(blackbox_bp, url_prefix='/api/blackbox')

# Initialize Flask-RESTX
api = Api(app, version='1.0.21', title='Hoshiyuki-API',
          description='A Simple Documentation API Created Using Flask-RestX\nThx For Xenzi-XN1 & YukiSmall',
          doc='/docs')

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
# NameSpace AI
api.add_namespace(blackbox_ns, path='/api/blackbox')

if __name__ == '__main__':
    app.run(debug=True)
