from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_script import Manager
from flask_restful import Api
from flask_bootstrap import Bootstrap
from flask_compress import Compress
import logging
import logging.handlers

# add mitigration
from flask_migrate import Migrate, MigrateCommand

# Create the app and configuration
# Read the configuration file
app = Flask(__name__)
app.config.from_object('application.default_settings')
if 'PRODUCTION_SETTINGS' in environ:
    # if set, production settings must be loaded for security reason
    app.config.from_envvar('PRODUCTION_SETTINGS', silent=False)

# Log only in production mode.
if not app.debug:
    app_handler = logging.handlers.WatchedFileHandler('/var/log/api/app.log')
    app_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(process)d] [%(levelname)s] %(message)s')
    app_handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(app_handler)
app.logger.info('using database %s', app.config['SQLALCHEMY_DATABASE_URI'])

# Connect to database with sqlalchemy.
db = SQLAlchemy(app)

# Create API
api = Api(app)

# Create cli manager
manager = Manager(app)

bootstrap = Bootstrap(app)


# add mitigration
mitigrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)  # install flask-migrate-2.0.0

Compress(app)


# 404 page not found "route"
@app.errorhandler(404)
def not_found(error):
    title = "404 Page not found"
    return render_template('404.html', title=title), 404


# 500 server error "route"
@app.errorhandler(500)
def server_error(error):
    title = "500 Server Error"
    db.session.rollback()
    return render_template('500.html', title=title), 500


# restful api
from .api_1_0 import api_bluePrint as api_1_0_blueprint

app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1_0')

from .route import *  # pylint: disable=wildcard-import,wrong-import-position
from .admin import *  # pylint: disable=wildcard-import,wrong-import-position

