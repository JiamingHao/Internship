import argparse
import sys
import math
from enum import Enum

global dirPath
dirPath="./ODPairs/"
global EARTH_RADIUS
EARTH_RADIUS=6378.137

SortPattern = Enum('ZIPCODE', 'DISTANCE')

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filePath", help="specify the path of the input file")
parser.add_argument("-n","--numberOfPairs", type=int, help="specify the number of OD pairs generated in each file")
parser.add_argument("-la","--latitude", type=float, help="specify the latitude for reference")
parser.add_argument("-lo","--longitude",type=float, help="specify the longitude for reference")
parser.add_argument("-d", "--debug", help="debug mode",action="store_true")

args = parser.parse_args()
if args.filePath:
    print "File path provided: ",args.filePath

if args.numberOfPairs:
    print "Number of pairs per file provided: ", args.numberOfPairs

# once one of the reference latitude or longitude is provided, the other one also
# needs to be provided   
if args.latitude==None or args.longitude==None:
    if not(args.latitude == None and args.longitude == None):
        print "Need reference latitude or longitude"
        sys.exit()

if args.debug:
    print "Debug mode on"

print args.latitude

def rad(d):
    ""
    return d*math.pi/180.0

def getDistance(lat1,lng1,lat2,lng2):
    "Calculate the sphere distance between two points when given their latitudes and longitudes"
    radLat1=rad(lat1)
    radLat2=rad(lat2)
    a=radLat1-radLat2
    b=rad(lng1)-rad(lng2)
    s=2*math.asin(math.sqrt(math.pow(math.sin(a/2), 2)+math.cos(radLat1)*math.cos(radLat2)*math.pow(math.sin(b/2),2)))
    s=s*EARTH_RADIUS
    s=round(s*10000)/10000
    return s


    