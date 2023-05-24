# Where's My Bus?
#### Video Demo:  https://youtu.be/-srC_OkOn4c
#### Description: This app tracks Houston Metro's buses arrival times. It can be used to efficiently track the buses. My goal was to make the app as minimal as it could be and user friendly. Flask based website and hosted it on Pythonanywhere.com. wheresmybus.pythonanywhere.com. All data is pulled from the API at time of request from the website.

#### Houston Metro Bus APIs (https://api-portal.ridemetro.org/apis) main feed for real-time bus data is "API METRO GTFS Realtime". It contains one dataset called "TripUpdates" with an endpoint at "https://api.ridemetro.org/GtfsRealtime/TripUpdates". TripUpdates is near real-time data feed provided by METRO (GTFS Realtime format).

#### GTFS Realtime is a feed specification that allows public transportation agencies to provide realtime updates about their fleet to application developers. It is an extension to GTFS (General Transit Feed Specification), an open data format for public transportation schedules and associated geographic information. See https://developers.google.com/transit/gtfs-realtime

#### The GTFS Realtime data exchange format is based on Protocol Buffers. See https://developers.google.com/protocol-buffers.

With protocol buffers, you write a .proto description of the data structure you wish to store. From that, the protocol buffer compiler creates a class that implements automatic encoding and parsing of the protocol buffer data with an efficient binary format.  See https://github.com/protocolbuffers/protobuf#protocol-compiler-installation.

Compiling Your Protocol Buffers:
protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/gtfs-realtime.proto

The generated class provides getters and setters for the fields that make up a protocol buffer and takes care of the details of reading and writing the protocol buffer as a unit.

Be sure to install prtobuf, (pip install protobuf) and/or update it (pip install --upgrade protobuf).

#### Other APIs from Houston Metro Bus APISs do not use the Protocol Buffer format and contain ancillary data.

Use the Nominatim API located at "https://nominatim.openstreetmap.org/search.php" to lookup addresses and return geo coordinates used as input into Houston Metro search by geo coordinates APIs.

Use openstreetmap to embedd a map of the users geo location that was used for the search. Creates from the single geo coordinates, a bounding box for the map so each embedded map would be zoomed into to the specific users geo location search area. Use openstreetmap's transit map which has the bus routes displayed on the street lines of the map.

Use one of the Houston Metro's transit APIs to find the lat lon of the stop and calculate the distance from the geo coordiantes used by the user/app. Then sortd by distance and displays that to the user.

#### geoareas.py and realtime.py are the files that access the APIs, parse, trim, add to and format the data. The data reqired were in differnt APIs and the real-time data was in one file which needed to be parsed by route and stop. They both use a file called shared.py which contains code to access APIs, time coversion, and distance calculations functions. realtime.py interacts and processes the real-time "TripUpdates" formatted in protobuf. geoareas.py processes other Houston Metro APIs not apart of the real-time feed such as vehicle data, stop geo coodinates, and full route names.

#### gtfs_realtime_pb2.py is the file created by compiling the GTFS schema to work with the programming language desired. Python in this case. It contains classes necessary to deserialize and convert the binary data to text.

### appy.py controls the routing and logic of the website. It contains the search by street address API function as well as the create bounding box function for the map.

### index.html contains the web forms and code to retrieve the geo location from the browser. It contains the iframe for the openstreetmap embedded map.

### realtime.html is designed to display the real-time bus data from realtime.py.

### layout.html is the styling and layout of the website. 
