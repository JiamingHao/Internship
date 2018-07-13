import argparse
import sys
import math
import os
import io
import dis
import random
import gc


global dirPath
dirPath = "./ODPairs/"
global EARTH_RADIUS
EARTH_RADIUS = 6378.137
global Dis_sort_size
Dis_sort_size = 0
global ID_sort_size
ID_sort_size = 0
global totalLines
totalLines = 0

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
        print "|        Folder ", '"', path , '"', " already exists", "              |"


def update_progress(progress):
    
    ''' Display or updates a console loading bar. Accept a float between 0 and 1.
        Any int will be converted to a float. A value under 0 represents a 'halt' 
        A value at 1 or bigger represents 100% 
    
        Parameters
        ----------------------------------------
        The value indicating the current progress
        ----------------------------------------
       
    '''
    
    barLength = 10  # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength * progress))
    text = "\r|    Percent: [{0}] {1}% {2}".format("#"*block + "-"*(barLength - block), int(progress * 100), status)
    
    sys.stdout.write(text)
    sys.stdout.flush()

def bufcount(filename):
    ''' Given a file, figure out its total number of lines'''
    
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read  # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    f.close()
    return lines

def sanityCheck(entry):
    # legal format for an entry requires 10 slots of info, even the slot is 
    # is empty itself, there should be an "" to indicate the position 
    if len(entry.split(",")) <= 9:
        return -1
        
    div = entry.split(",")
    # call modify function before return to remove the "|" in some entries
    result = modify(mytrim(div[len(div) - 1]))
    # for those entries lacking category id info or having illegal category id
    if cmp(result, "") == 0 or not isNumber(result):
        return -1
    
    return 0

def processAndStore(filePath, entries, illegalList):
    
    '''Open the file according to the given file path, read each entry, 
    calculate its sphere distance against the reference point. 
    Store its result at the end of the line
    
    Parameters
    -----------------
    filePath: String
    
    entries:  List ( the one used to store the file contents by lines )
    -----------------
    
    '''
    try:
        fp = io.open(filePath, mode="r", encoding="utf-8")
    except IOError:
        print "|    Error: Fail to read from file"
        print "==============================================================="
        sys.exit(1)
    
    # Get the total number of lines in advance to calculate the progress
    lineNo = bufcount(filePath)    
    count = 1
    print "|    Begin to process and store file: "
    for line in fp:
        # ignore those entries with irregular formats or too little information
        update_progress(count / float(lineNo))
        count = count + 1
        
        # store those problematic lines for later use
        if sanityCheck(line) == -1:
            illegalList.append(mytrim(line))
            continue
        
        # calculate the sphere distance between current point and given reference point
        dis = getDistance(args.latitude, args.longitude, extractLatitudes(line), extractLongitude(line))
        # remove leading and trailing white spaces
        line = mytrim(line)
        # In Python, all floats or non String types must be casted to Strings before concatenation
        line = line[:] + "," + str(dis)
        
        entries.append(mytrim(line))
        
    fp.close()
    
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
                writer.write(unicode(line))
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
    list_of_tuples = []
    
    fname = extract_filename(args.filePath) + "RandomPairs.xml"
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    
    if args.debug:
        fname_debug = extract_filename(args.filePath) + "RandomPairs.dat"
        writer_debug = io.open(dirPath + fname_debug, "w", encoding="utf-8")
    
    writeHeading(writer)
    
    for i in range(0, args.numberOfPairs):
        no = i + 1
        
        startNo = random.randint(0, len(entries) - 1)
        endNo = random.randint(0, len(entries) - 1)
        ODPair = (startNo, endNo)
        
        while ODPair in list_of_tuples:
            startNo = random.randint(0, len(entries) - 1)
            endNo = random.randint(0, len(entries) - 1)
            ODPair = (startNo, endNo)
            
        list_of_tuples.append(ODPair)
        
        writeOneODPair(writer, startNo, endNo, no)
        
        if args.debug:
            content = entries[startNo] + " -----> " + entries[endNo] + "\n"
            writer_debug.write(content)
    
    
    writeEnding(writer)
        
        
    print "|        produce " + fname + "                      "
    
    if args.debug:
        print "|        Debug Mode On:                               "
        print "|            produce " + fname_debug
       
    writer.close()
    if args.debug:
        writer_debug.close()
    
