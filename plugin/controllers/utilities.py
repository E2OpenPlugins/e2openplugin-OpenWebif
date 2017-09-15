#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

PATTERN_ITEM_OR_KEY_ACCESS = r'^(?P<attr_name>[a-zA-Z][\w\d]*)' \
							 r'\[((?P<index>\d+)|' \
							 r'[\'\"](?P<key>[\s\w\d]+)[\'\"])\]$'
REGEX_ITEM_OR_KEY_ACCESS = re.compile(PATTERN_ITEM_OR_KEY_ACCESS)


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
