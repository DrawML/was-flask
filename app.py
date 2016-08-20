from app import server
from flask import render_template

app = server.app
app.run(host='0.0.0.0', port=5000, debug=True)


@app.errorhandler(404)
def not_found(error):
	return render_template('404.html')