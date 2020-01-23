from __future__ import print_function
from io import StringIO
from copy import copy
import csv
import glob
import json
import os
import re
import sys

import xlsxwriter

TUTOR_STATE_FILE_NAME_RE = re.compile(r'^(\w+)\.tutor-state.json$')
SSCENE1_FILE_NAME_RE = re.compile(r'^(\w+)\.SScene1_1.json$')
FILE_NAME_RE = re.compile(r'^\w+?\.(?:tutor-state|SScene1_1)\.json$')
ANALYZED_CSV_FILE_RE = re.compile(r'^(\w+?)\.step3\.analyzed\.csv$')



def filter_recs1(recs):
    filtered = []
    for rec in recs:
        time = rec.get('time')
        prop = rec.get('prop')
        value = rec.get('value')
        if prop.startswith("VSel") and not value:
            continue
        if prop == "currentRow" and value == 5:
            continue
        filtered.append(rec)
    return filtered


def filter_recs2(recs):
    filtered = []
    ignore_corrects = False
    for rec in recs:
        time = rec.get('time')
        prop = rec.get('prop')
        value = rec.get('value')
        if prop == "currentRow":
            ignore_corrects = True
        if prop.startswith("TVSel") or prop.startswith("VSel"):
            ignore_corrects = False
        if prop == "correct" and ignore_corrects:
            continue
        filtered.append(rec)
    return filtered



def filter_recs3(recs):
    filtered = []
    prev_prop = ""
    for rec in recs:
        time = rec.get('time')
        prop = rec.get('prop')
        value = rec.get('value')
        if prop == "correct" and prev_prop == "correct":
            continue
        prev_prop = prop
        filtered.append(rec)
    return filtered


def read_csv(file_name):
    rows = []
    with open(file_name, "r") as infh:
        reader = csv.DictReader(infh)
        for i, row in enumerate(reader):
            rows.append((i+2, dict(row)))
    return rows