def sort(entries, pattern):
    '''Invoke Quick Sort algorithm on the given data according to
       the Pattern provided
       
       Parameters
       -----------------
       entries: List
           The list stores all the contents from the input file by lines
       
       pattern: 
            CATEGORYID: sort by the category id in ascending order
            DISTANCE: sort by the distance in ascending order
    '''

    if cmp(pattern, "CATEGORYID") == 0:
        print "|"
        print "|    Sort by category id                                      |"
        sortHelper_ID(entries, 0, len(entries) - 1)
        print "|                                                             |" 
    elif cmp(pattern, "DISTANCE") == 0:
        print "|"
        print "|    Sort by distance                                         |"
        sortHelper_Dis(entries, 0, len(entries) - 1)
        print "|                                                             |" 

def sortHelper_ID(vals, i, k):
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
        insertionSortByCategoryID(vals, i, k)
        
        global ID_sort_size
        ID_sort_size = ID_sort_size + (k - i + 1)
        update_progress(ID_sort_size / float(len(vals)))
        return 
    
    j = partitionByCategoryID(vals, i, k)
    sortHelper_ID(vals, i, j)
    sortHelper_ID(vals, j + 1, k)
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
        
        global Dis_sort_size
        Dis_sort_size = Dis_sort_size + (k - i + 1)
        update_progress(Dis_sort_size / float(len(vals)))
        return
    
    j = partitionByDis(vals, i, k)
    sortHelper_Dis(vals, i, j)
    sortHelper_Dis(vals, j + 1, k)
    return 

def partitionByCategoryID(vals, i, k):
    '''Partition the given data through comparing with the pivot produced by getMedium
    
        Parameters:
        -----------------
        Same as sortHelper_Zip
        -----------------
        
    '''
    temp = ""
    done = False
    pivot = extractCategoryID(vals[getMedium_Zip(vals, i, k)])
    l = i
    h = k
    
    while not done:
        while extractCategoryID(vals[l]) < pivot:
            l = l + 1
        while pivot < extractCategoryID(vals[h]):
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
    
    medium = extractCategoryID(vals[i + (k - i) / 2])
    head = extractCategoryID(vals[i])
    tail = extractCategoryID(vals[k])
    
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
    
    if medium == extractCategoryID(vals[i + (k - i) / 2]):
        return i + (k - i) / 2
    elif medium == extractCategoryID(vals[i]):
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

def insertionSortByCategoryID(vals, i, k):
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
        while sc > head and extractCategoryID(vals[sc]) < extractCategoryID(vals[sc - 1]):
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


def extractCategoryID(line):
    '''Extract the category id from the given line
    
    '''
    
    div = line.split(",")
    # call modify function before return to remove the "|" in some entries
    result = modify(mytrim(div[len(div) - 2]))
    # for those entries lacking category id info or having illegal category id
    if cmp(result, "") == 0 or not isNumber(result):
        return -1
    return int(result)

