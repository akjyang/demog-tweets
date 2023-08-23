import tweepy
import pandas as pd
import numpy as np
#%%
Client = tweepy.Client(
        bearer_token=BEARER_TOKEN[3],
        consumer_key=CONSUMER_KEY[3],
        consumer_secret=CONSUMER_SECRET[3],
        access_token=ACCESS_TOKEN[3],
        access_token_secret=ACCESS_SECRET[3],
        wait_on_rate_limit=True
    )

recents = Client.get_users_tweets(id = 1598315378521903106, max_results = 5, user_auth = True)
recents[0][0].id

query = "conversation_id:1664843648389750784 is:reply"

Client.search_all_tweets(query = query)
#%%
usernames = []

like_acc = []
retweet_acc = []
quote_acc = []
views_acc = []

tweet_objs = []

retweet_users = []

quotes_ids = []
quotes_texts = []
#%%
for i in range(len(CONSUMER_KEY)):
        
    Client = tweepy.Client(
        consumer_key=CONSUMER_KEY[i],
        consumer_secret=CONSUMER_SECRET[i],
        access_token=ACCESS_TOKEN[i],
        access_token_secret=ACCESS_SECRET[i],
        wait_on_rate_limit=True
    )

    print(str(Client.get_me().data.username) + "\n")
    usernames.append(str(Client.get_me().data.username))

    # getting the tweets
    test_tweets = []
    # filter for tweets from pilot start day
    for tweet in tweepy.Paginator(Client.get_users_tweets,
                                id = Client.get_me().data.id,
                                max_results = 100,
                                exclude = "retweets",
                                start_time = "2023-05-18T00:00:00Z",
                                end_time = "2023-06-02T23:59:59Z",
                                tweet_fields = "public_metrics",
                                user_auth = True).flatten():
        test_tweets.append(tweet)

    tweet_objs.append(test_tweets)

    print(str(len(test_tweets)) + " test tweets found. + \n")
    print("Oldest tweet should be: \n\n" + test_tweets[-1].text + "\n")

    like_count = 0
    quote_count = 0
    retweet_count = 0
    view_count = 0

    retweeters = []

    quote = []
    quoted_ids = []

    for tweet in test_tweets:
        
        like_count += tweet.data["public_metrics"]["like_count"]
        quote_count += tweet.data["public_metrics"]["quote_count"]
        retweet_count += tweet.data["public_metrics"]["retweet_count"]
        view_count += tweet.data["public_metrics"]["impression_count"]
        
        if tweet.data["public_metrics"]["quote_count"] != 0:
            quote_obj = Client.get_quote_tweets(id = tweet.id, user_auth = True).data
            if quote_obj != None:
                for qtweet in quote_obj:
                    quote.append(qtweet.text)
                    quoted_ids.append(qtweet.id)
            
        if tweet.data["public_metrics"]["retweet_count"] != 0:
            rtweet_obj = Client.get_retweeters(id = tweet.id, user_auth = True)[0]
            for rtweet in rtweet_obj:
                retweeters.append(rtweet.username)
        
    print(str(like_count) + " total likes.")
    print(str(quote_count) + " total quote tweets.")
    print(str(retweet_count) + " total retweets.")
    print(str(view_count) + " total views.")

    like_acc.append(like_count)
    quote_acc.append(quote_count)
    retweet_acc.append(retweet_count)
    views_acc.append(view_count)

    retweet_users.append(retweeters)

    quotes_ids.append(quoted_ids)
    quotes_texts.append(quote)
#%%
eng_df = pd.DataFrame({"account_name" : usernames,
                       "like_count" : like_acc,
                       "retweet_count" : retweet_acc,
                       "quote_tweet_count": quote_acc,
                       "view_count": views_acc,
                       "quote_tweet_texts": quotes_texts,
                       "quote_tweet_ids": quotes_ids,
                       "retweeter_users": retweet_users})
eng_df

from pathlib import Path
filepath = Path("/Users/akjyang/Desktop/BCFG/Scripts/twitter_engagements.csv")
filepath.parent.mkdir(parents=True, exist_ok=True)  
eng_df.to_csv(filepath, index = False)
