# Statement for enabling the development environment
DEBUG = True
PORT = 5000

# Define the application directory
import os
from datetime import timedelta
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
DB_PROTO    = 'mysql://'
DB_USER     = 'root'
DB_PWD      = '0000'
DB_SERVER   = 'localhost'
DB_NAME     = 'drawml'
DB_URI = DB_PROTO + DB_USER + ':' + DB_PWD + '@' + DB_SERVER + '/' + DB_NAME
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"
SESSION_COOKIE_NAME = 'drawml_flask_session'
PERMANENT_SESSION_LIFETIME = timedelta(31)

# file upload
UPLOAD_FOLDER = '/data'

# Setup configure for distribution module
MASTER_ADDR = 'tcp://*.*.*.*:16000'
RESULT_ROUTER_PROTOCOL = 'tcp'
RESULT_ROUTER_ADDR = '*.*.*.*'
RESULT_ROUTER_PORT = '15000'

# Cloud distribute file system configuration
CLOUDDFS_ADDR = '*.*.*.*'
CLOUDDFS_PORT = 10000
