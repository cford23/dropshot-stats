from datetime import date, datetime
import json
import numpy as np
import pandas as pd
import sqlite3
import tweepy

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

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.create_function("to_date", 1, to_date)
    return conn

def get_seasons():
    conn = get_db_connection()
    cur = conn.cursor()
    seasonList = []
    seasons = cur.execute("SELECT Season FROM Matches ORDER BY to_date(Date)").fetchall()
    conn.close()
    for season in seasons:
        if season[0] not in seasonList:
            seasonList.append(season[0])
    return seasonList

def get_teams():
    conn = get_db_connection()
    cur = conn.cursor()
    teams1, teams2 = [], []
    teams = cur.execute("SELECT DISTINCT [Team 1] FROM Matches").fetchall()
    for team in teams:
        teams1.append(team[0])
    teams = cur.execute("SELECT DISTINCT [Team 2] FROM Matches").fetchall()
    for team in teams:
        teams2.append(team[0])
    conn.close()
    
    teamList = list(pd.unique(teams1 + teams2))
    teamList.sort(key=lambda x: x.lower())

    return teamList

def get_events():
    conn = get_db_connection()
    cur = conn.cursor()
    eventList = []
    events = cur.execute("SELECT DISTINCT Event FROM Matches").fetchall()
    conn.close()
    for event in events:
        eventList.append(event[0])
    return eventList

def get_modes():
    conn = get_db_connection()
    cur = conn.cursor()
    modeList = []
    modes = cur.execute("SELECT DISTINCT Mode FROM Maps").fetchall()
    conn.close()
    for mode in modes:
        modeList.append(mode[0])
    return modeList

def get_mapList():
    conn = get_db_connection()
    cur = conn.cursor()
    mapList = []
    maps = cur.execute("SELECT DISTINCT Map FROM Maps WHERE Map IS NOT NULL ORDER BY Map").fetchall()
    conn.close()
    for m in maps:
        mapList.append(m[0])
    return mapList

def get_playerList():
    conn = get_db_connection()
    cur = conn.cursor()
    players = cur.execute("SELECT * FROM PlayerInfo ORDER BY Username COLLATE NOCASE ASC, [Last Name]").fetchall()
    conn.close()
    return players

def get_playerIDList():
    conn = get_db_connection()
    cur = conn.cursor()
    result = cur.execute("SELECT [Player ID], Username FROM PlayerInfo").fetchall()
    conn.close()
    playerIDs = {}
    for playerID in result:
        playerIDs[playerID['Player ID']] = playerID['Username']
    return playerIDs

def get_teamList():
    conn = get_db_connection()
    cur = conn.cursor()
    teams = cur.execute("SELECT * FROM TeamInfo ORDER BY Name COLLATE NOCASE ASC").fetchall()
    conn.close()
    return teams

def get_teamLastRecordedRoster():
    teamIDList = get_teamIDList()
    conn = get_db_connection()
    cur = conn.cursor()
    lastRecordedRosters = {}
    for teamID in teamIDList:
        cmd = """
            SELECT [Match ID]
            FROM Matches
            WHERE [Team 1 ID] = ?
                OR [Team 2 ID] = ?
            ORDER BY to_date(Date) DESC, [Season Match Number] DESC
            LIMIT 1
        """
        matchID = cur.execute(cmd, (teamID, teamID)).fetchone()[0]

        cmd = """
            SELECT Player
            FROM Players
            WHERE [Match ID] = ?
                AND [Team ID] = ?
            ORDER BY Player COLLATE NOCASE ASC
        """
        players = cur.execute(cmd, (matchID, teamID)).fetchall()
        playerList = []
        for player in players:
            if player[0] not in playerList:
                playerList.append(player[0])
        lastRecordedRosters[teamID] = playerList

    conn.close()
    return lastRecordedRosters

def get_teamIDList():
    conn = get_db_connection()
    cur = conn.cursor()
    result = cur.execute("SELECT [Team ID], Name FROM TeamInfo").fetchall()
    conn.close()
    teamIDs = {}
    for teamID in result:
        teamIDs[teamID['Team ID']] = teamID['Name']
    return teamIDs

