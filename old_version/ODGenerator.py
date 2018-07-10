import argparse
import sys
import math
#from enum import Enum
import os
import io
import dis
import random
import datetime
import gc

global dirPath
dirPath = "./ODPairs/"
global EARTH_RADIUS
EARTH_RADIUS = 6378.137
global noPartition
noPartition = 0
global noPartition_Dis
noPartition_Dis = 0
def rad(d):
    '''Convert degree to radian
    
    Parameters
    -----------------
    d: float
    -----------------
    
    '''
    return d * math.pi / 180.0

def getDistance(lat1, lng1, lat2, lng2):
    '''Calculate the sphere distance between two points when given their latitudes and longitudes.
    
    Parameters
    -----------------
    lat1: float
    lng1: float
    lat2: float
    lng2: float
    -----------------
    
    '''
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b / 2), 2)))
    s = s * EARTH_RADIUS
    s = round(s * 10000) / 10000
    return s

def isNumber(a):
    '''Check whether the given String type parameter is made up of by pure digits, including the floating point
    
    Parameters
    -----------------
    a: String
    -----------------
    
    '''
    try:
        f = float(a)
        f = True
        return f
    except ValueError:    
        return False
    
def mytrim(s):
    '''Given a string, remove all the leading and trailing space including the new line character
    
    Parameters
    -----------------
    s:String
    -----------------
    
    '''
    if len(s) == 0:
        return ''
    if s[:1] == ' ' :
        return mytrim(s[1:])
    if s[-1:] == ' ' or s[-1:] == '\n' or s[-1:] == '\t' :
        return mytrim(s[:-1])
    else:
        return s

def modify(s):
    '''Only used in extractZipCode to remove the '|'  and  quotation marks
    
    Parameters
    -----------------
    s:String
    -----------------
    
    '''
    result = ""
    for i in range(0, len(s)):
        if s[i] == "|":
            return result 
        elif s[i] == '"':
            continue
        else:
            result = result + s[i]
    return result


def mkdir(path):
    '''Create folder according to the given path if the folder does not exist
    
    Parameters
    -----------------
    path: String
    -----------------
    
    '''
    folder = os.path.exists(path)  
    if not folder:
        os.makedirs(path)
        print "|                                                             |"
        print "|        --- Create folder", path, "...---                  |"
        print "|        ---OK ---                                            |"
    else:
        print "|        Folder ", '"', path ,'"', " already exists", "              |"

def processAndStore(filePath, entries):
    '''Open the file according to the given file path, read each entry, 
    calculate its sphere distance against the reference point. 
    Store its result at the end of the line
    
    Parameters
    -----------------
    filePath: String
    
    entries:  List ( the one used to store the file contents by lines )
    -----------------
    
    '''
    
    fp = io.open(filePath, mode="r", encoding="utf-8")
    starttime = datetime.datetime.now()
    for line in fp:
        # ignore those entries with irregular formats or too little information
        if(len(line.split(",")) <= 4):
            continue
    
        dis = getDistance(args.latitude, args.longitude, extractLatitudes(line), extractLongitude(line))
        # remove leading and trailing white spaces
        line = mytrim(line)
        # All floats or non String types must be casted to Strings before concatenation
        line = line[:] + "," + str(dis)
        
        entries.append(mytrim(line))
    fp.close()
    endtime = datetime.datetime.now()
    print "|        Reading and store input file finished", "               |"
    print "|        Time used to process and store: " + str((endtime - starttime).seconds)+ "s","                  |"
    
def extractLatitudes(line):
    '''Extract latitude from the given String
    
    Parameters
    -----------------
    line: String
    -----------------
    
    '''
    div = line.split(",")
    result = 0.0
   
    '''First remove the leading and trailing white spaces 
    through calling mytrim() function then remove the quotation
    marks by modify() function'''
    try:
        if not isNumber(modify(mytrim(div[0]))):
            # if the first index is not a sequence of number....
            result = float(modify(mytrim(div[1])))
        else:
            # This is the general case where the latitude starts from the third index
            result = float(modify(mytrim(div[2])))
    except ValueError: 
        # start searching the latitude from the fourth index   
        target = 3
        while target <= len(div) - 1 and not isNumber(modify(mytrim(div[target]))):
            target = target + 1
            
        if target >= len(div):
            return -1
        try:
            result = float(modify(mytrim(div[target])))
        except ValueError:
            # the exception catch here seems unnecessary
            exit(1)
    
    return result
 
