import time

import praw

import random
from heapq import nlargest
from yahoo_fin import stock_info as si

reddit = praw.Reddit(
    client_id="*******************",
    client_secret="*************",
    password="***********",
    user_agent="reddit_bot",
    username="DependentEcstatic654",
    check_for_async=False
)



def get_price(stock_ticker):
    return(si.get_live_price(stock_ticker))

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, " ", ".", ";", ")", ",", "$", "?", ">", "<", "\"", "!", "+", "-", "*"]
phrase = "$"
all_stocks = []
rankings = {}
stock_prices = {}

for comment in reddit.subreddit("wallstreetbets+stocks+personalfinance").stream.comments():
    if phrase in comment.body:
        index = comment.body.index(phrase)
        ticker = ""
        ticker += comment.body[index]
        x = 1
        try:
            if comment.body[index + x] in str(numbers):
                continue
        except:
            continue
        while True:
            try:
                if comment.body[index + x] not in numbers:
                    ticker += comment.body[index + x]
                    x += 1
                else:
                    break
            except:
                break

        ticker = ticker.upper()
        if len(ticker) > 6:
            continue

        if ticker not in all_stocks:
            all_stocks.append(ticker)
            rankings[ticker] = 1

        elif ticker in all_stocks:
            rankings[ticker] += 1

        largest = nlargest(5, rankings, key=rankings.get)

        for i in range(len(largest)-1):
            a = largest[i]
            no_dollar = a[1:]
            try:
                stock_prices[largest[i]] = get_price(no_dollar)
            except:
                continue

        print(rankings)
        print(largest)
        print(stock_prices)
        print("\n")
