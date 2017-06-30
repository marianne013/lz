#!/bin/bash


if [ $# -ne 1 ]; then
    echo "Argument should be day number (01, 02, 03 etc)."
    exit 1
fi

TOPDIR="/pnfs/hep.ph.ic.ac.uk/data/lz/lz/data/MDC1/BACCARAT-1.2.3_DER-4.4.0/"

# lz_mdc1_07-17-2017
DAYNUM=$1
DAYDIR="lz_mdc1_07-${DAYNUM}-2017"

FULLDIR="${TOPDIR}${DAYDIR}"
echo $FULLDIR

if [ ! -d "$FULLDIR" ]; then
    echo "${FULLDIR} does not exist."
    exit 1
fi


OUTFILE="files_${DAYDIR}.txt" 
find "${FULLDIR}" -iname '*.root' \
    | sed -e 's#^/#root://gfe02.grid.hep.ph.ic.ac.uk/#' \
    | sort -n > "${OUTFILE}"

COUNT=`grep -cv "mctruth" "${OUTFILE}"`
echo "Found ${COUNT} files."

