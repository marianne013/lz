#!/bin/bash 
date 
pwd 
sleep 2
echo -e "\nChecking the environment \n"
ghostname=`hostname --long 2>&1` 
gipname=`hostname --ip-address 2>&1` 
echo $ghostname "has address" $gipname
uname -a
cat /etc/redhat-release
env | sort

if [ "$#" -ne 1 ]; then
    echo "This script requires exactly one argument: donotuploadbyhand, uploadbyhand or specifylfn."
    exit 0
fi

echo -e " \n ================================== \n"

# use some CPU to prevent job getting killed for sitting idle
# perl -e '$z=time()+(2*60); while (time()<$z) { $j++; $j *= 1.1 for (1..9999); }'

# to cover (most) bases, I will generate 3 outputfiles
# two ending in *.txt and a one ending in *.dat
MYDATE=`date +%s`
if [ -z "${DIRACSITE}" ]; then
  DIRACSITE=`hostname`
fi

env > testfile.${MYDATE}.${DIRACSITE}.txt
echo "This is the second testfile" > testfile.${MYDATE}.2.${DIRACSITE}.txt
echo "1 2 3 4 5 6 7 testing .... " > testfile.${MYDATE}.${DIRACSITE}.dat


# no wildcards allowed.
# of you sepcify the LFN you need to know the file name beforehand
if [ $1 = "specifylfn" ]; then
    env > testfile.lfn1.txt
    echo "This is the second testfile" > testfile.lfn2.txt
    echo "1 2 3 4 5 6 7 testing .... " > testfile.lfn3.dat
fi

    
# an example of uploading your data by hand using the dirac tools
# note that this is *not* the way the DIRAC developers envisioned this to work
# if you use this method, please *always* do a check on the return code and at least on retry to deal with intermittent failures
if [ $1 = "uploadbyhand" ]; then
    
    dirac-dms-add-file /gridpp/daniela.bauer/outputexamples/byhand/txt/testfile.${MYDATE}.${DIRACSITE}.txt testfile.${MYDATE}.${DIRACSITE}.txt UKI-LT2-IC-HEP-disk
    # if you do this, please always check if your upload has worked, and of not, try again in a couple of minutes, as failures are often transient
    if [ $? -ne 0 ]; then
	# wait 5 min and try again
	sleep 300
	dirac-dms-add-file /gridpp/daniela.bauer/outputexamples/byhand/txt/testfile.${MYDATE}.${DIRACSITE}.txt testfile.${MYDATE}.${DIRACSITE}.txt UKI-LT2-IC-HEP-disk
	if [ $? -ne 0 ]; then
	    echo "Upload failed even in second try."
	fi
    fi
    # make this fail (non-existing SE)
    dirac-dms-add-file /gridpp/daniela.bauer/outputexamples/byhand/txt/testfile.${MYDATE}.2.${DIRACSITE}.txt testfile.${MYDATE}.2.${DIRACSITE}.txt UKI-LT2-IC-HEP-nodisk
    ret_code=$?
    echo $ret_code
    if [ $ret_code -ne 0 ]; then
        # wait 5 min and try again, this time  with the correct SE
	sleep 300
        dirac-dms-add-file /gridpp/daniela.bauer/outputexamples/byhand/txt/testfile.${MYDATE}.2.${DIRACSITE}.txt testfile.${MYDATE}.2.${DIRACSITE}.txt UKI-LT2-IC-HEP-disk
        if [ $? -ne 0 ]; then
            echo "Upload failed even in second try."
	fi
    fi
    dirac-dms-add-file /gridpp/daniela.bauer/outputexamples/byhand/dat/testfile.${MYDATE}.${DIRACSITE}.dat testfile.${MYDATE}.${DIRACSITE}.dat UKI-LT2-IC-HEP-disk
    if [ $? -ne 0 ]; then
        # wait 5 min and try again
	sleep 300
        dirac-dms-add-file /gridpp/daniela.bauer/outputexamples/byhand/dat/testfile.${MYDATE}.${DIRACSITE}.dat testfile.${MYDATE}.${DIRACSITE}.dat UKI-LT2-IC-HEP-disk
        if [ $? -ne 0 ]; then
            echo "Upload failed even in second try."
        fi
    fi


fi


echo -e "\nI am done here."

