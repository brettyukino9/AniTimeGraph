# Do an API call to get all of a users activities
# Filter to only get the watched and completed activities
# Count the episodes per week
# Plot

import requests
import time
import json
import csv
import sys
url = 'https://graphql.anilist.co'

def get_user_id(username):
    queryUserId = '''
    query($name:String){User(name:$name){id}}
    '''

    # Define our query variables and values that will be used in the query request
    variablesUserId = {
        'name': username
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request to get the user id of the username
    response = requests.post(url, json={'query': queryUserId, 'variables': variablesUserId}).json()
    global_user_id = response['data']['User']['id']
    return global_user_id

def get_user_activities(user_id):
    activities = []
    activityQuery = '''
    query ($userId: Int, $page: Int, $perPage: Int) {
    Page(page: $page, perPage: $perPage) {
        activities(userId: $userId, sort: ID_DESC) {
        ... on ListActivity {
            id
            type
            status
            progress
            createdAt
            media {
            title {
                romaji
            }
            duration
            popularity
            averageScore
            }
        }
        }
    }
    }
    '''
    page = 0


    while(True):
        page = page + 1
        variables = {
            'userId': user_id,
            'page': page,
            'perPage': 50
        }
        
        response = requests.post(url, json={'query': activityQuery, 'variables': variables})
        print(response.json())
        response_activities = response.json()['data']['Page']['activities']
        if not response_activities:
            break
        activities.extend(response_activities)
        time.sleep(4)
    return activities

# Usage
if(len(sys.argv) != 2):
    print("Usage: python GetAllActivities.py <username>")
    sys.exit(1)
username = sys.argv[1]
user_id = get_user_id(username)
print(user_id)
activities = get_user_activities(user_id)
# print(json.dumps(activities, indent=4))
# print(activities)

# Save activities to a CSV file
activity_file_name = f"Activity Files/"+username+'_activities.csv'.format(username=username)
with open(activity_file_name, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write the header
    writer.writerow(['Activity ID', 'Type', 'Status', 'Progress', 'Created At', 'Media Title', 'Episode Length', 'Popularity', 'Average Score'])
    
    # Write activity rows
    for activity in activities:
        print(activity)
        if not activity.get('id'):
            continue
        writer.writerow([activity.get('id', 'N/A'), activity.get('type', 'N/A'), activity.get('status', 'N/A'), activity.get('progress', 'N/A'), activity.get('createdAt', 'N/A'), activity['media']['title'].get('romaji', 'N/A'), activity['media'].get('duration', 'N/A'), activity['media'].get('popularity', 'N/A'), activity['media'].get('averageScore', 'N/A')])
print("Activities saved")