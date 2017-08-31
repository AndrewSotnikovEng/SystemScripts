#! /usr/bin/python3
from subprocess import check_output, call, DEVNULL
from os.path import exists
from os import remove
from datetime import datetime
import re

#    Synchronize MEGA cloude drive with local files.
#    Main cycle divided into 3 sections:
#	
#	1. Removing files from cloud which is absent on local 
#	2. Removing file from cloud which has later modified time on local
#	3. Copying files to cloud.
#
#    Andrew Sotnikov 
#			aka Luca Brasi
#
#    andrew.sotnikov.eng@gmail.com
#    


locDirs = ["/media/Maindata/Книги/",
           "/media/Maindata/Дело/",
	   "/media/Maindata/install/"]

remDirs = ["/Root/Книги/",
           "/Root/Дело/",
	   "/Root/install/"]

# log location
log = "/var/log/megasync.log"                     
# config file location
id="--config /home/andrew/.megarc"


#define tmpLog
logTmp = "/tmp/megasync.log"
if(exists(logTmp)):
    print("removing Temporary log")
    remove(logTmp)

for i in range(len(locDirs)):
    locDir = locDirs[i]
    remDir = remDirs[i]
    
    # --- create directory on cloud drive if not exist
    dirExisted = check_output("megals {0} {1} | wc -l".format(id, remDir), shell=True, universal_newlines=True)
    dirExisted=dirExisted.strip()
    if (int(dirExisted) == 0):
        call('''megamkdir {0} "{1}"'''.format(id, remDir), shell=True, stderr=DEVNULL)    

    # --- delete localy absent files and directories from cloud drive																		
    absentFiles = check_output("megacopy {0} --dryrun --reload --download --local \"{1}\" --remote \"{2}\"".format(id,
				locDir, remDir), shell=True, universal_newlines=True, stderr=DEVNULL)


    for elem in absentFiles.split("\n"):
        try:
            # removing extrenerous in begin, D /path/to/file
            elem = re.search(r'/.*$',elem).group()
            elem = elem.replace(locDir, remDir)
            call("megarm {0} \"{1}\"".format(id, elem), shell=True, stderr=DEVNULL)
        except Exception:
            print(elem)


    # --- delete localy modified files from cloud drive...
    if(exists(log)):
        # ...using log modification as criterion
        modifiedFiles = check_output("find \"{0}\" -type f -newer \"{1}\"".format(locDir, log), shell=True, universal_newlines=True);
        for elem in modifiedFiles.split("\n"):
            elem = elem.replace(locDir, remDir)
            check_output("megarm {0} \"{1}\"".format(id, elem), shell=True, stderr=DEVNULL)


    # --- sync local data
    sync = check_output("megacopy --no-progress {0} --local \"{1}\" --remote \"{2}\"".format(id, locDir, remDir), shell=True, universal_newlines=True, stderr=DEVNULL)
    syncToLog = sync.replace(remDir, locDir)



    #getting current time
    now = datetime.now()

    # --- write results in log
    f = open(logTmp,"a")
    f.write("\n{0} synchronization to MEGA done!\n".format(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
    f.write("\n\tFiles removed:\n")
    f.write(absentFiles)
    f.write("\n\tFiles synchronized:\n")
    f.write(sync + "\n=================================================\n")
    f.close()

#writing info to permanent log
f = open(logTmp)
logData = f.read()
f.close()

f = open(log, "a")
f.write(logData)
f.close()


