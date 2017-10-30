#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

#: CORS - HTTP headers the client may use
CORS_ALLOWED_CLIENT_HEADERS = [
	'Content-Type',
]

#: CORS - HTTP methods the client may use
CORS_ALLOWED_METHODS_DEFAULT = ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS']

#: CORS - default origin header value
CORS_DEFAULT_ALLOW_ORIGIN = '*'

#: CORS - HTTP headers the server will send as part of OPTIONS response
CORS_DEFAULT = {
	'Access-Control-Allow-Origin': CORS_DEFAULT_ALLOW_ORIGIN,
	'Access-Control-Allow-Credentials': 'true',
	'Access-Control-Max-Age': '86400',
	'Access-Control-Allow-Methods': ','.join(CORS_ALLOWED_METHODS_DEFAULT),
	'Access-Control-Allow-Headers': ', '.join(CORS_ALLOWED_CLIENT_HEADERS)
}


def json_response(request, data, indent=1):
	"""
	Create a JSON representation for *data* and set HTTP headers indicating
	that JSON encoded data is returned.

	Args:
		request (twisted.web.server.Request): HTTP request object
		data: response content
		indent: indentation level or None
	Returns:
		JSON representation of *data* with appropriate HTTP headers
	"""
	request.setHeader("content-type", "application/json; charset=utf-8")
	return json.dumps(data, indent=indent)
