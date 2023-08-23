from TwitterAuth import TwitterAuth
from logDM import get_logger
import tweepy
import pandas as pd
import numpy as np
import random
import time

## initialize auth class

auth = TwitterAuth()

## anticipating removal of authentication

def modify_auth_column(df, start_index=153):
    auth_values = ['AUTH6', 'AUTH7']
    end_index = len(df)
    
    for i in range(start_index, end_index):
        df.loc[i, 'auth'] = auth_values[(i - start_index) % len(auth_values)]

    return df



## read in spreadsheet corresponding to user breakdown
## required columns: 'id_str', 'Following', 'perc_verified', 'perc_org', 'perc_us', 'perc_minority', 'link', 'treatment'

df = pd.read_csv('data/03-pilot/03-pilot_users_day0.csv')

# Rename the column to 'following_count'
df.rename(columns={'following_count_04a-data-pilot3-day0': 'following_count'}, inplace=True)

df=df[df['following_count'] != 0]

# Modify the DataFrame
df = modify_auth_column(df)

def generate_message(user_data):
    
    ## store user breakdowns
    total_followers = user_data["following_count"]
    verified_percentage = (user_data['perc_verified']) * 100
    organization_percentage = (user_data['perc_org']) * 100
    us_based_percentage = (user_data['perc_us']) * 100
    racial_minority_percentage = (user_data['perc_minority']) * 100
    link = user_data['link']
    user = user_data['screen_name']
    
    ## modify message for control v1
    
    if user_data["treatment"] == "control":
        percentage_strings = [
            f"{verified_percentage:.0f}% are verified",
            f"{organization_percentage:.0f}% are organizations",
            f"{us_based_percentage:.0f}% are U.S.-based"
        ]
        random.shuffle(percentage_strings)
        percentage_info = "\n".join(percentage_strings)
        closing_string = f"Check out this Wharton-curated list of diverse accounts! 👇\n{link}"
        
    ## modify message for treat v1
    elif user_data["treatment"] == "treat":
        percentage_strings = [
            f"{verified_percentage:.0f}% are verified",
            f"{organization_percentage:.0f}% are organizations",
            f"{us_based_percentage:.0f}% are U.S.-based"
        ]
        selected_strings = random.sample(percentage_strings, 2)
        percentage_info = f"{racial_minority_percentage:.0f}% are racial minorities\n" + "\n".join(selected_strings)
        closing_string = f"Check out this Wharton-curated list of diverse accounts! 👇\n{link}"
        
      
    else:
        raise ValueError("Invalid treatment value")

    message = f"""@{user} Today we’re sending complimentary reports to Twitter users. Here’s info on the ~{total_followers} accounts you follow:

{percentage_info}

{closing_string}"""
    return message, percentage_info

##############
## SEND DMs ##
##############

log_file='data/logs/02-interaction.log'
l=get_logger(log_file)


for i, row in df[153::].iterrows():
    #print(row)
    # retrieve auth, user_id
    auth_name = row['auth']
    user_id = row['id_str']
    print(i, row['screen_name'], auth_name)
    
    # assign API to auth in row
    auth_details = auth.get_auth_profile(profile=row['auth'])
    api = tweepy.Client(**auth_details, wait_on_rate_limit=True)
    # generate message
    user_message = generate_message(row)[0]
    selected_string = generate_message(row)[1]
    df.at[i, 'message'] = selected_string
    ## POST MESSAGE
    try:
        api.create_tweet(text = user_message, reply_settings='mentionedUsers')
        l.info("Auth name: %s, index: %s, screen_name: %s", auth_name, i, row['screen_name'])
    except Exception as e:
        print(e)
        print('ERROR --------------- ERROR')
        df.at[i, 'fail'] = True
        time.sleep(30)
        continue
    df.to_csv('data/03-pilot/03-pilot_users_day1.csv', index=False)
    
    if auth_name == 'AUTH7':
        sleep_time = random.uniform(30, 50)
        print(f"Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

############################



# Create a list of profile names
auth_profiles = [f'AUTH{i}' for i in range(1, 16)]

# Create a DataFrame with the profile names
auth_df = pd.DataFrame(auth_profiles, columns=['profile_name'])

for index, row in auth_df.iterrows():
    profile_name = row['profile_name']
    
    # Use the profile_name in the script
    auth_details = auth.get_auth_profile(profile=profile_name)
    api = tweepy.Client(**auth_details, wait_on_rate_limit=True)
    api.create_tweet(text = '@jacervantez hey', reply_settings='mentionedUsers')


auth_details = auth.get_auth_profile(profile='AUTH15')
api = tweepy.Client(**auth_details, wait_on_rate_limit=True)
api.get_me()
api.create_tweet(text = '@jacervantez hey', reply_settings='mentionedUsers')



