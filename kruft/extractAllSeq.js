let fs = require('fs');


const FILES = "1 2 3 4 5 6 7 8 9 10 11 12 12A 13 14 15 16 17 18 19 20 21".split(' ');

let allRecs = new Set();
let fileRecs = {};

// function sortRecs(recs) {
//     // console.log(seq);
//     recs.sort((a, b) => {
//         if (a[0] > b[0]) {
//             return 1;
//         } else if (a[0] < b[0]) {
//             return -1;
//         } else if (a[1].startsWith('SScene') && b[1].startsWith('EFMod')) {
//             return 1
//         } else if (a[1].startsWith('EFMod') && b[1].startsWith('SScene')) {
//             return -11;
//         } else {
//             let ap = parseInt(a[1].split('.')[2], 10);
//             let bp = parseInt(b[1].split('.')[2], 10);
//             if (ap > bp) {
//                 return 1;
//             } else if (bp > ap) {
//                 return -1;
//             } else {
//                 return 0;
//             }
//             // return a[1].localeCompare(b[1]);
//         }
//     });
// }

const sortRecs = (a, b) => {
    // console.log(seq);
    if (a[0] > b[0]) {
        return 1;
    } else if (a[0] < b[0]) {
        return -1;
    } else if (a[1].startsWith('SScene') && b[1].startsWith('EFMod')) {
        return 1
    } else if (a[1].startsWith('EFMod') && b[1].startsWith('SScene')) {
        return -11;
    } else {
        let ap = parseInt(a[1].split('.')[2], 10);
        let bp = parseInt(b[1].split('.')[2], 10);
        if (ap > bp) {
            return 1;
        } else if (bp > ap) {
            return -1;
        } else {
            return 0;
        }
        // return a[1].localeCompare(b[1]);
    }
};

function processFile(file) {
    let inputFile = `SScene${file}_1.json`;
    console.log(`processing ${inputFile}`);
    let obj = JSON.parse(fs.readFileSync(inputFile));
    let scene1seq = obj.scene.SScene1.$seq;
    // console.log(scene1seq);
    let moduleSeq = obj.module.EFMod_TEDInstr.$seq;
    // console.log(moduleSeq);
    let recs = new Set();
    // let fileSeq = new Set();
    fileSeqs = [];
    if ("1" === file) {
        scene1seq.forEach((o, i) => {
            let data = [o.time, `SScene1.$seq.${i}`, o];
            // delete o.time;
            // seq.push(o);
            recs.add(JSON.stringify(data));
        });
    }
    moduleSeq.forEach((o, i) => {
        let data = [o.time, `EFMod_TEDInstr.$seq.${i}`, o];
        // delete o.time;
        // seq.push(o);
        recs.add(JSON.stringify(data));
    });

    recs.forEach((rec) => {
        if (!allRecs.has(rec)) {
            allRecs.add(rec);
            fileSeqs.push(JSON.parse(rec));
            // console.log(`new record: ${rec}`);
        }
    });

    fileSeqs.sort(sortRecs);
    fileRecs[file] = fileSeqs;
    // let tmp = fileRecs[file];
    // console.log(tmp);

}

FILES.forEach((file) => {
     processFile(file)
});


FILES.forEach((file) => {
    console.log(file);
    let fr = fileRecs[file];
    fr.forEach((rec) => {
        console.log(`SScene${file}`, rec[0], rec[1], JSON.stringify(rec[2]));
    });
});