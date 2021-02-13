import json

from datetime import datetime
from dateutil import relativedelta
import pytz

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
    "Combat density" : 5,
    "Combat lethality" : 5,
    "Experience goal" : 100000000,
    "Current experience" : 0
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