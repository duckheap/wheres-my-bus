from shared import *


# parses realtime data to pretty format
def realtimePretty(route, stopID):
    real = realtime(route, stopID)
    # print(real)
    stopDetails = {}
    if len(real) != 0:
        stopDetails[
            "Route"
        ] = f"Route: {real['Route']['routeID']} ({real['Route']['routeLongName']})"
        stopDetails["Stop"] = f"Stop: {real['StopCode']} - {real['Name']}"
        stopDetails[
            "Direction"
        ] = f"{real['Route']['direction']} to {real['Route']['destination']}"

        stopDetails["Trips"] = []
        for index, trip in enumerate(real["Route"]["Trips"]):
            temp = {}
            temp[
                "trip"
            ] = f"{index+1}.) Arrives in {trip['timeUntil']} at {trip['arrivalTimePretty']} - {trip['vehicle']['distance']} miles away."
            stopDetails["Trips"].append(temp)

    return stopDetails


"""pulls data from GTFS Realtime API as primary sources but also pulls from:
   Vehicles API to retrieve lat/lon of vehicle,
   Routes('{route}')/Stops API for full stop information including stop lat/lon
   and Routes('{id}')API - gets offcial route ID."""


def realtime(route, stopID):
    route = str(route).rjust(3, "0")
    stopID = str(stopID)

    #  Calls GTFS Realtime API. This gets realitme data of the route provided.
    realtime = getRealtimeData(route)


    # This creates a new parsed down list of dicts containing just route, stop, time
    # etc from the realtime data collected by GTFS Realtime API.
    trips = []
    for entity in realtime:
        for update in entity.trip_update.stop_time_update:
            if update.stop_id == stopID:
                trip = {}
                trip["tripID"] = entity.trip_update.trip.trip_id
                trip["vehicleID"] = entity.trip_update.vehicle.id
                trip["delay"] = update.arrival.delay
                trip["arrivalTime"] = update.arrival.time
                # converts epoch time to regular time.
                trip["arrivalTimePretty"] = epochToReg(update.arrival.time)
                # Calculates amount of time til arrival
                trip["timeUntil"] = calcTimeTilEpoch(update.arrival.time)
                trip["timestamp"] = entity.trip_update.timestamp
                trips.append(trip)

    #  Sort trips by arrival times.
    trips = sorted(trips, key=lambda d: d["arrivalTime"], reverse=False)

    if len(trips) != 0:
        # Calls vehicel API. This gets all vehicle data (vehicles that are reporting their active status).
        vehicleData = getVehicleData()

        if len(vehicleData) > 1:
            # This createa a new dict from vehicleData containing route information.
            Route = {}
            for trip in trips:
                for vehicle in vehicleData:
                    if trip["vehicleID"] == vehicle["VehicleId"]:
                        Route["routeID"] = vehicle["RouteName"].lstrip("0")
                        Route["longRouteID"] = vehicle["RouteId"]
                        Route["direction"] = (
                            vehicle["DirectionName"].split(",")[1].strip().title()
                        )
                        Route["destination"] = vehicle["DestinationName"].title()
                        break

            # Calls Routes('{routeID}') API to retireve the long name of the route.
            longRouteID = Route["longRouteID"]  # input example "Ho414_4620_020"
            routeLongName = routeInfo(longRouteID)[0]["LongName"]
            # Adds the route long name to route dict.
            Route["routeLongName"] = routeLongName

            # calls Stops('{id}') API - to retireve lat/lon and full name of stops of the provided
            # route. First have to make a synthetic full stopID by combining the routeID with stop Id.
            routeIdparsed = longRouteID.split("_")
            stopId = f"{routeIdparsed[0]}_{routeIdparsed[1]}_{stopID}"
            stopDetails = stopInfo(stopId)[0]

            # This creata a new dict of relevant vehicle data per trip vehicle ID, including
            # vehicle report time and vehicel lat/lon) and adds the vehicle dict to the trip.
            for trip in trips:
                for vehicle in vehicleData:
                    if trip["vehicleID"] == vehicle["VehicleId"]:
                        vehicleparsed = {}
                        vehicleparsed["vehicleReportTime"] = vehicle[
                            "VehicleReportTime"
                        ]
                        #  This converts the zulu tim eto local time.
                        vehicleparsed["VRTpretty"] = UTCtolocal(
                            vehicle["VehicleReportTime"]
                        )
                        vehicleparsed["lat"] = vehicle["Latitude"]
                        vehicleparsed["lon"] = vehicle["Longitude"]
                        # Calculates vehicle distance from stop in miles.
                        vehicleparsed["distance"] = distance(
                            stopDetails["Lat"],
                            stopDetails["Lon"],
                            vehicle["Latitude"],
                            vehicle["Longitude"],
                        )
                        trip["vehicle"] = vehicleparsed
                        break

        # Add trips info to Route dict
        Route["Trips"] = trips

        # Add the Route info to the stopDetails dict,
        stopDetails["Route"] = Route

        # Making the final dict structure: stopDetails -> Route -> trips/trip -> vehicle
        return stopDetails
    return trips


# Vehicles API - Returns all current vehicle data.
def getVehicleData():
    url = "https://api.ridemetro.org/data/Vehicles"
    return callAPI(url)


# Routes('{id}')API - Returns route info by ID. RouteId": "Ho414_4620_020"
def routeInfo(routeID):
    url = f"https://api.ridemetro.org/data/Routes('{routeID}')"
    return callAPI(url)


# Stops('{id}') API - Returns stop info by ID. "StopId": "Ho414_4620_9297"
def stopInfo(stopId):
    url = f"https://api.ridemetro.org/data/Stops('{stopId}')"
    return callAPI(url)