def closeCategoryID(entries):
    '''produce an OD pair that the start point and end point have min difference
    
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    # Using a list to store every OD Pair as a tuple
    list_of_tuples = []
    
    
    fname = extract_filename(args.filePath) + "CloseCategoryID.xml"
    
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    
    if args.debug:
        fname_debug = extract_filename(args.filePath) + "CloseCategoryID.dat"
        writer_debug = io.open(dirPath + fname_debug, "w", encoding="utf-8")
    
    # add the format heading

    writeHeading(writer)
    
    for i in range(0, args.numberOfPairs):
        no = i + 1
        
        startNo = random.randint(0, len(entries) - 1 - 100)
        endNo = random.randint(startNo, startNo + 100)
        
        # store the index of O and D in a tuple
        ODPair = (startNo, endNo)
        
        # if this pair of OD has already been generated before
        while ODPair in list_of_tuples:
            startNo = random.randint(0, len(entries) - 1 - 100)
            endNo = random.randint(startNo, startNo + 100)
            ODPair = (startNo, endNo)
        
        list_of_tuples.append(ODPair)
        
        writeOneODPair(writer, startNo, endNo, no)
        
        if args.debug:
            content = entries[startNo] + " -----> " + entries[endNo] + "\n"
            writer_debug.write(content)
            
       
       
    writeEnding(writer)
        
       
    print "|        produce " + fname + "                  "
    
    if args.debug:
        print "|        Debug Mode On:                               "
        print "|            produce " + fname_debug
        print "|"
        
    writer.close()
      
    if args.debug: 
        writer_debug.close()
    
def distinctCategoryID(entries):
    '''Produce an OD pair that the start point and end point have max difference
        
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    
    list_of_tuples = []
    
    fname = extract_filename(args.filePath) + "DistinctCategoryID.xml"
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    
    if args.debug:
        fname_debug = extract_filename(args.filePath) + "DistinctCategoryID.dat"
        writer_debug = io.open(dirPath + fname_debug, "w", encoding="utf-8")

    writeHeading(writer)
    
    
    for i in range(0, args.numberOfPairs):
        no = i + 1
        startNo = random.randint(0, 200)
        endNo = random.randint(len(entries) - 1 - 200, len(entries) - 1)
        
        # store the index of O and D in a tuple
        ODPair = (startNo, endNo)
        
        while ODPair in list_of_tuples:
            startNo = random.randint(0, 200)
            endNo = random.randint(len(entries) - 1 - 200, len(entries) - 1)
            ODPair = (startNo, endNo)
        
        list_of_tuples.append(ODPair)
        
        writeOneODPair(writer, startNo, endNo, no)
        
        if args.debug:
            content = entries[startNo] + " -----> " + entries[endNo] + "\n"
            writer_debug.write(content)
            
    writeEnding(writer)  
    
    print "|        produce " + fname + "               " 
    
    if args.debug:
        print "|        Debug Mode On:                               "
        print "|            produce " + fname_debug
        print "|"
        
    writer.close()
    if args.debug:
        writer_debug.close()
    
def smallDisFromRef(entries):
    '''After sorting by distance from reference point, equally divide the whole data into three parts
    we think all the data in the first part has relatively small sphere distance.
    
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    
    interval = len(entries) / 3
    list_of_tuples = []
    
    fname = extract_filename(args.filePath) + "SmallDisFromRef.xml"
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    
    if args.debug:
        fname_debug = extract_filename(args.filePath) + "SmallDisFromRef.dat"
        writer_debug = io.open(dirPath + fname_debug, "w", encoding="utf-8")
        
    writeHeading(writer)
    
    for i in range(0, args.numberOfPairs):
        no = i + 1
        startNo = random.randint(0, interval)
        endNo = random.randint(0, interval)
        ODPair = (startNo, endNo)
        
        while ODPair in list_of_tuples:
            startNo = random.randint(0, interval)
            endNo = random.randint(0, interval)
            ODPair = (startNo, endNo)
            
        list_of_tuples.append(ODPair)
        
        writeOneODPair(writer, startNo, endNo, no)
        
        if args.debug:
            content = entries[startNo] + " -----> " + entries[endNo] + "\n"
            writer_debug.write(content)
       
    writeEnding(writer)
    
    print "|        produce " + fname + "                  "
    
    if args.debug:
        print "|        Debug Mode On:                               "
        print "|            produce " + fname_debug
        print "|"
        
    
    writer.close()
    if args.debug:
        writer_debug.close()

def middleDisFromRef(entries):
    '''Same as smallDisFromRef function, randomly pick out OD pairs from the second part from 
    the given data after sorting by distance from the reference point
        
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    
    interval = len(entries) / 3
    list_of_tuples = []
    
    fname = extract_filename(args.filePath) + "MiddleDisFromRef.xml"
    
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    
    if args.debug:
        fname_debug = extract_filename(args.filePath) + "MiddleDisFromRef.dat"
        writer_debug = io.open(dirPath + fname_debug, "w", encoding="utf-8")
        
    writeHeading(writer)
    
    
    for i in range(0, args.numberOfPairs):
        no = i + 1
        startNo = random.randint(interval, 2 * interval)
        endNo = random.randint(interval, 2 * interval)
        ODPair = (startNo, endNo)
        
        while ODPair in list_of_tuples:
            startNo = random.randint(interval, 2 * interval)
            endNo = random.randint(interval, 2 * interval)
            ODPair = (startNo, endNo)
        
        list_of_tuples.append(ODPair)
        
        writeOneODPair(writer, startNo, endNo, no)
        if args.debug:
            content = entries[startNo] + " -----> " + entries[endNo] + "\n"
            writer_debug.write(content)
       
    writeEnding(writer)
    
    print "|        produce " + fname + "                 "
    
    if args.debug:
        print "|        Debug Mode On:                               "
        print "|            produce " + fname_debug
        print "|"
        
    writer.close()
    if args.debug:
        writer_debug.close()
    
