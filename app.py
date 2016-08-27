from app import server
from flask import render_template
from config.app_config import PORT

app = server.app
app.run(host='0.0.0.0', port=PORT, debug=True)


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html')