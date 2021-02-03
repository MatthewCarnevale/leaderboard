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
from sqlalchemy import create_engine

dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)
riot = os.environ["RIOT"]

DATABASE_URL= os.environ["DATABASE_URL"]

def dbCon():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("db connection established")
    return conn, cur

def buildTables():
    conn, cur = dbCon()
    sql = "CREATE TABLE IF NOT EXISTS lifetime (name VARCHAR(255), kills Integer, deaths Integer, assists Integer, avgtime Integer, longestspree Integer, quads Integer, pentas Integer, bigkrit Integer, totalcreeps Integer, firstbloods Integer, dragons Integer, barons Integer, heralds Integer)"
    cur.execute(sql)
    conn.commit()
    sql = "CREATE TABLE IF NOT EXISTS dailylp (id Serial, summoner VARCHAR(255), date VARCHAR(255), lp Integer, totalgames Integer, yesterdaysdelta Integer)"
    cur.execute(sql)
    conn.commit()
    sql = "CREATE TABLE IF NOT EXISTS timetracker (id Serial, date VARCHAR(255), hour Integer, minutes Integer)"
    cur.execute(sql)
    conn.commit()
    sql = "CREATE TABLE IF NOT EXISTS matchhistory (id Serial, name VARCHAR(255), teamid Integer, championid Integer, gametime VARCHAR(255), win Boolean, kills Integer, deaths Integer, assists Integer, spree Integer, multi Integer, longlife VARCHAR(255), doubles Integer, triples Integer, quadras Integer, pentas Integer, bigkrit Integer, totalchampdmg Integer, towerdamage Integer, vision Integer, goldearned Integer, goldspent Integer, towerkills Integer, cs Integer, level Integer, firstblood Boolean, dragons Integer, barons Integer, heralds Integer, role VARCHAR(255), lane VARCHAR(255), gameid VARCHAR(255))"
    cur.execute(sql)
    conn.commit()
    sql = "CREATE TABLE IF NOT EXISTS playerdata (id Serial, name VARCHAR(255), level Integer, tier VARCHAR(255), rank VARCHAR(255), lp Integer, mmr Integer, lpdelta Integer, dailygames Integer, wins Integer, losses Integer)"
    cur.execute(sql)
    conn.commit()
    ##logic for adding new player to table
    # sql = "INSERT INTO lifetime (name, kills, deaths, assists, avgtime, longestspree, quads, pentas, bigkrit, totalcreeps, firstbloods, dragons, barons, heralds) VALUES ('Challenger1Month',0,0,0,0,0,0,0,0,0,0,0,0,0)"
    # cur.execute(sql)
    # conn.commit()
    # sql = "INSERT INTO dailylp (summoner,date,lp,totalgames,yesterdaysdelta) VALUES ('Challenger1Month','01/01/21',0,0,0)"
    # cur.execute(sql)
    # conn.commit()
    # sql = "INSERT INTO playerdata (name, level, tier, rank, lp, mmr, lpdelta, dailygames, wins, losses) VALUES ('Challenger1Month',0,0,0,0,0,0,0,0,0)"
    # cur.execute(sql)
    # conn.commit()
    ##logic for dumping tables and starting from scratch
    sql = "INSERT INTO timetracker (date, hour, minutes) VALUES ('01/01/21',0,0)"
    cur.execute(sql)
    conn.commit()
    for user in users:
        if user == "Trúst":
            user = "Trust"
        sql = "INSERT INTO lifetime (name, kills, deaths, assists, avgtime, longestspree, quads, pentas, bigkrit, totalcreeps, firstbloods, dragons, barons, heralds) VALUES (%s,0,0,0,0,0,0,0,0,0,0,0,0,0)"
        cur.execute(sql,(user,))
        conn.commit()
        sql = "INSERT INTO dailylp (summoner,date,lp,totalgames,yesterdaysdelta) VALUES (%s,'01/01/21',0,0,0)"
        cur.execute(sql,(user,))
        conn.commit()
        sql = "INSERT INTO playerdata (name, level, tier, rank, lp, mmr, lpdelta, dailygames, wins, losses) VALUES (%s,0,0,0,0,0,0,0,0,0)"
        cur.execute(sql,(user,))
        conn.commit()
    
