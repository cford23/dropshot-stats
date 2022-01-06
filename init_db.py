import os
import pandas as pd
import sqlite3

def to_date(date):
    # returns string in YYYYMMDD format for sql queries
    # input: '2/11/2021'    output: '20210211'
    date = date.split('/')
    month = date[0]
    day = date[1]
    year = date[2]
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    if len(year) == 2:
        year = '20' + year
    return year + month + day

conn = sqlite3.connect('database.db')

with open('schema.sql') as f:
    conn.executescript(f.read())

conn.create_function("to_date", 1, to_date)
cur = conn.cursor()

matchColumns = ['Match ID', 'Season Match Number', 'Team 1 ID', 'Team 1', 'Team 2 ID', 'Team 2', 'Event', 'Date', 'Team 1 Score', 'Team 2 Score', 'Winner', 'Match VOD']
mapColumns = ['Match ID', 'Map ID', 'Team 1 ID', 'Team 1', 'Team 2 ID', 'Team 2', 'Event', 'Mode', 'Map', 'Map Number', 'Team 1 Score', 'Team 2 Score', 'Map Winner', 'Map VOD']
playerColumns = ['Match ID', 'Map ID', 'Event', 'Team ID', 'Team', 'Opponent ID', 'Opponent', 'Mode', 'Map', 'Player ID', 'Player', 'Kills', 'Deaths', 'K/D', 'Engagements', 'Difference', 'Map Result']

# Get list of folders in data (should be in the form year - game)
files = os.listdir('data/')
folders = []
for f in files:
    if os.path.isdir('data/' + f):
        folders.append(f)

for folder in folders:
    path = 'data/' + folder + '/'
    matches = pd.read_csv(path + 'matches.csv')
    maps = pd.read_csv(path + 'maps.csv')
    players = pd.read_csv(path + 'players.csv')

    # Inserting match data
    matches = matches.drop(columns=[col for col in matches if col not in matchColumns])
    cur.executemany("INSERT INTO Matches ([Match ID], [Season Match Number], [Team 1 ID], [Team 1], [Team 2 ID], [Team 2], Event, Date, [Team 1 Score], [Team 2 Score], Winner, [Match VOD]) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    matches.values.tolist())

    # Inserting map data
    maps = maps.drop(columns=[col for col in maps if col not in mapColumns])
    cmd = """
        INSERT INTO Maps ([Match ID], [Map ID], [Team 1 ID], [Team 1], [Team 2 ID], [Team 2], Event, Mode, Map, [Map Number], [Team 1 Score], [Team 2 Score], [Map Winner], [Map VOD])
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.executemany(cmd, maps.values.tolist())

    # Inserting player data
    players = players.drop(columns=[col for col in players if col not in playerColumns])
    cmd = """
        INSERT INTO Players ([Match ID], [Map ID], Event, [Team ID], Team, [Opponent ID], Opponent, Mode, Map, [Player ID], Player, Kills, Deaths, KD, Engagements, Difference, [Map Result])
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.executemany(cmd, players.values.tolist())


# Inserting player info data
playerInfos = pd.read_csv('data/playerinfo.csv')
cmd = """
    INSERT INTO PlayerInfo ([Player ID], Username, [First Name], [Last Name], [Last Recorded Team], [Past Teams], [Date of Birth], [Country of Birth], [Twitter Username], [Instagram Username], [Reddit Username], [Twitch Channel], [YouTube Channel], [Past Usernames], [Twitter Followers], [Instagram Followers], [Twitch Followers], [YouTube Subscribers])
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
cur.executemany(cmd, playerInfos.values.tolist())

# Inserting team info data
teamInfos = pd.read_csv('data/teaminfo.csv')
cmd = """
    INSERT INTO TeamInfo ([Team ID], Name, [Twitter Username], [Instagram Username], [Twitch Channel], [YouTube Channel], [Past Team Names], [Twitter Followers], [Instagram Followers], [Twitch Followers], [YouTube Subscribers])
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
cur.executemany(cmd, teamInfos.values.tolist())

# Add Season column to Matches based on match date
cur.execute("ALTER TABLE Matches ADD Season VARCHAR(25)")
cmd = """
    UPDATE Matches
    SET Season = CASE
        WHEN to_date(Date) BETWEEN '20171208' AND '20180819' THEN '2018 - WW2'
        WHEN to_date(Date) BETWEEN '20181206' AND '20190818' THEN '2019 - Black Ops 4'
        WHEN to_date(Date) BETWEEN '20200124' AND '20200830' THEN '2020 - Modern Warfare'
        WHEN to_date(Date) BETWEEN '20210211' AND '20210822' THEN '2021 - Cold War'
    END;
"""
cur.execute(cmd)

# Add Season column to Maps based on match date in Matches
cur.execute("ALTER TABLE Maps ADD Season VARCHAR(25)")
cmd = """
    UPDATE Maps
    SET Season = (SELECT Season
                  FROM Matches
                  WHERE Matches.[Match ID] = Maps.[Match ID])
"""
cur.execute(cmd)

# Add Season column to Players based on match date in Matches
cur.execute("ALTER TABLE Players ADD Season VARCHAR(25)")
cmd = """
    UPDATE Players
    SET Season = (SELECT Season
                  FROM Matches
                  WHERE Matches.[Match ID] = Players.[Match ID])
"""
cur.execute(cmd)

conn.commit()
conn.close()