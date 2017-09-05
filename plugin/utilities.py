#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

MANY_SLASHES_PATTERN = r'[\/]+'
MANY_SLASHES_REGEX = re.compile(MANY_SLASHES_PATTERN)


def lenient_decode(value, encoding=None):
	"""
	Decode an encoded string and convert it to an unicode string.

	:param value: input value
	:param encoding: string encoding, defaults to utf-8
	:return: decoded value
	:rtype: unicode

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


if __name__ == '__main__':
	import doctest

	(FAILED, SUCCEEDED) = doctest.testmod()
	print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