def rankedStatsBuilder(user):
    lolwatcher = LolWatcher(riot)
    my_region="na1"
    print("making summoner api call")
    summoner = lolwatcher.summoner.by_name(my_region, user)
    print("making ranked stats api call")
    ranked_stats = lolwatcher.league.by_summoner(my_region, summoner['id'])
    #print(ranked_stats)
    return summoner, ranked_stats, lolwatcher
#ranked stats dont exist for players without 10 games played
#users = ["MarTea", "Stin God", "Bassel", "Trúst", "Big Itzweird", "K3v1nRul3s", "Kareem100", "aminrhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin VI", "Kerø"]
users = ["MarTea", "Trúst","Bassel", "Big Itzweird", "Kalichi", "Challenger1Month", "aminrhino", "Godric", "shadowninjas13", "Glorious Duelist", "Kareem100", "Xerous", "A GIANT 8IIIID", "Stin God", "Vayler", "khalí", "19PX", "Riko Best Girl"]
def matchFunc(summoner, lolwatcher):
    conn, cur = dbCon()
    name = summoner["name"]
    print(name)
    print("making matches api call")
    matches = lolwatcher.match.matchlist_by_account("na1",summoner['accountId'])
    #print(matches)
    last_match = matches['matches'][0]
    gameId = last_match['gameId']
    sql = "SELECT gameid FROM matchhistory WHERE name=%s"
    if name == "Trúst":
        name = "Trust"
    #HERE
    cur.execute(sql, (name,))
    pastIds = cur.fetchall()
    counter = 0
    for tup in pastIds:
        try:
            if gameId == int(tup[0]):
                return 0
                print("should never hit")
            counter = counter+1
        except:
            counter = counter+1
    #print(name)
    #THIS FLIP IS INTENTIONAL
    if name == "Trust":
        name = "Trúst"
    print("making match details api call")
    match_details = lolwatcher.match.by_id("na1", last_match['gameId'])
    #print(match_details)
    queue_type = match_details["queueId"]
    if queue_type == 420:
        game_time = match_details["gameDuration"]
        minutes = game_time / 60
        minutes = str(int(minutes))
        seconds = game_time % 60
        if seconds < 10:
            fixed = "0"+str(seconds)
        else:
            fixed = str(seconds)
        game_time = minutes + ":" + fixed
        teams = match_details["teams"]
        identities = match_details["participantIdentities"]
        i = 0
        while name != identities[i]["player"]["summonerName"]:
            i = i+1
        participantId = i+1
        for person in match_details["participants"]:
            if person["participantId"] != participantId:
                continue
            else:
                teamId = person["teamId"]
                #convert champ id to name from number
                championId = person["championId"]
                stats = person["stats"]
                win = stats["win"]
                kills = stats["kills"]
                deaths = stats["deaths"]
                assists = stats["assists"]
                spree = stats["largestKillingSpree"]
                multi = stats["largestMultiKill"]
                longLife = stats["longestTimeSpentLiving"]
                minutes = longLife / 60
                minutes = str(int(minutes))
                seconds = longLife % 60
                if seconds < 10:
                    fixed = "0"+str(seconds)
                else:
                    fixed = str(seconds)
                longLife = minutes + ":" + fixed
                doubles = stats["doubleKills"]
                triples = stats["tripleKills"]
                quadras = stats["quadraKills"]
                pentas = stats["pentaKills"]
                bigKrit = stats["largestCriticalStrike"]
                champDmg = stats["totalDamageDealtToChampions"]
                peter = stats["damageDealtToTurrets"]
                vision = stats["visionScore"]
                gold = stats["goldEarned"]
                spent = stats["goldSpent"]
                turrets = stats["turretKills"]
                creeps = stats["totalMinionsKilled"]
                creeps = creeps + stats["neutralMinionsKilled"]
                level = stats["champLevel"]
                firstBlood = stats["firstBloodKill"]

                if teamId == teams[0]["teamId"]:
                    dragCount = teams[0]["dragonKills"]
                    baronCount = teams[0]["baronKills"]
                    heraldCount = teams[0]["riftHeraldKills"]
                else:
                    dragCount = teams[1]["dragonKills"]
                    baronCount = teams[1]["baronKills"]
                    heraldCount = teams[1]["riftHeraldKills"]

                timeline = person["timeline"]
                role = timeline["role"]
                lane = timeline["lane"]
                sql = "INSERT INTO matchhistory (name, teamid, championid, gametime, win, kills, deaths, assists, spree, multi, longlife, doubles, triples, quadras, pentas, bigkrit, totalchampdmg, towerdamage, vision, goldearned, goldspent, towerkills, cs, level, firstblood, dragons, barons, heralds, role, lane, gameid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                if name == "Trúst":
                    name = "Trust"
                #HERE
                cur.execute(sql, (name, teamId, championId, game_time, win, kills, deaths, assists, spree, multi, longLife, doubles, triples, quadras, pentas, bigKrit, champDmg, peter, vision, gold, spent, turrets, creeps, level, firstBlood, dragCount, baronCount, heraldCount, role, lane, gameId))
                conn.commit()
                sql = "SELECT * FROM lifetime WHERE name=%s"
                cur.execute(sql, (name,))
                oldTotals = cur.fetchall()
                newKills = int(oldTotals[0][1]) + kills
                newDeaths = int(oldTotals[0][2]) + deaths
                newAssists = int(oldTotals[0][3]) + assists
                #need total number of games for avg time to work
                #avgTime = int()
                if int(oldTotals[0][5]) > spree:
                    spree = int(oldTotals[0][5])
                newQuads = int(oldTotals[0][6]) + quadras
                newPentas = int(oldTotals[0][7]) + pentas
                if int(oldTotals[0][8]) > bigKrit:
                    bigKrit = int(oldTotals[0][8])
                totalCreeps = int(oldTotals[0][9]) + creeps
                if firstBlood == True:
                    firstbloods = int(oldTotals[0][10]) + 1
                else:
                    firstbloods = int(oldTotals[0][10])
                newDragons = int(oldTotals[0][11]) + dragCount
                newBarons = int(oldTotals[0][12]) + baronCount
                newHeralds = int(oldTotals[0][13]) + heraldCount
                sql = "UPDATE lifetime SET kills=%s, deaths=%s, assists=%s, longestspree=%s, quads=%s, pentas=%s, bigkrit=%s, totalcreeps=%s, firstbloods=%s, dragons=%s, barons=%s, heralds=%s WHERE name = %s"
                #HERE
                if name == "Trúst":
                    name = "Trust"
                cur.execute(sql, (newKills,newDeaths,newAssists, spree, newQuads, newPentas, bigKrit, totalCreeps, firstbloods, newDragons, newBarons, newHeralds, name))
                conn.commit()
                break
    else:
        print("not a ranked solo/duo game, skipping person")