def extractLongitude(line):
    '''extract longitude from the given String
    
    Parameters
    -----------------
    line: String
    -----------------
    
    '''
    div = line.split(",")
    try:
        _ = float(modify(mytrim(div[2])))
        result = float(modify(mytrim(div[3])))
    except ValueError:
        if len(div) >= 5 and cmp(modify(mytrim(div[4])), "") == 0:
            if not isNumber(modify(mytrim(div[2]))):
                return 38.351
            result = float(modify(mytrim(div[2])))
        else:
            if not isNumber(modify(mytrim(div[4]))):
                result = -1
            else:
                result = float(modify(mytrim(div[4])))
    
    return result

def debug_Output(entries, filepath):
    '''Generate the debug output when the -d flag is turned on
    
    Parameters
    -----------------
    entries:List 
        the one stores all the input file contents by lines
    
    filePath:String
        the path to output the debug file
    -----------------
    
    '''
    if args.debug:
        writer = io.open(filepath, "w", encoding="utf-8")
        for i in range(len(entries)):
                line = entries[i][:] + "\n"
                writer.write(line)
        writer.close()
    else:
        print "|        Debug mode off, thus no debug_output produced        |"
        print "|                                                             |"
def extract_filename(filepath):
    '''Extract the filename from the given filepath. 
    The default is that all files has csv extension
    
    Parameters
    -----------------
    filePath:String 
        the path of the input file
    -----------------
    
    '''
    temp = ""
    for i in range(5, len(filepath) + 1):
        if not filepath[0 - i] == '/':
            temp = temp + filepath[0 - i]
        else:
            break
    result = ""
    
    for i in range(1, len(temp) + 1):
        result = result + temp[0 - i]
        
    return result

def extractDis(line):
    '''Extract the distance from the content of the given line
       Need to be invoked after the processAndStore function
       
    Parameters
    -----------------
    line: Sting
        The line where the distance info resides
    -----------------
    
    '''
    div = line.split(",")
    return float(mytrim(div[len(div) - 1]))

def generateRandomPairs(entries):
    '''Randomly pick out start and end points to make OD pairs
    
    Parameters
    -----------------
    entries:List
        The list stores all the contents from the input file by lines
    -----------------
    
    '''
    start = []
    end = []
    fname = extract_filename(args.filePath) + "RandomPairs.dat"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    for _ in range(0, args.numberOfPairs):
        startNo = random.randint(0, len(entries) - 1)
        endNo = random.randint(0, len(entries) - 1)
        while startNo in start and endNo in end:
            startNo = random.randint(0, len(entries) - 1)
            endNo = random.randint(0, len(entries) - 1)
        start.append(startNo)
        end.append(endNo)
        content = entries[startNo] + " -----> " + entries[endNo] + "\n"
        writer.write(content)
    writer.close()

def sort(entries, pattern):
    '''Invoke Quick Sort algorithm on the given data according to
       the Pattern provided
       
       Parameters
       -----------------
       entries: List
           The list stores all the contents from the input file by lines
       
       pattern: Enum 
            ZIPCODE: sort by the zipcode in ascending order
            DISTANCE: sort by the distance in ascending order
    '''
    #if pattern == SortPattern['ZIPCODE']:
    if cmp(pattern, "ZIPCODE") == 0:
        print "|    Sort by zip code                                         |"
        starttime = datetime.datetime.now()
        sortHelper_Zip(entries, 0, len(entries) - 1)
        # sortHelper_Zip_MergeSort(entries, 0, len(entries)-1)
        endtime = datetime.datetime.now()
        print "|    Sort ends                                                |" 
        print "|    time used: " + str((endtime - starttime).seconds) +"s                                            |"
        print "|                                                             |"
    #elif pattern == SortPattern['DISTANCE']:
    elif cmp(pattern,"DISTANCE") == 0:
        print "|    Sort by distance                                         |"
        starttime = datetime.datetime.now()
        sortHelper_Dis(entries, 0, len(entries) - 1)
        endtime = datetime.datetime.now()
        print "|    Sort ends                                                |" 
        print "|    time used: " + str((endtime - starttime).seconds) +"s                                            |"
        print "|                                                             |"
def sortHelper_Zip_MergeSort(vals, i, k):
    '''Merge Sort algorithm as another option, current not used
    
       Parameters
       -----------------
       vals: List
            The data needed to be sort
       i: int
           Start index of the data
       k: int 
           End index of the data( inclusive)
       -----------------
       
    '''
    length = k - i + 1
    if length > 5:
        j = (i + k) / 2
        sortHelper_Zip_MergeSort(vals, i, j)
        sortHelper_Zip_MergeSort(vals, j + 1, k)
    else:
        insertionSortByZip(vals, i, k)
        return
    merge(vals, i, j, k)

