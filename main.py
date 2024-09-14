from stravalib.client import Client
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

strava_client_id = os.getenv('strava_client_id')
strava_client_secret = os.getenv('strava_client_secret')

# Open the following link
print(
    f'http://www.strava.com/oauth/authorize?client_id={strava_client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:write')
# And obtain
# http://localhost/exchange_token?state=&code={strava_code}&scope=read,activity:write

strava_code = None

# Add the access token printet in the first run, so you don't have to autherize and copy the strava_code again.
access_token = None

if not access_token:
    token_dict = Client().exchange_code_for_token(client_id=strava_client_id,
                                                  client_secret=strava_client_secret,
                                                  code=strava_code)
    access_token = token_dict["access_token"]
    print(f'{access_token = }')

client = Client(access_token=access_token)

# The .csv-file exported from Hevy
df = pd.read_csv('workout_data.csv')


def set_type_str(data):
    if data == 'warmup':
        return '[Warm-up]'
    elif data == 'dropset':
        return '[Drop]'
    elif data == 'failure':
        return '[Failure]'
    return ''


title = ''
for index, row in df.iterrows():
    if title != row.title:
        if index > 1:
            client.create_activity(name=title,
                                   start_date_local=start,
                                   elapsed_time=duration,
                                   activity_type='WeightTraining',
                                   description=body)
            print(f'{title = }')
            print(f'{duration = }')
            print(body)
            print('\n'*5)

        title = row.title
        start = datetime.strptime(row.start_time, '%d %b %Y, %H:%M')
        end = datetime.strptime(row.end_time, '%d %b %Y, %H:%M')
        duration = int((end - start).total_seconds())
        body = 'Logged with Hevy\n'

    if row.set_index == 0:
        body += f'\n{row.exercise_title}\n'

    if not pd.isna(row.weight_kg):  # Weight
        set_type = set_type_str(row.set_type)
        body += f'Set {row.set_index + 1}: {int(row.weight_kg)} kg x {int(row.reps)} {set_type}\n'
    elif not pd.isna(row.reps):  # Bodyweight
        set_type = set_type_str(row.set_type)
        body += f'Set {row.set_index + 1}: {int(row.reps)} {set_type}\n'
    elif not pd.isna(row.distance_km):  # Distance
        duration_min = int(row.duration_seconds / 60)
        remain_seconds = row.duration_seconds % 60
        time_stamp = f'{int(duration_min)}min'
        if remain_seconds > 0:
            time_stamp += f'{remain_seconds}s'
        body += f'Set {row.set_index + 1}: {row.distance_km}km - {time_stamp}\n'
    else:  # Time only
        duration_min = int(row.duration_seconds / 60)
        remain_seconds = row.duration_seconds % 60
        time_stamp = f'{int(duration_min)}min'
        if remain_seconds > 0:
            time_stamp += f' {int(remain_seconds)}s'
        body += f'Set {row.set_index + 1}: {time_stamp}\n'
