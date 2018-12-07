#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import copy
import logging
import argparse

logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(levelname)-8s %(message)s',
					datefmt='%Y-%m-%d %H:%M:%S')

LOG = logging.getLogger("inotify_watcher")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: default scss arguments
SCSS_ARGS = [
	"-t compressed",
	"--unix-newlines",
	"--sourcemap=none"
]

SCSS_ROOT = os.path.join(PROJECT_ROOT, 'sourcefiles/scss')

CSS_ROOT = os.path.join(PROJECT_ROOT, 'plugin/public/css')

#: source (SCSS) -> target (CSS) locations
SCSS_MAP = [
	(
		os.path.join(SCSS_ROOT, "style.scss"),
		os.path.join(CSS_ROOT, "style.min.css")
	),
	(
		os.path.join(SCSS_ROOT, "theme/original.scss"),
		os.path.join(CSS_ROOT, "theme_original.css")
	),
	(
		os.path.join(SCSS_ROOT, "theme/original-small-screen.scss"),
		os.path.join(CSS_ROOT, "../themes/original-small-screen.css")
	),
]

#: default locations of used binaries
BINARIES_DEFAULT = {
	"inotifywait": "inotifywait",
	"scss": "scss"
}

#: locations of used binaries (may be overridden by environment variables)
BINARIES = copy.copy(BINARIES_DEFAULT)


def call_scss(scss_map):
	for (src, dst) in scss_map:
		scss_call = '{binary} {args} "{src}":"{dst}"'.format(
			binary=BINARIES['scss'], args=' '.join(SCSS_ARGS),
			src=src, dst=dst)
		LOG.info(" {!s}".format(scss_call))
		scss_rc = subprocess.call(scss_call, shell=True)
		LOG.info("# RC={!s}".format(scss_rc))


def watch(root, scss_map=SCSS_MAP):
	LOG.debug("Watching {!s}".format(root))
	inotifywait_call = "{binary} -r -e modify {folder}".format(
		binary=BINARIES['inotifywait'], folder=root)

	rc = subprocess.call(inotifywait_call, shell=True)
	while rc == 0:
		LOG.info("About to run:")
		call_scss(scss_map)

		rc = subprocess.call(inotifywait_call, shell=True)


if __name__ == '__main__':
	argparser = argparse.ArgumentParser()
	argparser.add_argument(
		'--force-update', '-u', action='store_true',
		dest="force_update",
		help="Force updating of CSS files and terminate", default=False)
	argparser.add_argument(
		'--verbose', '-v', action='count',
		default=0, dest="verbose",
		help="verbosity (more v: more verbosity)")

	args = argparser.parse_args()

	LOG.warning("inotifywait and scss binaries need to be installed!")
	LOG.warning(
		" 'apt-get install inotify-tools ruby-sass' on debian "
		"derived distributions")

	for key in BINARIES_DEFAULT:
		env_key = key.upper()
		try:
			BINARIES[key] = os.environ[env_key]
		except KeyError:
			LOG.debug(
				"You may use environment variable {env_key!r} to "
				"override used binary {binary!r}.".format(
					env_key=env_key, binary=BINARIES_DEFAULT[key]))

	if args.verbose > 0:
		LOG.debug("Supported S/CSS transformations:")
		for (src, dst) in SCSS_MAP:
			LOG.debug("{!r} -> {!r}".format(src, dst))

	if args.force_update:
		call_scss(SCSS_MAP)
		sys.exit(0)

	try:
		watch(SCSS_ROOT)
	except KeyboardInterrupt:
		LOG.info("\nAborted.")
