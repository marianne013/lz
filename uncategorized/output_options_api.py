#!/usr/bin/env python
"""
requires a DIRAC UI to be set up (source bashrc)
and a valid proxy: dirac-proxy-init -g [your vo here]_user -M
"""
import pprint
# DIRAC does not work otherwise
from DIRAC.Core.Base import Script
Script.initialize()
# end of DIRAC setup

from DIRAC.Interfaces.API.Job import Job
from DIRAC.Interfaces.API.Dirac import Dirac

def configure_and_submit(dirac, job, logfile): 
  """set job options"""
  job.setCPUTime(500)
  # job.setExecutable('output_examples.sh', arguments='donotuploadbyhand')
  job.setExecutable('output_examples.sh', arguments='specifylfn')
  job.setName('API_out')
  # any site you don't want your jobs to go to:
  job.setBannedSites(['LCG.UKI-SOUTHGRID-BRIS-HEP.uk', 'LCG.pic.es'])
  job.setPlatform("AnyPlatform")

  # goes with 'donotuploadbyhand'
  #job.setOutputData(['*.txt', '*.dat'], outputSE='UKI-LT2-IC-HEP-disk', outputPath='/api/specialpath')
  #job.setOutputData(['*.txt', '*.dat'], outputSE='UKI-LT2-IC-HEP-disk')
  # goes with 'specifylfn' above
  job.setOutputData(["LFN:/gridpp/dbauer/testlfnapi/txt/testfile.lfn1.txt", "LFN:/gridpp/dbauer/testlfnapi/txt/testfile.lfn2.txt", "LFN:/gridpp/dbauer/testlfnapi/dat/testfile.lfn3.dat"],  outputSE='UKI-LT2-IC-HEP-disk')

  result = dirac.submitJob(job)
  logfile.write('Submission Result: ')
  pprint.pprint(result, logfile)
  jobid = result['JobID']

  # print job id to file for future reference
  joblog = open("api_out_jobid.log", "a")
  joblog.write(str(jobid)+'\n')
  joblog.close()

  return jobid

def check_job(dirac, jobid, logfile):
  """ to interactively check on job status do:
  dirac-wms-job-status -f api_jobid.log"""
  logfile.write("\nThe current status of this job is:")
  pprint.pprint(dirac.getJobStatus(jobid), logfile)

def check_all_jobs(dirac, logfile):
  """check status of all jobs mentioned in the api_out_jobid.log"""
  joblog = open("api_out_jobid.log", "r")
  # list comprehension :-D
  all_jobids = [jobid.strip() for jobid in joblog.readlines()]

  logfile.write("\nThe current status of all jobs is:")
  all_status = dirac.getJobStatus(all_jobids)
  pprint.pprint(all_status, logfile)


def main():
  """actually submist the job"""
  logfile = open("api.log", "w")
  dirac = Dirac()
  job = Job()

  jobid = configure_and_submit(dirac, job, logfile)
  check_job(dirac, jobid, logfile)
  check_all_jobs(dirac, logfile)
  logfile.close()
  print "API logs can be found in api.log and api_out_jobid.log."

if __name__ == "__main__":
  main()