def largeDisFromRef(entries):
    '''Same as smallDisFromRef function, randomly pick out OD pairs from the third part from 
    the given data after sorting by distance from the reference point
        
        Parameter:
        -----------------
        entries: List( same as other entries above)
        -----------------
        
    '''
    
    interval = len(entries) / 3
    list_of_tuples = []
    
    fname = extract_filename(args.filePath) + "LargeDisFromRef.xml"
        
    writer = io.open(dirPath + fname, "w", encoding="utf-8")
    
    if args.debug:
        fname_debug = extract_filename(args.filePath) + "LargeDisFromRef.dat"
        writer_debug = io.open(dirPath + fname_debug, "w", encoding="utf-8")
    
    writeHeading(writer)
    
    for i in range(0, args.numberOfPairs):
        no = i + 1
        startNo = random.randint(interval * 2, len(entries) - 1)
        endNo = random.randint(interval * 2, len(entries) - 1)
        ODPair = (startNo, endNo)
        
        while ODPair in list_of_tuples:
            startNo = random.randint(interval * 2, len(entries) - 1)
            endNo = random.randint(interval * 2, len(entries) - 1)
            ODPair = (startNo, endNo)
                
        list_of_tuples.append(ODPair)
        writeOneODPair(writer, startNo, endNo, no)
        
        if args.debug:
            content = entries[startNo] + " -----> " + entries[endNo] + "\n"
            writer_debug.write(content)
    
    writeEnding(writer)
        
      
    print "|        produce " + fname + "                  "
    
    if args.debug:
        print "|        Debug Mode On:                               "
        print "|            produce " + fname_debug
    
    writer.close()
    if args.debug:
        writer_debug.close()
    
def writeHeading(writer):
    '''Writting the beginning tag to the xml format output files'''
    
    heading = '''<?xml version='1.0' encoding='UTF-8'?>
<testSuite description="" env="win32_data_path=D:\denali_18Q1\;UseHistoricalSpeed=false;open_route_log=false;win32_config_path=D:\RoutingRegx\BackendConfig\denali\cn\;
win32_data_config_path=D:\denali_18Q1\\tiles\\access_config.json;" javaClass="TestRouting" name="routing">
  <input>
    <inputSet name="Test">\n'''
    
    # the 1st argument of write must be unicode
    writer.write(unicode(heading))  
     
