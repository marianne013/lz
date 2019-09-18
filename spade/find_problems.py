#!/usr/bin/env python
"""
Two cases considered:
a) semaphore exists, but no matching file
b) file exists, but no matching semaphore
LZ MC data are organized by days, hence comparison is day-by-day.
"""
from __future__ import print_function

import sys
import glob
import re

PREFIX = "/pnfs/hep.ph.ic.ac.uk/data/lz"


def process_semaphores(semaphore_location, day):
    """generates a list containing the names of all the existing semaphores
    files for a given day"""
    file_dir = PREFIX+semaphore_location
    file_pattern = file_dir+'lz_'+day+'*_raw.mdc3'
    file_list = glob.glob(file_pattern)
    print("There are %s semaphore files in the requested directory (%s)."
          %(len(file_list), file_dir))
    return file_list

def process_files(file_location, day):
    """generates a list containing the names of all the existing mc data
    files for a given day"""
    # construct file path
    file_dir = PREFIX+file_location
    file_pattern = file_dir+'lz_'+day+'*_raw.root'
    # print(file_pattern)
    file_list = glob.glob(file_pattern)
    print("There are %s MC files in the requested directory (%s)." %(len(file_list), file_dir))
    # fd = open("debug_me", "w")
    # fd.write(str(file_list))
    # fd.close()
    return file_list

def sem_sanity_check(mcfile, mcsem):
    """checks if a semaphore file refers to the correct file"""
    # read in semaphore file and extract file name
    # this needs a time out
    with open(mcsem, 'r') as semfile:
        # print("opened")
        contents = semfile.read()
        # print("read")
        result = re.search('<original_path>(.*)</original_path>', contents)
        if result:
            ref_file_in_sem = result.group(1)
            if ref_file_in_sem == mcfile:
                return True
            else:
                print("Error: Semaphore file does not match data file: \n%s\n%s"
                      %(ref_file_in_sem, mcfile))
                return False
        else:
            print("Error: No match for root file found in %s" %mcsem)
def sem_file_name(mcfile):
    """finds/generates the filename for a semaphore to match the
    MC data file name"""
    filename = mcfile.split('/')[-1]
    # to construct the sem file, remove .root and replace with .mdc3
    sem_filename = filename[:-4]+'mdc3'
    return sem_filename

def mc_file_name(semfile):
    """finds/generates the root file name matching a given 
    semaphore file name"""
    filename = semfile.split('/')[-1]
    # to construct the mc file, remove .mdc3 and replace with .root
    mc_filename = filename[:-4]+'root'
    return mc_filename


def main():
    # example paths
    # /pnfs/hep.ph.ic.ac.uk/data/lz/spade/sending/usdc/MDC3/BACCARAT-_DER-/lz_201802170159_000047_007117_raw.mdc3
    # /pnfs/hep.ph.ic.ac.uk/data/lz/lz/data/MDC3tests/jsitests/lz_201802170159_000047_007117_raw.root
    # TODO: These should become input parameters

    # specify everthing here

    # mc_dir = "/lz/data/MDC3/commissioning/BACCARAT-4.9.11_DER-8.5.13/20180222"
    # mc_dir = "/lz/data/MDC3/commissioning/BACCARAT-4.9.11_DER-8.5.13/20180302"
    # mc_dir = "/lz/data/MDC3/calibration/BACCARAT-4.9.9_DER-8.5.7/20180204"
    mc_dir = "/lz/data/MDC3/commissioning/BACCARAT-4.10.3_DER-8.5.13/20180303"

    # sem_dir = "/spade/sending/usdc/MDC3/BACCARAT-4.9.11_DER-8.5.13/"
    # sem_dir = "/spade/semaphores/verytmp/usdc/"
    # sem_dir = "/spade/sending/usdc/MDC3/BACCARAT-4.10.3_DER-8.5.13"
    # sem_dir = "/spade/semaphores/newtest/20180303/usdc"
    sem_dir = "/spade/sending/usdc/MDC3/test/"

    # day = "20180222"
    # day = "20180204"
    day = "20180303"

    # all done


    # too many typos
    if mc_dir[-1] != '/':
        mc_dir = mc_dir+'/'
    if sem_dir[-1] != '/':
        sem_dir = sem_dir+'/'

    print("Processing data for %s\n" %day)
    # sanity check:
    if len(day) != 8:
        print("Wrong date format, must be YYYYMMDD")
        sys.exit(0)

    mc_file_list = process_files(mc_dir, day)
    sem_file_list = process_semaphores(sem_dir, day)

    # check 1: data exists, but no matching semaphore
    print("checking for missing semaphores")
    output_file_name = "missing_semaphore_files_"+day+".txt"
    no_sem = open(output_file_name, "w")

    i = 0
    for mfile in mc_file_list:
        i = i+1
        if i%500 == 0:
            print("Processing file %s" %i)
        sem_file = str(sem_file_name(mfile))
        full_sem_file = PREFIX+sem_dir+sem_file
        # print(full_sem_file)
        if full_sem_file not in sem_file_list:
            no_sem.write("%s\n" %mfile)
        else:
            if not sem_sanity_check(mfile, full_sem_file):
                print ("Mismatched semaphore: %s\n" %mfile)
                no_sem.write("Mismatched semaphore: %s\n" %mfile)
            else:
                pass
    no_sem.close()

    # check 2: semaphore exists, but no matching data
    # this should never happen....
    print("\nchecking for missing files")
    output_file_name = "missing_mcdata_files_"+day+".txt"
    no_mc = open(output_file_name, "w")
    i = 0
    for sfile in sem_file_list:
        i = i+1
        if i%500 == 0:
            print("Processing file %s" %i)
        mc_file = str(mc_file_name(sfile))
        full_mc_file = PREFIX+mc_dir+mc_file
        if full_mc_file not in mc_file_list:
            no_mc.write("%s\n" %sfile)
        else:
            pass
    no_mc.close()
if __name__ == "__main__":
    main()
