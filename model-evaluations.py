#%% imports and downloads
import numpy as np
import pandas as pd
import re

# gender-guesser for gender guessing
import gender_guesser.detector as gender

# raceBERT for race guessing
from racebert import RaceBERT

# spacy for person identification
import spacy
nlp = spacy.load('en_core_web_sm')
#%%
df = pd.read_csv('/content/gender_person_checked.csv')
df.drop(['id', 'id_str'], axis = 1, inplace = True)

df_race = pd.read_csv('/content/race_coded.csv')

df_300 = df[:len(df_race)]
df_300['actual_race'] = df_race['race_coding\n(white, api, black, hispanic)']
#%% cleaning names
regex = re.compile("^\w*\S")

def clean_name(twitter_df):
  for i in range(len(twitter_df)):
    # if name begins with 'Dr.' or 'Professor', actual name begins from the second word
    if regex.findall(twitter_df['name'][i])[0] == 'Dr.' or regex.findall(twitter_df['name'][i])[0] == 'Professor':
      twitter_df.at[i, 'cleaned_name'] = " ".join(twitter_df.loc[i, 'name'].split(" ")[1:])
    else:
      twitter_df.at[i, 'cleaned_name'] = twitter_df['name'][i]
    # make sure that the first letter of each name is capitalized (for case sensitivity)
    twitter_df.at[i, 'cleaned_name'] = ' '.join([name.capitalize() for name in twitter_df.at[i, 'cleaned_name'].split(' ')])
    
clean_name(df_300)
#%% identify people using spacy
def spacy_person(x):
  for i in range(0, len(x)):
    doc = nlp(x.at[i, 'cleaned_name'] + ' was born in London')
    if 'PERSON' in [e.label_ for e in doc.ents]:
      x.at[i, 'person_guess'] = True
    else:
      x.at[i, 'person_guess'] = False
      
spacy_person(df_300)
#%% filter faulty twitter names
def first_last(x):
  for i in range(len(x)):
    if x.at[i, 'person_guess'] == True:
      x.at[i, 'first_name'] = x['cleaned_name'][i].split(" ")[0]
      x.at[i, 'last_name'] = x['cleaned_name'][i].split(" ")[-1]
    else:
      x.at[i, 'first_name'] = 'NA'
      x.at[i, 'last_name'] = 'NA'

first_last(df_300)
#%% run gender-guesser, merge "mostly" results
d = gender.Detector(case_sensitive = True)
def gender_guesser(x):
  for i in range(len(x)):
    if x.at[i, 'person_guess'] == True:
      x.at[i, 'gender_guess'] = d.get_gender(regex.findall(x['cleaned_name'][i])[0])
      # changing output of 'mostly_female' and 'mostly_male' to just 'female' and 'male'
      if x.at[i, 'gender_guess'].split("_")[0] == 'mostly':
        x.at[i, 'gender_guess'] = x.at[i, 'gender_guess'].split("_")[1]
        
gender_guesser(df_300)
#%% raceBERT
model = RaceBERT()
def race_guesser(x):
  for i in range(len(x)):
    if x.at[i, 'person_guess'] == True:
      x.at[i, 'race_guess'] = model.predict_race(x['cleaned_name'][i])[0]['label']
      # adjusting 'nh_white' and 'nh_black' to just 'white' and 'black' as the nh part is not manually coded for
      if x.at[i, 'race_guess'] == 'nh_white':
        x.at[i, 'race_guess'] = 'white'
      if x.at[i, 'race_guess'] == 'nh_black':
        x.at[i, 'race_guess'] = 'black'

race_guesser(df_300)
#%% metrics (300 accounts)
print("accuracy for spacy " + str(sum((df_300['actual_person'] == df_300['person_guess'])) / len(df_300)))
#0.8733

df_300_human = df_300[df_300['person_guess'] == True]
print("accuracy for gender-guesser " + str(sum(df_300_human['actual_gender'] == df_300_human['gender_guess']) / len(df_300_human)))
#0.8502

print("accuracy for raceBERT " + str(sum(df_300_human['actual_race'] == df_300_human['race_guess']) / len(df_300_human)))
#0.7530
#%% metrics (all 900 accounts)
clean_name(df)
spacy_person(df)
gender_guesser(df)
race_guesser(df)

print("accuracy for spacy " + str(sum((df['actual_person'] == df['person_guess'])) / len(df)))
#0.8744

df_human = df[df['person_guess'] == True]
print("accuracy for gender-guesser " + str(sum(df_human['actual_gender'] == df_human['gender_guess']) / len(df_human)))
#0.8782