def get_matches(seasons, team1, team2, event):
    if team1 == 'All':
        team1 = '%'
    if team2 == 'All':
        team2 = '%'
    if event == 'All':
        event = '%'

    conn = get_db_connection()
    cur = conn.cursor()
    if len(seasons) > 1:
        cmd = """
            SELECT *
            FROM Matches
            WHERE (([Team 1] LIKE ? AND [Team 2] LIKE ?) OR ([Team 1] LIKE ? AND [Team 2] LIKE ?))
                AND Season IN {}
                AND Event LIKE ?
            ORDER BY to_date(Date), [Season Match Number]
        """.format(tuple(seasons))
        matches = cur.execute(cmd, (team1, team2, team2, team1, event)).fetchall()
    elif len(seasons) == 1:
        cmd = """
            SELECT *
            FROM Matches
            WHERE (([Team 1] LIKE ? AND [Team 2] LIKE ?) OR ([Team 1] LIKE ? AND [Team 2] LIKE ?))
                AND Season = ?
                AND Event LIKE ?
            ORDER BY to_date(Date), [Season Match Number]
        """
        season = seasons[0]
        matches = cur.execute(cmd, (team1, team2, team2, team1, season, event)).fetchall()
    else:
        matches = ()
    conn.close()
    return matches

def get_maps(seasons, team1, team2, event, mode, mapPlayed):
    if team1 == 'All':
        team1 = '%'
    if team2 == 'All':
        team2 = '%'
    if event == 'All':
        event = '%'
    if mode == 'All':
        mode = '%'
    if mapPlayed == 'All':
        mapPlayed = '%'

    conn = get_db_connection()
    cur = conn.cursor()
    if len(seasons) > 1:
        cmd = """
            SELECT *
            FROM Maps
            WHERE (([Team 1] LIKE ? AND [Team 2] LIKE ?) OR ([Team 1] LIKE ? AND [Team 2] LIKE ?))
                AND Season IN {}
                AND Event LIKE ?
                AND Mode LIKE ?
                AND (Map LIKE ? OR Map IS NULL)
        """.format(tuple(seasons))
        maps = cur.execute(cmd, (team1, team2, team2, team1, event, mode, mapPlayed)).fetchall()
    elif len(seasons) == 1:
        cmd = """
            SELECT *
            FROM Maps
            WHERE (([Team 1] LIKE ? AND [Team 2] LIKE ?) OR ([Team 1] LIKE ? AND [Team 2] LIKE ?))
                AND Season = ?
                AND Event LIKE ?
                AND Mode LIKE ?
                AND (Map LIKE ? OR Map IS NULL)
        """
        season = seasons[0]
        maps = cur.execute(cmd, (team1, team2, team2, team1, season, event, mode, mapPlayed)).fetchall()
    else:
        maps = ()
    conn.close()
    return maps

def get_mapIDList(matchID):
    conn = get_db_connection()
    cur = conn.cursor()
    cmd = """
        SELECT [Map ID]
        FROM Maps
        WHERE [Match ID] = ?
        ORDER BY [Map Number]
    """
    mapIDs = cur.execute(cmd, (matchID,)).fetchall()
    conn.close()
    mapIDList = []
    for mapID in mapIDs:
        mapIDList.append(mapID[0])
    return mapIDList

def get_matchDetails(matchID):
    matchDetails = {}
    conn = get_db_connection()
    cur = conn.cursor()
    cmd = """
        SELECT Team, Player, CAST(SUM(Kills) AS FLOAT) / CAST(SUM(Deaths) AS FLOAT) KD,
            SUM(Kills) Kills, SUM(Deaths) Deaths,
            SUM(Engagements) Engagements, SUM(Difference) Difference
        FROM Players
        WHERE [Match ID] = ?
        GROUP BY Player, Team
        ORDER BY Team, Player COLLATE NOCASE ASC
    """ # or ORDER BY KD DESC
    match = cur.execute(cmd, (matchID,)).fetchall()
    matchDetails['Overall'] = match

    cmd = """
        SELECT [Team 1], [Team 2], [Team 1 Score], [Team 2 Score], [Match VOD]
        FROM Matches
        WHERE [Match ID] = ?
    """
    matchDetails['Team 1'], matchDetails['Team 2'], matchDetails['Team 1 Score'], matchDetails['Team 2 Score'], matchDetails['Match VOD'] = cur.execute(cmd, (matchID,)).fetchone()

    # Get list of map IDs for the given match ID
    mapIDList = get_mapIDList(matchID)
    matchDetails['Map Details'] = []
    for mapID in mapIDList:
        mapDetails = get_mapDetails(mapID)
        matchDetails['Map Details'].append(mapDetails)

    conn.close()
    return matchDetails

