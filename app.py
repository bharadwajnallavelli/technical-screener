from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, render_template
from stocks import nasdaq_stock_list
from squeeze_stocks import run_code
import sqlite3
import datetime

app = Flask(__name__)
scheduler = BackgroundScheduler()

connect = sqlite3.connect('database.db')
connect.execute('CREATE TABLE IF NOT EXISTS Squeeze_Stocks_tbl (Datetime TEXT, Long_Stocks TEXT, Short_Stocks TEXT)')


def my_cron_job():
    # Code to be executed by the cron job
    stock_list = nasdaq_stock_list()
    out_squeeze_long, out_squeeze_short = run_code(stock_list)
    now = datetime.datetime.now()
    # Insert into database table
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute("INSERT INTO Squeeze_Stocks_tbl (Datetime,Long_Stocks,Short_Stocks) VALUES (?,?,?)",
                       (str(now), str(out_squeeze_long), str(out_squeeze_short)))
        users.commit()
    # Now you can use the returned lists as needed
    print("Stocks for long positions:", out_squeeze_long)
    print("Stocks for short positions:", out_squeeze_short)
    print("Now:", now)

# test scheduler
scheduler.add_job(
     func=my_cron_job, trigger=CronTrigger.from_crontab('*/5 * * * *')
 )

# Schedule the job from 6:30 PM to 11:59 PM
# scheduler.add_job(
#     func=my_cron_job, trigger=CronTrigger.from_crontab('30 18-23 * * *')
# )

# Schedule the job from 12:00 AM to 2:30 AM
# scheduler.add_job(
#     func=my_cron_job, trigger=CronTrigger.from_crontab('30 0-2 * * *')
# )

# Start the scheduler
scheduler.start()


@app.route("/")
def hello_world():
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM Squeeze_Stocks_tbl')
    data = cursor.fetchall()
    return render_template("index.html", stocks=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
