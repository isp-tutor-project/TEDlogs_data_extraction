from __future__ import print_function
from io import StringIO
from copy import copy
import csv
import json
import os
import re
import sys

import xlsxwriter

TUTOR_STATE_FILE_NAME_RE = re.compile(r'^(\w+)\.tutor-state.json$')
SSCENE1_FILE_NAME_RE = re.compile(r'^(\w+)\.SScene1_1.json$')
FILE_NAME_RE = re.compile(r^(\w+))\.(?:tutor-state|SScene1_1)\.json$')



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
    # reader = None
    rows = []
    with open(file_name, "r") as infh:
        reader = csv.DictReader(infh)
        for i, row in enumerate(reader):
            rows.append((i+2, dict(row)))
    return rows

# def dump_json(obj, path):
#     with open(path, 'w') as fh:
#         json.dump(obj, fh, indent=4)

# def dump_simplified_json(scene1_seq, module_seq, path):
#     print(path)
#     indent = ""
#     txt = "{\n"
#     indent = 4 * " "
#     txt += '%s"scene.SScene1.$seq": [\n' % indent
#     indent = 8 * " "
#     for rec in scene1_seq:
#         txt += "%s%s,\n" % (indent, json.dumps(rec))
#     txt = txt.rstrip(',\n')
#     txt += '\n'
#     indent = 4 * " "
#     txt += "%s],\n" % indent
#     txt += '%s"module.EFMod_TEDInstr.$seq": [\n' % indent
#     indent = 8 * " "
#     for rec in module_seq:
#         value = rec.get('value')
#         if isinstance(value, (dict, list)):
#             val = json.dumps(value, indent=4)
#             lines = val.rstrip().split('\n')
#             nested_indent = "    " + indent
#             txt += '%s{\n' % indent
#             txt += '%s"prop": "%s",\n' % (nested_indent, rec.get('prop'))
#             txt += '%s"time": %d,\n' % (nested_indent, rec.get('time'))
#             if isinstance(value, (dict)):
#                 txt += '%s"value": {\n' % nested_indent
#             else:
#                 txt += '%s"value": [\n' % nested_indent
#             for line in lines[1:-1]:
#                 txt += "%s%s\n" % (nested_indent, line)
#             txt = txt.rstrip(',\n')
#             txt += '\n'
#             if isinstance(value, (dict)):
#                 txt += '%s}\n' % nested_indent
#             else:
#                 txt += '%s]\n' % nested_indent
#             txt += "%s},\n" % indent
#         else:
#             txt += "%s%s,\n" % (indent, json.dumps(rec))
#     txt = txt.rstrip(',\n')
#     txt += '\n'
#     indent = 4 * " "
#     txt += "%s]\n}\n" % indent
#     # print(txt)
#     sanity_check = json.loads(txt)
#     with open(path, "w") as fh:
#         fh.write(txt)


