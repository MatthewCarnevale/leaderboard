import os
import flask
import flask_sqlalchemy
from data import rankedPull, deltaDate, summonerInfo, lifetime, users, yesterdaysDelta, isQueue

app = flask.Flask(__name__)
@app.route("/")
def index():
    playerDict = rankedPull()
    date = deltaDate()
    yesterday = yesterdaysDelta()
    winnerDict, loserDict = isQueue()
    print("page should be loaded")
    return flask.render_template(
        "index.html",
        playerDict = playerDict,
        date = date,
        yesterday = yesterday,
        winnerDict = winnerDict,
        loserDict = loserDict
    )

@app.route("/<SUMMONER>")
def summoner_index(SUMMONER):
    recentGameStats = summonerInfo(SUMMONER)
    accolades = lifetime(SUMMONER)
    accolades = accolades[0]
    print(accolades)
    if SUMMONER not in users:
        return flask.render_template("notfound.html")
    else:
        return flask.render_template(
            "summoner.html",
            recentGameStats = recentGameStats,
            name = SUMMONER,
            accolades = accolades
        )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))