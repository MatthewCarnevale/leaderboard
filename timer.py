import psycopg2
import datetime
from datetime import timedelta
import schedule
import time

date = datetime.datetime.now()
print(date)
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

schedule.every().day.at("01:00").do(daily)

while True:
    schedule.run_pending()
    time.sleep(60) # checks every minute to see if the time is the right time