import numpy as np
import pandas as pd
import time
import math
import tweepy

#%% test with one api key
Client = tweepy.Client(consumer_key = consumer_key_lst[0],
          consumer_secret = consumer_secret_lst[0],
          access_token = access_token_lst[0],
          access_token_secret = access_token_secret_lst[0],
          wait_on_rate_limit = False
      )

test_users_df = pd.read_csv("/content/test_users.csv")

test_users = test_users_df["screen_name"]
short_test = test_users[:30]
#%%
response_list = []
protected_user_index = []
user_index = 0
key_index = 0

while key_index < len(consumer_key_lst):

  # finish running when all of the users have been iterated through
  # also prevent infinite exceptions (errors) from the "user_index" exceeding length of user dataframe
  if user_index == len(short_test):
    break
  
  try:

    num_pages = 0

    while num_pages < 15:
      client = tweepy.Client(
          consumer_key = consumer_key_lst[key_index],
          consumer_secret = consumer_secret_lst[key_index],
          access_token = access_token_lst[key_index],
          access_token_secret = access_token_secret_lst[key_index],
          wait_on_rate_limit = False
      )

      key_index += 1
      # if we have iterated through all the keys, go back to the first, trigger the except (and timer)
      if key_index == len(consumer_key_lst):
        key_index = 0

      for j in range(user_index, len(short_test)):
        user = client.get_user(username = short_test[j], user_auth = True, user_fields = ['verified', 'public_metrics', 'protected'])

        # if user is protected, go to next user, else ignore
        if user.data["protected"] == True:
          protected_user_index.append(j)
          continue

        num_pages += math.ceil(user.data["public_metrics"]["following_count"] / 1000)
        # if rate limit is met, break "j" for loop and go to next key (while loop)
        if num_pages > 15:
          break

        # list to save the followings of each user, will later be aggregated to "response_list"
        per_user_response_list = []
        
        for response in tweepy.Paginator(client.get_users_following, 
                                      user.data['id'], 
                                      user_auth=True, 
                                      user_fields=['verified', 'public_metrics', 'created_at'],
                                      max_results=1000, 
                                      limit=math.ceil(user.data.public_metrics['following_count']/1000)):
          per_user_response_list.append(response.data)
        
        # the for loop for user_index has completed, add one to user_index
        user_index += 1

        response_list.append([element for sublist in per_user_response_list for element in sublist])

  except: 

    # save the time for when rate limit should be replenished
    timer = time.time() + 60*15

    # continuously check for whether timer has been met, once met break while
    while True:
      if time.time() > timer:
          break
    
    # once while loop is broken start entire loop again, from the first key
    continue
#%%
print([len(response_list[i]) for i in range(0, len(response_list))])
print(len(response_list))
