import datetime

import requests
from api import *
import datetime as dt
from datetime import date, datetime
import smtplib as smt
from email_desc import *
import pytz
import html

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
curr_date = date.today()
tz_NY = pytz.timezone('America/New_York')
datetime_NY = datetime.now(tz_NY)
if curr_date != datetime_NY.date():
    curr_date = datetime_NY.date()
# print(curr_date)
# if d1 <= curr_time < d2:
#     curr_date -= datetime.timedelta(days=1)


## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

news_parameters={
    "q": COMPANY_NAME,
    "from": str(curr_date-dt.timedelta(days=1)),
    "to": str(curr_date-dt.timedelta(days=2)),
    "sortBy": "popularity",
    "apikey": news_api_key
}


def get_news():
    with requests.get(url="https://newsapi.org/v2/everything?", params=news_parameters) as response:
        data = response.json()
        # print(data["articles"][:3])
        news_data = [(articles["title"], articles["description"])for articles in data["articles"][:3]]
        # print(news_data[0])
        return news_data


def send_mail(message):
    with smt.SMTP("smtp.gmail.com", port=587) as conn:
        conn.starttls()
        conn.login(user=my_email, password=my_pass)
        conn.sendmail(
            from_addr=my_email,
            to_addrs=my_email,
            msg=message
        )
        print("Mail sent")

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_api_key
}
with requests.get(url="https://www.alphavantage.co/query?", params=stock_parameters) as response:
    stock_data = response.json()
    # print(stock_data)
    # print(curr_date)
    yesterday_data_close = float(stock_data["Time Series (Daily)"][str(curr_date-dt.timedelta(days=1))]["4. close"])
    # print(yesterday_data)
    previous_day_data_close = float(stock_data["Time Series (Daily)"][str(curr_date-dt.timedelta(days=2))]["4. close"])
    # print(previous_day_data_close)
    change = abs(yesterday_data_close - previous_day_data_close)/previous_day_data_close * 100
    if yesterday_data_close < previous_day_data_close:
        change *= -1
    if change >= 5 or change <= -5:
        news_data = get_news()
        body = ""
        for i in news_data:
            body += "Headline: " + str(i[0]) + "\n" + "Brief: " + str(i[1]) +"\n"
        message = f"subject:TSLA {change}\n\n {body}"
        # print(message)
        send_mail(message.encode("utf-8"))
    else:
        print(abs(yesterday_data_close - previous_day_data_close)/previous_day_data_close)


## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

