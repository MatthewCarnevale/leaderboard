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
import json

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

users = ["MarTea", "StinGod", "Bassel", "Trúst", "Big ItzWeird", "K3v1nRul3s", "Kareem100", "AminRhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "Shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin Vi", "KerØ"]
#users = ["MarTea", "StinGod"]

def playerCreate():
    playerList = []
    print("hello i am making riot games api calls")
    for user in users:
        queueID = 0
        summoner = lolwatcher.summoner.by_name(my_region, user)
        ranked_stats = lolwatcher.league.by_summoner(my_region, summoner['id'])
        queue = ranked_stats[queueID].get("queueType")
        if queue == "RANKED_SOLO_5x5":
            queueID = 0
        else:
            queueID = 1
        ranks = {}
        ranks[summoner.get("name")] = [ranked_stats[queueID].get("leaguePoints"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank")]
        #print(ranks)
        convertedMMR = rankConversion(ranks)
        player =  Player(summoner.get("name"), summoner.get("summonerLevel"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank"), ranked_stats[queueID].get("leaguePoints"), convertedMMR, ranked_stats[queueID].get("wins"), ranked_stats[queueID].get("losses"))
        #player =  Player(summoner.get("name"), summoner.get("summonerLevel"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank"),ranked_stats[queueID].get("leaguePoints"),ranked_stats[queueID].get("wins"), ranked_stats[queueID].get("losses"))
        playerList.append(player)
    return playerList

def rankConversion(ranks):
    mmr = 0
    for name, rank in ranks.items():
        if rank[1] == "Iron":
           mmr = 0
        elif rank[1] == "Bronze":
            mmr = 1000
        elif rank[1] == "Silver":
            mmr = 2000
        elif rank[1] == "Gold":
            mmr = 3000
        elif rank[1] == "Platinum":
            mmr = 4000
        elif rank[1] == "Diamond":
            mmr = 5000
        elif rank[1] == "Master":
            mmr = 6000
        elif rank[1] == "Grandmaster":
            mmr = 7000
        elif rank[1] == "Challenger":
            mmr = 8000
        else:
            mmr = -1
        if rank[2] == "I":
            mmr = mmr + 400
        elif rank[2] == "II":
            mmr = mmr + 300
        elif rank[2] == "III":
            mmr = mmr + 200
        elif rank[2] == "IV":
            mmr = mmr + 100
        else:
            mmr = 0
        convert = 0
        convert = int(rank[0]) + mmr
    return convert

def constructDict(playerList):
    playerDict = {}
    for player in playerList:
        playerDict[player.name] = [player.level, player.tier, player.rank, player.lp, player.wins, player.losses, player.mmr]
    return playerDict

def timeTest():
    #playerList = playerCreate()
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
    try:
        #needs a smaller miunte window, probably 20~. if a real api key makes things faster i can do even smaller intervals (10 is optimal), if a real api key is the same we wont as large a window as possible without losing game tracking
        if date != oldDate[0] or hour != oldHour[0] or (oldMinute[0] <= 30 and minutes > 30):
            print("doin the update")
            players = playerCreate()
            playerDict = constructDict(players)
            sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
            cur.execute(sql, (date, hour, minutes))
            conn.commit()
            for key, value in playerDict.items():
                sql = "INSERT INTO playerdata(name,level,tier,rank,lp,wins,losses, mmr) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(sql, (key, value[0],value[1],value[2],value[3],value[4],value[5],value[6]))
                conn.commit()
        else:
            print("pullin the database")
            playerList = []
            fetchPlayers = "SELECT name,level,tier,rank,lp,wins,losses, mmr FROM playerdata ORDER BY id DESC LIMIT 19"
            cur.execute(fetchPlayers)
            players = cur.fetchall()
            players.reverse()
            for dump in players:
                player = Player(dump[0],dump[1],dump[2],dump[3],dump[4],dump[5],dump[6], dump[7])
                playerList.append(player)
            playerDict = constructDict(playerList)
    #really need to figure out what to do with this, its suppsosed to make things work if tables are empty.        
    except:
        sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
        cur.execute(sql, (date, hour, minutes))
        conn.commit()
        #TEMP TEMP TEMP TEMP TEMP BELOW TEMP TEMP TEMP TEMP
        playerDict = {}
        print("FUUUUUUUCK")
    cur.close()
    conn.close()
    return playerDict

@app.route("/")
def index():
    playerDict = timeTest()
    return flask.render_template(
        "index.html",
        playerDict = playerDict,
        data=json.dumps(playerDict)
    )

app.run(port=int(os.getenv("PORT", 8080)), host=os.getenv("IP", "0.0.0.0"))