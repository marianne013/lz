#!/usr/bin/env python

# reads in list of broken raw files and finds the matching mctruth files
# converts both to a handy pair of lfns

import sys

fd = open(sys.argv[1], "r")

outfilename = "brokenlfns_"+sys.argv[1][-14:-4]+".txt"

outfile = open(outfilename, "w")

i = 0

for line in fd:
  line = line.strip()
  filenamebits = line.rsplit('_',2)
  # check this is a raw file
  print line
  # pad seed with leading zeros
  seed = filenamebits[1].zfill(5)
  
  # check this is a raw file
  if filenamebits[2] != "raw.root":
    print "This looks like an mc truth file ! Not doing anything"
    continue
  rawlfn = "/"+line.split('/',7)[-1]
  outfile.write("%s\n" % rawlfn)

  # can I construct the matching mctruth file ?
  # mctruth_filename = "lz_mdc1_07-01-2017" + padded seed + _mctruth.root
  firstpart =  line.split('/')[11]
  secondpart =  firstpart.split('-')[1]
  mctruth_filename = firstpart + "_7"+ secondpart + str(seed) + "_mctruth.root"
  mctruthlfn = rawlfn[0:58] + mctruth_filename
  outfile.write("%s\n" % mctruthlfn) 
  
fd.close()
outfile.close()
