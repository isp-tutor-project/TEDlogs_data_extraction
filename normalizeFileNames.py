from __future__ import print_function
import argparse
import json
import os
import re
import sys

TUTOR_STATE_FILE_NAME_RE = re.compile(r'^(\w+?)_?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)?_?([0-9]{1,2})?.tutor-state.json$')
SSCENE1_FILE_NAME_RE = re.compile(r'^(\w+?)_?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)?_([0-9]{1,2})?.SScene1_1.json$')


def collect_logs(args):
    path = args.input
    pretend = args.pretend
    log_type = args.type
    regexp_str = path.replace('*', r'([a-zA-Z0-9_]+?)')
    # print(regexp_str)
    # sys.exit(0)
    top_level_dir = path.split('/')[0]
    new_toplevel_dir = top_level_dir.replace("_files", "_logs")
    if not os.path.exists(new_toplevel_dir):
        os.mkdir(new_toplevel_dir)

    regexp = re.compile(regexp_str)
    orig_paths = glob.glob(path)
    # print(type(file_names))
    # sys.exit(0)
    for orig_path in orig_paths:
        mat = regexp.match(orig_path)
        if mat:
            username = mat.group(1)
            # bn = None
            new_file_name = None
            if "tutor-state" == log_type:
                new_file_name = os.path.basename(orig_path)
                #     bn = 'tutor-state.json'
            else:
                bn = os.path.basename(orig_path)
                new_file_name = "%s.%s" % (username, bn)
            new_path = os.path.join(new_toplevel_dir, new_file_name)
            if pretend:
                print('(WOULD) copy %s => %s' %
                      (orig_path, new_path))
            else:
                print('copying %s => %s' %
                      (orig_path, new_path))
                with open(orig_path, 'r') as in_fh:
                    obj = json.load(in_fh)
                    with open(new_path, "w") as out_fh:
                        json.dump(obj, out_fh, indent=4)
        else:
            print('no match: %s' % orig_path)


def get_logfiles(dirname):
    logfiles = []
    for (root, dirnames, filenames) in os.walk(dirname):
            for filename in filenames:
                if filename.endswith(".json"):
                    logfiles.append({'path': dirname, 'orig_file_name': filename, 'transformations': []})
            break
    return logfiles

def transform_file_names(file_objs, replace, _with):
    new_file_objs = []
    for file_obj in file_objs:
        file_name = None
        if not len(file_obj['transformations']):
            file_name = file_obj['orig_file_name']
        else:
            file_name = file_obj['transformations'][-1]
        # print(file_name)
        transformed = file_name.replace(replace, _with)
        # print(transformed)
        if transformed != file_name:
            file_obj['transformations'].append(transformed)
        new_file_objs.append(file_obj)
    return new_file_objs

def normalize_file_names(logfiles, pretend):
    for logfile in logfiles:
        path = logfile['path']
        orig_fn = logfile['orig_file_name']
        orig_path = os.path.join(path, orig_fn)
        # print(logfile['transformations'])
        # new_fn = None
        if len(logfile['transformations']):
            new_fn = logfile['transformations'][-1]
            # print(new_fn)
            new_path = orig_path.replace(orig_fn, new_fn)
            # new_path = os.path.join(orig_path, new_fn)
            # print(new_path)
            if pretend:
                print("(would) rename: %s  =>  %s" % (orig_path, new_path))
            else:
                print("renaming: %s  =>  %s" % (orig_path, new_path))
                os.replace(orig_path, new_path)


def rename_files(args):
    dirname = args.directory
    replace = args.replace
    _with = args._with
    pretend = args.pretend
    logfiles = get_logfiles(dirname)
    transformed = transform_file_names(logfiles, replace, _with)
    normalize_file_names(transformed, pretend)


def auto_normalize(args):
    dirname = args.directory
    pretend = args.pretend
    logfiles = get_logfiles(dirname)
    transformed = transform_file_names(logfiles, "tutor_state.json", "tutor-state.json")
    transformed = transform_file_names(transformed, "_TED_tutor-state.json", ".tutor-state.json")
    transformed = transform_file_names(transformed, "_TEDtutor-state.json", ".tutor-state.json")
    transformed = transform_file_names(transformed, "TEDtutor-state.json", ".tutor-state.json")
    normalize_file_names(transformed, pretend)


def list_non_matching(args):
    dirname = args.directory
    logfiles = get_logfiles(dirname)
    for logfile in logfiles:
        path = logfile['path']
        file_name = logfile['orig_file_name']
        mat1 = TUTOR_STATE_FILE_NAME_RE.match(file_name)
        mat2 = SSCENE1_FILE_NAME_RE.match(file_name)
        if mat1:
            pass
        elif mat2:
            pass
        else:
            print("%s%s" % (path, file_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logfile Filename Normalization Command")
    subparsers = parser.add_subparsers(help="command help", title="sub-commands")

    collect_logs_parser = subparsers.add_parser("collect-logs",
                                                help="grabs files from your STUDY_NAME_files folder and places them in STUDY_NAME_logs")
    collect_logs_parser.set_defaults(func=collect_logs)
    collect_logs_parser.add_argument("-i", "--input",
                        action="store",
                        help="path to log files (pattern can contain '*' make sure to wrap in quotes)",
                        required=True)
    collect_logs_parser.add_argument("-t", "--type",
                        action="store",
                        choices=["scene", "tutor-state"],
                        help="log file type",
                        required=True)
    collect_logs_parser.add_argument("-p", "--pretend",
                        action="store_true",
                        help="print what would be done without actually doing it",
                        default=False)

    list_parser = subparsers.add_parser("list-non-matching",
                                        help="will list files which don't conform to either USERNAME.tutor-state.json or USERNAME.SScene1.json")
    list_parser.set_defaults(func=list_non_matching)

    list_parser.add_argument("-d", "--directory",
                             metavar="LOGFILE_DIRECTORY",
                             action="store",
                             help="logfile directory to work on",
                             required=True)

    auto_normalize_parser = subparsers.add_parser("auto-normalize")
    auto_normalize_parser.set_defaults(func=auto_normalize)

    auto_normalize_parser.add_argument("-d", "--directory",
                                       metavar="LOGFILE_DIRECTORY",
                                       action="store",
                                       help="logfile directory to work on",
                                       required=True)
    auto_normalize_parser.add_argument("-p", "--pretend",
                                       action="store_true",
                                       help="list file name changes without actually changing them",
                                       default=False)

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


    args = parser.parse_args()
    args.func(args)
