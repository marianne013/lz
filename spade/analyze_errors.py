#!/usr/bin/env python
"""
The errors are grouped by type:
(a) examiner.FileToken
(b) pre_shipper.FileToken
(c) fetcher.FileToken
(d) post_shipper.FileToken
(e) Parallel Gateway
(f) gather fork
(g) scatter fork
(h) places
(i) other
"""

from __future__ import print_function
import sys
import argparse
import os
import glob
import re
import datetime as dt


def dirs_in_time_range(time_in_hours):
    """ returns a list of error log directories in a given time frame
    (hours before now)"""
    now = dt.datetime.now()
    ago = now-dt.timedelta(hours=int(time_in_hours))
    basepath = '/pnfs/hep.ph.ic.ac.uk/data/lz/spade/cache/problems'
    error_dirs = []
    for cdir in os.listdir(basepath):
        path = os.path.join(basepath, cdir)
        osstat = os.stat(path)
        mtime = dt.datetime.fromtimestamp(osstat.st_mtime)
        if mtime > ago:
            error_dirs.append(path)
            # print('%s modified %s'%(path, mtime))

    return error_dirs

def find_affected_files(files_string, stacktrace):
    """tries to find the files (semaphore or root files) affected by an error;
    searches the 'files' and 'files/payload' dirs and the stacktrace if present;
    returns a list of files"""
    file_list = []
    if os.path.isdir(files_string):
        file_pattern = files_string+'*_raw.mdc[2|3]'
        file_list = glob.glob(file_pattern)
    payload_string = files_string+'payload/'
    if os.path.isdir(payload_string):
        file_pattern = payload_string+'*root'
        rootfile = (glob.glob(file_pattern))
        if rootfile:
            file_list.append(rootfile[0])
    if os.path.isfile(stacktrace):
        stackfile = open(stacktrace, "r")
        stackfile_content = stackfile.read()
        result = re.search('/pnfs/hep.ph.ic.ac.uk/data/lz(.+?).mdc[2|3]', stackfile_content)
        if result:
            affected_file = result.group(0)
            file_list.append(affected_file)
    return file_list


def error_type(error_dir):
    """determines the type of error for each error directory"""
    # get files in directory and check if any of the keywords are present
    content = os.listdir(error_dir)
    files_string = error_dir+"/files/"
    stacktrace = error_dir+"/throwable.stacktrace"
    err_number = error_dir.split('/')[-1]
    file_list = []
    matching = [s for s in content if "examiner" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['examiner', err_number, file_list]
        return summary

    matching = [s for s in content if "pre_shipper" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        # preshipper errors tend not to contain the filename in the stacktrace
        file_pattern = error_dir+'/pre_shipper.FileToken_*'
        error_file = glob.glob(file_pattern)
        if len(error_file) == 1:
            error_log = open(error_file[0], "r")
            error_content = error_log.read()
            result = re.search('/pnfs/hep.ph.ic.ac.uk/data/lz(.+?).mdc[2|3]', error_content)
            if result:
                affected_file = result.group(0)
                file_list.append(affected_file)
        else:
            print("More than one error log for preshipper error found, please check.")
        summary = ['pre_shipper', err_number, file_list]
        return summary

    matching = [s for s in content if "fetcher" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['fetcher', err_number, file_list]
        return summary

    matching = [s for s in content if "post_shipper" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['post_shipper', err_number, file_list]
        return summary

    matching = [s for s in content if "Parallel" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['parallel_gateway', err_number, file_list]
        return summary

    matching = [s for s in content if "gather.fork" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['gatherfork', err_number, file_list]
        return summary

    matching = [s for s in content if "scatter.fork" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['scatterfork', err_number, file_list]
        return summary

    matching = [s for s in content if "placer" in s]
    if matching:
        file_list = find_affected_files(files_string, stacktrace)
        summary = ['placer', err_number, file_list]
        return summary

    # other errors
    file_list = find_affected_files(files_string, stacktrace)
    print("Uncategorized error in %s" %err_number)
    summary = ['other', err_number, file_list]
    return summary



def main():
    print("Looking for errors in /pnfs/hep.ph.ic.ac.uk/data/lz/spade/cache/problems/")
    parser = argparse.ArgumentParser(description='Tally errors')
    parser.add_argument('-t', '--time', help='time range for errors in hours, default 24',
                        required=False)
    args = vars(parser.parse_args())

    time_range = 24
    if args['time'] != None:
        time_range = args['time']

    error_dirs = dirs_in_time_range(time_range)
    error_summaries = []
    n_of_fetch = 0
    n_of_pre = 0
    n_of_ex = 0
    n_of_post = 0
    n_of_para = 0
    n_of_gfork = 0
    n_of_sfork = 0
    n_of_placer = 0
    n_of_other = 0

    if not error_dirs:
        print("No errors found in the last %s hours." %time_range)
        sys.exit(0)
    else:
        for edir in error_dirs:
            error_summary = error_type(edir)
            if error_summary[0] == "fetcher":
                n_of_fetch = n_of_fetch+1
            elif error_summary[0] == "pre_shipper":
                n_of_pre = n_of_pre+1
            elif error_summary[0] == "examiner":
                n_of_ex = n_of_ex+1
            elif error_summary[0] == "post_shipper":
                n_of_post = n_of_post+1
            elif error_summary[0] == "parallel_gateway":
                n_of_para = n_of_para+1
            elif error_summary[0] == "gatherfork":
                n_of_gfork = n_of_gfork+1
            elif error_summary[0] == "scatterfork":
                n_of_sfork = n_of_sfork+1
            elif error_summary[0] == "placer":
                n_of_placer = n_of_placer+1
            else:
                n_of_other = n_of_other+1

            # I might want to do something with this later
            error_summaries.append(error_summary)

    print("\nThere were %s errors in the last %s hours." %(len(error_summaries), time_range))
    print("Number of fetcher errors: %s" %n_of_fetch)
    print("Number of examiner errors: %s" %n_of_ex)
    print("Number of pre_shipper errors: %s" %n_of_pre)
    print("Number of post_shipper errors: %s" %n_of_post)
    print("Number of Parallel Gateway errors: %s" %n_of_para)
    print("Number of gather fork errors: %s" %n_of_gfork)
    print("Number of scatter fork errors: %s" %n_of_sfork)
    print("Number of placer errors: %s" %n_of_placer)
    print("Number of other errors: %s" %n_of_other)

    print("\nDirectly affected files found in the logs:")
    for es in error_summaries:
        if es[2]:
            print(es[1], es[0], es[2][0])


if __name__ == "__main__":
    main()
