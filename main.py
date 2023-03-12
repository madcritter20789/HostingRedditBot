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

subreddit = reddit.subreddit("cool")
print(subreddit.display_name)
print(subreddit.title)
print(subreddit.description)

for submission in reddit.subreddit("cars").hot(limit=5):
    print(submission.title)
    print(submission.score)
    print(submission.id)
    print(submission.url)

for post in reddit.subreddit("cars").hot(limit=5):
    print(post.title)
    print(post.score)
    print(post.id)
    print(post.url)


def karma():
    try:
        messages = ["Upvoted, upvote in return","Great Post,cure to upvoteQ"]
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
