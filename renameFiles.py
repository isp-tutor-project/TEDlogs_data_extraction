from __future__ import print_function
import json
import os
import re
import sys

FILE_NAME_RE = re.compile(r'^(\w+).TED_tutor_state.json')

def normalize_file_name(orig_fn):
    fn = orig_fn
    fn = fn.replace(".json", "")
    fn = fn.replace("tutor_state", "")
    if fn.endswith('_'):
        fn = fn[0:-1]
    if fn.endswith('_TED'):
        fn = fn[0:-4]
    fn += '.TED_tutor_state.json'
    return fn

def mk_newfiles(orig_path, new_path):
    orig_file_names = []
    for (dirpath, dirnames, filenames) in os.walk(orig_path):
        for filename in filenames:
            orig_file_names.append(filename)
        break
    for orig_file_name in orig_file_names:
        fn = normalize_file_name(orig_file_name)
        mat = FILE_NAME_RE.match(fn)
        if not mat:
            print('ERROR no match %s' % fn)
        else:
            bn = mat.group(1)
            new_file_name = "%s.TED_tutor_state.json" % bn
            orig_file_path = os.path.join(orig_path, orig_file_name)
            new_file_path = os.path.join(new_path, new_file_name)
            obj = json.load(open(orig_file_path, "r"))
            with open(new_file_path, "w") as fh:
                fh.write(json.dumps(obj, indent=4))
        
if __name__ == "__main__":
    orig_dir = sys.argv[1]
    new_dir = sys.argv[2]
    mk_newfiles(orig_dir, new_dir)
