import os
import urllib.request, json
from math import cos, asin, sqrt, pi
from time import strftime, gmtime, time
from datetime import datetime
import pytz
import gtfs_realtime_pb2

# makes the API call
def callAPI(url):
    transit_API_key = os.environ.get('METROTRANSITAPIKEY')
    try:
        hdr = {
            # Request headers
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": transit_API_key,
        }
        req = urllib.request.Request(url, headers=hdr)
        req.get_method = lambda: "GET"
        response = urllib.request.urlopen(req)
        http_code = response.getcode()
        if http_code == 200:
            content = json.loads(response.read())
            return content["value"]
        else:
            return []

    except Exception as e:
        return e


# METRO GTFS Realtime API - Returns list of routes from realtime arrival data
# for route provided.
def getRealtimeData(route):
    route = route.rjust(3, "0")
    realtime_API_key = os.environ.get('METROREALTIMEAPIKEY')
    try:
        url = "https://api.ridemetro.org/GtfsRealtime/TripUpdates"

        hdr = {
            # Request headers
            "Cache-Control": "no-cache",
            "Ocp-Apim-Subscription-Key": realtime_API_key,
        }

        req = urllib.request.Request(url, headers=hdr)

        req.get_method = lambda: "GET"
        response = urllib.request.urlopen(req)
        realtimedata = gtfs_realtime_pb2.FeedMessage()
        realtimedata.ParseFromString(response.read())

        data = []
        for entity in realtimedata.entity:
            if entity.trip_update.trip.route_id == route:
                data.append(entity)

        return data

    except Exception as e:
        return e

        

# Calculates distance between two lat/lons in miles.
def distance(lat1, lon1, lat2, lon2):
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    p = pi / 180
    a = (
        0.5
        - cos((lat2 - lat1) * p) / 2
        + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    )
    return round(12742 * asin(sqrt(a)) * 0.6214, 2)  # 2*R*asin...
    


# This part just formats the amount of time til in easy to read sentence.
def prettyTime(diff):
    
    intimeA = str(diff).split(".")[0]
    intimeA = intimeA.split(":")
    newTime = []
    for idx, unit in enumerate(intimeA):
        if unit != "00" and unit != "0":
            howlong = f"{unit.lstrip('0')}"
            match idx:
                case 0:
                    howlong += " hour"
                case 1:
                    howlong += " minute"
                case 2:
                    howlong += " second"
            if unit != "01":
                howlong += "s"
            newTime.append(howlong)
    if len(newTime) == 2:
        timeString = f"{newTime[0]} and {newTime[1]}"
    elif len(newTime) == 3:
        timeString = f"{newTime[0]}, {newTime[1]} and {newTime[2]}"
    elif len(newTime) == 1:
        timeString = newTime[0]
    else:
        timeString = "0"

    return timeString



#-----------used in geoareas.py


# This converts UTC to local time. "vehicleReportTime": "2022-11-24T01:12:49Z"
# Returns the time in 10:00 PM format.
def UTCtolocal(tempo):
    # converts the time string into a datetime object
    date_format_str = "%Y-%m-%dT%H:%M:%SZ"
    dt = datetime.strptime(tempo, date_format_str)

    # makes the tzinfo, UTC
    dt_utc = pytz.utc.localize(dt)

    #converts the UTC to CST time
    cst_time = dt_utc.astimezone(pytz.timezone("America/Chicago"))

    # Only outputs the time.
    time = cst_time.strftime("%I:%M %p")
    
    return time.lstrip("0")


# This calculates the amount of time until event. "arrivalTime": "2022-11-24T01:12:49Z"
# takes in UTC time.
def calcTimeTil(date_1):
    # converts the arrival time string into a datetime object
    date_format_str = "%Y-%m-%dT%H:%M:%SZ"
    arrival = datetime.strptime(date_1, date_format_str)

    # makes the tzinfo, UTC
    arrival_aware = pytz.utc.localize(arrival)

    # Gets the utc time and assigns it as a utc time in datetime object
    utc_now = pytz.utc.localize(datetime.utcnow())

    # diff variable is actually a timedelta object used to find the difference between two dates or times. 

    if arrival_aware >= utc_now:
        diff = arrival_aware - utc_now
        return prettyTime(diff)
    else:
        diff = utc_now - arrival_aware
        return f"-{prettyTime(diff)}"


#-----------used in realtime.py


# This calculates the amount of time until event. Takes epoch. "arrivalTime": 1669252486
def calcTimeTilEpoch(arrivalTime):
    currentTime = time()
    if arrivalTime >= time():
        intime = strftime("%H:%M:%S", gmtime(arrivalTime - currentTime))
        return prettyTime(intime)
    else:
        intime = strftime("%H:%M:%S", gmtime(currentTime - arrivalTime))
        return f"-{prettyTime(intime)}"



# This takes the epoch time and returns the time in 10:00 PM format.
def epochToReg(epoch):
    # get time in tz
    tz = pytz.timezone('America/Chicago')
    dt = datetime.fromtimestamp(epoch, tz)
    regTime = dt.strftime("%I:%M %p")

    return regTime.lstrip("0")