def get_mapDetails(mapID):
    mapDetails = {}
    conn = get_db_connection()
    cur = conn.cursor()
    cmd = """
        SELECT Team, Player, CAST(SUM(Kills) AS FLOAT) / CAST(SUM(Deaths) AS FLOAT) KD,
            SUM(Kills) Kills, SUM(Deaths) Deaths, SUM(Engagements) Engagements,
            SUM(Difference) Difference, [Map Result]
        FROM Players
        WHERE [Map ID] = ?
        GROUP BY Player, Team, [Map Result]
        ORDER BY Team, Player COLLATE NOCASE ASC
    """ # or ORDER BY KD DESC
    mapStats = cur.execute(cmd, (mapID,)).fetchall()
    mapDetails['Map Stats'] = mapStats

    cmd = """
        SELECT [Map Number], Map, [Team 1], [Team 2], [Team 1 Score], [Team 2 Score], [Map VOD]
        FROM Maps
        WHERE [Map ID] = ?
    """
    mapDetails['Map Number'], mapDetails['Map'], mapDetails['Team 1'], mapDetails['Team 2'], mapDetails['Team 1 Score'], mapDetails['Team 2 Score'], mapDetails['Map VOD'] = cur.execute(cmd, (mapID,)).fetchone()

    conn.close()
    return mapDetails

def get_playerLeaderboard(seasons, team, opponent, event, mode, mapPlayed):
    if team == 'All':
        team = '%'
    if opponent == 'All':
        opponent = '%'
    if event == 'All':
        event = '%'
    if mode == 'All':
        mode = '%'
    if mapPlayed == 'All':
        mapPlayed = '%'

    if len(seasons) == 1:
        seasons = (seasons[0], '')

    conn = get_db_connection()
    cur = conn.cursor()

    cmd = """
        SELECT [Player ID], CAST(SUM(Kills) AS FLOAT) / CAST(SUM(Deaths) AS FLOAT) KD, SUM(Kills) Kills,
            SUM(Deaths) Deaths, SUM(Engagements) Engagements, SUM(Difference) Difference, COUNT(*) MapsPlayed
        FROM Players
        WHERE Season IN {}
            AND Team LIKE ?
            AND Opponent LIKE ?
            AND Event LIKE ?
            AND Mode LIKE ?
            AND (Map LIKE ? OR Map IS NULL)
        GROUP BY [Player ID]
    """.format(tuple(seasons))
    result = cur.execute(cmd, (team, opponent, event, mode, mapPlayed)).fetchall()
    conn.close()
    return result

def get_teamLeaderboard(seasons, opponent, event, mode, mapPlayed):
    if opponent == 'All':
        opponent = '%'
    if event == 'All':
        event = '%'
    if mode == 'All':
        mode = '%'
    if mapPlayed == 'All':
        mapPlayed = '%'
    
    # IN doesn't work if tuple is of size 1
    if len(seasons) == 1:
        seasons = (seasons[0], '')

    conn = get_db_connection()
    cur = conn.cursor()

    cmd = """
        SELECT [Team ID], CAST(SUM(Kills) AS FLOAT) / CAST(SUM(Deaths) AS FLOAT) KD, SUM(Kills) Kills,
            SUM(Deaths) Deaths, SUM(Engagements) Engagements, SUM(Difference) Difference, COUNT(*) MapsPlayed
        FROM Players
        WHERE Season IN {}
            AND Opponent LIKE ?
            AND Event LIKE ?
            AND Mode LIKE ?
            AND (Map LIKE ? OR Map IS NULL)
        GROUP BY [Team ID]
    """.format(tuple(seasons))
    result = cur.execute(cmd, (opponent, event, mode, mapPlayed)).fetchall()
    conn.close()
    return result

