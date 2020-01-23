let fs = require('fs');

let tedInstrOntology = "TED_Instr_ONTOLOGY.json";
let rqSelectOntology = "RQ_Select_ONTOLOGY.json";
let mergedOntology = "ONTOLOGY.json";

let ONTOLOGY = JSON.parse(fs.readFileSync(tedInstrOntology))._ONTOLOGY;
let rqOnt = JSON.parse(fs.readFileSync(rqSelectOntology))._ONTOLOGY;

function getOntologyKey(obj, path) {
    // let obj = ONTOLOGY;
    path = normalizeOntologyKey(path);
    var parts = path.split('.'),
        rv,
        index;
    for (rv = obj, index = 0; rv && index < parts.length; ++index) {
        rv = rv[parts[index]];
    }
    return rv;
}

function normalizeOntologyKey(key) {
    key = key.replace(/_/g, '.');
    key = key.replace('|', '.');
    return key;
}

// ONTOLOGY = {...ONTOLOGY, ...rqOnt}  would clobber most of ONTOLOGY as
// duplicate keys would get clobbered.  So we only mix in RQs manually
for (let a of [1, 2, 3, 4]) {
    let A = `A${a}`;
    rqA = rqOnt.S[A];
    // merge in any area of science keys present in rqOnt that aren't
    // in ONTOLOGY
    for (let k of Object.keys(rqA)) {
        if (!ONTOLOGY.S[A].hasOwnProperty(k)) {
            ONTOLOGY.S[A][k] = rqOnt.S[A][k];
        }
    }
    for (let t of [1, 2]) {
        let T = `T${t}`;

        rqT = rqOnt.S[A][T];
        for (let k of Object.keys(rqT)) {
            if (!ONTOLOGY.S[A][T].hasOwnProperty(k)) {
                ONTOLOGY.S[A][T][k] = rqOnt.S[A][T][k];
            }
        }
        // for (let rq of [1, 2, 3, 4]) {
        //     let RQ = `RQ${rq}`;
        //     let path = `S.${A}.${T}.${RQ}`;
        //     let val = getOntologyKey(rqOnt, path);
        //     // console.log(path, val);
        //     ONTOLOGY.S[A][T][RQ] = val
        // }
    }
}

fs.writeFileSync(mergedOntology, JSON.stringify(ONTOLOGY, null, 4));
