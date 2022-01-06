DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Maps;
DROP TABLE IF EXISTS Players;
DROP TABLE IF EXISTS PlayerInfo;
DROP TABLE IF EXISTS TeamInfo;

-- Create Matches table
CREATE TABLE Matches (
    [Match ID] VARCHAR(50) NOT NULL,
    [Season Match Number] INT NOT NULL,
    [Team 1 ID] INT NULL,
    [Team 1] INT NULL,
    [Team 2 ID] INT NULL,
    [Team 2] INT NULL,
    Event VARCHAR(50) NULL,
    Date DATE NULL,
    [Team 1 Score] INT NULL,
    [Team 2 Score] INT NULL,
    Winner VARCHAR(30) NULL,
    [Match VOD] VARCHAR(75) NULL
);

-- Create Maps table
CREATE TABLE Maps (
    [Match ID] VARCHAR(50) NOT NULL,
    [Map ID] VARCHAR(50) NOT NULL,
    [Team 1 ID] INT NULL,
    [Team 1] INT NULL,
    [Team 2 ID] INT NULL,
    [Team 2] INT NULL,
    Event VARCHAR(50) NULL,
    Mode VARCHAR(25) NULL,
    Map VARCHAR(25) NULL,
    [Map Number] INT NULL,
    [Team 1 Score] INT NULL,
    [Team 2 Score] INT NULL,
    [Map Winner] VARCHAR(30) NULL,
    [Map VOD] VARCHAR(75) NULL
);

-- Create Players table
CREATE TABLE Players (
    [Match ID] VARCHAR(50) NOT NULL,
    [Map ID] VARCHAR(50) NOT NULL,
    Event VARCHAR(50) NULL,
    [Team ID] INT NULL,
    Team VARCHAR(30) NULL,
    [Opponent ID] INT NULL,
    Opponent VARCHAR(30) NULL,
    Mode VARCHAR(25) NULL,
    Map VARCHAR(25) NULL,
    [Player ID] INT NOT NULL,
    Player VARCHAR(20) NULL,
    Kills INT NULL,
    Deaths INT NULL,
    KD NUMERIC(4, 2) NULL,
    Engagements INT NULL,
    Difference INT NULL,
    [Map Result] VARCHAR(4) NULL
);

-- Create Player Info table
CREATE TABLE PlayerInfo (
    [Player ID] INT NOT NULL,
    Username VARCHAR(30) NOT NULL,
    [First Name] VARCHAR(30) NULL,
    [Last Name] VARCHAR(30) NULL,
    [Last Recorded Team] VARCHAR(40) NULL,
    [Past Teams] VARCHAR(200) NULL,
    [Date of Birth] DATE NULL,
    [Country of Birth] VARCHAR(30) NULL,
    [Twitter Username] VARCHAR(25) NULL,
    [Instagram Username] VARCHAR(25) NULL,
    [Reddit Username] VARCHAR(25) NULL,
    [Twitch Channel] VARCHAR(25) NULL,
    [YouTube Channel] VARCHAR(100) NULL,
    [Past Usernames] VARCHAR(100) NULL,
    [Twitter Followers] INT NULL,
    [Instagram Followers] INT NULL,
    [Twitch Followers] INT NULL,
    [YouTube Subscribers] INT NULL
);

-- Create Team Info table
CREATE TABLE TeamInfo (
    [Team ID] INT NOT NULL,
    Name VARCHAR(30) NOT NULL,
    [Twitter Username] VARCHAR(25) NULL,
    [Instagram Username] VARCHAR(25) NULL,
    [Twitch Channel] VARCHAR(25) NULL,
    [YouTube Channel] VARCHAR(100) NULL,
    [Past Team Names] VARCHAR(100) NULL,
    [Twitter Followers] INT NULL,
    [Instagram Followers] INT NULL,
    [Twitch Followers] INT NULL,
    [YouTube Subscribers] INT NULL
);