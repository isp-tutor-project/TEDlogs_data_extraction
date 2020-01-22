from __future__ import print_function
import argparse
import json
import os
import re
import sys

TUTOR_STATE_FILE_NAME_RE = re.compile(r'^(\w+?)_?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)?_?([0-9]{1,2})?.tutor-state.json$')
SSCENE1_FILE_NAME_RE = re.compile(r'^(\w+?)_?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)?_([0-9]{1,2})?.SScene1.json$')

def get_logfiles(dirname):
    logfiles = []
    for (root, dirnames, filenames) in os.walk(dirname):
            for filename in filenames:
                if filename.endswith(".json"):
                    logfiles.append((dirname, filename))
            break
    return logfiles

def rename_files(args):
    dirname = args.directory
    replace = args.replace
    _with = args._with
    pretend = args.pretend
    logfiles = get_logfiles(dirname)
    for logfile in logfiles:
        (path, orig_fn) = logfile
        if replace in orig_fn:
            new_fn = orig_fn.replace(replace, _with)
            orig_path = os.path.join(dirname, orig_fn)
            new_path = os.path.join(dirname, new_fn)
            if pretend:
                print("I would rename: %s  to:  %s" % (orig_path, new_path))
            else:
                print("renaming: %s  to:  %s" % (orig_path, new_path))
                os.replace(orig_path, new_path)

def list_non_matching(args):
    dirname = args.directory
    logfiles = get_logfiles(dirname)
    for logfile in logfiles:
        mat1 = TUTOR_STATE_FILE_NAME_RE.match(logfile[1])
        mat2 = SSCENE1_FILE_NAME_RE.match(logfile[1])
        if mat1:
            pass
        elif mat2:
            pass
        else:
            print(logfile[1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logfile Filename Normalization Command")
    subparsers = parser.add_subparsers(help="command help", title="sub-commands")
    
    rename_parser = subparsers.add_parser("rename",
                                          help="type '%(prog)s rename -h' to see rename command help")
    rename_parser.set_defaults(func=rename_files)
    
    rename_parser.add_argument("-r", "--replace",
                               metavar="ORIG_PART_OF_FILENAME",
                               action="store",
                               help="part of filename you wish to match and be replaced",
                               required=True)
    rename_parser.add_argument("-w", "--with",
                               metavar="NEW_PART_OF_FILENAME",
                               dest="_with",
                               action="store",
                               help="part of filename you wish to replace ORIG_PART_OF_FILENAME with",
                               required=True)
    rename_parser.add_argument("-d", "--directory",
                               metavar="LOGFILE_DIRECTORY",
                               action="store",
                               help="logfile directory to work on",
                               required=True)
    rename_parser.add_argument("-p", "--pretend",
                              action="store_true",
                              help="list file name changes without actually changing them",
                              default=False)
    list_parser = subparsers.add_parser("list-non-matching",
                                        help="will list files which don't conform to either USERNAME.tutor-state.json or USERNAME.SScene1.json")
    list_parser.set_defaults(func=list_non_matching)
    
    list_parser.add_argument("-d", "--directory",
                             metavar="LOGFILE_DIRECTORY",
                             action="store",
                             help="logfile directory to work on",
                             required=True)

    args = parser.parse_args()
    args.func(args)
