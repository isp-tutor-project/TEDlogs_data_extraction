# process_study1_logs

## Description
createExcelFile.py can operate on either tutor-state.json or SScene1.json files,
however the username is not contained within these logfiles and instead is
gotten from the filename.

This means that the filenames need to be normalized to either

USERNAME.tutor-state.json or USERNAME.SScene1.json

the tutor-state files are typically in a single folder, whereas the
SScene1 files are more likely to be in a directory hierarchy such as
USERNAME/some subdirectory/perhaps another subdirectory/SScene1.json

I've provided several utility programs to make the filename normalization
process easier.


1) mkSScene1Directory.py which will grab all of the SScene1.json files from 
   wherever they live to a new directory where they will all be named
   USERNAME.SScene1.json

2) normalizeFileNames.py which can both list files which don't match
   either USERNAME.tutor-state.json or USERNAME.SScene1.json as well
   as providing options to rename files which match a particular pattern
   with a new one

## Installation
1) open a command line terminal in this directory, this may require more
   instructions on windows
2) type 'python3 -m venv venv'
3) type 'source venv/bin/activate' after doing this your command prompt will start with (venv)
4) type 'pip install -r requirements.txt'

## Instructions
1) open a command line terminal in this directory
2) type 'source venv/bin/activate'
3) download a .zip file from BOX or whatever other method use use to the 
   directory of log files to reside within this directory. 
   a) unzip the .zip file if necessary
4) remove any spaces from the log file directory name.  the directory name
   will be used when creating the excel spreadsheet name
5) if:
   a) it's a directory hierarchy containing SScene1.json files use
      mkSScene1Directory.py to extract and rename all of the files into
      a single directory
   b) if it's a single directory containing tutor-logs, you'll need to
      run normalizeFileNames.py several times until all of the filenames
      conform to USERNAME.tutor-state.json
6) Finally, you can run createExcelFile.py on your log file directory.
   this will add to the logfile directory a <logfile_directory_name>.xslx
   file