def merge(vals, i, j, k):
    '''Merge two sorted parts back into the original List
    
       Parameters
       -----------------
       i: int
           Start index of the left merge part
       j: int
           The delimiter of right part and left part
       k: int
           The end index of the right part
       -----------------
    '''
    mergedSize = k - i + 1
    mergedData = []
    mergePos = 0
    leftPos = i
    rightPos = j + 1
    
    while leftPos <= j and rightPos <= k:
        if extractZipCode(vals[leftPos]) <= extractZipCode(vals[rightPos]):
            mergedData.append(vals[leftPos])
            leftPos = leftPos + 1
        else:
            mergedData.append(vals[rightPos])
            rightPos = rightPos + 1
        
        mergePos = mergePos + 1
        
    while leftPos <= j:
        mergedData.append(vals[leftPos])
        leftPos = leftPos + 1
        mergePos = mergePos + 1
    
    
    while rightPos <= k:
        mergedData.append(vals[rightPos])
        rightPos = rightPos + 1
        mergePos = mergePos + 1
        
    for a in range(0 , mergedSize):
        vals[i + a] = mergedData[a]
     
        
        
def sortHelper_Zip(vals, i, k):
    ''' Helper function called by sort function
        called by pattern ZIPCODE
        
        Parameters:
        -----------------
        vals: List
            The data needed to be sort
        i: int
            Start index 
        k: int 
            End index( inclusive)
    '''
    fixedSize = 110
    
    if k - i + 1 <= fixedSize:
        insertionSortByZip(vals, i, k)
        return 
    
    j = partitionByZip(vals, i, k)
    sortHelper_Zip(vals, i, j)
    sortHelper_Zip(vals, j + 1, k)
    return 

def sortHelper_Dis(vals, i, k):
    '''Helper function called by sort function
       called by pattern DISTANCE
       
       parameters:
       -----------------
       Same as sortHelper_Zip
       -----------------
       
    '''
    fixedSize = 5
    
    if k - i + 1 <= fixedSize:
        insertionSortByDistance(vals, i, k)
        return
    
    j = partitionByDis(vals, i, k)
    sortHelper_Dis(vals, i, j)
    sortHelper_Dis(vals, j + 1, k)
    return 

def partitionByZip(vals, i, k):
    '''Partition the given data through comparing with the pivot produced by getMedium
    
        Parameters:
        -----------------
        Same as sortHelper_Zip
        -----------------
        
    '''
    
    global noPartition
    noPartition += 1
    
    temp = ""
    done = False
    pivot = extractZipCode(vals[getMedium_Zip(vals, i, k)])
    l = i
    h = k
    
    while not done:
        while extractZipCode(vals[l]) < pivot:
            l = l + 1
        while pivot < extractZipCode(vals[h]):
            h = h - 1
        if l >= h:
            done = True
        else:
            temp = vals[l]
            vals[l] = vals[h]
            vals[h] = temp
            
            l = l + 1
            h = h - 1
    
    return h

def partitionByDis(vals, i , k):
    '''The distance version of partition
    
        Parameters:
        -----------------
        Same as sortHelper_Zip
        -----------------
        
    '''
    global noPartition_Dis
    noPartition_Dis += 1
    temp = ""
    done = False
    pivot = extractDis(vals[getMedium_Dis(vals, i, k)])
    l = i
    h = k 
    
    while not done:
        while extractDis(vals[l]) < pivot:
            l = l + 1
        while pivot < extractDis(vals[h]):
            h = h - 1
        if l >= h:
            done = True
        else:
            temp = vals[l]
            vals[l] = vals[h]
            vals[h] = temp
            
            l = l + 1
            h = h - 1
    return h

def getMedium_Zip(vals, i, k):
    '''Pick out the first, middle, and last elements from the given part of the list.
    From them, choose the medium value to use as the pivot in quick sort,
    return the index of the medium value
    
        Parameters:
        -----------------
        vals: List
            The list storing all the contents from input file by line
        i: int
            The beginning index of the interval where we pick the pivot
        k: int
            The ending index of the interval where we pick the pivot
        -----------------
        
        '''
    medium = extractZipCode(vals[i + (k - i) / 2])
    head = extractZipCode(vals[i])
    tail = extractZipCode(vals[k])
    
    temp = 0
    if head > medium:
        temp = head
        head = medium
        medium = temp
    
    if head > tail:
        temp = head
        head = tail
        tail = temp
    
    if medium > tail:
        temp = medium
        medium = tail
        tail = temp
    
    if medium == extractZipCode(vals[i + (k - i) / 2]):
        return i + (k - i) / 2
    elif medium == extractZipCode(vals[i]):
        return i
    else:
        return k 
    
    return i