def dump_csv(obj, path):
    field_names = ['time', 'prop', 'value']
    with open(path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for rec in obj:
            writer.writerow(rec)


def dump_simplified_csv(recs, path):
    field_names = ['time', 'prop', 'value']
    filtered1 = filter_recs1(recs)
    filtered2 = filter_recs2(filtered1)
    filtered3 = filter_recs3(filtered2)
    with open(path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for rec in filtered3:
            writer.writerow(rec)

def analyze_simplified_csv(orig, new_file):
    # print(new_file)
    with open(orig, "r") as infh:
        reader = csv.DictReader(infh)
        currentRow = None
        currentValue = None
        rows = {
            1: {"isTV": False, "values":[]},
            2: {"isTV": False, "values":[]},
            3: {"isTV": False, "values":[]},
            4: {"isTV": False, "values":[]}
        }
        for row in reader:
            data = dict(row)
            time = int(data.get('time'))
            prop = data.get('prop')
            value = data.get('value')
            if "rowsComplete" == prop:
                continue
            elif "complete" == prop:
                if value == "True":
                    break
                else:
                    continue                
            elif prop == "currentRow":
                currentRow = int(value)
                currentValue = {}
            elif prop.startswith('TVSel'):
                rows[currentRow]['isTV'] = True
                if len(rows[currentRow]["values"]) > 0:
                    currentValue = copy(rows[currentRow]["values"][-1])
                if "TVSel.col1" == prop:
                    currentValue['col1'] = int(value)
                    currentValue['col1_ts'] = time
                elif "TVSel.col2" == prop:
                    currentValue['col2'] = int(value)
                    currentValue['col2_ts'] = time
            elif prop.startswith('VSel'):
                rows[currentRow]['isTV'] = False
                if len(rows[currentRow]["values"]) > 0:
                    currentValue = copy(rows[currentRow]["values"][-1])
                if "VSel.col1" == prop:
                    currentValue['col1'] = int(value)
                    currentValue['col1_ts'] = time
                elif "VSel.col2" == prop:
                    currentValue['col2'] = int(value)
                    currentValue['col2_ts'] = time
            elif "correct" == prop:
                val = True if "True" == value else False
                currentValue['correct'] = val
                rows[currentRow]["values"].append(currentValue)
            else:
                raise Exception("unhandled prop: %s" % prop)
        ntv_var = 0
        recs = []
        for row in sorted(rows):
            row_data = rows[row]
            # print(rowData)
            isTV = row_data['isTV']
            row_name = None
            if isTV:
                row_name = "TV"
            else:
                ntv_var += 1
                row_name = "NTV%d" % ntv_var
            for i, val in enumerate(row_data['values']):
                suffix = "(changed)" if i != 0 else ""
                rec = {
                    "variable": "%s%s" % (row_name, suffix),
                    "col1": val['col1'],
                    "col1_ts": val['col1_ts'],
                    "col2": val['col2'],
                    "col2_ts": val['col2_ts'],
                    "isCorrect": val['correct']
                }
                recs.append(rec)
        out_fields = ["variable", "col1", "col1_ts", "col2", "col2_ts", "isCorrect"]
        with open(new_file, "w") as outfh:
            writer = csv.DictWriter(outfh, fieldnames=out_fields, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for rec in recs:
                writer.writerow(rec)
   

def create_excel_file(path, analyzed_file_pattern):
    outfile = path.replace("_logs", ".xlsx")
    output_path = os.path.join(path, outfile)
    analyzed_file_pattern = analyzed_file_pattern.replace("%s", "*")
    csv_files = glob.glob(analyzed_file_pattern)
    wb = xlsxwriter.Workbook(output_path)
    bold = wb.add_format({'bold': True})
    ws = wb.add_worksheet()
    # write header
    ws.write('A1', 'Student')
    ws.write('B1', 'Variable', bold)
    ws.write('C1', 'Col1', bold)
    ws.write('D1', 'Col1_time', bold)
    ws.write('E1', 'Col2', bold)
    ws.write('F1', 'Col2_time', bold)
    ws.write('G1', 'isCorrect', bold)
    start_row = 0
    for csv_file in sorted(csv_files):
        bn = os.path.basename(csv_file)
        # this SHOUlD match since it already matched the glob
        mat = ANALYZED_CSV_FILE_RE.match(bn)
        if mat is None:
            raise Exception("no match %s" % csv_file)
        student = mat.group(1)
        ws_data = read_csv(csv_file)
        for (row_num, row_data) in ws_data:
            ws.write('A%d' % (row_num + start_row), student)
            ws.write('B%d' % (row_num + start_row), row_data['variable'])
            ws.write('C%d' % (row_num + start_row), row_data['col1'])
            ws.write('D%d' % (row_num + start_row), row_data['col1_ts'])
            ws.write('E%d' % (row_num + start_row), row_data['col2'])
            ws.write('F%d' % (row_num + start_row), row_data['col2_ts'])
            ws.write('G%d' % (row_num + start_row), row_data['isCorrect'])
        start_row += len(ws_data) + 1
    wb.close()
    print("excel file saved at %s" % output_path)


def read_log_file(student_data, path, orig_file_name):
    file_type = False
    tutor_state_mat = TUTOR_STATE_FILE_NAME_RE.match(orig_file_name)
    sscene1_mat = SSCENE1_FILE_NAME_RE.match(orig_file_name)
    bn = None # (username) used as basename in output file names
    if tutor_state_mat:
        file_type = "tutor_file"
        bn = tutor_state_mat.group(1)
    elif sscene1_mat:
        file_type = "sscene1_file"
        bn = sscene1_mat.group(1)
    if not file_type:
        print("ERROR: '%s' is neither a tutor-state nor sscene1 file")
        return
    
    #too hard to make a default dict this deep
    if bn not in student_data:
        student_data[bn] = {}

    orig_file_path = os.path.join(path, orig_file_name)
    obj = json.load(open(orig_file_path, "r"))
    sceneKey = 'scene'
    if sceneKey not in obj:
        sceneKey = 'sceneState'
        if sceneKey not in obj:
            print("ERRORL no scene data in %s" % orig_file_name)
            return

    sscene1_seq = obj.get(sceneKey, {}).get('SScene1', {}).get('$seq', None)
    # may store 'None'. this will be handled by process_data()
    student_data[bn][file_type] = sscene1_seq
    

def process_data(orig_data, new_data, path):
    missing_data_users = []
    for user_name in orig_data:
        user_data = orig_data[user_name]
        have_tutor_data, have_scene_data = False, False
        if "tutor_file" in user_data:
            if user_data["tutor_file"] is not None:
                have_tutor_data = True
        if "scene1_file" in user_data:
            if user_data["scene1_file"] is not None:
                have_scene_data = True
        if not (have_tutor_data or have_scene_data):
            missing_data_users.append(user_name)
        elif have_tutor_data:
            new_data[user_name] = user_data["tutor_file"]
        elif have_scene_data:
            new_data[user_name] = user_data["scene1_file"]
        else:
            print("ERROR: How the *^%# did I get here!")
    return missing_data_users


def dump_intermediate_files(data, step1_path, step2_path, step3_path):
    for user_name in data:
        sscene1_seq = data[user_name]
        step1_file = step1_path % user_name
        step2_file = step2_path % user_name
        step3_file = step3_path % user_name
        dump_csv(sscene1_seq, step1_file)
        dump_simplified_csv(sscene1_seq, step2_file)
        analyze_simplified_csv(step2_file, step3_file)


def main(path):
    user_data = {}
    processed_data = {}
    int_files_path = os.path.join(path, "intermediate_files")
    if not os.path.exists(int_files_path):
        os.makedirs(int_files_path)
    s1_path = os.path.join(int_files_path, "%s.step1.json2csv.csv")
    s2_path = os.path.join(int_files_path, "%s.step2.filtered.csv")
    s3_path = os.path.join(int_files_path, "%s.step3.analyzed.csv")

    for (_unused1, _unused2, file_names) in os.walk(path):
        for file_name in sorted(file_names):
            mat = FILE_NAME_RE.match(file_name)
            if mat:
                read_log_file(user_data, path, file_name)
        missing_data_users = process_data(user_data, processed_data, path)
        dump_intermediate_files(processed_data, s1_path, s2_path, s3_path)
        create_excel_file(path, s3_path)
        if len(missing_data_users):
            error_file = os.path.join(path, "students_missing_data.txt")
            with open(error_file, "w") as fh:
                fh.writelines("\n".join(missing_data_users))
            print("NOTE: A list of usernames missing the required data have "
                  "been saved to %s" % error_file)
        break


if __name__ == "__main__":
    main(sys.argv[1])
