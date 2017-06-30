#include <fstream>
#include <iostream>
#include <unistd.h>
#include <cstdlib>
#include <TFile.h>
#include <TError.h>
// finds root files that have not been closed properly
// needs:                  
// source /cvmfs/grid.cern.ch/umd-sl6ui-test/etc/profile.d/setup-ui-example.sh
// source /cvmfs/lz.opensciencegrid.org/ROOT/v5.34.32/slc6_gcc44_x86_64/root/bin/thisroot.sh
// input file is generated using                                                    
// ./lisfiles.sh 01


int main(int argc, const char **argv)
{

  // Disable ROOT error messages
  gErrorIgnoreLevel = 5000;

  // Get the file name
  if (argc != 2)
  {
    std::cerr << "Usage: zf <input_file>" << std::endl << std::endl;
    return 1;
  }

  // Make sure the prefered ROOT version is setup
  std::string rootver = "";
  char * rs = getenv("ROOTSYS");
  if (rs != NULL) { rootver = rs; }
  else { std::cerr << "ROOTSYS not set." << std::endl; return 1;}
  if (rootver != "/cvmfs/lz.opensciencegrid.org/ROOT/v5.34.32/slc6_gcc44_x86_64/root") {
    std::cerr << "LZ ROOT version expected, got " << rootver << " instead." << std::endl;
    return 1;
  }

  std::ifstream xFD(argv[1]);
  std::string xPath;
  while (xFD.good())
  {
    xFD >> xPath;

    // Fast path for EOF
    if (!xFD.good())
      break;
    int xRetry = 0;
    for (xRetry = 0; xRetry < 3; xRetry++)
    {
      bool isBad = false;
      // Test the file
      TFile *xFile = TFile::Open(xPath.c_str());
      if (xFile)
      {
        if (xFile->TestBit(TFile::kRecovered))
        {
          std::cerr << "Recovered file: " << xPath << std::endl;
          isBad = true;
        }
        else if (xFile->IsZombie())
        {
          std::cerr << "Zombile file: " << xPath << std::endl;
          isBad = true;
        }
      }
      else
      {
        std::cerr << "Failed to open: " << xPath << std::endl;
        sleep(xRetry + 1);
	continue;
      }
  
      if (isBad)
      {
        std::cout << xPath << std::endl;
      } else
      {
        std::cerr << "File is OK: " << xPath << std::endl;
      }
  
      // Tidy up
      if (xFile)
      {
	xFile->Close();
        delete xFile;
      }
      break;
    } // for

    if (xRetry == 3)
    {
      std::cerr << "Totally failed to open: " << xPath << std::endl;
      std::cout << xPath << std::endl;
    }

  } // while

  return 0;
}

