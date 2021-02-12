import json

from datetime import datetime
from dateutil import relativedelta
import pytz

campaignDataDefault = {
    "Campaign name" : "Playtest Campaign 1",
    "Timestamp of last activity" : datetime.now(pytz.timezone('US/Eastern')).timestamp(),
    "Expected length" : 20,
    "Seconds of plot play" : 0.0,
    "Last timer tick" : 0,
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

times = {
    "Inciting Incident" : 0.13,
    "Second Thoughts" : 0.235,
    "Climax of Act One" : 0.313,
    "Obstacle 1 of Act Two" : 0.4085,
    "Obstacle 2 of Act Two" : 0.505,
    "Midpoint Big Twist" : 0.6,
    "Obstacle 3 of Act Two" : 0.685,
    "Disaster" : 0.78,
    "Crisis" : 0.843,
    "Climax of Act Two" : 0.889,
    "Climax of Act Three" : 1.0,
    "Obstacles of Act Three" : 1.069,
    "Denouement" : 1.138,
    "End" : 1.188
}