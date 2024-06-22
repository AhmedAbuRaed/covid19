import json

with open('D:/Research/UBC/CollectTweets/jan_tweets.txt', 'r') as f:
    lines = f.readlines()
    stored_data = json.loads(lines[0])
    print("Hi")