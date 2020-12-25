import os
import flask
from riotwatcher import LolWatcher, ApiError
import flask_sqlalchemy
import psycopg2
import datetime
from os.path import join, dirname
from dotenv import load_dotenv
import enum
from timer import daily, hourly
import time

dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)

app = flask.Flask(__name__)
riot = os.environ["RIOT"]

lolwatcher = LolWatcher(riot)
my_region="na1"
users = ["MarTea", "StinGod", "Bassel", "Trúst", "Big ItzWeird", "K3v1nRul3s", "Kareem100", "AminRhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "Shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin Vi", "KerØ"]
#users = ["MarTea"]
length = len(users)
nameList, levelList, tierList, rankList, lpList, winsList, loseList = [], [], [], [], [], [], []
def rankedUpdate():
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

class Ranks(enum.Enum):
    Iron = 0
    Bronze = 1
    Silver = 2
    Gold = 3
    Platinum = 4
    Diamond = 5
    Master = 6
    Grandmaster = 7
    Challenger = 8
#for rank in (Ranks):
#    print(rank)
testRank = Ranks.Platinum
#print("the enum associated with " + testRank.name + " is " + str(testRank.value))

def dbCon():
    conn = psycopg2.connect(
        host="localhost",
        database="leaderboard",
        user="postgres",
        password="password")
    cur = conn.cursor()
    return conn, cur

def timeTest():
    conn, cur = dbCon()
    date = datetime.datetime.now()
    hour = int(date.strftime("%H"))
    date = date.strftime("%x")
    oldDateFetch = "SELECT date FROM timetracker ORDER BY id DESC LIMIT 1;"
    cur.execute(oldDateFetch)
    oldDate = cur.fetchone()
    oldHourFetch = "SELECT hour FROM timetracker ORDER BY id DESC LIMIT 1;"
    cur.execute(oldHourFetch)
    oldHour = cur.fetchone()
    try:
        if date != oldDate[0] or hour != oldHour[0]:
            sql = "INSERT INTO timetracker(date, hour) VALUES (%s,%s);"
            cur.execute(sql, (date, hour))
            conn.commit()
    except:
        sql = "INSERT INTO timetracker(date, hour) VALUES (%s,%s);"
        cur.execute(sql, (date, hour))
        conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    timeTest()
    rankedUpdate()
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