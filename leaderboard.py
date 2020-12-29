import os
import flask
import flask_sqlalchemy
from data import rankedPull, deltaDate, statsPull, summonerInfo, test

app = flask.Flask(__name__)
@app.route("/")
def index():
    playerDict = rankedPull()
    date = deltaDate()
    stats = statsPull()
    print("page should be loaded")
    return flask.render_template(
        "index.html",
        playerDict = playerDict,
        date = date,
    )

@app.route("/<SUMMONER>")
def summoner_index(SUMMONER):
    te = test()
    #print(stats)
    #stat = stats[0]
    #print(stat)
    return flask.render_template(
        "summoner.html",
        te = te
    )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))