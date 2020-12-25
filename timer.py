import psycopg2
import datetime
from datetime import timedelta
import schedule
import time
import os
from os.path import join, dirname
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError
"""
dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)

riot = os.environ["RIOT"]

lolwatcher = LolWatcher(riot)
my_region="na1"

date = datetime.datetime.now()
users = ["MarTea"]
def daily():
    for user in users:
        user = lolwatcher.summoner.by_name(my_region, user)
        #matches = lolwatcher.match.matchlist_by_account(my_region, user['accountId'])
        #print(matches)
        #last_match = matches['matches'][0]
        #if(last_match['queue'] != 420):
        #    continue
        #print(last_match)
        #match_detail = lolwatcher.match.by_id(my_region, last_match['gameId'])
        #print(match_detail)





daily()


"""

dotenv_path = join(dirname(__file__), "keys.env")
load_dotenv(dotenv_path)

riot = os.environ["RIOT"]

lolwatcher = LolWatcher(riot)
my_region="na1"

date = datetime.datetime.now()

users = ["MarTea"]
def hourly():
    queueID = 0
    for user in users:
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

#schedule.every().hour.do(hourly)

def daily():
    conn = psycopg2.connect(
        host="localhost",
        database="leaderboard",
        user="postgres",
        password="password")

    cur = conn.cursor()
    date = datetime.datetime.now()
    date = date.strftime("%x")
    summoner = "MarTea"
    starting_lp = 5
    ending_lp = 0
    lp_delta = ending_lp - starting_lp
    sql = "INSERT INTO lptracker(date, summoner, starting_lp, ending_lp, lpdelta) VALUES (%s,%s,%s,%s,%s);"

    cur.execute(sql, (date, summoner, starting_lp, ending_lp, lp_delta))
    conn.commit()
    cur.close()
    conn.close()

#schedule.every().day.at("01:00").do(daily)

#while True:
#    schedule.run_pending()
#    time.sleep(60) # checks every minute to see if the time is the right time