def getMedium_Dis(vals, i, k):
    '''The distance version of the getMedium function
    
        Parameters:
        -----------------
        Same as getMedium_Zip
        -----------------
        
    '''
    medium = extractDis(vals[i + (k - i) / 2])
    head = extractDis(vals[i])
    tail = extractDis(vals[k])
    
    temp = 0
    if head > medium:
        temp = head
        head = medium
        medium = temp
    
    if head > tail:
        temp = head
        head = tail
        tail = temp
    
    if medium > tail:
        temp = medium
        medium = tail
        tail = temp
            
    if medium == extractDis(vals[i + (k - i) / 2]):
        return i + (k - i) / 2
    elif medium == extractDis(vals[i]):
        return i
    else:
        return k 
    return i 

def insertionSortByZip(vals, i, k):
    '''insertion sort is used to sort very small fragment of the data
    
        Parameters
        -----------------
        Same as sortHelper_Zip
        -----------------
    
    '''
    head = i
    temp = ""
    for a in range(head + 1, k + 1):
        sc = a
        while sc > head and extractZipCode(vals[sc]) < extractZipCode(vals[sc - 1]):
            temp = vals[sc]
            vals[sc] = vals[sc - 1]
            vals[sc - 1] = temp
            sc = sc - 1
    
def insertionSortByDistance(vals, i, k):
    ''' distance version of insertion sort
    
        Parameters
        -----------------
        Same as sortHelper_Zip
        -----------------
        
    '''
    head = i
    temp = ""
    for a in range(head + 1, k + 1):
        sc = a
        while sc > head and extractDis(vals[sc]) < extractDis(vals[sc - 1]):
            temp = vals[sc]
            vals[sc] = vals[sc - 1]
            vals[sc - 1] = temp
            sc = sc - 1


def extractZipCode(line):
    div = line.split(",")
    # for those entries lacking zip code info or having illegal zip code
    result = modify(mytrim(div[len(div) - 2]))
    
    if cmp(result, "") == 0 or not isNumber(result):
        return -1
    # call modify function before return to remove the "|" in some entries
    return int(result)

def minZipCodeDifference(entries):
    '''produce an OD pair that the start point and end point have min difference
    
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    start = []
    end = []
    fname = extract_filename(args.filePath) + "MinZipCodeDifference.dat"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    for _ in range(0, args.numberOfPairs):
        startNo = random.randint(0, len(entries) - 1 - 100)
        endNo = random.randint(startNo, startNo + 100)
        
        while startNo in start and endNo in end:
            if start.index(startNo) == end.index(endNo):
                break
            startNo = random.randint(0, len(entries) - 1 - 100)
            endNo = random.randint(startNo, startNo + 100)
        start.append(startNo)
        end.append(endNo)
        content = entries[startNo] + " -----> " + entries[endNo] + "\n"
        writer.write(content)
    writer.close()   

def largeZipCodeDifference(entries):
    '''Produce an OD pair that the start point and end point have max difference
        
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    start = []
    end = []
    
    #print "start length: ", len(start)
    #print "end   length: ", len(end)
    
    fname = extract_filename(args.filePath) + "MaxZipCodeDifference.dat"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    for _ in range(0, args.numberOfPairs):
        startNo = random.randint(0, 200)
        endNo = random.randint(len(entries) - 1 - 200, len(entries) - 1)
        
        #print startNo
        #print endNo
        
        while startNo in start and endNo in end:
            """ if the already existing startNo and endNo have the same index, meaning that they have been 
            once chosen as origin and destination in the past """
            
            if start.index(startNo) == end.index(endNo):
                break
            startNo = random.randint(0, 200)
            endNo = random.randint(len(entries) - 1 - 200, len(entries) - 1)
        
        start.append(startNo)
        end.append(endNo)
        content = entries[startNo] + " -----> " + entries[endNo] + "\n"
        writer.write(content)
    writer.close()

