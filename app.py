#!env/bin/python3.5
from app import server

app = server.app
app.run(host='0.0.0.0', threaded=True, processes=1, use_reloader=False)
