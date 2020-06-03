#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
#!/usr/bin/env python
import re
import six

MANY_SLASHES_PATTERN = r'[\/]+'
MANY_SLASHES_REGEX = re.compile(MANY_SLASHES_PATTERN)

PATTERN_ITEM_OR_KEY_ACCESS = r'^(?P<attr_name>[a-zA-Z][\w\d]*)' \
							r'\[((?P<index>\d+)|' \
							r'[\'\"](?P<key>[\s\w\d]+)[\'\"])\]$'
REGEX_ITEM_OR_KEY_ACCESS = re.compile(PATTERN_ITEM_OR_KEY_ACCESS)

# stolen from enigma2_http_api ...
# https://wiki.neutrino-hd.de/wiki/Enigma:Services:Formatbeschreibung
# Dezimalwert: 1=TV, 2=Radio, 4=NVod, andere=Daten

SERVICE_TYPE_TV = 0x01
SERVICE_TYPE_RADIO = 0x02
SERVICE_TYPE_SD4 = 0x16
SERVICE_TYPE_HDTV = 0x19
SERVICE_TYPE_UHD = 0x1f
SERVICE_TYPE_OPT = 0xd3
SERVICE_TYPE_RADIOA = 0x0a

# type 1 = digital television service
# type 2 = digital radio sound service
# type 4 = nvod reference service (NYI)
# type 10 = advanced codec digital radio sound service
# type 17 = MPEG-2 HD digital television service
# type 22 = advanced codec SD digital television
# type 24 = advanced codec SD NVOD reference service (NYI)
# type 25 = advanced codec HD digital television
# type 27 = advanced codec HD NVOD reference service (NYI)


SERVICE_TYPE = {
	SERVICE_TYPE_TV: 'TV',
	SERVICE_TYPE_HDTV: 'HDTV',
	SERVICE_TYPE_RADIO: 'RADIO',
	SERVICE_TYPE_RADIOA: 'RADIO',
	SERVICE_TYPE_UHD: 'UHD',
	SERVICE_TYPE_SD4: 'SD4',
	SERVICE_TYPE_OPT: 'OPT',
}

SERVICE_TYPE_LOOKUP = {k: v for k, v in six.iteritems(SERVICE_TYPE)}

#: Namespace - DVB-C services
NS_DVB_C = 0xffff0000

#: Namespace - DVB-S services
# NS_DVB_S = 0x00c00000

#: Namespace - DVB-T services
NS_DVB_T = 0xeeee0000

#: Label:Namespace map
NS = {
	'DVB-C': NS_DVB_C,
	# 'DVB-S': NS_DVB_S,
	'DVB-T': NS_DVB_T,
}

#: Namespace:Label lookup map
NS_LOOKUP = {v: k for k, v in six.iteritems(NS)}


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


def parse_servicereference(serviceref):
	"""
	Parse a Enigma2 style service reference string representation.

	:param serviceref: Enigma2 style service reference
	:type serviceref: string

	>>> sref = '1:0:1:300:7:85:00c00000:0:0:0:'
	>>> result = parse_servicereference(sref)
	>>> result
	{'service_type': 1, 'oid': 133, 'tsid': 7, 'ns': 12582912, 'sid': 768}
	>>> sref_g = create_servicereference(**result)
	>>> sref_g
	'1:0:1:300:7:85:00c00000:0:0:0:'
	>>> sref_g2 = create_servicereference(result)
	>>> sref_g2
	'1:0:1:300:7:85:00c00000:0:0:0:'
	>>> sref == sref_g
	True
	>>> sref2 = '1:64:A:0:0:0:0:0:0:0::SKY Sport'
	>>> result2 = parse_servicereference(sref2)
	>>> result2
	{'service_type': 10, 'oid': 0, 'tsid': 0, 'ns': 0, 'sid': 0}
	>>> sref3 = '1:0:0:0:0:0:0:0:0:0:/media/hdd/movie/20170921 2055 - DASDING - DASDING Sprechstunde - .ts'
	>>> result3 = parse_servicereference(sref3)
	>>> result3
	{'service_type': 0, 'oid': 0, 'tsid': 0, 'ns': 0, 'sid': 0}
	"""
	parts = serviceref.split(":")
	sref_data = {
		'service_type': int(parts[2], 16),
		'sid': int(parts[3], 16),
		'tsid': int(parts[4], 16),
		'oid': int(parts[5], 16),
		'ns': int(parts[6], 16)
	}
	return sref_data


def create_servicereference(*args, **kwargs):
	"""
	Generate a (Enigma2 style) service reference string representation.

	:param args[0]: Service Reference Parameter as dict
	:type args[0]: :class:`dict`

	:param service_type: Service Type
	:type service_type: int

	:param sid: SID
	:type sid: int

	:param tsid: TSID
	:type tsid: int

	:param oid: OID
	:type oid: int

	:param ns: Enigma2 Namespace
	:type ns: int
	"""
	if len(args) == 1 and isinstance(args[0], dict):
		kwargs = args[0]
	service_type = kwargs.get('service_type', 0)
	sid = kwargs.get('sid', 0)
	tsid = kwargs.get('tsid', 0)
	oid = kwargs.get('oid', 0)
	ns = kwargs.get('ns', 0)

	return '{:x}:0:{:x}:{:x}:{:x}:{:x}:{:08x}:0:0:0:'.format(
		1,
		service_type,
		sid,
		tsid,
		oid,
		ns)

# Fallback genre
def getGenreStringLong(hn, ln):
	return ""

# Fallback moviePlayState
def _moviePlayState(cutsFileName, ref, length):
	return 0


if __name__ == '__main__':
	import doctest

	(FAILED, SUCCEEDED) = doctest.testmod()
	print(("[doctest] SUCCEEDED/FAILED: {:d}/{:d}".format(SUCCEEDED, FAILED)))
