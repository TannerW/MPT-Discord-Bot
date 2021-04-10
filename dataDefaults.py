import json

from datetime import datetime
from dateutil import relativedelta
import pytz

ttsEnabled = True

campaignDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
    "Timestamp of last activity" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Expected length" : 20.0,
    "Seconds of plot play" : 0.0,
    "Last timer tick" : 0,
    "Confirmed completed story beats" : [],
    "Seconds of progress delay" : 0.0,
    "Last delay timer tick" : 0,
    "Number of completed sessions" : 0,
    "Total number of progress rolls" : 0,
    "Average number of progressiveness rolls per minute" : 0
}

sessionDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
    "Session number" : 1,
    "Timestamp of last activity" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Session start time" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Session end time" : 0,
    "Number of progressiveness rolls this session" : 0,
    "Current number of progressiveness rolls per minute" : 0
}

advenDayDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
    "AdvenDay start time" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "PCs" : {},
    "Experience goal" : 0,
    "Current experience" : 0
}

advenDayAdjExpPerChar = {
    1 : 300,
    2 : 600,
    3 : 1200,
    4 : 1700,
    5 : 3500,
    6 : 4000,
    7 : 5000,
    8 : 6000,
    9 : 7500,
    10 : 9000,
    11 : 10500,
    12 : 11500,
    13 : 13500,
    14 : 15000,
    15 : 18000,
    16 : 20000,
    17 : 25000,
    18 : 27000,
    19 : 30000,
    20 : 40000
}

expThresholdPerChar = {
    1 : {"easy" : 25, "medium" : 50, "hard" : 75, "deadly" : 100},
    2 : {"easy" : 50, "medium" : 100, "hard" : 150, "deadly" : 200},
    3 : {"easy" : 75, "medium" : 150, "hard" : 225, "deadly" : 400},
    4 : {"easy" : 125, "medium" : 250, "hard" : 375, "deadly" : 500},
    5 : {"easy" : 250, "medium" : 500, "hard" : 750, "deadly" : 1100},
    6 : {"easy" : 300, "medium" : 600, "hard" : 900, "deadly" : 1400},
    7 : {"easy" : 350, "medium" : 750, "hard" : 1100, "deadly" : 1700},
    8 : {"easy" : 450, "medium" : 900, "hard" : 1400, "deadly" : 2100},
    9 : {"easy" : 550, "medium" : 1100, "hard" : 1600, "deadly" : 2400},
    10: {"easy" : 600, "medium" : 1200, "hard" : 1900, "deadly" : 2800},
    11: {"easy" : 800, "medium" : 1600, "hard" : 2400, "deadly" : 3600},
    12: {"easy" : 1000, "medium" : 2000, "hard" : 3000, "deadly" : 4500},
    13: {"easy" : 1100, "medium" : 2200, "hard" : 3400, "deadly" : 5100},
    14: {"easy" : 1250, "medium" : 2500, "hard" : 3800, "deadly" : 5700},
    15: {"easy" : 1400, "medium" : 2800, "hard" : 4300, "deadly" : 6400},
    16: {"easy" : 1600, "medium" : 3200, "hard" : 4800, "deadly" : 7200},
    17: {"easy" : 2000, "medium" : 3900, "hard" : 5900, "deadly" : 8800},
    18: {"easy" : 2100, "medium" : 4200, "hard" : 6300, "deadly" : 9500},
    19: {"easy" : 2400, "medium" : 4900, "hard" : 7300, "deadly" : 10900},
    20: {"easy" : 2800, "medium" : 5700, "hard" : 8500, "deadly" : 1270}
}


timingDataDefault = {

}

timesOfBeats = {
    0.13 : "Inciting Incident",
    0.235 : "Second Thoughts",
    0.313 : "Climax of Act One",
    0.4085 : "Obstacle 1 of Act Two",
    0.505 : "Obstacle 2 of Act Two",
    0.6 : "Midpoint Big Twist",
    0.685 : "Obstacle 3 of Act Two",
    0.78 : "Disaster",
    0.843 : "Crisis",
    0.889 : "Climax of Act Two",
    1.0 : "Climax of Act Three",
    1.069 : "Obstacles of Act Three",
    1.138 : "Denouement",
    1.188 : "End"
}

beatsOfTimes = {value:key for key, value in timesOfBeats.items()}