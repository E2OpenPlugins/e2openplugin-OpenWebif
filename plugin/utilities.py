#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

MANY_SLASHES_PATTERN = r'[\/]+'
MANY_SLASHES_REGEX = re.compile(MANY_SLASHES_PATTERN)


def lenient_decode(value, encoding=None):
	"""
	Decode an encoded string and convert it to an unicode string.

	Args:
		value: input value
		encoding: string encoding, defaults to utf-8
	Returns:
		(unicode) decoded value

	>>> lenient_decode("Hallo")
	u'Hallo'
	>>> lenient_decode(u"Hallo")
	u'Hallo'
	>>> lenient_decode("HällöÜ")
	u'H\\xe4ll\\xf6\\xdc'
	"""
	if isinstance(value, unicode):
		return value

	if encoding is None:
		encoding = 'utf_8'

	return value.decode(encoding, 'ignore')


def lenient_force_utf_8(value):
	"""

	Args:
		value: input value
	Returns:
		(basestring) utf-8 encoded value

	>>> isinstance(lenient_force_utf_8(''), basestring)
	True
	>>> lenient_force_utf_8(u"Hallo")
	'Hallo'
	>>> lenient_force_utf_8("HällöÜ")
	'H\\xc3\\xa4ll\\xc3\\xb6\\xc3\\x9c'
	"""
	return lenient_decode(value).encode('utf_8')


def sanitise_filename_slashes(value):
	"""

	Args:
		value: input value
	Returns:
		value w/o multiple slashes

	>>> in_value = "///tmp/x/y/z"
	>>> expected = re.sub("^/+", "/", "///tmp/x/y/z")
	>>> sanitise_filename_slashes(in_value) == expected
	True
	"""
	return re.sub(MANY_SLASHES_REGEX, '/', value)


if __name__ == '__main__':
	import doctest

	(FAILED, SUCCEEDED) = doctest.testmod()
	print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
