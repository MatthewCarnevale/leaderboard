import psycopg2
import datetime
import time
from data import dbCon, playerCreate, constructDict

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
    #if date != oldDate[0] or hour != oldHour[0] or (oldMinute[0] <= 20 and minutes > 20) or (oldMinute[0] <= 40 and minutes > 40):
    print("doin the update")
    players = playerCreate()
    playerDict = constructDict(players)
    #because the Heroku psql server is in UTC time this hour == 5 is used to compensate and make update happen at midnight EST
    # print(oldHour[0])
    # print(oldMinutes[0])
    if hour == 5 and minutes >= 0 and minutes <= 10:
        print("making daily lp check")
        #sql = "INSERT INTO dailylp (summoner, date, lp, totalgames, yesterdaysdelta) VALUES (%s,%s,%s,%s,%s);"
        sql = "UPDATE dailylp SET date=%s, lp=%s, totalgames=%s, yesterdaysdelta=%s WHERE name=%s"
        sql2 = "SELECT lpdelta FROM playerdata WHERE name=%s ORDER BY id DESC limit 1"
        print(playerDict.items())
        for key, value in playerDict.items():
            if key == "Trúst":
                key = "Trust"
            cur.execute(sql2, (key,))
            dailyDelta = cur.fetchall()
            totalGames = value[7] + value[8]
            cur.execute(sql, (date, value[4], totalGames, dailyDelta[0],key))
            conn.commit()

    sql = "INSERT INTO timetracker(date, hour, minutes) VALUES (%s,%s,%s);"
    cur.execute(sql, (date, hour, minutes))
    conn.commit()
    #get lp from playerDict, compare it to select query from dailylp lp value, insert new value as lpdelta
    counter = 0
    for key, value in playerDict.items():
        sql = "SELECT lp FROM dailylp ORDER BY id DESC LIMIT 20"
        cur.execute(sql)
        dailyLP = cur.fetchall()
        dailyLP.reverse()
        startingMmr = dailyLP[counter][0]
        sql = "SELECT totalgames FROM dailylp ORDER BY id DESC LIMIT 20"
        cur.execute(sql)
        dailyGames = cur.fetchall()
        dailyGames.reverse()
        totalDayGames = (value[7] + value[8]) - dailyGames[counter][0]
        counter = counter+1
        delta = value[4] - startingMmr
        #HERE
        #sql = "INSERT INTO playerdata(name,level,tier,rank,lp, mmr, lpdelta, dailygames, wins,losses) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        sql = "UPDATE playerdata SET level=%s, tier=%s, rank=%s, lp=%s, mmr=%s, lpdelta=%s, dailygames=%s, wins=%s, losses=%s WHERE name=%s;"
        if key == "Trúst":
            key = "Trust"
        #HERE
        cur.execute(sql, (value[0],value[1],value[2],value[3],value[4], delta, totalDayGames, value[7],value[8],key))
        conn.commit()
#
print("ok me done with api push")