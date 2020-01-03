let fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const SCENES = "1 2 3 4 5 6 7 8 9 10 11 12 12A 13 14 15 16 17 18 19 20 21".split(' ');

if (process.argv.length !== 3) {
    console.error("Usage: node extractSEQ2.js FILE.json");
    process.exit(1);
}

let inputFile = process.argv[2];
let intermediateFile = inputFile.replace('json', 'intermediate.json');

let obj = JSON.parse(fs.readFileSync(inputFile));

let seq = [];

SCENES.forEach((scene) => {
    const s = `SScene${scene}`;
    if (obj.scene.hasOwnProperty(s)) {
        obj.scene[s].$seq.forEach((o, i) => {
            // if (o.prop !== 'complete') {
            let rec = [o.time, `${s}.$seq.${i}`, o];
            delete o.time;
            seq.push(rec);
        // }
        });
    } else {
        console.log(`skipping ${s}`);
    }
});

let moduleSeq = obj.module.EFMod_TEDInstr.$seq;
moduleSeq.forEach((o, i) => {
    let data = [o.time, `EFMod_TEDInstr.$seq.${i}`, o];
    delete o.time;
    seq.push(data);
// }
});

// console.log(seq);
seq.sort((a, b) => {
    if (a[0] > b[0]) {
        return 1;
    } else if (a[0] < b[0]) {
        return -1;
    } else if (a[1].startsWith('SScene') && b[1].startsWith('EFMod')) {
        return -1;
    } else if (a[1].startsWith('EFMod') && b[1].startsWith('SScene')) {
        return 1;
    } else {
        let ap = parseInt(a[1].split('.')[2], 10);
        let bp = parseInt(b[1].split('.')[2], 10);
        if (ap > bp ) {
            return 1;
        } else if (bp > ap) {
            return -1;
        } else {
            return 0;
        }
        // return a[1].localeCompare(b[1]);
    }
});

const selectValueRE = /^(TVSel|VSel)/;
const skipProps = ["complete", "rowsComplete"]
function filterRecords(recs) {
    let filtered = [];
    recs.forEach((rec) => {
        let obj = rec[2];
        if (selectValueRE.test(obj.prop) && obj.value === null) {
            //noop
        } else if (skipProps.includes(obj.prop)) {
            // noop
        } else { 
            filtered.push(rec);
        }
    });
    return filtered;
}


function filterIntermediateRecords(recs) {
    // filter out any correct props which occur between currentRow and the
    // actual selection of a value
    let filtered = [];
    let filterCorrect = false;
    recs.forEach((rec) => {
        let skip = false;
        let o = rec[2];
        if (o.prop === "currentRow") {
            filterCorrect = true;
        } else if (filterCorrect && o.prop === "correct") {
            skip = true;
        } else if (selectValueRE.test(o.prop)) {
            filterCorrect = false;
        }
        if (!skip) {
            filtered.push(rec);
        }
    });
    return filtered;
}

function clobberDups(recs) {
    let recs2 = [];
    let props = {};
    let i;
    for (i=0; i < recs.length; i++) {
        let rec = recs[i];
        let o = rec[2];
        if (o.prop === "currentRow") {
            break;
        }
        props[o.prop] = rec;
    }
    for (let r of Object.values(props)) {
        recs2.push(r)
    }
    recs2.sort((a, b) => {
        if (a[0] > b[0]) {
            return 1
        } else if (a[0] < b[0]) {
            return -1;
        } else if (a[0] === b[0]) {
            return 0
        }
    });
    for (let j=i; j< recs.length; j++) {
        recs2.push(recs[j]);
    }
    return recs2;
}

let filteredRecs = filterRecords(seq);

let filteredRecs2 = filterIntermediateRecords(filteredRecs);

let filteredRecs3 = clobberDups(filteredRecs2)


fs.writeFileSync(intermediateFile, JSON.stringify(filteredRecs3, null, 4));

// let ONTOLOGY = JSON.parse(fs.readFileSync("ONTOLOGY.json"))._ONTOLOGY;

// function getType(obj) {
//     let dataType = typeof (obj);
//     dataType = Array.isArray(obj) ? "array" : dataType;
//     dataType = null === obj ? "null" : dataType;
//     dataType = (dataType === obj && Object.keys(obj).length === 0) ? "emptyobj" : dataType;
//     return dataType
// }

// function getOntologyKey(obj, path) {
//     // let obj = ONTOLOGY;
//     path = normalizeOntologyKey(path);
//     var parts = path.split('.'),
//         rv,
//         index;
//     for (rv = obj, index = 0; rv && index < parts.length; ++index) {
//         rv = rv[parts[index]];
//     }
//     return rv;
// }

