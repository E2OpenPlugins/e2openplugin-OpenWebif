#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCSS_ROOT = os.path.join(PROJECT_ROOT, 'sourcefiles/scss')

CSS_ROOT = os.path.join(PROJECT_ROOT, 'plugin/public/css')

SCSS_ARGS = [
	"-t compressed",
	"--unix-newlines",
	"--sourcemap=none"
]

SCSS_MAP = [
	(os.path.join(SCSS_ROOT, "style.scss"), os.path.join(CSS_ROOT, "style.min.css")),
	(os.path.join(SCSS_ROOT, "theme/original.scss"), os.path.join(CSS_ROOT, "theme_original.css")),
]

if __name__ == '__main__':
	print("Watching {!s}".format(SCSS_ROOT))
	inotifywait_call = "inotifywait -r -e modify {folder}".format(folder=SCSS_ROOT)
	rc = subprocess.call(inotifywait_call, shell=True)

	while rc == 0:
		print("About to run:")

		for(src, dst) in SCSS_MAP:
			scss_call = 'scss {args} "{src}":"{dst}"'.format(args=' '.join(SCSS_ARGS), src=src, dst=dst)
			print(" {!s}".format(scss_call))
			scss_rc = subprocess.call(scss_call, shell=True)
			print("# RC={!s}".format(scss_rc))

		rc = subprocess.call(inotifywait_call, shell=True)