def smallDisFromRef(entries):
    '''After sorting by distance from reference point, equally divide the whole data into three parts
    we think all the data in the first part has relatively small sphere distance.
    
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    interval = len(entries) / 3
    start = []
    end = []
    fname = extract_filename(args.filePath) + "SmallDisFromRef.dat"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    for _ in range(0, args.numberOfPairs):
        startNo = random.randint(0, interval)
        endNo = random.randint(0, interval)
        
        while startNo in start and endNo in end:
            startNo = random.randint(0, interval)
            endNo = random.randint(0, interval)
        start.append(startNo)
        end.append(endNo)
        content = entries[startNo] + " -----> " + entries[endNo] + "\n"
        writer.write(content)
    writer.close()

def middleDisFromRef(entries):
    '''Same as smallDisFromRef function, randomly pick out OD pairs from the second part from 
    the given data after sorting by distance from the reference point
        
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    interval = len(entries) / 3
    start = []
    end = []
    fname = extract_filename(args.filePath) + "MiddleDisFromRef.dat"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    for _ in range(0, args.numberOfPairs):
        startNo = random.randint(interval, 2 * interval)
        endNo = random.randint(interval, 2 * interval)
        
        while startNo in start and endNo in end:
            startNo = random.randint(interval, 2 * interval)
            endNo = random.randint(interval, 2 * interval)
        start.append(startNo)
        end.append(endNo)
        content = entries[startNo] + " -----> " + entries[endNo] + "\n"
        writer.write(content)
    writer.close()

def largeDisFromRef(entries):
    '''Same as smallDisFromRef function, randomly pick out OD pairs from the third part from 
    the given data after sorting by distance from the reference point
        
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    interval = len(entries) / 3
    start = []
    end = []
    fname = extract_filename(args.filePath) + "LargeDisFromRef.dat"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    for _ in range(0, args.numberOfPairs):
        startNo = random.randint(interval * 2, len(entries) - 1)
        endNo = random.randint(interval * 2, len(entries) - 1)
        
        while startNo in start and endNo in end:
            startNo = random.randint(interval * 2, len(entries) - 1)
            endNo = random.randint(interval * 2, len(entries) - 1)
        start.append(startNo)
        end.append(endNo)
        content = entries[startNo] + " -----> " + entries[endNo] + "\n"
        writer.write(content)
    writer.close()
    
'''I was going to use enum at the very beginning. However, it seems that not all Python2.7 has enum module...'''
#SortPattern = Enum('SortPattern', 'DISTANCE ZIPCODE')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filePath", help="specify the path of the input file")
    parser.add_argument("-n", "--numberOfPairs", type=int, help="specify the number of OD pairs generated in each file")
    parser.add_argument("-la", "--latitude", type=float, help="specify the latitude for reference")
    parser.add_argument("-lo", "--longitude", type=float, help="specify the longitude for reference")
    parser.add_argument("-d", "--debug", help="debug mode", action="store_true")

    args = parser.parse_args()


    print "==============================================================="
    if args.numberOfPairs:
        print "|    Number of pairs per file provided: ", args.numberOfPairs, "                 |"
        print "|                                                             |"
    else:
        args.numberOfPairs = 50

        # once one of the reference latitude or longitude is provided, the other one also
        # needs to be provided   
    if args.latitude == None or args.longitude == None:
        if not(args.latitude == None and args.longitude == None):
            print "|    Lack reference latitude or longitude                     |"
            print "=============================================================="
            sys.exit()


    if args.latitude == None and args.longitude == None:
        # if no reference latitude and longitude provided, use default 0, 0
        args.latitude = 0.0
        args.longitude = 0.0

    print "|    Processing command line argument over:                   |"
    print "|        Reference latitude: ", args.latitude, "  Reference longitude: ", args.longitude,""

    if args.filePath:
        print "|        File path provided: ", '"', args.filePath, '"',"             "
    else:
        print "|        Using default file path"
        args.filePath = "./Shanghai3.csv"

    if args.debug:
        print "|        Debug Mode On","                                       |"
    else:
        print "|        Debug Mode Off","                                      |"


    print "|-------------------------------------------------------------|"
    print "|    Start processing the data......", "                         |"
    mkdir(dirPath)
    entries = []
    processAndStore(args.filePath, entries)
    print "|    Total number of lines: ", len(entries), "                           |"
    print"|                                                             |"
    debug_Output(entries, dirPath + extract_filename(args.filePath) + "Debug.dat")
    generateRandomPairs(entries)

    #sort(entries, SortPattern['DISTANCE'])
    sort(entries,"DISTANCE")
    # print "Number of partition called: ", noPartition_Dis
    
    debug_Output(entries, dirPath + extract_filename(args.filePath) + "SortedByDistanceDebug.dat")
    smallDisFromRef(entries)
    middleDisFromRef(entries)
    largeDisFromRef(entries)
    #sort(entries, SortPattern['ZIPCODE'])
    sort(entries,"ZIPCODE")
  
    debug_Output(entries, dirPath + extract_filename(args.filePath) + "SortedByZipDebug.dat")
    minZipCodeDifference(entries)
    largeZipCodeDifference(entries)
    gc.collect()
    print "==============================================================="
