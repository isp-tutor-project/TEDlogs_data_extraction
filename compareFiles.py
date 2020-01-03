from __future__ import print_function

import json
import os
import re
import sys

from typing import Dict, List, Tuple

FILE_FILTER_RE = re.compile(r'SScene(?P<num1>\d{1,2})(?P<ltr>A?)_(?P<num2>\d)\.json')

def compare_scene_data(data: Dict, scene_names: List[str]) -> None:
    tutor_state_data = json.load(open("tutor_state.json"))
    good_data = {}
    for i, scene_name in enumerate(scene_names):
        # compare scene_file data with tutor_state data for each scene
        if scene_name not in tutor_state_data['scene']:
            print("tutor_data missing %s...skipping" % scene_name)
            # tutor_state is missing this scene, so don't compare
            # with the scene_file data, but preserve so we can
            # compare data with other scene_files which *should* contain
            # this scene
            good_data[scene_name] = data[scene_name]
            continue
        tutor_data = tutor_state_data['scene'][scene_name]["$seq"]
        tutor_data_len = len(tutor_data)
        sfn, sf_json = data[scene_name]
        sf_data = sf_json['scene'][scene_name]["$seq"]
        sf_data_len = len(sf_data)
        if sf_data_len != tutor_data_len:
            print("%s len(%d) != tutor_state len(%d)" % (sfn, sf_data_len))
        elif sf_data != tutor_data:
            print("%s data != tutor_state data" % sfn)
        else:
            good_data[scene_name] = [sfn, sf_json]
    # build up data structure of which scenes should exist in which files
    # (along with their data)
    # should_contain_scene = {}
    # contains_scene = {}
    # not_contains_scene = {}
    for i, scene_name in enumerate(scene_names):
        should_contain = set()
        contains = set()
        not_contains = set()
        fn_scene_data = {}
        for sn in scene_names[i:]:
            fn, fd = good_data[sn]
            should_contain.add(fn)
        # should_contain_scene[scene_name] = should_contain
        for fn in should_contain:
            (fn2, fd) = data[scene_name]
            if fn != fn2:
                print("%s != %s" % (fn, fn2))
                break
            fn_scene = fd.get("scene", {}).get(scene_name, {}).get("$seq", None)
            if fn_scene is None:
                not_contains.add(fn)
            else:
                contains.add(fn)
                fn_scene_data[fn] = fn_scene
        sys.exit(0)
        # print("%s\n\tcontains: %s\nnocontains: %s" %
        #       (scene_name, contains, not_contains))
        # contains_scene[scene_name] = contains
        # not_contains_scene[scene_name] = not_contains
        print(scene_name, should_contain)
        # sys.exit(0)
        if should_contain == contains and len(not_contains) == 0:
            # print("%s in all expected files" % scene_name)
            added = set()
            compare = set()
            l = 1
            for fn in contains:
                # print("print adding %s scene data" % fn)
                added.add(fn)
                compare.add(json.dumps(fn_scene_data[fn]))
                if len(compare) > 1:
                    print("%s data different from %s" % (fn, added))
                    break
            # print(len(compare))
        else:
            print("%s missing in %s" % (scene_name, not_contains))

    # do the actual comparing

            # print("%s == %s => %s" % (fn, fn2, fn == fn2))
            # continue
            # fd_data = fd.get('scene', {}).get(scene_name, {}).get('$seq', None)
            # if fd_data is None:
            #     pass
            #     # print("%s does not contain scene %s" % (fn, scene_name))
            # else:
            #     does_contain_scene[scene_name].add(fn)
            #     fn_data[fn] = fd_data

        # print(scene_name)
        # for file_name in fn_data:
        #     print("\t", file_name)


def main():
    for (root, dirs, files) in os.walk("."):
        scene_file_versions = {}
        for file_name in files:
            mat = FILE_FILTER_RE.match(file_name)
            if mat:
                parts = mat.groupdict()
                num1 = parts['num1']
                if len(num1) == 1:
                    num1 = "0" + num1
                ltr = parts['ltr']
                num2 = int(parts['num2'])
                scene_name = 'SScene%s%s' % (num1.lstrip("0"), ltr)
                if scene_name not in scene_file_versions:
                    scene_file_versions[scene_name] = []
                scene_file_versions[scene_name].append(
                    (num2, {
                        'fileName': file_name,
                        'sortKey': (num1, ltr, num2),
                        'sceneName': scene_name
                }))

    # grab the max version file for each scene
    file_data = [
        sorted(scene_file_versions[scene], key=lambda x: x[0])[-1][1]
        for scene in scene_file_versions
    ]
    file_data.sort(key=lambda x: x['sortKey'])
    scene_names = [obj['sceneName'] for obj in file_data]
    file_names = [obj['fileName'] for obj in file_data]
    # generates scene_name -> file_name tuples 
    scenes_n_files = zip(scene_names, file_names)
    # a mapping of scene names to a (file_name, file data) tuple
    scene_data = {}
    for sn, fn in scenes_n_files:
        scene_data[sn] = [fn, json.load(open(fn, "r"))]
    compare_scene_data(scene_data, scene_names)

if __name__ == "__main__":
    main()
