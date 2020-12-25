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
from player import Player

dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)

app = flask.Flask(__name__)
riot = os.environ["RIOT"]

lolwatcher = LolWatcher(riot)
my_region="na1"

def dbCon():
    conn = psycopg2.connect(
        host="localhost",
        database="leaderboard",
        user="postgres",
        password="password")
    cur = conn.cursor()
    return conn, cur

#users = ["MarTea", "StinGod", "Bassel", "Trúst", "Big ItzWeird", "K3v1nRul3s", "Kareem100", "AminRhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "Shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin Vi", "KerØ"]
users = ["MarTea", "StinGod"]

def playerCreate():
    playerList = []
    for user in users:
        queueID = 0
        summoner = lolwatcher.summoner.by_name(my_region, user)
        ranked_stats = lolwatcher.league.by_summoner(my_region, summoner['id'])
        queue = ranked_stats[queueID].get("queueType")
        if queue == "RANKED_SOLO_5x5":
            queueID = 0
        else:
            queueID = 1
        player =  Player(summoner.get("name"), summoner.get("summonerLevel"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank"),ranked_stats[queueID].get("leaguePoints"),ranked_stats[queueID].get("wins"), ranked_stats[queueID].get("losses"))
        playerList.append(player)
    length = len(playerList)
    return playerList, length
players, length = playerCreate()

def constructDict(playerList):
    playerDict = {}
    for player in players:
        playerDict[player.name] = [player.level, player.tier, player.rank, player.lp, player.wins, player.losses]
    return playerDict
print(constructDict(players))

def timeTest():
    playerList = playerCreate()
    conn, cur = dbCon()
    date = datetime.datetime.now()
    hour = int(date.strftime("%H"))
    minutes = int(date.strftime("%M"))
    date = date.strftime("%x")
    oldDateFetch = "SELECT date FROM timetracker ORDER BY id DESC LIMIT 1;"
    cur.execute(oldDateFetch)
    oldDate = cur.fetchone()
    oldHourFetch = "SELECT hour FROM timetracker ORDER BY id DESC LIMIT 1;"
    cur.execute(oldHourFetch)
    oldHour = cur.fetchone()
    oldMinuteFetch = "SELECT minutes FROM timetracker ORDER BY id DESC LIMIT 1;"
    cur.execute(oldMinuteFetch)
    oldMinute = cur.fetchone()
    #checks for timeing, updates every 30 minutes or sooner. right now just tracks time accurately, under the if should store all player data into database, add an else to load that data rather than str8 api pull
    try:
        if date != oldDate[0] or hour != oldHour[0] or (oldMinute[0] <= 30 and minutes > 30) :
            sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
            cur.execute(sql, (date, hour, minutes))
            conn.commit()
            playerDict = constructDict(playerList)
            #gonna try and make dictonary like good boy instead of list otp
            #sql = "INSERT INTO playerdata()"
        #TEMP TEMP TEMP TEMP TEMP BELOW TEMP TEMP TEMP TEMP
        playerDict = constructDict(playerList)
    except:
        sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
        cur.execute(sql, (date, hour, minutes))
        conn.commit()
        #TEMP TEMP TEMP TEMP TEMP BELOW TEMP TEMP TEMP TEMP
        playerDict = constructDict(playerList)
    cur.close()
    conn.close()
    return playerDict

@app.route("/")
def index():
    playerDict = timeTest()
    return flask.render_template(
        "index.html",
        playerDict = playerDict
    )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))
