from flask import Flask, render_template, request
from models import *
import sqlite3

app = Flask(__name__)

dropdownLists = {}
dropdownLists['seasonList'] = get_seasons()
dropdownLists['teamList'] = get_teams()
dropdownLists['eventList'] = get_events()
dropdownLists['modeList'] = get_modes()
dropdownLists['mapList'] = get_mapList()
playerList = get_playerList()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/viewMatches', methods=["GET", "POST"])
def viewMatches():
    seasons = request.form.getlist('seasons')
    team1 = request.form.get('team1')
    team2 = request.form.get('team2')
    event = request.form.get('event')

    selectedItems = {
        'seasons': seasons,
        'team1': team1,
        'team2': team2,
        'event': event
    }

    matches = get_matches(seasons, team1, team2, event)
    return render_template('viewMatches.html', matches=matches, dropdownLists=dropdownLists, selectedItems=selectedItems)

@app.route('/matchDetails/<matchID>')
def matchDetails(matchID):
    matchDetails = get_matchDetails(matchID)
    return render_template('matchDetails.html', matchDetails=matchDetails)

@app.route('/viewMaps', methods=["GET", "POST"])
def viewMaps():
    seasons = request.form.getlist('seasons')
    team1 = request.form.get('team1')
    team2 = request.form.get('team2')
    event = request.form.get('event')
    mode = request.form.get('mode')
    mapPlayed = request.form.get('map')

    selectedItems = {
        'seasons': seasons,
        'team1': team1,
        'team2': team2,
        'event': event,
        'mode': mode,
        'mapPlayed': mapPlayed
    }

    maps = get_maps(seasons, team1, team2, event, mode, mapPlayed)
    return render_template('viewMaps.html', maps=maps, dropdownLists=dropdownLists, selectedItems=selectedItems)

@app.route('/mapDetails/<mapID>')
def mapDetails(mapID):
    mapDetails = get_mapDetails(mapID)
    return render_template('mapDetails.html', mapDetails=mapDetails)

@app.route('/playerProfiles')
def playerProfiles():
    profiles = get_playerList()
    return render_template('playerProfiles.html', profiles=profiles)

@app.route('/playerProfiles/<playerID>', methods=["GET", "POST"])
def playerProfile(playerID):
    player = PlayerProfile(playerID)
    return render_template('playerProfile.html', player=player)

@app.route('/teamProfiles')
def teamProfiles():
    profiles = get_teamList()
    lastRecordedRosters = get_teamLastRecordedRoster()
    return render_template('teamProfiles.html', profiles=profiles, lastRecordedRosters=lastRecordedRosters)

@app.route('/teamProfiles/<teamID>', methods=["GET", "POST"])
def teamProfile(teamID):
    team = TeamProfile(teamID)
    return render_template('teamProfile.html', team=team)

@app.route('/playerLeaderboard', methods=["GET", "POST"])
def playerLeaderboard():
    seasons = request.form.getlist('seasons')
    team = request.form.get('team')
    opponent = request.form.get('opponent')
    event = request.form.get('event')
    mode = request.form.get('mode')
    mapPlayed = request.form.get('map')

    selectedItems = {
        'seasons': seasons,
        'team': team,
        'opponent': opponent,
        'event': event,
        'mode': mode,
        'mapPlayed': mapPlayed
    }

    leaderboard = get_playerLeaderboard(seasons, team, opponent, event, mode, mapPlayed)
    playerIDList = get_playerIDList()
    return render_template('playerLeaderboard.html', leaderboard=leaderboard, playerIDList=playerIDList, dropdownLists=dropdownLists, selectedItems=selectedItems)

@app.route('/teamLeaderboard', methods=["GET", "POST"])
def teamLeaderboard():
    seasons = request.form.getlist('seasons')
    opponent = request.form.get('opponent')
    event = request.form.get('event')
    mode = request.form.get('mode')
    mapPlayed = request.form.get('map')

    selectedItems = {
        'seasons': seasons,
        'opponent': opponent,
        'event': event,
        'mode': mode,
        'mapPlayed': mapPlayed
    }

    leaderboard = get_teamLeaderboard(seasons, opponent, event, mode, mapPlayed)
    teamIDList = get_teamIDList()
    return render_template('teamLeaderboard.html', leaderboard=leaderboard, teamIDList=teamIDList, dropdownLists=dropdownLists, selectedItems=selectedItems)

if __name__ == "__main__":
    app.run()