def dump_csv(obj, path):
    # print("writing %s" % path)
    field_names = ['time', 'prop', 'value']
    with open(path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for rec in obj:
            writer.writerow(rec)


def dump_simplified_csv(recs, path):
    # print("writing %s" % path)
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
   

# def merge_seqs(scene1_seqs, module_seqs, file_name):
#     print(file_name)
#     records = []
#     for i, rec in enumerate(scene1_seqs):
#         obj = {
#             "time": rec.pop('time'),
#             "path": "scene.SScene1.$seq[%03d]" % i,
#             "data": json.dumps(rec)
#         }
#         records.append(obj)
#     for i, rec in enumerate(module_seqs):
#         obj = {
#             "time": rec.pop('time'),
#             "path": "module.EFMod_TEDInstr.$seq[%03d]" % i,
#             "data": json.dumps(rec)
#         }
#         records.append(obj)
#     records.sort(key=lambda x: x['path'])
#     records.sort(key=lambda x: x['time'])
#     fields = ["time", "path", "data"]
#     with open(file_name, "w") as outfh:
#         writer = csv.DictWriter(outfh, fieldnames=fields, quoting=csv.QUOTE_NONNUMERIC)
#         writer.writeheader()
#         for rec in records:
#             writer.writerow(rec)

SSCENE1_SEQ_CSV_RE = re.compile(r'^(\w+)\.SScene1_seq\.csv$')
SSCENE1_SEQ_ANALYZED_RE = re.compile(r'^(\w+)\.SScene1_seq\.simplified_csv\.analyzed\.csv$')


# def mk_scene1_excel_file(path, csv_files):
#     # print(csv_files)
#     wb = xlsxwriter.Workbook(os.path.join(path,'SScene1_seqs.xlsx'))
#     bold = wb.add_format({'bold': True})
#     ws = wb.add_worksheet()
#     # write header
#     ws.write('A1', 'Student')
#     ws.write('B1', 'Time', bold)
#     ws.write('C1', 'Prop', bold)
#     ws.write('D1', 'Value', bold)
#     start_row = 0
#     for csv_file in sorted(csv_files):
#         mat = SSCENE1_SEQ_CSV_RE.match(csv_file)
#         if mat is None:
#             raise Exception("no match %s" % csv_file)
#         student = mat.group(1)
#         ws_data = read_csv(os.path.join(path, csv_file))
#         for (row_num, row_data) in ws_data:
#             ws.write('A%d' % (row_num + start_row), student)
#             ws.write('B%d' % (row_num + start_row), row_data['time'])
#             ws.write('C%d' % (row_num + start_row), row_data['prop'])
#             ws.write('D%d' % (row_num + start_row), row_data['value'])
#         start_row += len(ws_data) + 1
#     wb.close()


def mk_analyzed_seq_excel_file(path, csv_files):
    # print(csv_files)
    wb = xlsxwriter.Workbook(os.path.join(path, "SScene1_seqs_analysis.xlsx"))
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
        mat = SSCENE1_SEQ_ANALYZED_RE.match(csv_file)
        if mat is None:
            raise Exception("no match %s" % csv_file)
        student = mat.group(1)
        ws_data = read_csv(os.path.join(path, csv_file))
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

def mk_excel_files(path, file_names):
    # scene1_seq_csv_files = []
    scene1_seq_analyzed_csv_files = []
    for file_name in file_names:
        # print(file_name)
        # if SSCENE1_SEQ_CSV_RE.match(file_name):
        #     scene1_seq_csv_files.append(file_name)
        if SSCENE1_SEQ_ANALYZED_RE.match(file_name):
            scene1_seq_analyzed_csv_files.append(file_name)
    # print(scene1_seq_csv_files)
    # print(scene1_seq_analyzed_csv_files)
    # mk_scene1_excel_file(path, scene1_seq_csv_files)
    mk_analyzed_seq_excel_file(path, scene1_seq_analyzed_csv_files)


def process_file(path, base_name):
    tutor_state_file_name = "%s.tutor_state.json" % base_name
    sscene1_file_name = "%s.SScene1_1.json" % base_name

    print(orig_file_name)

    orig_file_path = os.path.join(path, orig_file_name)
    obj = json.load(open(orig_file_path, "r"))

    sceneKey1 = 'scene'
    sceneKey2 = 'sceneState'
    sn = 'SScene1_seq'

    sscene1_seq = obj.get(sceneKey, {}).get('SScene1', {}).get('$seq', None)
    if sscene1_seq is None:
        raise Exception('Error no SScene1.$seq in %s' % orig_file_name)
    # json_file_path = os.path.join(path, "%s.%s.json" % (base_name, sn))
    csv_file_path = os.path.join(path, "%s.%s.csv" % (base_name, sn))
    csv_simplified_path = os.path.join(path, "%s.%s.simplified.csv" % (base_name, sn))
    csv_simplified_analyzed_path = os.path.join(path, "%s.%s.simplified_csv.analyzed.csv" % (base_name, sn))
    print(csv_file_path)
    print(csv_simplified_path)
    print(csv_simplified_analyzed_path)
    # dump_json(sscene1_seq, json_file_path)
    # dump_csv(sscene1_seq, csv_file_path)
    # dump_csv_simplified(sscene1_seq, csv_simplified_path)
    # analyze_simplified_csv(csv_simplified_path, csv_simplified_analyzed_path)
    # dump_simplified_json(sscene1_seq, module_seq, simplified_json_path)
    # print(only_seq_file_path)

def main(path):
    for (_unused1, _unused2, file_names) in os.walk(path):
        for file_name in sorted(file_names):
            mat = FILE_NAME_RE.match(file_name)
            if mat:
                base_name = mat.group(1)
                print(base_name)
                # process_file(path, base_name)
                # break
        # mk_excel_files(path, file_names)          
        break


if __name__ == "__main__":
    main(sys.argv[1])