class PlayerProfile():
    def __init__(self, playerID):
        self.playerID = playerID
        self.firstName, self.lastName, self.username = self.get_playerName()
        self.socialMedia = self.get_playerSocialMedia()
        self.matches = self.get_playerMatches('Overall')
        self.kills, self.deaths, self.kd = self.get_playerKD('Overall')
        self.matchesPlayed, self.matchWins, self.matchLosses = self.get_playerMatchRecord('Overall')
        self.mapsPlayed, self.mapWins, self.mapLosses = self.get_playerMapRecord('Overall')
        self.seasons = self.get_playerSeasons()
        self.playerStats = self.get_playerSeasonStats()
        self.birthday, self.age = self.get_playerBirthdayAge()
        self.lastRecordedTeam, self.previousTeams = self.get_playerTeams()
        if self.socialMedia['Twitter Username'] != None:
            self.twitterFollowers = self.get_playerTwitterFollowers()
        else:
            self.twitterFollowers = 0

    def get_playerName(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT [First Name], [Last Name], Username
            FROM PlayerInfo
            WHERE [Player ID] = ?
        """
        playerName = cur.execute(cmd, (self.playerID,)).fetchall()
        firstName = playerName[0][0]
        lastName = playerName[0][1]
        username = playerName[0][2]
        conn.close()
        return firstName, lastName, username
    
    def get_playerSocialMedia(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT [Twitter Username], [Instagram Username], [Reddit Username], [Twitch Channel], [YouTube Channel],
                [Twitter Followers], [Instagram Followers], [Twitch Followers], [YouTube Subscribers]
            FROM PlayerInfo
            WHERE [Player ID] = ?
        """
        socialMedia = cur.execute(cmd, (self.playerID,)).fetchone()
        conn.close()
        return socialMedia

    def get_playerKD(self, season):
        matchIDTuple = self.get_playerMatchIDTuple(season)
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT SUM(Kills), SUM(Deaths)
            FROM Players
            WHERE [Match ID] IN {}
                AND [Player ID] = ?
        """.format(matchIDTuple)
        kills, deaths = cur.execute(cmd, (self.playerID,)).fetchone()
        conn.close()
        if kills is None and deaths is None:
            kd = None
        elif int(deaths) == 0 and int(kills) > 0:
            kd = kills
        else:
            kd = kills / deaths
        return kills, deaths, kd

    def get_playerMatchIDTuple(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT DISTINCT [Match ID]
            FROM Players p
            WHERE p.[Player ID] = ?
                AND Season LIKE ?
        """
        matchIDs = cur.execute(cmd, (self.playerID, season)).fetchall()
        conn.close()
        matchIDList = []
        for matchID in matchIDs:
            matchIDList.append(matchID[0])
        return tuple(matchIDList)

    def get_playerMapIDTuple(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT DISTINCT [Map ID]
            FROM Players p
            WHERE p.[Player ID] = ?
                AND Season LIKE ?
        """
        mapIDs = cur.execute(cmd, (self.playerID, season)).fetchall()
        conn.close()
        mapIDList = []
        for mapID in mapIDs:
            mapIDList.append(mapID[0])
        return tuple(mapIDList)

    def get_playerMatches(self, season):
        matchIDTuple = self.get_playerMatchIDTuple(season)
        if season == 'Overall':
            season = '%'

        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT DISTINCT p.Team, p.Opponent, m.*,
                CASE
                    WHEN m.[Team 1] = p.Team THEN [Team 1 Score]
                    WHEN m.[Team 2] = p.Team THEN [Team 2 Score]
                END [Team Score],
                CASE
                    WHEN m.[Team 1] = p.Team THEN [Team 2 Score]
                    WHEN m.[Team 2] = p.Team THEN [Team 1 Score]
                END [Opponent Score]
            FROM Players p
                INNER JOIN Matches m ON m.[Match ID] = p.[Match ID]
            WHERE [Player ID] = ?
                AND m.Season LIKE ?
        """
        matches = cur.execute(cmd, (self.playerID, season)).fetchall()
        conn.close()
        return matches
    
    def get_playerMatchRecord(self, season):
        matchIDTuple = self.get_playerMatchIDTuple(season)
        if season == 'Overall':
            season = '%'

        conn = get_db_connection()
        cur = conn.cursor()
        matchesPlayed, wins, losses = 0, 0, 0
        for matchID in matchIDTuple:
            cmd = """
                SELECT Team, Opponent
                FROM Players
                WHERE [Match ID] = ?
                    AND [Player ID] = ?
                    
            """
            playerTeam, opponent = cur.execute(cmd, (matchID, self.playerID)).fetchone()
            cmd = """
                SELECT Winner
                FROM Matches
                WHERE [Match ID] = ?
            """
            winner = cur.execute(cmd, (matchID,)).fetchone()[0]
            matchesPlayed += 1
            if playerTeam == winner:
                wins += 1
            elif opponent == winner:
                losses += 1
        conn.close()

        return matchesPlayed, wins, losses
    
    def get_playerMapRecord(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT COUNT(*)
            FROM Players
            WHERE [Player ID] = ?
                AND Season LIKE ?
        """
        mapsPlayed = cur.execute(cmd, (self.playerID, season)).fetchone()[0]

        cmd = """
            SELECT COUNT(*)
            FROM Players
            WHERE [Player ID] = ?
                AND Season LIKE ?
                AND [Map Result] = 'Win'
        """
        mapsWon = cur.execute(cmd, (self.playerID, season)).fetchone()[0]

        cmd = """
            SELECT COUNT(*)
            FROM Players
            WHERE [Player ID] = ?
                AND Season LIKE ?
                AND [Map Result] = 'Loss'
        """
        mapsLost = cur.execute(cmd, (self.playerID, season)).fetchone()[0]
        conn.close()
        return mapsPlayed, mapsWon, mapsLost

    def get_playerSeasons(self):
        matchIDTuple = self.get_playerMatchIDTuple('Overall')
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT p.Season
            FROM Players p
                INNER JOIN Matches m ON m.[Match ID] = p.[Match ID]
            WHERE p.[Match ID] IN {}
                AND p.[Player ID] = ?
            ORDER BY to_date(m.Date), m.[Season Match Number]
        """.format(matchIDTuple)
        seasons = cur.execute(cmd, (self.playerID,)).fetchall()
        conn.close()
        seasonList = []
        for season in seasons:
            if season[0] not in seasonList:
                seasonList.append(season[0])
        return seasonList
    
    def get_playerSeasonStats(self):
        playerStats = {}
        for season in self.seasons:
            seasonStats = {}
            seasonStats['kills'], seasonStats['deaths'], seasonStats['kd'] = self.get_playerKD(season)
            seasonStats['matchesPlayed'], seasonStats['matchWins'], seasonStats['matchLosses'] = self.get_playerMatchRecord(season)
            seasonStats['mapsPlayed'], seasonStats['mapWins'], seasonStats['mapLosses'] = self.get_playerMapRecord(season)
            playerStats[season] = seasonStats

        return playerStats
    
    def get_playerBirthdayAge(self):
        # returns birthday in form January 1, 0000 and age
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT to_date([Date of Birth])
            FROM PlayerInfo
            WHERE [Player ID] = ?
                AND [Date of Birth] IS NOT NULL
        """
        birthdayDate = cur.execute(cmd, (self.playerID,)).fetchone()
        conn.close()
        if birthdayDate == None:
            return None, None
        birthday = datetime.strptime(birthdayDate[0], '%Y%m%d')
        today = date.today()

        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        return birthday.strftime('%B %d, %Y'), age
    
    def get_playerTeams(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT DISTINCT p.Team
            FROM Players p
                INNER JOIN Matches m ON m.[Match ID] = p.[Match ID]
            WHERE p.[Player ID] = ?
            ORDER BY to_date(m.Date), m.[Season Match Number]
        """
        teams = cur.execute(cmd, (self.playerID,)).fetchall()
        conn.close()
        teamList = []
        for team in teams:
            if team[0] not in teamList:
                teamList.append(team[0])
        return teamList[-1], teamList[:-1]

    def update_playerTwitterFollowers(self):
        # updates twitter followers in sql table for given player
        f = open('api_secrets.json')
        secrets = json.load(f)
        consumer_key = secrets['consumer_key']
        consumer_secret = secrets['consumer_key_secret']
        access_token = secrets['access_token']
        access_token_secret = secrets['access_token_secret']

        # Twitter authentication
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # Get Twitter followers
        user = api.get_user(screen_name=self.socialMedia['Twitter Username'])
        followers = int(user.followers_count)

        # Update PlayerInfo with number of followers
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            UPDATE PlayerInfo
            SET [Twitter Followers] = ?
            WHERE [Player ID] = ?
        """
        cur.execute(cmd, (followers, self.playerID))
        conn.commit()
        conn.close()

    def get_playerTwitterFollowers(self):
        self.update_playerTwitterFollowers()

        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT [Twitter Followers]
            FROM PlayerInfo
            WHERE [Player ID] = ?
        """
        followers = cur.execute(cmd, (self.playerID,)).fetchone()[0]
        conn.close()
        return followers

class TeamProfile():
    def __init__(self, teamID):
        self.teamID = teamID
        self.teamName = self.get_teamName()
        self.socialMedia = self.get_teamSocialMedia()
        self.matches = self.get_teamMatches('Overall')
        self.kills, self.deaths, self.kd = self.get_teamKD('Overall')
        self.matchesPlayed, self.matchWins, self.matchLosses = self.get_teamMatchRecord('Overall')
        self.mapsPlayed, self.mapWins, self.mapLosses = self.get_teamMapRecord('Overall')
        self.seasons = self.get_teamSeasons()
        self.teamStats = self.get_teamSeasonStats()
        self.lastRecordedRoster = get_teamLastRecordedRoster()[int(self.teamID)]
        self.previousPlayers = self.get_teamPreviousPlayers()
        if self.socialMedia['Twitter Username'] != None:
            self.twitterFollowers = self.get_teamTwitterFollowers()
        else:
            self.twitterFollowers = 0
    
    def get_teamName(self):
        conn = get_db_connection()
        cur = conn.cursor()
        teamName = cur.execute("SELECT Name FROM TeamInfo WHERE [Team ID] = ?", (self.teamID,)).fetchone()[0]
        conn.close()
        return teamName
    
    def get_teamSocialMedia(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT [Twitter Username], [Instagram Username], [Twitch Channel], [YouTube Channel],
                [Twitter Followers], [Instagram Followers], [Twitch Followers], [YouTube Subscribers]
            FROM TeamInfo
            WHERE [Team ID] = ?
        """
        socialMedia = cur.execute(cmd, (self.teamID,)).fetchone()
        conn.close()
        return socialMedia
    
    def get_teamKD(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT SUM(Kills), SUM(Deaths)
            FROM Players
            WHERE [Team ID] = ?
                AND Season LIKE ?
        """
        kills, deaths = cur.execute(cmd, (self.teamID, season)).fetchone()
        conn.close()
        if kills is None and deaths is None:
            kd = None
        elif int(deaths) == 0 and int(kills) > 0:
            kd = kills
        else:
            kd = kills / deaths
        return kills, deaths, kd
    
    def get_teamMatchRecord(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT COUNT(Winner)
            FROM Matches
            WHERE (([Team 1 ID] = ? AND Winner = [Team 1]) OR ([Team 2 ID] = ? AND Winner = [Team 2]))
                AND Season LIKE ?

        """
        wins = cur.execute(cmd, (self.teamID, self.teamID, season)).fetchone()[0]

        cmd = """
            SELECT COUNT(Winner)
            FROM Matches
            WHERE (([Team 1 ID] = ? AND Winner = [Team 2]) OR ([Team 2 ID] = ? AND Winner = [Team 1]))
                AND Season LIKE ?
        """
        losses = cur.execute(cmd, (self.teamID, self.teamID, season)).fetchone()[0]

        cmd = """
            SELECT COUNT(Winner)
            FROM Matches
            WHERE ([Team 1 ID] = ? OR [Team 2 ID] = ?)
                AND Season LIKE ?
        """
        matches = cur.execute(cmd, (self.teamID, self.teamID, season)).fetchone()[0]
        conn.close()

        return matches, wins, losses

    def get_teamMatches(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT CASE
                        WHEN [Team 1 ID] = ? THEN [Team 1]
                        WHEN [Team 2 ID] = ? THEN [Team 2]
                   END Team,
                   CASE
                        WHEN [Team 1 ID] = ? THEN [Team 2]
                        WHEN [Team 2 ID] = ? THEN [Team 1]
                   END Opponent,
                   CASE
                        WHEN [Team 1 ID] = ? THEN [Team 1 Score]
                        WHEN [Team 2 ID] = ? THEN [Team 2 Score]
                   END [Team Score],
                   CASE
                        WHEN [Team 1 ID] = ? THEN [Team 2 Score]
                        WHEN [Team 2 ID] = ? THEN [Team 1 Score]
                   END [Opponent Score]
                   , *
            FROM Matches
            WHERE ([Team 1 ID] = ? OR [Team 2 ID] = ?)
                AND Season LIKE ?
        """
        matches = cur.execute(cmd, (self.teamID, self.teamID, self.teamID, self.teamID, self.teamID, self.teamID, self.teamID, self.teamID, self.teamID, self.teamID, season)).fetchall()
        conn.close()
        return matches
    
    def get_teamMapRecord(self, season):
        if season == 'Overall':
            season = '%'
        
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT COUNT([Map Winner])
            FROM Maps
            WHERE (([Team 1 ID] = ? AND [Map Winner] = [Team 1]) OR ([Team 2 ID] = ? AND [Map Winner] = [Team 2]))
                AND Season LIKE ?

        """
        wins = cur.execute(cmd, (self.teamID, self.teamID, season)).fetchone()[0]

        cmd = """
            SELECT COUNT([Map Winner])
            FROM Maps
            WHERE (([Team 1 ID] = ? AND [Map Winner] = [Team 2]) OR ([Team 2 ID] = ? AND [Map Winner] = [Team 1]))
                AND Season LIKE ?
        """
        losses = cur.execute(cmd, (self.teamID, self.teamID, season)).fetchone()[0]

        cmd = """
            SELECT COUNT([Map Winner])
            FROM Maps
            WHERE ([Team 1 ID] = ? OR [Team 2 ID] = ?)
                AND Season LIKE ?
        """
        mapsPlayed = cur.execute(cmd, (self.teamID, self.teamID, season)).fetchone()[0]
        conn.close()

        return mapsPlayed, wins, losses

    def get_teamSeasons(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT DISTINCT Season
            FROM Matches
            WHERE ([Team 1 ID] = ? OR [Team 2 ID] = ?)
            ORDER BY to_date(Date), [Season Match Number]
        """
        seasons = cur.execute(cmd, (self.teamID, self.teamID)).fetchall()
        conn.close()
        seasonList = []
        for season in seasons:
            if season[0] not in seasonList:
                seasonList.append(season[0])
        return seasonList
    
    def get_teamSeasonStats(self):
        teamStats = {}
        for season in self.seasons:
            seasonStats = {}
            seasonStats['kills'], seasonStats['deaths'], seasonStats['kd'] = self.get_teamKD(season)
            seasonStats['matchesPlayed'], seasonStats['matchWins'], seasonStats['matchLosses'] = self.get_teamMatchRecord(season)
            seasonStats['mapsPlayed'], seasonStats['mapWins'], seasonStats['mapLosses'] = self.get_teamMapRecord(season)
            teamStats[season] = seasonStats

        return teamStats
    
    def update_teamTwitterFollowers(self):
        # updates twitter followers in sql table for given player
        f = open('api_secrets.json')
        secrets = json.load(f)
        consumer_key = secrets['consumer_key']
        consumer_secret = secrets['consumer_key_secret']
        access_token = secrets['access_token']
        access_token_secret = secrets['access_token_secret']

        # Twitter authentication
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # Get Twitter followers
        user = api.get_user(screen_name=self.socialMedia['Twitter Username'])
        followers = int(user.followers_count)

        # Update PlayerInfo with number of followers
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            UPDATE TeamInfo
            SET [Twitter Followers] = ?
            WHERE [Team ID] = ?
        """
        cur.execute(cmd, (followers, self.teamID))
        conn.commit()
        conn.close()
    
    def get_teamTwitterFollowers(self):
        self.update_teamTwitterFollowers()

        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT [Twitter Followers]
            FROM TeamInfo
            WHERE [Team ID] = ?
        """
        followers = cur.execute(cmd, (self.teamID,)).fetchone()[0]
        conn.close()
        return followers
    
    def get_teamPreviousPlayers(self):
        lastRoster = get_teamLastRecordedRoster()[int(self.teamID)]
        conn = get_db_connection()
        cur = conn.cursor()
        cmd = """
            SELECT DISTINCT p.[Player ID]
            FROM Players p
                INNER JOIN Matches m ON m.[Match ID] = p.[Match ID]
            WHERE p.[Team ID] = ?
            ORDER BY to_date(m.Date), m.[Season Match Number]
        """
        playerIDs = cur.execute(cmd, (self.teamID,)).fetchall()
        playerList = []
        for playerID in playerIDs:
            playerName = cur.execute("SELECT Username FROM PlayerInfo WHERE [Player ID] = ?", (playerID[0],)).fetchone()[0]
            if playerName not in playerList:
                playerList.append(playerName)
        conn.close()
        return [x for x in playerList if x not in lastRoster]