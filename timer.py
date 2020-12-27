import psycopg2
import datetime
import time
from leaderboard import dbCon, playerCreate, constructDict


def timeTest():
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
    #try:
    #needs a smaller miunte window, probably 20~. if a real api key makes things faster i can do even smaller intervals (10 is optimal), if a real api key is the same we wont as large a window as possible without losing game tracking
    if date != oldDate[0] or hour != oldHour[0] or (oldMinute[0] <= 20 and minutes > 20) or (oldMinute[0] <= 40 and minutes > 40) or 1 == 1:
        print("doin the update")
        players = playerCreate()
        playerDict = constructDict(players)
        if date != oldDate[0]:
            print("making daily lp check")
            sql = "INSERT INTO dailylp (summoner, date, lp) VALUES (%s,%s,%s);"
            for key, value in playerDict.items():
                cur.execute(sql, (key, date, value[4]))
                conn.commit()
        sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
        cur.execute(sql, (date, hour, minutes))
        conn.commit()
        #get lp from playerDict, compare it to select query from dailylp lp value, insert new value as lpdelta
        counter = 0
        for key, value in playerDict.items():
            sql = "SELECT lp FROM dailylp ORDER BY id DESC LIMIT 19"
            cur.execute(sql)
            dailyLP = cur.fetchall()
            dailyLP.reverse()
            startingMmr = dailyLP[counter][0]
            counter = counter+1
            #value[4] is currnet mmr
            if startingMmr > value[4]:
                delta = startingMmr - value[4]
            elif startingMmr <= value[4]:
                delta = value[4] - startingMmr

            sql = "INSERT INTO playerdata(name,level,tier,rank,lp, mmr, lpdelta, wins,losses) VALUES (%s,%s,%s,%s,%s,%s,%s,%s, %s);"
            cur.execute(sql, (key, value[0],value[1],value[2],value[3],value[4], delta, value[5],value[6]))
            conn.commit()
timeTest()