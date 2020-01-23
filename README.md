# TEDlogs_data_extraction

## Description
---
This git repository contains a program `createExcelFile.py` which will process
log files and output an excel file containing the data you care about.

`createExcelFile.py` can operate on either `tutor-state.json` or `SScene1_1.json` files,
however, since the username is not contained within these logfiles, it must be
gotten from the filename, meaning that the filenames need to be **canonicalized** as either:

`USERNAME.tutor-state.json`

\- or - 

`USERNAME.SScene1_1.json`

Thankfully, the `prepareLogs.py` utility provides commands so that you don't
need to rename them all manually.

Typically the logfiles are gotten in one of 2 formats:

1) a single folder containing all of the tutor-state files (which I believe
   was pain-stakingly created by copying all of the files from their original
   folders (from 2 below) to this single folder - something which can be 
   automated by `prepareLogs.py`)

    \- or -
  
2) A directory hierarchy possibly containing both `SScene1_1.json` files and 
   `tutor-state.json` (perhaps with a different name such as 'tutorstate_RQTED.json')
    files where they might be located at:

     some_folder/*USERNAME*/some_subdirectory/perhaps_another_subdirectory/SScene1_1.json

    \- or -

     some_folder/*USERNAME*/some_subdirectory/perhaps_some_other_directory/tutor-state.json

In the latter case, the `prepareLogs.py` utility can copy all of these files
from the directory hierarchy and place them in a **single** directory 

Once the files are in a single directory, the filenames need to be canonicalized.
The `prepareLogs.py` utility is used for this. I've encountered numerous
variations in log file names, and this program has an auto-normalize feature
which can handle many of the file renamings.

Finally, for some studies, log files were erroneous or missing data.  If you have
access to both tutor-state and SScene1 log files, I suggest you use `prepareLogs.py`
to place both of these files for each student in a single directory, so that
that `createExcelFile.py` can work with both (if they both exist) and it can
report errors if neither contain the data we care about.

---
## Installation Instructions
---
1) open a command line terminal in this directory, this may require more
   instructions on windows
2) type `python3 -m venv venv`
3) type `source venv/bin/activate` after doing this your command prompt will start with (venv)
4) type `pip install -r requirements.txt`

---
## High-level Instructions for Using the Software
---
1) open a command line terminal in this directory
2) type `source venv/bin/activate`
3) download a .zip file from BOX or whatever other method use use to the 
   directory of log files to reside within this directory. 
   a) unzip the .zip file if necessary
4) rename the directory containing the log files `STUDY_NAME_files`.
   The generated excel spreadsheet will be named `STUDY_NAME.xslx`
5) if:
   
   *  `STUDY_NAME_files` is a directory hierarchy containing (potentially) both
       SScene1_1.json and tutor-state.json files
       * use the `prepareLogs.py collect-logs`
       command to locate the files within the hierarcy and place them in a new
       (created automatically) `STUDY_NAME_logs` directory.
       * see details below  
   * **else** if `STUDY_NAME_files` is simply a folder containing tutor-state logs
      * you will still need to run the `prepareLogs.py collect-logs`, but with
        different parameters. See details below
      * this will simply copy the files from you `STUDY_NAME_files` directory to
      an (automaticaly created) `STUDY_NAME_logs` directory, but the JSON data
      will get pretty-printed in the process. 
      * You will probably also need to make use of `prepareLogs.py` various
        file-normalzation related commands more than once until all the file names
        are canonicalized.
6) Finally, you can run `createExcelFile.py` on your `STUDY_NAME_logs` directory.
   If all goes well, `STUDY_NAME_logs/STUDY_NAME.xslx` will be created.


---
## Instructions for `prepareLogs.py`
---
prepareLogs.py performs the following operations:
* the `collect-logs` command grabs files from STUDY_NAME_files and copies then to an automatically created
  STUDY_NAME_logs directory
  * in the process, the JSON data will be pretty-printed
  * also, in the process common variants of file names I've seen before will get
    auto-canonicalized for you
* the `list-non-matching` command will list files which don't matched the canonical file name format
* the `rename` command lets you rename files using pattern matching
  

* It can be passed a `-h` option to list help
* each subcommand supports `<subcommand_name> -h` to list help specific to that sub-command
* certain operations may invite user-error, and support a `-p` (pretend) option
  which will merely list what would be done, rather than operations actually being performed
* make use of the `-h` (help) to see nore details than described here


###  The **collect-logs** sub-command:

* specify The input directory via the `-i` option. You'll want to pass it a path starting with '*STUDY_NAME*_files'
  * make sure to wrap the input directory in quotes

  * The `*` in specified input directory path (see examples below) represents where in the path the STUDENTS subdirectory is

* specify the log file type with the `--type` option. the choices or `scene` and `tutor-state`
  
##### Grabbing SScene1 logs from a **hierarchical** directory
  
`python prepareLogs.py collect-logs -t scene -i "STUDY_NAME_files/*/some_subdirectory/SScene1_1.json"`

##### Grabbing tutor-state logs from a **hierarchical** directory

`python prepareLogs.py collect-logs -t tutor-state -i "STUDY_NAME_files/*/some_subdirectory/tutor-state.json"` 
  
  (the tutor logs *may* have a different name, tutorstate_RQTED.json for instance, - use whatever naming convention they follow)
  
##### Grabbing tutor-state logs from a **flat directory** (no subdirectories within it)

`python prepareLogs collect-logs -t tutor-state -i "STUDY_NAME_FILES/*.json"`



### The  **list-non-matching** sub-command

simply type:

`python prepareLogs.py list-non-matching -d STUDY_NAME_logs`

files whose names are not canonicalized will be listed


### The  **rename** sub-command


The `rename` command allows you to rename files via pattern matching. if **list-non-matching** only list a few files, you feel more comfortable renaming them manually
  
I This command supports a `-p` (pretend) option. I **highly** recommend that you make use of it to see what files would be renamed, prior to actually renaming them
  
WHERE:

* specify, via `-d`, the input directory. `STUDY_NAME_logs` is specified in the example below
* specify, via `--find`, the sub-string of the filename(s) to wish to match and replace. The example below specifies the value of `bad_part_of_file_name`
* specify, via `--replace`, the string to replace what was matched via `--find` with. The example below specifies the value of `good_part_of_file_name`
  
example:

`python prepareLogs.py --find 'bad_part_of_file_name' --replace 'good_part_of_file_name' -d STUDY_NAME_logs` -p

This command will:
  * output any filenames which contain 'bad_part_of_file_name' and show how they would be renamed with 'good_part_of_file_name' substituted in it's place
  * if you're happy with what you see, remove the trailing `-p` from the command, and run again
  * run the **list-non-matching** command to see what files still require renaming
  
---
## Instructions for `createExcelFile.py`
---
simply type:

`python createExcelFile.py STUDY_NAME_logs`
  
* `STUDY_NAME_logs/STUDY_NAME.xlsx`  will be created
* if there are users which don't have data in any of their logs, a `STUDY_NAME_logs/students_missing_data.txt` file will be created.

---
## Further help
---
* For something more concrete, look in the `examples` subdirectory.  I've recorded my sessions where I created the excel files for both SciTGr6_Study1 and Deerlake
* make use of prepareLog.py's -h and sub-command -h options
* Contact Scott
* Yell at Scott for not documenting the code well enough, as I thought these were a one-time throw-away scripts