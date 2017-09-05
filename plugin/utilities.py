#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

MANY_SLASHES_PATTERN = r'[\/]+'
MANY_SLASHES_REGEX = re.compile(MANY_SLASHES_PATTERN)


def lenient_decode(value, encoding=None):
	"""
	Decode an URL encoded string and convert it to an unicode string.

	:param value: input value
	:param encoding: string encoding, defaults to utf-8
	:return: decoded value
	:rtype: unicode
	"""
	if encoding is None:
		encoding = 'utf_8'
	return value.decode(encoding, 'ignore')


def sanitise_url_path_parameter(value, encoding=None):
	"""
	Decode an URL encoded path and convert it to an unicode string.
	Multiple slashes are replaced by a single slash and path is normalised.

	:param value: input value
	:param encoding: string encoding, defaults to utf-8
	:return: decoded path
	:rtype: unicode

	>>> sanitise_url_path_parameter('/bla')
	u'/bla'
	>>> sanitise_url_path_parameter('/bla')
	u'/bla'
	>>> sanitise_url_path_parameter('../etc/passwd')
	u'../etc/passwd'
	>>> sanitise_url_path_parameter('../haha/////../../hihi 123$/')
	u'../../hihi 123$'
	>>> sanitise_url_path_parameter('/////haha/hoho////huch/../../hihi 123$/')
	u'/haha/hihi 123$'
	>>> sanitise_url_path_parameter('')
	Traceback (most recent call last):
		...
	ValueError: Empty
	"""
	mangled = lenient_decode(value, encoding)
	if not mangled:
		raise ValueError("Empty")
	mangled = re.sub(MANY_SLASHES_REGEX, '/', mangled)
	mangled = os.path.normpath(mangled)
	return mangled


if __name__ == '__main__':
	import doctest

	(FAILED, SUCCEEDED) = doctest.testmod()
	print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
