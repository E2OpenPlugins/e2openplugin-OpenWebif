#!/bin/sh

echo ""
echo "NPM Build JS AND CSS"
echo ""
echo "Changing py files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "Run npm to minimize CSS and JS"
cd sourcefiles
npm install
npm run build-css
npm run build-classic-js
npm run build-js
cd ..
git add -u
git add *
git commit -m "Update JS/CSS min files"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast changing would be less than 1 minute."
echo ""
echo "NPM Build Done!"
echo ""