def playerCreate():
    playerList = []
    print("hello i am making riot games api calls")
    counter = 0
    dayGames = dailyGames()
    for user in users:
        queueID = 0
        summoner, ranked_stats, lolwatcher = rankedStatsBuilder(user)
        matchFunc(summoner, lolwatcher)
        #print(ranked_stats)
        #print(ranked_stats[queueID])
        queue = ranked_stats[queueID].get("queueType")
        if queue == "RANKED_SOLO_5x5":
            queueID = 0
        else:
            queueID = 1
        ranks = {}
        ranks[summoner.get("name")] = [ranked_stats[queueID].get("leaguePoints"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank")]
        convertedMMR = rankConversion(ranks)
        yesterday = yesterdaysDelta()
        player =  Player(summoner.get("name"), summoner.get("summonerLevel"), ranked_stats[queueID].get("tier").lower().capitalize(), ranked_stats[queueID].get("rank"), ranked_stats[queueID].get("leaguePoints"), convertedMMR, 0, dayGames[counter], ranked_stats[queueID].get("wins"), ranked_stats[queueID].get("losses"), yesterday[counter][0])
        playerList.append(player)
        counter = counter+1
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
    conn, cur = dbCon()
    sql = "SELECT totalgames FROM dailylp ORDER BY id DESC LIMIT 18"
    cur.execute(sql)
    totalgames = cur.fetchall()
    totalgames.reverse()
    dGames = []
    for i in range(0,18):
        dGames.append(totalgames[i][0])
    return dGames

def constructDict(playerList):
    playerDict = {}
    for player in playerList:
        playerDict[player.name] = [player.level, player.tier, player.rank, player.lp, player.mmr, player.lpdelta, player.dailywins, player.wins, player.losses, player.yesterdaysDelta]
    print("dict of player objects made")
    return playerDict

def deltaDate():
    conn, cur = dbCon()
    fetchDate = "SELECT date FROM dailylp ORDER BY id DESC LIMIT 1"
    cur.execute(fetchDate)
    date = cur.fetchone()
    date = date[0]
    return date

def rankedPull():
    conn, cur = dbCon()
    print("pullin the ranks")
    playerList = []
    fetchPlayers = "SELECT name,level,tier,rank,lp,mmr,lpdelta,dailygames,wins,losses FROM playerdata ORDER BY id DESC LIMIT 18"
    cur.execute(fetchPlayers)
    players = cur.fetchall()
    players.reverse()
    yesterday = yesterdaysDelta()
    counter = 0
    for dump in players:
        player = Player(dump[0],dump[1],dump[2],dump[3],dump[4],dump[5],dump[6], dump[7], dump[8],dump[9],yesterday[counter][0])
        playerList.append(player)
        counter = counter + 1
    playerDict = constructDict(playerList)
    cur.close()
    conn.close()
    print("time based updating checked")
    return playerDict

def summonerInfo(summonerName):
    conn, cur = dbCon()
    sql = "SELECT * FROM matchhistory WHERE name=%s ORDER BY id DESC LIMIT 10"
    if summonerName == "Trúst":
        summonerName = "Trust"
    #HERE
    cur.execute(sql, (summonerName,))
    stats = cur.fetchall()
    # print(stats)
    # stats.reverse()
    # print(stats)
    cur.close()
    conn.close()
    return stats

def lifetime(summonerName):
    conn, cur = dbCon()
    sql = "SELECT * FROM lifetime WHERE name=%s"
    if summonerName == "Trúst":
        summonerName = "Trust"
    #HERE
    cur.execute(sql, (summonerName,))
    accolades = cur.fetchall()
    cur.close()
    conn.close()
    return accolades

def yesterdaysDelta():
    conn, cur = dbCon()
    sql = "SELECT yesterdaysdelta FROM dailylp ORDER BY id DESC LIMIT 18"
    cur.execute(sql)
    yesterday = cur.fetchall()
    yesterday.reverse()
    cur.close()
    conn.close()
    return yesterday

def isQueue():
    conn, cur = dbCon()
    loserDict = {}
    winnerDict = {}
    sql = "SELECT win FROM matchhistory WHERE name=%s ORDER BY id DESC"
    for user in users:
        if user == "Trúst":
            user = "Trust"
        cur.execute(sql, (user,))
        data = cur.fetchall()
        lossCounter = 0
        for value in data:
            if value[0] == True:
                break
            else:
                lossCounter = lossCounter + 1
        winCounter = 0
        for value in data:
            if value[0] == False:
                break
            else:
                winCounter = winCounter + 1
        if lossCounter >= 3:
            loserDict[user] = lossCounter
        elif winCounter >= 3:
            winnerDict[user] = winCounter
    if len(winnerDict) == 0:
        winnerDict["none"] = "none"
    if len(loserDict) == 0:
        loserDict["none"] = "none"
    return winnerDict, loserDict

# db = dbCon()
# test = "no"
# db.execute("INSERT INTO poopy (name) VALUES (%test)")
#buildTables()