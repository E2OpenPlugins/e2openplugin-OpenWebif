#! /usr/bin/env node

const glob = require('glob');
const path = require('path');
const mkdirp = require('mkdirp');
const cleanCssCli = require('clean-css-cli');

// test for -o

// -o '../../plugin/public/' './css/**/*.css'"
const outputDir = path.resolve(process.argv.slice(0, 4)[3]);
const srcFiles = process.argv.slice(4).join();
console.log(outputDir)
glob(srcFiles, (err, files) => {
  files.forEach((file) => {
    let srcFile = path.parse(file);
    let outDirPath = path.resolve(outputDir, srcFile.dir);
    mkdirp(outDirPath).then( (newDir) => {
      process.argv[3] = `${outDirPath}${path.sep}${srcFile.name}.min${srcFile.ext}`;
      process.argv[4] = file;
      cleanCssCli(process, function beforeMinify(cleanCss) {
        cleanCss.options.inline = ['none'];
        cleanCss.options.rebase = false;
      });
    });
  });
});
