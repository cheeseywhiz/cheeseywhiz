import praw
import webbrowser
import time

reddit = praw.Reddit('cheeseywhiz')

def stream(sub='all'):
    t0=time.clock()
    list=[]
    xy=[]
    try:
        for submission in reddit.subreddit(sub).stream.submissions(pause_after=0):
            elapsed=time.clock()-t0
            if submission is not None: list.append(elapsed)
            past_minute=[n for n in list if n>elapsed-min(60,elapsed)]
            num_past_minute=len(past_minute)
            xy.append((elapsed,60*num_past_minute/min(60,elapsed)))
            print(xy[-1][1],'posts per minute',xy[-1][0])
    except KeyboardInterrupt:
        return xy