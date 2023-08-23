import re
# gender-guesser for gender guessing
import gender_guesser.detector as gender
# raceBERT for race guessing
from racebert import RaceBERT
# spacy for person identification
import spacy
import pandas as pd
import tweepy
import math
import time
from configparser import ConfigParser
from geopy import geocoders

# locations API

gn = geocoders.TomTom(api_key='',
                      timeout=5)

# API Keys 

config = ConfigParser()
config.read('config.ini')
CONSUMER_KEY=config.get('AUTH', 'CONSUMER_KEY')
CONSUMER_SECRET=config.get('AUTH', 'CONSUMER_SECRET')
ACCESS_TOKEN=config.get('AUTH', 'ACCESS_TOKEN')
ACCESS_SECRET=config.get('AUTH', 'ACCESS_SECRET')

client = tweepy.Client(
   consumer_key=CONSUMER_KEY, 
   consumer_secret=CONSUMER_SECRET,
   access_token=ACCESS_TOKEN, 
   access_token_secret=ACCESS_SECRET,
   wait_on_rate_limit=True
)

# race and gender models

def r_model():
    return RaceBERT().predict_race
model = r_model()
nlp = spacy.load('en_core_web_sm')

def g_model():
    return gender.Detector(case_sensitive=True)
d = g_model()


# name cleaning
regex = re.compile("^\w*\S")

def clean_twitter_name(x):
  if regex.findall(x)[0] == 'Dr.' or regex.findall(x)[0] == 'Professor':
    clean_x = " ".join(x.split(" ")[1:])
  else:
    clean_x = x
  clean_x = " ".join(name.capitalize() for name in clean_x.split(" "))
  return clean_x

# person identifier

def spacy_person(x):
  doc = nlp(x + ' was born in London')
  if 'PERSON' in [e.label_ for e in doc.ents]:
    return 1
  else:
    return 0

# race guesser

minority_races = ['api', 'hispanic', 'black', 'aian']

def race_guesser(x):
  race = model(x)[0]['label']
  if race == 'nh_white':
    race = 'white'
  if race == 'nh_black':
    race = 'black'

  if race in minority_races:
    return 1
  else:
    return 0

# gender
re.search('([^\s]+)', string='Michelle Brantley')[1]
def gender_guesser(x):
  gender = d.get_gender(x)
  if gender.split("_")[0] == 'mostly':
    gender = gender.split("_")[1]
  if gender == "female":
    return 1
  else:
    return 0

# locations

locations = pd.read_csv('locations.csv', index_col=0)

def locations_fun(user):
    if locations['location'].eq(user).any():
        mask = locations['location'].eq(user)
        return locations.loc[mask]['bool'].iloc[0]
    else:
        if user is None:
            return False
        else:
            user = user.replace('/', ',')
            if user[0]==' ':
                user=user[1:]
                location = gn.geocode(user)
                time.sleep(7/40)
    
                if location is None:
                    locations.loc[len(locations.index)] = [user, False]
                    return False
                try:
                    if location.raw['address']['country']=='United States':
                        locations.loc[len(locations.index)] = [user, True]
                        return True
                except KeyError:
                    locations.loc[len(locations.index)] = [user, False]
                    return False
                else:
                    locations.loc[len(locations.index)] = [user, False]
                    return False

# followings


def followings(user_text, i):
    try:
        user = client.get_user(username=user_text, user_auth=True, user_fields=['verified', 'public_metrics', 'protected', 'location'])
        df = pd.DataFrame({'Name': user.data['name']}, index = [i])
    except TypeError:
        return False
    verified = 0
    response_list = []
    follow_count = []
    us_based = 0
    i = 0
    if user.data.protected:
            return False
    for response in tweepy.Paginator(client.get_users_following, 
                                     user.data['id'], 
                                     user_auth=True, 
                                     user_fields=['verified', 'public_metrics', 'location'],
                                     max_results=1000, 
                                     limit=math.ceil(user.data.public_metrics['following_count']/1000)):
        response_list.append(response.data)
        for j in range(len(response_list[i])):
            follow_count.append(response_list[i][j])
            if response_list[i][j]['verified']:
                verified += 1
            if locations_fun(response_list[i][j]['location']):
                us_based += 1
            
        i += 1
    df['minority'] = race_guesser(user.data['name'])
    df['woman'] = gender_guesser(user.data['name'].split(" ")[0])
    df['verified'] = user.data['verified']
    df['us_based'] = locations_fun(user.data['location'])
    if not len(follow_count):
        df['Following'] = 0
        df['perc_verified'] = 0
        df['perc_us'] = 0

    else:
        df['Following'] = len(follow_count)
        df['perc_verified'] = verified/len(follow_count)
        df['perc_us'] = us_based/len(follow_count)

    return(df, follow_count, user.data)

def breakdown(df, followings):
    minority_prop = []
    female_prop = []
    human_count_lst = []
    minority_count = 0
    female_count = 0
    human_count = 0
    org_count = 0
    org_lst = []
    follow_count = followings
    
    for i in range(len(followings)):
      try:
        name = clean_twitter_name(follow_count[i].name)

        if spacy_person(name) == 1:
          human_count += 1
          minority_count += race_guesser(name)
          female_count += gender_guesser(name.split(" ")[0])

      except:
        continue
    if not len(follow_count):
        df['perc_org'] = 0
        df['perc_minority'] = 0
        df['perc_woman'] = 0
        df['\"Human\" Accounts'] = 0
        
    else:
        org_count = len(follow_count) - human_count
        org_lst.append(org_count / len(follow_count))
        human_count_lst.append(human_count)
        minority_prop.append(minority_count / human_count)
        female_prop.append(female_count / human_count)
        df['\"Human\" Accounts'] = human_count_lst
        df['perc_minority'] = minority_prop
        df['perc_woman'] = female_prop
        df['perc_org'] = org_lst
    return(df)
 


df = pd.read_excel('pilot_results2.xlsx')
df_new = pd.DataFrame()

for i in range(len(df)):
    print(i)
    print(df['screen_name'][i])
    try:
        followings_fun = followings(df['screen_name'][i], i)
        if not followings_fun:
            pass
        else:
            df_new = pd.concat([df_new, breakdown(followings_fun[0], followings_fun[1])])
    except tweepy.TweepyException:
        pass

df = pd.concat((df, df_new), axis = 1)
df.to_excel('pilot_results.xlsx', index=False, header=True, float_format='%.20f')
