#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

MANY_SLASHES_PATTERN = r'[\/]+'
MANY_SLASHES_REGEX = re.compile(MANY_SLASHES_PATTERN)


PATTERN_ITEM_OR_KEY_ACCESS = r'^(?P<attr_name>[a-zA-Z][\w\d]*)' \
							 r'\[((?P<index>\d+)|' \
							 r'[\'\"](?P<key>[\s\w\d]+)[\'\"])\]$'
REGEX_ITEM_OR_KEY_ACCESS = re.compile(PATTERN_ITEM_OR_KEY_ACCESS)


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


def get_config_attribute(path, root_obj, head=None):
	"""
	Determine attribute of *root_obj* to be accessed by *path* in a
	(somewhat) safe manner.
	This implementation will allow key and index based accessing too
	(e.g. ``config.some_list[0]`` or ``config.some_dict['some_key']``)
	The *path* value needs to start with *head* (default='config').

	Args:
		path: character string specifying which attribute is to be accessed
		root_obj: An object whose attributes are to be accessed.
		head: Value of the first portion of *path*

	Returns:
		Attribute of *root_obj*

	Raises:
		ValueError: If *path* is invalid.
		AttributeError: If attribute cannot be accessed
	"""
	if head is None:
		head = 'config'
	portions = path.split('.')

	if len(portions) < 2:
		raise ValueError('Invalid path length')

	if portions[0] != head:
		raise ValueError(
			'Head is {!r}, expected {!r}'.format(portions[0], head))

	current_obj = root_obj

	for attr_name in portions[1:]:
		if not attr_name:
			raise ValueError("empty attr_name")

		if attr_name.startswith('_'):
			raise ValueError('private member')

		matcher = REGEX_ITEM_OR_KEY_ACCESS.match(attr_name)

		if matcher:
			gdict = matcher.groupdict()
			attr_name = gdict.get('attr_name')
			next_obj = getattr(current_obj, attr_name)

			if gdict.get("index"):
				index = int(gdict.get("index"))
				current_obj = next_obj[index]
			else:
				key = gdict["key"]
				current_obj = next_obj[key]
		else:
			current_obj = getattr(current_obj, attr_name)

	return current_obj


if __name__ == '__main__':
	import doctest

	(FAILED, SUCCEEDED) = doctest.testmod()
	print("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED))
