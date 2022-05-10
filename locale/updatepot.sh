#!/bin/bash
# Script to generate pot file outside of the normal build process
#  
# Pre-requisite:
# The following tools must be installed on your system and accessible from path
# gawk, find, xgettext, (g)sed, python, msguniq, msgmerge, msgattrib, msgfmt, msginit
#
# Run this script from within the locale folder.
#
# Author: Pr2
# Version: 1.1
#
#
# On Mac OSX find option are specific
#
findoptions=""
if [[ "$OSTYPE" == "darwin"* ]]
	then
		# Mac OSX
		printf "Script running on Mac OSX [%s]\n" "$OSTYPE"
    	findoptions="-s -X"
fi
#
# sed detection
#
localgsed="sed"
gsed --version 2> /dev/null | grep -q "GNU"
if [ $? -eq 0 ]; then
        localgsed="gsed"
else
        "$localgsed" --version | grep -q "GNU"
        if [ $? -eq 0 ]; then
                printf "GNU sed found: [%s]\n" $localgsed
        fi
fi
Plugin=OpenWebif

#
# Arguments to generate the pot and po files are not retrieved from the Makefile.
# So if parameters are changed in Makefile please report the same changes in this script.
#

printf "Creating temporary file $Plugin-py.pot\n"
find $findoptions ../plugin -name "*.py" -exec xgettext --no-wrap -L Python --from-code=UTF-8 -kpgettext:1c,2 --add-comments="TRANSLATORS:" -d $Plugin -s -o $Plugin-py.pot {} \+
$localgsed --in-place $Plugin-py.pot --expression=s/CHARSET/UTF-8/
printf "Creating temporary file $Plugin-xml.pot\n"
which python
if [ $? -eq 0 ]; then
	find $findoptions ../plugin -name "*.xml" -exec python xml2po.py {} \+ > $Plugin-xml.pot
else
	find $findoptions ../plugin -name "*.xml" -exec python3 xml2po.py {} \+ > $Plugin-xml.pot
fi
printf "Merging pot files to create: $Plugin.pot\n"
cat $Plugin-py.pot $Plugin-xml.pot | msguniq --no-wrap -o $Plugin.pot -
OLDIFS=$IFS
IFS=" "
rm $Plugin-py.pot $Plugin-xml.pot
IFS=$OLDIFS
printf "Pot file update/creation from script finished!\n"


