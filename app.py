from flask import Flask, render_template, request
import requests
import json
from geoareas import *
from realtime import *

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        latlon = request.form.get("latlon")
        street = request.form.get("street")
        display_name = ""
        if latlon:
            temp = latlon.split(",")
            lat = temp[0].strip()
            lon = temp[1].strip()
            radius = request.form.get("radius")
            accuracy = -1
        elif street:
            data = searchou(street)
            if data == None:
                data = search(street)

            if data != None:
                lat = data["lat"]
                lon = data["lon"]
                display_name = data["display_name"]
                radius = request.form.get("radius")
                accuracy = -1
            else:
                msg1 = "Address Not Found"
                return render_template("index.html", msg=msg1)

        else:
            lat = request.form.get("lat")
            lon = request.form.get("lon")
            radius = request.form.get("radius")
            accuracy = request.form.get("accuracy")
            accuracy = round(float(accuracy), 2)

        
        bbox = createbbox(lat, lon, radius)

        # This pulls all the stops based on lat, lon and radius.
        nextbyStops = nextArrivalsbyStop(lat, lon, radius)

        if len(nextbyStops) < 1:
            msg2 = "No Buses Found"
            return render_template(
                "index.html",
                msg=msg2,
                accuracy=accuracy,
                lon=lon,
                lat=lat,
                bbox=bbox,
                display_name=display_name,
            )
        else:
            return render_template(
                "index.html",
                nextbyStops=nextbyStops,
                accuracy=accuracy,
                lon=lon,
                lat=lat,
                bbox=bbox,
                display_name=display_name,
            )
    else:
        # if request.method == "GET":
        return render_template("index.html")


@app.route("/realtime/<route>/<stopId>")
def realtimedata(route, stopId):
    real = realtimePretty(route, stopId)
    return render_template("realtime.html", real=real)


# this creates a bound box for use in the iframe openstreetmap.
def createbbox(lat, lon, radius):
    lat = float(lat)
    lon = float(lon)
    radius = float(radius) / 0.00062137

    # Bounding box will be size of radius in meters plus 10 meters
    
    degrees = 360 * (radius + 10) / 40075000
    minlat = lat - degrees
    minlon = lon - degrees
    maxlat = lat + degrees
    maxlon = lon + degrees
    bbox = f"{minlon}%2C{minlat}%2C{maxlon}%2C{maxlat}"
    return bbox


def searchou(address):  
    baseUrl = "https://nominatim.openstreetmap.org/search.php"
    parameters = {"street": address, "state": "Texas", "country": "USA", 
    "viewbox": "-95.89005,30.36694,-94.72412,29.20970", 
    "bounded": "1", "dedupe": "0", "format": "jsonv2"}
    data = callAPItwo(baseUrl, parameters)

    return processAdress(data)


def search(que):  
    baseUrl = "https://nominatim.openstreetmap.org/search.php"
    parameters = {"q": que,
    "viewbox": "-95.89005,30.36694,-94.72412,29.20970", 
    "bounded": "1", "dedupe": "0", "format": "jsonv2"}
    data = callAPItwo(baseUrl, parameters)

    return processAdress(data)


def processAdress(data):
    if len(data) >= 1:
        for place in data:
            if place["place_rank"] == 30:
                res = {key: place[key] for key in place.keys()
                    & {'lat', 'lon', 'display_name'}}
                myList = res['display_name'].split(",")
                del myList[-5:]
                res['display_name'] = ''.join(myList)
                return res
        return None

# makes the API call
def callAPItwo(baseUrl, parameters):
    try:
        response = requests.get(baseUrl, params=parameters)
        return response.json()

    except Exception as e:
        return e

