#!/bin/sh

echo ""
echo "PEP8 double aggressive safe cleanup by Persian Prince"
# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.
echo ""
echo "Changing py files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "PEP8 double aggressive E401"
autopep8 . -a -a -j 0 --recursive --select=E401 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E401 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive E701, E70 and E502"
autopep8 . -a -a -j 0 --recursive --select=E701,E70,E502 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E701, E70 and E502 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive E251 and E252"
autopep8 . -a -a -j 0 --recursive --select=E251,E252 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E251 and E252 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive E20 and E211"
autopep8 . -a -a -j 0 --recursive --select=E20,E211 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E20 and E211 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive E22, E224, E241, E242 and E27"
autopep8 . -a -a -j 0 --recursive --select=E22,E224,E241,E242,E27 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E22, E224, E241, E242 and E27 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive E225 ~ E228 and E231"
autopep8 . -a -a -j 0 --recursive --select=E225,E226,E227,E228,E231 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E225 ~ E228 and E231 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive E301 ~ E306"
autopep8 . -a -a -j 0 --recursive --select=E301,E302,E303,E304,E305,E306 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive E301 ~ E306 (build $TRAVIS_BUILD_NUMBER)"

echo ""
echo "PEP8 double aggressive W291 ~ W293 and W391"
autopep8 . -a -a -j 0 --recursive --select=W291,W292,W293,W391 --in-place
git add -u
git add *
git commit -m "PEP8 double aggressive W291 ~ W293 and W391 (build $TRAVIS_BUILD_NUMBER)"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
echo -e "Change time was $(($timediff / 60)) minutes and $(($timediff % 60)) seconds."
echo -e "Fast changing would be less than 1 minute."
echo ""
echo "PEP8 Done!"
echo ""
