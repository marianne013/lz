#!/usr/bin/env python
"""
Checks for files that are at the UKDC, but not at NERSC,
to follow uptransfer failures
Input: List of files for a given day present at NERSC
If given a target directory: ./compare.py -s mytargetdir
it will generate semaphores for the files missing at NERSC
"""
from __future__ import print_function
import os
import glob
import subprocess
import argparse
import shlex

PREFIX = "/pnfs/hep.ph.ic.ac.uk/data/lz"

SHFILETEXT = r"""#!/bin/bash
remote_site=$1
file=$2
current_dir=${PWD}
base=$(basename $file | cut -d . -f 1)
dir=$(dirname $file)
IFS="/" read -ra DIRS <<< ${file}
dropbox=%s
sem_file=${dropbox}/${remote_site}/${base}.mdc3
if [[ -e ${sem_file} ]]; then exit; fi
cd ${dir}
adler=$(printf '%%d' 0x$(cat ".(get)(${base}.root)(checksum)" | grep ADLER32 | cut -d : -f 2 ))
size=$(stat -c%%s ${file})
type=${DIRS[8]}
equip=${DIRS[7]}
#source=${DIRS[11]}
read baccarat_vers source der_vers < <(echo ${DIRS[9]} | sed -e 's/BACCARAT-\([0-9.]\+\)_\(.\+\)-\([0-9.]\+\)/\1 \2 \3/')
# cat << EOF
echo ${sem_file}
cat > ${sem_file} << EOF
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<lz_metadata>
    <original_path>${file}</original_path>
    <adler32>${adler}</adler32>
    <file_size>${size}</file_size>
    <baccarat_vers>${baccarat_vers}</baccarat_vers>
    <der_vers>${der_vers}</der_vers>
    <equipment>${equip}</equipment>
    <source>${source}</source>
    <type>${type}</type>
</lz_metadata>
EOF
"""


def process_nersc(filename):
    files_at_nersc = []
    fd = open(filename)
    for line in fd.readlines():
        line = line.split()
        # [4] == filesize
        # [8] == filename
        # in first try only use the file name
        files_at_nersc.append(line[8])
    print("There are %s files at NERSC." %len(files_at_nersc))
    return files_at_nersc



def process_files(file_location, day):
    """generates a list containing the names of all the existing mc data
    files for a given day"""
    # construct file path
    file_dir = PREFIX+file_location
    file_pattern = file_dir+'lz_'+day+'*_raw.root'
    # print(file_pattern)
    file_list = glob.glob(file_pattern)
    print("There are %s MC files in the requested directory (%s)." %(len(file_list), file_dir))
    file_names = []
    for f in file_list:
        file_name_only = f.split('/')
        file_names.append(file_name_only[-1])
    return file_names


def main():
    # specify all input here
    day = "20180303"
    imperial_location = "/lz/data/MDC3/commissioning/BACCARAT-4.10.3_DER-8.5.13/20180303"
    nersc_file = "nersc_20180303.txt"

    #day = "20180222"
    #imperial_location = "/lz/data/MDC3/commissioning/BACCARAT-4.9.11_DER-8.5.13/20180222"
    #nersc_file = "nersc_20180222.txt"

    #day = "20180204"
    #imperial_location = "/lz/data/MDC3/calibration/BACCARAT-4.9.9_DER-8.5.7/20180204"
    #nersc_file = "nersc_20180204.txt"



    # deciding whether or not to generate the semaphores is a command line argument
    parser = argparse.ArgumentParser(description='Assess the damage')
    parser.add_argument('-s', '--semaphore', help='generate sempaphores for missing files, needs target fir for semaphores', required=False)
    args = vars(parser.parse_args())

    print("Processing Day: %s\n" %day)

    make_semaphore = False
    semaphore_dir = ''
    if args['semaphore'] != None:
        make_semaphore = True
        semaphore_dir = args['semaphore']
        print("Auto-generating semaphores for missing files in %s" %semaphore_dir)
        # target dir must exist, if it doesn't, create it
        if semaphore_dir[-1] != '/':
            semaphore_dir = semaphore_dir+'/'
        semaphore_dir = "/pnfs/hep.ph.ic.ac.uk/data/lz/spade/semaphores/"+semaphore_dir
        print(semaphore_dir)
        if not os.path.exists(semaphore_dir):
            os.makedirs(semaphore_dir)
        semaphore_dir_usdc = semaphore_dir+"usdc"
        if not os.path.exists(semaphore_dir_usdc):
            os.makedirs(semaphore_dir_usdc)

        semscript = open("mksemaphore.sh", 'w')
        semscript.write(SHFILETEXT % (semaphore_dir))
        semscript.close()
        os.chmod('mksemaphore.sh', 0o755)


    if imperial_location[-1] != '/':
        imperial_location = imperial_location+'/'


    # Case 1: Files at Imperial, not at NERSC
    files_at_nersc = process_nersc(nersc_file)
    files_at_imperial = process_files(imperial_location, day)
    file_counter = 0
    outputfile = "redo_these_"+day+".txt"
    fd1 = open(outputfile, "w")

    n_processed = 0
    for root_file in files_at_imperial:
        if root_file not in files_at_nersc:
            file_counter = file_counter+1
            # at this point I need the full file name, hmmmmm
            # just reconstruct it for now
            missing_file = PREFIX+imperial_location+root_file
            if make_semaphore:
                n_processed = n_processed+1
                if (n_processed%500 == 0):
                    print("Generating semphore number %s" %n_processed)
                # subprocess.call(['/opt/spade/not_at_nersc/test.sh'])
                command_string = '/opt/spade/not_at_nersc/mksemaphore.sh usdc %s' %missing_file
                subprocess.call(shlex.split(command_string))
                # subprocess.call(shlex.split('/opt/spade/not_at_nersc/mksemaphore.sh usdc
                # /pnfs/hep.ph.ic.ac.uk/data/lz/lz/data/MDC3/commissioning/BACCARAT-4.9.11_DER-8.5.13/20180302/lz_201803021405_000081_004381_raw.root'))
                # subprocess.check_call(['/opt/spade/not_at_nersc/mksemaphore.sh', 'usdc', 
                # '/pnfs/hep.ph.ic.ac.uk/data/lz/lz/data/MDC3/commissioning/BACCARAT-4.9.11_DER-8.5.13/20180302/lz_201803021405_000081_004381_raw.root'])
                # last time I lost a file, how can that happen ?
            print(missing_file, file=fd1)
    print("There are %s files missing at NERSC." %file_counter)
    fd1.close()

    # Case 2: Files at NERSC, not at Imperial
    # (I thought this wouldn't happen, but it does)

    file_counter = 0
    outputfile = "only_at_nersc_"+day+".txt"
    fd2 = open(outputfile, "w")
    for root_file in files_at_nersc:
        if root_file not in files_at_imperial:
            file_counter = file_counter+1
            print(root_file, file=fd2)

    print("There are %s files only present at NERSC." %file_counter)
    fd2.close()

if __name__ == "__main__":
    main()
