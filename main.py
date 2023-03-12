import time
import praw
import random

reddit = praw.Reddit(
    client_id="Fa5UzGLCvcDg-b5YvFQYUQ",
    client_secret="iASpu4AM0PNTsMl-jT2KNrmKRa6Kog",
    password="123asd123asd",
    user_agent="reddit_bot",
    username="DependentEcstatic654",
    check_for_async=False
)

def karma():
    try:
        messages = ["Upvoted, upvote in return","Great Post,care to upvote"]
        for submission in reddit.subreddit("FreeKarma4U+FreeKarma4You").stream.submissions():
            submission.upvote()
            rand = random.randint(0, (len(messages)-1))
            print(submission.title)
            submission.reply(messages[rand])
            time.sleep(300000)
    except:
        time.sleep(300000)
        karma()

karma()
