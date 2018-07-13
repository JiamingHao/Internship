There are two small programs.  The program written in 
python2.7 is the main OD pairs generator. The one named generator_driver is a 
bash shell script.

For the purpose of giving one particular csv file and generate OD pairs 
from that. Just invoke the python program by itself, the syntax is:
 				
				python2 ODGenerator.py [-f filePath] [-n numOfPairs] [-la latitude] [-lo longitude] [-d]
				(if corresponding command line arguments are not provided, it will use defaults)

 			[numOfPairs]: represents the number of OD pairs you want to generate in each 
					output file eg. "python2 ODGenerator.py -n 100" will make the script 100 pairs of OD in each output file using different strategies.
					default num of pairs: 50

			[filePath]:represents the input file path
					default file path: ./Shanghai3.csv

 			[latitude] and [longitude]: these two arguments are related with 
 					the strategy used in generating the OD pairs.(see below for details)
					default latitude: 0.0
					default longitude:0.0

 			[-d]: when the -d flag is turned on the program will run in debug mode. It will generate debug 
					files after each sorting operation.(see below for details)

 	Altogether there are six methods to generate OD pairs, each of them will produce a single output 
file with the name in the format of [inputFileName][methodName].xml. All the methods guarantee that
no duplicate OD pairs (pairs with the same starting and ending points) will be generated more than 
once in one file.

			generateRandomPairs: just randomly generate OD pairs

			closeCategoryID: sort all the entries by their category id, and then produce OD pairs having 
                              very close category id, usually this will produce OD pairs with the same category id.

			distinctCategoryID: sort all the entries by their category id, produce OD pairs having most distinct category id

			smallDisFromRef: sort all the entries by their distance from given reference point or from default(latitude: 0.0 longitude: 0.0)
                              then produce OD pairs having comparatively small sphere distance from the reference point.

			middleDisFromRef: same as the previous except producing OD pairs having comparatively medium sphere distance from the point.

			largeDisFromRef: same as the previous except producing OD pairs having comparatively large sphere distance from the point.

	The bash script is used for the situation when users want to batch process a large number of input files. Since it is written in 
bash, it can only be run in OS with bash shell. To run the script, make sure that you give the script execution permission,
the script and the ODGenerator program need to be in the same directory, and all the input files neeeded to be put in a directory named POI. When running, 
the script will scan all the files in the POI directory and automatically invoke the Generator on them. All the output files will be put in 
a directory called ODPairs (same as invoking the ODGenerator by itself)

	User can just invoke the bash shell script generator_driver by itself with no command line arguments or specify the path of the directory storing all 
the input csv files you want to run the Generator on in one time as well as telling how many pairs of OD are required in each file and providing reference 
latitude and longitude.Usage of the bash shell script is:

			generator_driver [[-f|--file DirectoryPath ] [-n|--numOfPairs NumberOfPairs] [-d|--debug] [-h|--help] [-la|--latitude reference latitude] [-lo|--longitude reference longitude]]

			default directory path: ./POI
			default numOfPairs: 50
			default reference latitude: 0.0
			default reference longitude: 0.0

Other points to notice:
			It turns out that some entries in some files have irregular format. For instance, the 4327th entry of Qinghai0.csv,which is 
 			'"803486270","海西供电公司�', entries like this will be ignored

 			The program is only tested with the POI inputs of China, for POI from foreign countries, it might work, but no guarantee.

			For those entries with no category id provided, the program will recognize them as the ones with the smallest zip codes by default.

			For those entry having optional category id, such as 34|1098.... The program will only consider the first one

			All the problematic lines in each input file will be collected and produce a report for them under debug mode

	Thanks for your reading.
 