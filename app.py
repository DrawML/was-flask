#!env/bin/python3.5
from app import server
from config.app_config import PORT, DEBUG

app = server.app
app.run(host='0.0.0.0', threaded=True, processes=1, use_reloader=False, debug=DEBUG, port=PORT)
