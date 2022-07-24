#!/bin/sh

echo ""
echo "NPM build JS and CSS"
begin=$(date +"%s")

echo ""
echo "Run npm to compile and minimise JS and CSS files"
cd sourcefiles
npm install
npm install path-exists
npm install semver
npm update
npm ci --prefix modern
npm run build-css
npm run build-classic-css
npm run build-classic-js
npm run build-js
cd ..
git add -u
git add *
git commit -m "Compile JS & CSS assets"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo ""
echo "NPM build done!"
echo ""
