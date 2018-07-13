	There are two small programs in the zip file.  The program written in 
 python2.7 is the main OD pairs generator. The one named generator_driver is a 
 bash shell script.
 
    For the purpose of giving one particular file and generate OD pairs 
 according to it. Just invoke the python program by itself, the syntax is:
 				
 			ODGenerator.py [-f filePath] [-n numOfPairs] [-la latitude] [-lo longitude] [-d]
 
 			[numOfPairs]: represents the num of OD pairs you want to generate in each 
 					output file
 
 
			[filePath]:represents the input file path
 
 			[latitude] and [longitude]: these two arguments are related with 
 					the strategy used in generating the OD pairs.(see below for details)
 
 			[-d]: when the -d flag is turned on the program will run in debug mode. It will generate debug 
  					files after each sorting opreation.
 
 	Altogether there are six methods to generate OD pairs, each of them will produce a single output 
file with the name in the format of [inputFileName][methodName].dat. All the methods guarantee that
no duplicate OD pairs (pairs with the same starting and ending points) will be generated more than 
once in one file.

			generateRandomPairs: just randomly generate OD pairs

			minZipCodeDifference: sort all the entries by their zip code, and then produce OD pairs having 
                              very close zip code, usually this will produce OD pairs with the same zip code.

			largeZipCodeDifference: sort all the entries by their zip code, produce OD pairs having largest zip
                              code differnece

			smallDisFromRef: sort all the entries by their distance from given reference point or from default(latitude: 0.0 longitude: 0.0)
                              then produce OD pairs having comparatively small sphere distance from the reference point.

			middleDisFromRef: same as the previous except producing OD pairs having comparatively medium sphere distance from the point.

			largeDisFromRef: same as the previous except producing OD pairs having comparatively large sphere distance from the point.

	The bash script is used for the situation when users want to batch process a large number of input files. Since it is written in 
bash, it can only be run in OS with bash shell. To run the script, make sure that you give the script execution permission,
the script and the ODGenerator program need to be in the same directory, and all the input files neeeded to be put in a directory named POI. When running, 
the script will scan all the files in the POI directory and automatically invoke the Generator on them. All the output files will be put in 
a directory called ODPairs (same as invoking the ODGenerator by itself)
 
Other points to notice：
			It turns out that some entries in some files have irregular format. For instance, the 4327th entry of Qinghai0.csv,which is 
 			'"803486270","海西供电公司�', entries like this will be ignored

 			The program is only tested with the POI inputs of China, for POI from foreign countries, it might work, but no guarantee.

			For those entries with no zip codes provided, the program will recognize them as the ones with the smallest zip codes by default.

			For those entry having option zip codes, such as 34|1098.... The program will only consider the first one

	Thanks for your reading.
 