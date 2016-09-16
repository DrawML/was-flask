from app import server
from flask import render_template
from config.app_config import PORT

app = server.app
app.run(host='0.0.0.0', threaded=True, processes=1)
