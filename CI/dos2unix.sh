#!/bin/sh

echo ""
echo "dos2unix safe cleanup by Persian Prince"
# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.
echo ""
echo "Changing py files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "dos2unix files"
find . -type f \( -iname \*.bb -o -iname \*.conf -o -iname \*.c -o -iname \*.h -o -iname \*.po -o -iname \*.am -o -iname \*.inc -o -iname \*.py -o -iname \*.xml -o -iname \*.sh -o -iname \*.bbappend -o -iname \*.md \) -exec dos2unix {} +
git add -u
git add *
git commit -m "dos2unix files"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast changing would be less than 1 minute."
echo ""
echo "dos2unix Done!"
echo ""