def writeOneODPair(writer, startNo, endNo, no):
    ''' Generate a block of OD pairs. in the required XML format.
        
        writer: the file pointer
        startNo: the index of the origin
        endNo: the index of the destination
        no: the case number
        
    '''
    nameTag = '''      <testCase description="" name="Case_''' + str(no) + "\"" + ">\n"
    writer.write(unicode(nameTag))
        
    OrignlocationTag = '''        <param name="Orig" type="java.lang.String" value="''' + "OLL=" + \
        str(extractLatitudes(entries[startNo])) + "," + str(extractLongitude(entries[startNo])) + \
        "\"" + " />\n"
    writer.write(unicode(OrignlocationTag))
        
    DeslocationTag = '''        <param name="Dest" type="java.lang.String" value="''' + "DLL=" + \
        str(extractLatitudes(entries[endNo])) + "," + str(extractLongitude(entries[endNo])) + \
        "\"" + " />\n"
    writer.write(unicode(DeslocationTag))
        
    RouteStyle = '''        <param name="Routestyle" type="long" value="1" />\n'''
    writer.write(unicode(RouteStyle))
        
    endTag = '''      </testCase>\n'''
    writer.write(unicode(endTag))
    
def writeEnding(writer):
    # Add ending tag and other information as required to the output xml file
        blockEndTag = '''    </inputSet>
  </input>\n'''
        writer.write(unicode(blockEndTag))
    
        reference = '''  <ref fileName="../services.xml" />
    <services>
      <service description="sample test service" inputSet="Test" methodName="basicRouteTest" name="CN_Case" commonExpectations="routeSame">
        <rule name="status_comp_rule" parent="status_comp_rule" />
        <rule name="route_comp_rule" parent="route_comp_rule" />
        <rule name="edge_comp_rule" parent="edge_comp_rule" />
        <rule name="od_comp_rule" parent="od_comp_rule" />
        <rule name="edge_summary_comp_rule" parent="edge_summary_comp_rule" />
      </service>
    </services>
</testSuite>\n'''
    
        writer.write(unicode(reference))

def showIllegalContents(illegalList):
    '''Show the number of illegal lines. Produce the illegal lines collection
       under debug mode'''
    
    print "|     ProblematicLines: " + str(len(illegalList))
    print "|"
    fname = extract_filename(args.filePath) + "problematicLines.dat"
    filePath = dirPath + fname
    debug_Output(illegalList, filePath)
             
'''I was going to use enum at the very beginning. However, it seems that not all Python2.7 has enum module...'''
# SortPattern = Enum('SortPattern', 'DISTANCE ZIPCODE')

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
        print "|    Number of pairs per file provided: ", args.numberOfPairs, "                 "
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
    print "|        Reference latitude: ", args.latitude, "  Reference longitude: ", args.longitude, ""

    if args.filePath:
        print "|        File path provided: ", '"', args.filePath, '"', "             "
    else:
        print "|        Using default file path"
        args.filePath = "./Shanghai3.csv"

    if args.debug:
        print "|        Debug Mode On", "                                       |"
    else:
        print "|        Debug Mode Off", "                                      |"

    
    print "|-------------------------------------------------------------|"
    print "|    Start processing the data......", "                         |"
    mkdir(dirPath)
    entries = []
    illegalList = []
    processAndStore(args.filePath, entries, illegalList)
    print "|    Total number of lines: ", len(entries), "                           "
    print"|                                                             |"
    
   
    totalLines = len(entries)
    
    debug_Output(entries, dirPath + extract_filename(args.filePath) + "Debug.dat")
    generateRandomPairs(entries)

  
    sort(entries, "DISTANCE")
    
    
    debug_Output(entries, dirPath + extract_filename(args.filePath) + "SortedByDistance.dat")
    smallDisFromRef(entries)
    middleDisFromRef(entries)
    largeDisFromRef(entries)
 
    sort(entries, "CATEGORYID")
  
    debug_Output(entries, dirPath + extract_filename(args.filePath) + "SortedByCategoryID.dat")
    closeCategoryID(entries)
    distinctCategoryID(entries)
    
    showIllegalContents(illegalList)
    gc.collect()
    print "|     ALL FINISH!                                             |"
    print "==============================================================="
