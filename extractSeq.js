let fs = require('fs');

if (process.argv.length !== 3) {
    console.error("Usage: node extractSEQ.js FILE.json");
    process.exit(1);
}
let inputFile = process.argv[2];

let obj = JSON.parse(fs.readFileSync(inputFile));
let scene1seq = obj.scene.SScene1.$seq;
// console.log(scene1seq);
let moduleSeq = obj.module.EFMod_TEDInstr.$seq;
// console.log(moduleSeq);
let seq = [];
scene1seq.forEach((o, i) => {
    let data = [o.time, `SScene1.$seq.${i}`, o];
    delete o.time;
    seq.push(data);
});
moduleSeq.forEach((o, i) => {
    let data = [o.time, `EFMod_TEDInstr.$seq.${i}`, o];
    delete o.time;
    seq.push(data);
});

// console.log(seq);
seq.sort((a, b) => {
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
seq.forEach((entry) => {
    console.log(JSON.stringify(entry));
});
