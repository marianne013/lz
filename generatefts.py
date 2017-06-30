#!/usr/bin/env python

# reads in file list (e.g. files_lz_mdc1_07-02-2017.txt.pass2) 
# in this format:
# root://gfe02.grid.hep.ph.ic.ac.uk/pnfs/hep.ph.ic.ac.uk/data/lz/lz/data/MDC1/BACCARAT-1.2.3_DER-4.4.0/lz_mdc1_07-02-2017/DER/lz_201707020000_000010_0_raw.root
#
# and transforms it into something fts understands:
# srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=/pnfs/hep.ph.ic.ac.uk/data/lz/lz/data/MDC1/BACCARAT-1.2.3_DER-4.4.0/lz_mdc1_07-01-2017/DER/lz_201707010000_000010_0_raw.root gsiftp://dtn01.nersc.gov:2811/global/project/projectdirs/lz/users/marianne/lz/data/MDC1/BACCARAT-1.2.3_DER-4.4.0/lz_mdc1_07-01-2017/DER/lz_201707010000_000010_0_raw.root
#
# cycles through the dtn transfer nodes: dtn01 to dtn11

import sys

NERSCPATH="/global/projecta/projectdirs/lz/data/mdc1/5d419e5756a4740eee95721281f8d6c3/"

fd = open(sys.argv[1], "r")

outfilename = "fts_"+sys.argv[1][-20:-10]+".txt"

outfile = open(outfilename, "w")

i = 0

for line in fd:
  i = i+1
  if i == 12:
    i = 1
  # avoid dtn03
  if i == 3:
    i = 4
  line = line.strip()
  # replace
  # root://gfe02.grid.hep.ph.ic.ac.uk 
  # with srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN
  ftsgfe02 = "srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=" + line[33:] 
  # print ftsgfe02
  filename = line.split('/',9)[-1]
  # print filename
  # generate the receiving path
  nersc = "gsiftp://dtn%02u.nersc.gov:2811" % i + str(NERSCPATH) + filename
  # print nersc
  outfile.write("%s %s\n" %(ftsgfe02, nersc))