// function normalizeOntologyKey(key) {
//     key = key.replace(/_/g, '.');
//     key = key.replace('|', '.');
//     return key;
// }

// let props = [];
// seq.forEach((entry) => {
//     // console.log(JSON.stringify(entry));
//     let o = entry[2];
//     if (!props.includes(o.prop)) {
//         props.push(o.prop);
//     }
// });

// props.sort();
// props.forEach((p) => {
//     console.log(p);
// });

    // let prop = o.prop;
    // let mat = selectedRE.exec(prop);
    // let skip = false;
    // if (mat) {
    //     if (prop.endsWith("ontologyKey")) {
    //         if (mat[1].endsWith('RQ') ) {
    //             o.value = getOntologyKey(RQ_ONTOLOGY, o.value).ExpSelected2;
    //         }
    //         else {
    //             o.value = getOntologyKey(ONTOLOGY, o.value);
    //         }
    //         o.prop = mat[1];
    //     } else {
    //         skip = true;
    //     }
    // }
    // if (!skip) {

// const selectedRE = /^(selected.+)\./;
// let intermediateFile = inputFile.replace('json', 'intermediate.json');

// let outputFile = inputFile.replace('json', 'csv');


// let state = {
//     time: null,
//     source: null,
//     // "selectedArea.index": null,
//     // "selectedArea.ontologyKey": null,
//     "selectedArea": null,
//     // "selectedTopic.index": null,
//     // "selectedTopic.ontologyKey": null,
//     "selectedTopic": null,
//     // "selectedVariable.index": null,
//     // "selectedVariable.ontologyKey": null,
//     "selectedVariable": null,
//     // "selectedRQ.ontologyKey": null,
//     "selectedRQ": null,
//     TEDExptArea: null,
//     TEDExptTopic: null,
//     TEDExptVariable: null,
//     TEDExptRQ: null,
//     independentVarN: null,
//     "TVSel.col1": null,
//     "TVSel.col2": null,
//     "VSel.col1": null,
//     "VSel.col2": null,
//     correct: null,
//     Expt1_Q1: null,
//     Expt1_Q2_RIGHT: null,
//     Expt1_Q4: null,
//     Expt1_Q4A_RIGHT: null,
//     TEDExpt1V1: null,
//     TEDExpt1V2: null,
//     TEDExpt1V3: null,
//     TEDExpt1V4: null,
//     TEDExpt2V1: null,
//     TEDExpt2V2: null,
//     TEDExpt2V3: null,
//     TEDExpt2V4: null,
//     TEDExptConfounds: null,
//     TEDExptDifferent: null,
//     TEDExptNC1Confound: null,
//     TEDExptNC1SameDiff: null,
//     TEDExptNC2Confound: null,
//     TEDExptNC2SameDiff: null,
//     TEDExptNC3Confound: null,
//     TEDExptNC3SameDiff: null,
//     TEDExptNonTarget: null,
//     TEDExptPOSTSequence: null,
//     TEDExptPOSTTV: null,
//     TEDExptVarNC1: null,
//     TEDExptVarNC2: null,
//     TEDExptVarNC3: null,
//     TEDFeatureFocus: null,
//     TEDcorrection: null,
//     complete: null,
//     currentRow: null,
//     differentRow: null,
//     rowsComplete: null,
//     sameRow1: null,
//     sameRow2: null,
//     sameRow3: null,

// };
// let columns = [];
// for (k of Object.keys(state)) {
//     columns.push({
//         id: k,
//         title: k
//     });
// }

// const csvWriter = createCsvWriter({
//     path: outputFile,
//     header: columns
// });

// let states = [];

// seq.forEach((entry) => {
//     let newState = JSON.parse(JSON.stringify(state));
//     newState.time = entry[0];
//     newState.source = entry[1];
//     let prop = entry[2].prop;
//     let value = entry[2].value;
//     if ("object" === getType(value)) {
//         if (value.hasOwnProperty('ontologyKey')) {
//             value = getOntologyKey(ONTOLOGY, value.ontologyKey);
//             if ("object" === getType(value)) {
//                 if (value.hasOwnProperty('name')) {
//                     value = value.name;
//                 }
//             }
//         }
//         value = JSON.stringify(value);
//     } else if ("array" === getType(value)) {
//         value = JSON.stringify(value);
//     }
//     newState[prop] = value;
//     states.push(newState);
// });

// // states.forEach((st) => {
// //     console.log(st);
// // });
// csvWriter.writeRecords(states)
//     .then(() => console.log('success'))
//     .catch((err) => console.errror(err));