import requests
import time
from datetime import datetime
import json
import pandas as pd
import sqlite3

# change path when running in docker
DBPath = "/app/data/data.db"
#DBPath = "data.db"
RefreshInterval = 3600

def getKeyChain():
    with open("keys.json", "r") as jsonfile:
        keyChain = json.load(jsonfile)
    return keyChain

def getPersonalAcessToken(credentials):
    authUrl = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': credentials['client_id'],
        'client_secret': credentials['client_secret'],
        'refresh_token': credentials['refresh_token'],
        'grant_type': 'refresh_token'
    }
    try:
        response = requests.post(authUrl, data=payload).json()
        return response.get('access_token')
    except:
        return None
    
def getPersonalStats(accessToken):
    # Get all the stats of this year
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {accessToken}'}
    
    now = datetime.now()
    epoch_start_year = int(time.mktime(datetime(now.year, 1, 1).timetuple()))

    dataset = []
    page = 1
    while True:
        param = {'per_page': 200, 'after': epoch_start_year, 'page': page}
        response = requests.get(url, headers=headers, params=param).json()
        if not response or isinstance(response, dict): break
        dataset.extend(response)
        page += 1

    df = pd.DataFrame(columns=["ActivityId", "Date", "Distance"])

    for act in dataset:
        if act.get('type') == 'Run' or act.get('sport_type') == 'Run':
            df.loc[len(df)] = [act['id'], act['start_date_local'], round(act['distance']/1000, 3)]

    return df
 
def getDataPersonForThisYear(token, name):
    dfPerson = getPersonalStats(token)
    dfPerson["Name"] = name
    return dfPerson

def init_db():
    conn = sqlite3.connect(DBPath)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        ActivityId INTEGER PRIMARY KEY,
        Date TEXT,
        Distance REAL,
        Name TEXT
    )
    """)

    conn.commit()
    return conn

def loadExistingData(conn):
    return pd.read_sql("SELECT ActivityId FROM activities", conn)

def saveNewActivities(conn, df_new):
    if df_new.empty:
        return

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT OR IGNORE INTO activities (ActivityId, Date, Distance, Name)
        VALUES (?, ?, ?, ?)
    """, df_new.values.tolist())

    conn.commit()

def main():
    conn = init_db()

    existing_df = loadExistingData(conn)
    existing_ids = set(existing_df["ActivityId"])

    chain, activitysAdded = getKeyChain(), 0

    for id in range(len(chain)):
        token = getPersonalAcessToken(chain[id])
        dfPerson = getDataPersonForThisYear(token, chain[id]['name'])

        newActivitys = dfPerson[~dfPerson["ActivityId"].isin(existing_ids)]

        activitysAdded += len(newActivitys)

        saveNewActivities(conn, newActivitys)

        # update set zodat dubbele in dezelfde run ook niet dubbel gaan
        existing_ids.update(newActivitys["ActivityId"])

    conn.close()

    print(activitysAdded, "Activities added to the DB")

if __name__ == "__main__":
    while True:
        startTime = datetime.now()
        main()
        endTime = datetime.now()
        time.sleep(RefreshInterval - int(round((endTime -  startTime).total_seconds(), 0)))
