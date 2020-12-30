import os
import flask
import flask_sqlalchemy
from data import rankedPull, deltaDate, statsPull, summonerInfo

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
    recentGameStats = summonerInfo(SUMMONER)
    #print(recentGameStats)
    #print(stats)
    #stat = stats[0]
    #print(stat)
    return flask.render_template(
        "summoner.html",
        recentGameStats = recentGameStats,
        name = SUMMONER
    )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))