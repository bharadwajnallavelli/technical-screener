import datetime
import sqlite3

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, render_template

from squeeze_stocks import run_code
from stocks import nasdaq_stock_list

app = Flask(__name__)
scheduler = BackgroundScheduler()

connect = sqlite3.connect('database.db')
connect.execute(
    'CREATE TABLE IF NOT EXISTS Squeeze_Stocks_tbl (Datetime TEXT, Long_Stocks_squeeze TEXT, Short_Stocks_squeeze TEXT, Macd_Stocks_long TEXT, Macd_Stocks_short TEXT)')


def my_cron_job():
    # Code to be executed by the cron job
    stock_list = nasdaq_stock_list()
    out_squeeze_long, out_squeeze_short, macd_buy, macd_sell = run_code(stock_list)
    now = datetime.datetime.now()
    # Insert into database table
    with sqlite3.connect("database.db") as users:
        cursor = users.cursor()
        cursor.execute(
            "INSERT INTO Squeeze_Stocks_tbl (Datetime,Long_Stocks_squeeze,Short_Stocks_squeeze,Macd_Stocks_long,Macd_Stocks_short) VALUES (?,?,?,?,?)",
            (str(now), str(out_squeeze_long).replace('[', '').replace(']', ''),
             str(out_squeeze_short).replace('[', '').replace(']', ''),
             str(macd_buy).replace('[', '').replace(']', ''),
             str(macd_sell).replace('[', '').replace(']', '')))
        users.commit()
    # Now you can use the returned lists as needed
    print("Stocks for long positions:", out_squeeze_long)
    print("Stocks for short positions:", out_squeeze_short)
    print("Stocks for macd long positions:", macd_buy)
    print("Stocks for macd short positions:", macd_sell)
    print("Now:", now)


# test scheduler
scheduler.add_job(
    func=my_cron_job, trigger=CronTrigger.from_crontab('30 * * * *')
)

# Schedule the job from 7:30 PM to 3:30 PM
# scheduler.add_job(
#     func=my_cron_job, trigger=CronTrigger.from_crontab('30 18-23 * * *')
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
