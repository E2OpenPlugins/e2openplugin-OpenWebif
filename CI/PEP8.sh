#!/bin/sh

echo ""
echo "PEP8 double aggressive safe cleanup by Persian Prince"
# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.
echo ""
echo "Changing py files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "PEP8 double aggressive"
autopep8 . -a -a -j 0 --recursive --select=E401,E701,W605,E70,E502,E251,E252,E20,E211,E22,E224,E241,E242,E27,E225,E226,E227,E228,E231,E261,E262,E301,E302,E303,E304,E305,E306,W291,W292,W293,W391 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast changing would be less than 1 minute."
echo ""
echo "PEP8 Done!"
echo ""
