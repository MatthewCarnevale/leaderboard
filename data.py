import os
import flask
from riotwatcher import LolWatcher, ApiError
import flask_sqlalchemy
import psycopg2
import datetime
from os.path import join, dirname
from dotenv import load_dotenv
import enum
import time
from player import Player

dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)
riot = os.environ["RIOT"]
def dbCon():
    conn = psycopg2.connect(
        host="localhost",
        database="leaderboard",
        user="postgres",
        password="password")
    cur = conn.cursor()
    print("db connection established")
    return conn, cur

users = ["MarTea", "StinGod", "Bassel", "Trúst", "Big ItzWeird", "K3v1nRul3s", "Kareem100", "AminRhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "Shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin Vi", "KerØ"]
#users = ["MarTea", "StinGod"]

def playerCreate():
    lolwatcher = LolWatcher(riot)
    my_region="na1"
    playerList = []
    print("hello i am making riot games api calls")
    counter = 0
    dayGames = dailyGames()
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
        convertedMMR = rankConversion(ranks)
        player =  Player(summoner.get("name"), summoner.get("summonerLevel"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank"), ranked_stats[queueID].get("leaguePoints"), convertedMMR, 0, dayGames[counter], ranked_stats[queueID].get("wins"), ranked_stats[queueID].get("losses"))
        playerList.append(player)
        counter = counter+1
        #match history stuff makes more api calls which is bad news
        #matches = lolwatcher.match.matchlist_by_account(my_region, summoner['accountId'])
        #print(matches)
        """
        for value in matches["matches"]:
            #value is a dict of things that includes (most importantly) gameId to be used to find data related to the specific game
            print(value)
            #from value we need gameId, champion, queue, role, lane
            matchDetails = lolwatcher.match.by_id(my_region, value['gameId'])
            #from matchDetails we need gameDuration, teams, bans, participants
            #from matchDetails teams list->dict need win, firstBlood, firstTower, firstBaron, firstDragon, firstRiftHearld... etc
            #from bans list->dict we need champion id many times
        """

    print("list of players loaded")
    return playerList

def rankConversion(ranks):
    mmr = 0
    for name, rank in ranks.items():
        if rank[1] == "Iron":
           mmr = 0
        elif rank[1] == "Bronze":
            mmr = 400
        elif rank[1] == "Silver":
            mmr = 800
        elif rank[1] == "Gold":
            mmr = 1200
        elif rank[1] == "Platinum":
            mmr = 1600
        elif rank[1] == "Diamond":
            mmr = 2000
        elif rank[1] == "Master":
            mmr = 2100
        elif rank[1] == "Grandmaster":
            mmr = 2200
        elif rank[1] == "Challenger":
            mmr = 2300
        else:
            mmr = -1
        if rank[2] == "I":
            mmr = mmr + 300
        elif rank[2] == "II":
            mmr = mmr + 200
        elif rank[2] == "III":
            mmr = mmr + 100
        elif rank[2] == "IV":
            mmr = mmr + 0
        else:
            mmr = 0
        convert = 0
        convert = int(rank[0]) + mmr
    return convert

def dailyGames():
    #run select query for daily games?
    conn, cur = dbCon()
    sql = "SELECT totalgames FROM dailylp ORDER BY id DESC LIMIT 19"
    cur.execute(sql)
    totalgames = cur.fetchall()
    totalgames.reverse()
    dGames = []
    for i in range(0,19):
        dGames.append(totalgames[i][0])
    return dGames

def constructDict(playerList):
    playerDict = {}
    for player in playerList:
        playerDict[player.name] = [player.level, player.tier, player.rank, player.lp, player.mmr, player.lpdelta, player.dailywins, player.wins, player.losses]
    print("dict of player objects made")
    return playerDict

def deltaDate():
    #select date from daily update
    #use jinja to display date somewhere
    conn, cur = dbCon()
    fetchDate = "SELECT date FROM dailylp ORDER BY id DESC LIMIT 1"
    cur.execute(fetchDate)
    date = cur.fetchone()
    date = date[0]
    return date
def dbPull():
    conn, cur = dbCon()
    print("pullin the database")
    playerList = []
    fetchPlayers = "SELECT name,level,tier,rank,lp,mmr,lpdelta,dailygames,wins,losses FROM playerdata ORDER BY id DESC LIMIT 19"
    cur.execute(fetchPlayers)
    players = cur.fetchall()
    players.reverse()
    for dump in players:
        player = Player(dump[0],dump[1],dump[2],dump[3],dump[4],dump[5],dump[6], dump[7], dump[8],dump[9])
        playerList.append(player)
    playerDict = constructDict(playerList)
    #really need to figure out what to do with this, its suppsosed to make things work if tables are empty.        
    # except:
    #     sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
    #     cur.execute(sql, (date, hour, minutes))
    #     conn.commit()
    #     #TEMP TEMP TEMP TEMP TEMP BELOW TEMP TEMP TEMP TEMP
    #     playerDict = {}
    #     print("FUUUUUUUCK")
    cur.close()
    conn.close()
    print("time based updating checked")
    return playerDict
