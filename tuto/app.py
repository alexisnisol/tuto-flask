from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config['BOOSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)