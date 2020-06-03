#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import pprint

directory = os.path.abspath('./folder')

if not os.path.isdir(directory):
	print("Please run create_example_folders.sh first")
	sys.exit(1)

bookmarklist_legacy = [x for x in os.listdir(directory) if (x[0] != '.' and (os.path.isdir(os.path.join(directory, x)) or (os.path.islink(os.path.join(directory, x)) and os.path.exists(os.path.join(directory, x)))))]
bookmarklist_legacy.sort()

bookmarklist = []
for item in sorted(os.listdir(directory)):
	abs_p = os.path.join(directory, item)
	if os.path.isdir(abs_p):
		bookmarklist.append(item)

print("Legacy lambda function result:")
pprint.pprint(bookmarklist_legacy)

print("Brave new function result:")
pprint.pprint(bookmarklist)
