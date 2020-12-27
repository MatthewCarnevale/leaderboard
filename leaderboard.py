import os
import flask
import flask_sqlalchemy
from data import dbPull

app = flask.Flask(__name__)

@app.route("/")
def index():
    playerDict = dbPull()
    print("page should be loaded")
    return flask.render_template(
        "index.html",
        playerDict = playerDict
    )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))