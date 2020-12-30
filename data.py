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

def rankedStatsBuilder(user):
    lolwatcher = LolWatcher(riot)
    my_region="na1"
    print("making summoner api call")
    summoner = lolwatcher.summoner.by_name(my_region, user)
    print("making ranked stats api call")
    ranked_stats = lolwatcher.league.by_summoner(my_region, summoner['id'])
    return summoner, ranked_stats, lolwatcher

users = ["MarTea", "StinGod", "Bassel", "Trúst", "Big ItzWeird", "K3v1nRul3s", "Kareem100", "AminRhino", "Mama Zer0", "Xerous", "Vayler", "Glorious Duelist", "Godric II", "Shadowninjas13", "Kalichi", "Riko Best Girl", "Jebal", "Jin Vi", "KerØ"]
#users = ["Bassel", "Vayler"]

def matchFunc(summoner, lolwatcher):
    conn, cur = dbCon()
    name = summoner["name"]
    print("making matches api call")
    matches = lolwatcher.match.matchlist_by_account("na1",summoner['accountId'])
    last_match = matches['matches'][0]
    gameId = last_match['gameId']
    sql = "SELECT gameid FROM matchhistory WHERE name LIKE (%s)"
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
    print("making match details api call")
    match_details = lolwatcher.match.by_id("na1", last_match['gameId'])
    queue_type = match_details["queueId"]
    if queue_type == 420:
        #convert game time to minutes/seconds from seconds
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
                #win is False/True bool
                win = stats["win"]
                kills = stats["kills"]
                deaths = stats["deaths"]
                assists = stats["assists"]
                spree = stats["largestKillingSpree"]
                #multi is 0,1,2,3,4 or 5
                multi = stats["largestMultiKill"]
                #convert longLife to minutes/seconds from seconds
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
                level = stats["champLevel"]
                #true/false value for first blood
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
                cur.execute(sql, (name, teamId, championId, game_time, win, kills, deaths, assists, spree, multi, longLife, doubles, triples, quadras, pentas, bigKrit, champDmg, peter, vision, gold, spent, turrets, creeps, level, firstBlood, dragCount, baronCount, heraldCount, role, lane, gameId))
                conn.commit()

                break
    else:
        print("not a ranked solo/duo game, skipping person")
    #its 30 s rn


def playerCreate():
    # lolwatcher = LolWatcher(riot)
    # my_region="na1"
    playerList = []
    # print("hello i am making riot games api calls")
    counter = 0
    dayGames = dailyGames()
    for user in users:
        queueID = 0
        # summoner = lolwatcher.summoner.by_name(my_region, user)
        # ranked_stats = lolwatcher.league.by_summoner(my_region, summoner['id'])
        summoner, ranked_stats, lolwatcher = rankedStatsBuilder(user)
        #if statement time check for match data call?
        if 1 == 1:
             matchFunc(summoner, lolwatcher)
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

def rankedPull():
    conn, cur = dbCon()
    print("pullin the ranks")
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

def statsPull():
    conn, cur = dbCon()
    print("pullin the matches")
    for user in users:
        sql = "SELECT teamid, championid, gametime, win, kills, deaths, assists, spree, multi, longlife, doubles, triples, quadras, pentas, bigkrit, totalchampdmg, towerdamage, vision, goldearned, goldspent, towerkills, cs, level, firstblood, dragons, barons, heralds, role, lane FROM matchhistory WHERE name LIKE (%s)"
        cur.execute(sql, (user,))
        stats = cur.fetchall()
        print(user)
        print(stats)
    cur.close()
    conn.close()

def summonerInfo(summonerName):
    conn, cur = dbCon()
    sql = "SELECT * FROM matchhistory WHERE name=%s LIMIT 10"
    cur.execute(sql, (summonerName,))
    stats = cur.fetchall()
    cur.close()
    conn.close()
    return stats
