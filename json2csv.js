const createCsvWriter = require('csv-writer').createObjectCsvWriter

let fs = require('fs');

const MAX_DEPTH = 6;
const DONT_RECUR_TYPES = ["number", "string", "boolean", "null", "emptyobj"];

let RECORDS = [];

function dumpData(pth, val) {
    // let v = val.replace(/"/g, '');
    // console.log(`"${pth}", "${v}"`);
    RECORDS.push({path: pth, value: val})
}

function getType(obj) {
    let dataType = typeof(obj);
    dataType = Array.isArray(obj) ? "array" : dataType;
    dataType = null === obj ? "null" : dataType;
    dataType = (dataType === obj && Object.keys(obj).length === 0) ? "emptyobj" : dataType;
    return dataType
}

function dontRecur(elementTypes) {
    return elementTypes.every((eleType) => DONT_RECUR_TYPES.includes(eleType));
}

function escapedJson(obj) {
    json = JSON.stringify(obj);
    // json = json.replace(/"/g, "'");
    // return `"${json}"`;
    return json;
}

function recurse_data(currPath, currData, currDepth) {
    if (currDepth === MAX_DEPTH) {
        return;
    }
    let dataType = getType(currData);
    switch(dataType) {
        case "number":
        case "boolean":
        case "null":
            dumpData(currPath, currData);
            break;
        case "emptyobj":
            // console.log(`${currPath}, {}`);
            dumpData(currPath, {});
            break;
        case "string":
            // console.log(`${curr_path}, "${curr_data}"`);
            dumpData(currPath, `"${currData}"`);
            break;
        case "array":
            if (currPath.endsWith("$seq")) {
                currData.forEach((item, idx) => {
                    dumpData(`${currPath}[${idx}]`, escapedJson(currData[idx]));
                });
            } else {
                let itemTypes = currData.map((item) => getType(item));
                if (dontRecur(itemTypes)) {
                    dumpData(currPath, JSON.stringify(currData));
                } else {
                    currData.forEach((item, idx) => {
                        recurse_data(`${currPath}[${idx}]`, item, currDepth + 1);
                    });
                }
            }
            break;
        case "object":
            // console.log(currPath);
            let keys = Object.keys(currData);
            let keyTypes = keys.map((key) => getType(currData[key]));
            // let dontRecur = key_types.every((type) => DONT_RECUR_TYPES.includes(type));
            if (dontRecur(keyTypes)) {
                dumpData(currPath, escapedJson(currData));
            } else {
                for (let key of Object.keys(currData)) {
                    recurse_data(`${currPath}.${key}`, currData[key], currDepth + 1);
                }
            }
            break;
        default:
            console.log(`ERROR: unhandled type: ${curr_path}, ${data_type.toUpperCase()}`);
    }
}

// function main() {
if (process.argv.length !== 3) {
    console.error("Usage: node json2csv.js file.json");
    process.exit(1);
}
let inputFile = process.argv[2];
let outputFile = inputFile.replace('.json', '.csv')

const csvWriter = createCsvWriter({
    path: outputFile,
    header: [{
        id: 'path',
        title: 'Path'
    }, {
        id: 'value',
        title: 'Value'
    }]
});

let data = JSON.parse(fs.readFileSync(inputFile));
// top_level_keys = ["scene", "module", "tutor"];
// recurse_data(inputFile, data, 0);
recurse_data("", data, 0);
// console.log(RECORDS);
csvWriter.writeRecords(RECORDS)
.then(() => console.log('success'))
.catch((err) => console.error(err));
// }
// main();
