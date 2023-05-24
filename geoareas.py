from shared import *


def nextArrivalsbyStop(lat, lon, radius):

    routes = geoRoutes(lat, lon, radius)
    stops = geoStops(lat, lon, radius)
    nextArrivals = geoNextArrivals(lat, lon, radius)

    #  this sorts the arrivals by stop. And merges some fields.
    nextArrivalsbyStop = []
    for stop in stops:
        #  This merges the Stop Number and Stop Name into one field.
        tempStop = {}
        tempStop = stop
        tempStop["Stop"] = f"{tempStop['StopNumber']} - {tempStop['StopName']}"
        # del tempStop["StopNumber"]
        del tempStop["StopName"]

        # This creates a new list for arrivals/routes by stop ID
        tempStop["NextArrivals"] = []
        for nextArrival in nextArrivals:
            if stop["StopId"] == nextArrival["StopId"]:
                tempArrival = {}
                tempArrival = nextArrival
                # This merges the long name or route into the route name.
                for route in routes:
                    if tempArrival["RouteName"] == route["RouteName"]:
                        tempArrival[
                            "Route"
                        ] = f"{tempArrival['RouteName'].lstrip('0')} ({route['LongName']})"
                        # del tempArrival["RouteName"]
                # This converts all the arrival times to pretty text
                for idx, arrivalTime in enumerate(tempArrival["Arrivals"]):
                    tempArrival["Arrivals"][
                        idx
                    ] = f"Arrives in {calcTimeTil(arrivalTime)} at {UTCtolocal(arrivalTime)}"

                # This appends the nextArrival to the Stop dict.
                tempStop["NextArrivals"].append(tempArrival)
        nextArrivalsbyStop.append(tempStop)

    return nextArrivalsbyStop


# This pulls all routes that operate within radius of lat, lon.
def geoRoutes(lat, lon, radius):
    url = f"https://api.ridemetro.org/data/GeoAreas('{lat}|{lon}|{radius}')/Routes"
    routes = callAPI(url)

    routesParsed = []
    for route in routes:
        temp = {}
        temp["RouteId"] = route["RouteId"]
        temp["RouteName"] = route["RouteName"]
        temp["LongName"] = route["LongName"]

        routesParsed.append(temp)

    return routesParsed


# This pulls all stops within radius of lat, lon.
def geoStops(lat, lon, radius):
    url = f"https://api.ridemetro.org/data/GeoAreas('{lat}|{lon}|{radius}')/Stops"
    stops = callAPI(url)

    stopsParsed = []
    for stop in stops:
        temp = {}
        temp["StopId"] = stop["StopId"]
        temp["StopNumber"] = stop["StopCode"]
        temp["StopName"] = stop["Name"]
        temp["Coordinates"] = f"{stop['Lat']}, {stop['Lon']}"
        # temp["DistanceFromCenter"] = stop["DistanceFromCenter"]
        temp["Distance"] = distance(lat, lon, stop["Lat"], stop["Lon"])
        stopsParsed.append(temp)

    # sort by distance
    stopsParsed = sorted(stopsParsed, key=lambda d: d["Distance"], reverse=False)
    return stopsParsed


# This pulls all next arrivals within radius of lat, lon.
def geoNextArrivals(lat, lon, radius):
    url = (
        f"https://api.ridemetro.org/data/GeoAreas('{lat}|{lon}|{radius}')/NextArrivals"
    )
    nextArrivals = callAPI(url)

    # sort by "ArrivalTime"
    nextArrivals = sorted(
        nextArrivals, key=lambda d: d["LocalArrivalTime"], reverse=False
    )

    # parses thorugh the nextArrivals and creates a new array of only data wanted.
    nextArrivalsParsed = []
    for nextArrival in nextArrivals:
        if nextArrival["IsRealTime"] == True:  # only use if it is real time data.
            temp = {}
            # temp["IsRealTime"] = nextArrival["IsRealTime"]
            # temp["TripId"] = nextArrival["TripId"]
            temp["StopId"] = nextArrival["StopId"]
            # temp["StopName"] = nextArrival["StopName"]
            temp["ArrivalTime"] = nextArrival["UtcArrivalTime"]
            temp["RouteId"] = nextArrival["RouteId"]
            temp["RouteName"] = nextArrival["RouteName"]
            temp["DirectionAndDestination"] = nextArrival["DestinationName"].title()
            nextArrivalsParsed.append(temp)

    # This second parsing merges the arrivals of the same stop and route info.
    stops_and_routes_merged_arrivals = []
    for nextArrival in nextArrivalsParsed:
        result = next(
            (
                item
                for item in stops_and_routes_merged_arrivals
                if item["RouteId"] == nextArrival["RouteId"]
                and item["StopId"] == nextArrival["StopId"]
            ),
            None,
        )
        if result == None:
            nextArrival["Arrivals"] = []
            nextArrival["Arrivals"].append(nextArrival["ArrivalTime"])
            del nextArrival["ArrivalTime"]
            stops_and_routes_merged_arrivals.append(nextArrival)
        else:
            result["Arrivals"].append(nextArrival["ArrivalTime"])

    return stops_and_routes_merged_arrivals


