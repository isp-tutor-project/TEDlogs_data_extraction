from __future__ import print_function
import argparse
import glob
import json
import os
import re
import sys

TUTOR_STATE_FILE_NAME_RE = re.compile(r'^(\w+?)_?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)?_?([0-9]{1,2})?.tutor-state.json$')
SSCENE1_FILE_NAME_RE = re.compile(r'^(\w+?)_?(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)?_([0-9]{1,2})?.SScene1_1.json$')


def returnUsernameDepth(pth):
    dirs = pth.split('/')
    for i, dirname in enumerate(dirs):
        if dirname.startswith('*'):
            return i


def collect_logs(args):
    dirs = args.input.split('/')
    top_level_dir = dirs[0]
    file_depth = len(dirs) - 1
    username_depth = returnUsernameDepth(args.input)
    is_flat_dir = (file_depth == username_depth)
    regexp_str = args.input.replace('*', r'([a-zA-Z0-9_]+?)')
    regexp = re.compile(regexp_str)
    new_toplevel_dir = top_level_dir.replace("_files", "_logs")
    
    if not os.path.exists(new_toplevel_dir):
        os.mkdir(new_toplevel_dir)
    
    for orig_path in glob.glob(args.input):
        mat = regexp.match(orig_path)
        if mat:
            username = mat.group(1)
            new_file_name = None
            if "tutor-state" == args.type:
                if is_flat_dir:
                    new_file_name = os.path.basename(orig_path)
                else:
                    bn = os.path.basename(orig_path)
                    new_file_name = "%s.%s" % (username, bn)
            else:
                bn = os.path.basename(orig_path)
                new_file_name = "%s.%s" % (username, bn)
            new_path = os.path.join(new_toplevel_dir, new_file_name)
            if args.pretend:
                print('(WOULD) copy %s => %s' % (orig_path, new_path))
            else:
                if args.verbose:
                    print('copying %s => %s' % (orig_path, new_path))
                with open(orig_path, 'r') as in_fh:
                    obj = json.load(in_fh)
                    with open(new_path, "w") as out_fh:
                        json.dump(obj, out_fh, indent=4)
        else:
            print('no match: %s' % orig_path)
    if not args.pretend:
        logfiles = get_logfiles(new_toplevel_dir)
        transformed = auto_normalize_file_names(logfiles)
        normalize_file_names(transformed, args.pretend, args.verbose)


def get_logfiles(dirname):
    logfiles = []
    for (root, dirnames, filenames) in os.walk(dirname):
            for filename in filenames:
                if filename.endswith(".json"):
                    logfiles.append({'path': dirname, 'orig_file_name': filename, 'transformations': []})
            break
    return logfiles


def transform_file_names(file_objs, match_str, replacement):
    new_file_objs = []
    for file_obj in file_objs:
        file_name = None
        if not len(file_obj['transformations']):
            file_name = file_obj['orig_file_name']
        else:
            file_name = file_obj['transformations'][-1]
        transformed = file_name.replace(match_str, replacement)
        if transformed != file_name:
            file_obj['transformations'].append(transformed)
        new_file_objs.append(file_obj)
    return new_file_objs


def normalize_file_names(logfiles, pretend, verbose):
    for logfile in logfiles:
        path = logfile['path']
        orig_fn = logfile['orig_file_name']
        orig_path = os.path.join(path, orig_fn)
        if len(logfile['transformations']):
            new_fn = logfile['transformations'][-1]
            new_path = orig_path.replace(orig_fn, new_fn)
            if pretend:
                print("(would) rename: %s  =>  %s" % (orig_path, new_path))
            else:
                if verbose:
                    print("renaming: %s  =>  %s" % (orig_path, new_path))
                os.replace(orig_path, new_path)
        else:
            if verbose:
                print("no transformations %s" % orig_path)
            else:
                pass


def rename_files(args):
    logfiles = get_logfiles(args.directory)
    transformed = transform_file_names(logfiles, args.match_str, args.replacement_str)
    normalize_file_names(transformed, args.pretend, args.verbose)


def auto_normalize_file_names(logfiles):
    transformed = transform_file_names(
        logfiles, ".tutorstate_RQTED.json", ".tutor-state.json"
    )
    transformed = transform_file_names(
        transformed, "tutor_state.json", "tutor-state.json"
    )
    transformed = transform_file_names(
        transformed, "_TED_tutor-state.json", ".tutor-state.json"
    )
    transformed = transform_file_names(
        transformed, "_TEDtutor-state.json", ".tutor-state.json"
    )
    transformed = transform_file_names(
        transformed, "TEDtutor-state.json", ".tutor-state.json"
    )
    return transformed


def list_non_matching(args):
    logfiles = get_logfiles(args.directory)
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
            full_path = os.path.join(path, file_name)
            print(full_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logfile Filename Normalization Command")
    def usage(args):
        parser.print_usage()
    parser.set_defaults(func=usage)

    subparsers = parser.add_subparsers(help="command help", title="sub-commands")

    collect_logs_parser = subparsers.add_parser(
        "collect-logs",
        help="grabs files from your STUDY_NAME_files folder and places them in STUDY_NAME_logs"
    )
    collect_logs_parser.set_defaults(func=collect_logs)

    collect_logs_parser.add_argument("-i", "--input",
                        action="store",
                        help="path to log files (pattern can contain '*'. make sure to wrap entire path in quotes)",
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
    collect_logs_parser.add_argument("-v", "--verbose",
                                     action="store_true",
                                     help="display operations performed when not using --pretend",
                                     default=False)
    list_parser = subparsers.add_parser(
        "list-non-matching",
        help="will list files which don't conform to either USERNAME.tutor-state.json or USERNAME.SScene1_1.json"
    )
    list_parser.set_defaults(func=list_non_matching)

    list_parser.add_argument("-d", "--directory",
                             metavar="LOGFILE_DIRECTORY",
                             action="store",
                             help="logfile directory to work on",
                             required=True)

    rename_parser = subparsers.add_parser(
        "rename",
        help="type '%(prog)s rename -h' to see rename command help"
    )
    rename_parser.set_defaults(func=rename_files)
    
    rename_parser.add_argument("-f", "--find",
                               metavar="MATCH_STR",
                               dest="match_str",
                               action="store",
                               help="part of filename(s) you wish to match",
                               required=True)
    rename_parser.add_argument("-r", "--replace",
                               metavar="REPLACEMENT_STR",
                               dest="replacement_str",
                               action="store",
                               help="part of filename, you wish to substitute for what was matched via --find",
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
    rename_parser.add_argument("-v", "--verbose",
                               action="store_true",
                               help="display operations performed when not using --pretend",
                               default=False)

    args = parser.parse_args()
    args.func(args)
