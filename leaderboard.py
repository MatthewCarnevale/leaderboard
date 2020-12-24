import os
import flask
from riotwatcher import LolWatcher, ApiError
import flask_sqlalchemy
import psycopg2
import datetime
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)

app = flask.Flask(__name__)
riot = os.environ["RIOT"]

lolwatcher = LolWatcher(riot)
my_region="na1"
#account specific data
#full user list, currently limited by api call amount
#users = ["MarTea", "StinGod", "Bassel", "Trúst", "Big ItzWeird", "K3v1nRul3s", "Kareem100", "AminRhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "Shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin Vi", "KerØ"]
users = ["MarTea", "StinGod", "Bassel", "Trúst"]
length = len(users)
nameList, levelList, tierList, rankList, lpList, winsList, loseList = [], [], [], [], [], [], []
for user in users:
    queueID = 0
    user = lolwatcher.summoner.by_name(my_region, user)
    ranked_stats = lolwatcher.league.by_summoner(my_region, user['id'])
    queue = ranked_stats[queueID].get("queueType")
    if queue == "RANKED_SOLO_5x5":
        queueID = 0
    else:
        queueID = 1
    nameList.append(user.get("name"))
    levelList.append(user.get("summonerLevel"))
    tierList.append(ranked_stats[queueID].get("tier").lower().capitalize())
    rankList.append(ranked_stats[queueID].get("rank"))
    lpList.append(ranked_stats[queueID].get("leaguePoints"))
    winsList.append(ranked_stats[queueID].get("wins"))
    loseList.append(ranked_stats[queueID].get("losses"))
    #print(queueID)
    #print(name)
    #print(level)
    #print(tier)
    #print(rank)
    #print(lp)
    #print(wins)
    #print(lose)

@app.route("/")
def index():
    return flask.render_template(
        "index.html",
        nameList=nameList,
        levelList=levelList,
        tierList=tierList,
        rankList=rankList,
        lpList=lpList,
        winsList=winsList,
        loseList=loseList,
        length=length
    )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))





"""    
me = lolwatcher.summoner.by_name(my_region, "Stin God")
#ranked data, seperated into flex and solo for the account
my_ranked_stats = lolwatcher.league.by_summoner(my_region, me['id'])
print(my_ranked_stats)
name = me.get("name")
level = me.get("summonerLevel")
tier = my_ranked_stats[0].get("tier") 
rank = my_ranked_stats[0].get("rank")
lp = my_ranked_stats[0].get("leaguePoints")
wins = my_ranked_stats[0].get("wins")
lose = my_ranked_stats[0].get("losses")
#test print statements to make sure things work
print(name)
print(level)
print(tier)
print(rank)
print(lp)
print(wins)
print(lose)
"""