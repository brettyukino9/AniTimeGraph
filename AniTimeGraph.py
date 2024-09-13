import csv
import pandas as pd
import numpy as np
import sys 

if(len(sys.argv) != 2):
    print("Usage: python AniTimeGraph.py <username>")
    sys.exit(1)
username = sys.argv[1]
df = pd.read_csv(f'Activity Files/{username}_activities.csv')

# get the days watched for this user from the anilist api


anime_activities = df[df['Type'] == 'ANIME_LIST']

def process_string(x):
    if pd.isna(x): # if the value is Nan (completed) return 1
        return 1
    if '-' in x:
        a, b = map(int, x.split('-'))
        return b - a + 1
    else:
        return 1
    

  
# Make a new column called "Episodes Watched"; if the progress is in the form number - number, then it will take the difference
# between the two numbers and add 1 to it. If the progress is in the form of a single number, then it will just take that number.
anime_activities['Episodes Watched'] = anime_activities['Progress'].apply(process_string)

anime_activities['Time Watched'] = anime_activities['Episodes Watched'] * anime_activities['Episode Length']

# 1:38:06 wednesday 9/11/2024 = 786180712

# find what second corresponds to 0:00:00 on wednesday
# 1726076286 - 5886 = 1726070400
# 604800 every week
week_time = 604800
wednesday_time = 1726076286
# find the min time created
min_time = anime_activities['Created At'].min()

def find_first_threshold():
    step = 0
    while(True):
        newtime = wednesday_time - step * week_time
        if newtime < min_time:
            return wednesday_time - (step -1) * week_time
        else:
            step += 1

first_threshold = find_first_threshold()

def find_week_number(x):
    return ((x - first_threshold) // week_time) + 2

anime_activities['Week Number'] = anime_activities['Created At'].apply(find_week_number)


# Create a running count of time watched by summing all previous values of time watched but start at the bottom
# and go up
anime_activities = anime_activities.sort_values('Created At', ascending=True)
anime_activities['Cumulative Time Watched'] = anime_activities['Time Watched'].cumsum()
anime_activities['Cumulative Days Watched'] = anime_activities['Cumulative Time Watched'] / 60  / 24


anime_activities['Timestamp'] = pd.to_datetime(anime_activities['Created At'], unit='s')
print(anime_activities)

anime_activities['Year'] = anime_activities['Timestamp'].dt.year
anime_activities['Month'] = anime_activities['Timestamp'].dt.month


import matplotlib.pyplot as plt

# plot the cumulative days watched on y and week number on x
plt.plot(anime_activities['Timestamp'], anime_activities['Cumulative Days Watched'])
plt.title('Cumulative Days Watched')
plt.xlabel('Timestamp')
plt.ylabel('Days Watched')
plt.show()

# figure out how much time watched per week
weekly_time = anime_activities.groupby('Week Number')['Time Watched'].sum()

# figure out how many episodes watched per week by doing weekly_time / 24
weekly_episodes = weekly_time / 24

print(weekly_episodes)

# make a histogram for episodes watched per week
plt.hist(weekly_episodes, bins=20)
plt.title('Episodes Watched per Week')
plt.xlabel('Episodes')
plt.ylabel('Frequency')
plt.show()

# show me the most recent 5 weeks
print(weekly_episodes.tail(5))


# add a new field that shows the popularity of the last 50 activities with a unique media title
anime_activities['Popularity'] = anime_activities['Popularity'].fillna(0)
anime_activities['Popularity'] = anime_activities['Popularity'].astype(int)
anime_activities['Popularity'] = anime_activities['Popularity'].rolling(50).median()

# graph the popularity
plt.plot(anime_activities['Timestamp'], anime_activities['Popularity'])
plt.title('Popularity of Last 50 Activities')
plt.xlabel('Timestamp')
plt.ylabel('Popularity')
plt.show()


# do the same with average score
anime_activities['Average Score'] = anime_activities['Average Score'].fillna(0)
anime_activities['Average Score'] = anime_activities['Average Score'].rolling(50).median()
print(anime_activities)

# graph the score
plt.plot(anime_activities['Timestamp'], anime_activities['Average Score'])
plt.title('Average Score of Last 50 Activities')
plt.xlabel('Timestamp')
plt.ylabel('Average Score')
plt.show()


# bar graph of days watched per year
days_per_year = anime_activities.groupby('Year')['Time Watched'].sum() / 24 / 60
print(days_per_year)
plt.bar(days_per_year.index, days_per_year)
plt.title('Days Watched per Year')
plt.xlabel('Year')
plt.ylabel('Days Watched')
plt.show()

# bar graph of days watched per month
days_per_month = anime_activities.groupby('Month')['Time Watched'].sum() / 24 / 60
print(days_per_month)
plt.bar(days_per_month.index, days_per_month)
plt.title('Days Watched per Month')
plt.xlabel('Month')
plt.ylabel('Days Watched')
plt.show()
