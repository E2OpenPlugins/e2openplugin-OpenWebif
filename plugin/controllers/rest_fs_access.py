#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESTful Filesystem access using HTTP
------------------------------------

This controller exposes parts or all of the server's filesystem.
Means to retrieve and delete files are provided as well as the
ability to list folder contents.

The generated responses are returned as JSON data with appropriate HTTP headers.
Output will be compressed using gzip for some files if using wrapper
and requested by client.

Example calls using curl
++++++++++++++++++++++++

The following examples assume that the FileController instance is accessible
as '/file' on 'localhost', port 18888 (http://localhost:18888/file).

Fetch list of files and folders in root folder:

    curl --noproxy localhost -iv http://localhost:18888/file

Fetch example file 'example.txt'

    curl --noproxy localhost -iv http://localhost:18888/file/example.txt

Fetch gzipped example file 'example.txt'

    curl --compressed -H "Accept-Encoding: gzip" --noproxy localhost -iv http://localhost:18888/file/example.txt

Delete example file 'example.txt'

    curl --noproxy localhost -iv -X DELETE http://localhost:18888/file/example.txt

Create example file 'test.dat' using HTTP POST request on /file

    curl --noproxy localhost -iv -X POST http://localhost:18888/file?filename=test.dat -F "data=blabla"

"""
import os
import json
import glob
import re
import urlparse
import datetime
import time
from wsgiref.handlers import format_date_time

import twisted.web.static
from twisted.web import http
from twisted.web.server import GzipEncoderFactory

from utilities import MANY_SLASHES_REGEX, lenient_force_utf_8

try:
	import file

	HAVE_LEGACY_FILE = True
except ImportError:
	HAVE_LEGACY_FILE = False

#: default path from which files will be served
DEFAULT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

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

#: paths where file delete operations shall be allowed
DELETE_WHITELIST = [
	'/media',
]


def dump_upload(request, target_filename):
	with open(target_filename, "wb") as handle:
		handle.write(request.args['data'][0])


class GzipEncodeByFileExtensionFactory(GzipEncoderFactory):
	"""
	A gzip content encoding factory. Compression is enabled for paths having
	an extension contained in *self.gzip_allowed*.

	Args:
		extensions: Extensions for which compression will be enabled.
			Default is [] -- no compression at all
		compressLevel: Gzip compression level
			Default is 6
	"""

	def __init__(self, *args, **kwargs):
		self.gzip_allowed = kwargs.get("extensions", [])
		self.compressLevel = kwargs.get("compressLevel", 6)

	def encoderForRequest(self, request):
		"""
		Check the request path if the extension allows the file to be
		send compressed. If so use GzipEncoderFactory which may compress
		the file contents if the client supports it.
		"""
		try:
			(trunk, ext) = os.path.splitext(request.path)
			ext_normalised = ext.lower()[1:]

			if ext_normalised in self.gzip_allowed:
				# print("{!r}: we want GZIP!".format(ext_normalised))
				return GzipEncoderFactory.encoderForRequest(self, request)
			# else:
			# 	print("{!r}: we do not want GZIP!".format(ext_normalised))
		except Exception as exc:
			print exc


class FileController(twisted.web.resource.Resource):
	isLeaf = True
	_override_args = (
		'resource_prefix', 'root', 'do_delete', 'delete_whitelist')
	_resource_prefix = '/file'
	_root = os.path.abspath(os.path.dirname(__file__))
	_do_delete = False
	_delete_whitelist = DELETE_WHITELIST

	def __init__(self, *args, **kwargs):
		"""
		Default Constructor.

		Args:
			resource_prefix: Prefix value for this controller instance.
				Default is :py:data:`FileController._resource_prefix`
			root: Root path of files to be served.
				Default is the path where the current file is located
			do_delete: Try to actually delete files?
				Default is False.
			delete_whitelist: Folder prefixes where delete operations are
				allowed _at all_. Default is :py:data:`DELETE_WHITELIST`
		"""
		if args:
			for key, value in zip(self._override_args, args):
				kwargs[key] = value

		for arg_name in self._override_args:
			if kwargs.get(arg_name) is not None:
				attr_name = '_{:s}'.format(arg_name)
				setattr(self, attr_name, kwargs.get(arg_name))
		self.session = kwargs.get("session")

	def _cache(self, request, expires=False):
		if expires is False:
			request.setHeader('Cache-Control',
							  'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0')
			request.setHeader('Expires', '-1')
		else:
			now = datetime.datetime.now()
			expires_time = now + datetime.timedelta(seconds=expires)
			request.setHeader('Cache-Control', 'public')
			request.setHeader('Expires', format_date_time(
				time.mktime(expires_time.timetuple())))

	def _json_response(self, request, data):
		"""
		Create a JSON representation for *data* and set HTTP headers indicating
		that JSON encoded data is returned.

		Args:
			request (twisted.web.server.Request): HTTP request object
			data: response content
		Returns:
			JSON representation of *data* with appropriate HTTP headers
		"""
		request.setHeader("content-type", "application/json; charset=utf-8")
		return json.dumps(data, indent=2)

	def get_response_data_template(self, request):
		"""
		Generate a response data :class:`dict` containing default values and
		some request attribute values for debugging purposes.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			(dict) response template data
		"""
		file_path = None
		if request.path.startswith(self._resource_prefix):
			file_path = request.path[len(self._resource_prefix):]

		response_data = {
			"_request": {
				"path": request.path,
				"uri": request.uri,
				"method": request.method,
				"file_path": file_path,
			},
			"result": False,
		}

		return response_data

	def error_response(self, request, response_code=None, **kwargs):
		"""
		Create and return an HTTP error response with data as JSON.

		Args:
			request (twisted.web.server.Request): HTTP request object
			response_code: HTTP Status Code (default is 500)
			**kwargs: additional key/value pairs
		Returns:
			JSON encoded data with appropriate HTTP headers
		"""
		if response_code is None:
			response_code = http.INTERNAL_SERVER_ERROR

		response_data = self.get_response_data_template(request)
		response_data.update(**kwargs)

		response_data['me'] = dict()
		for arg_name in self._override_args:
			attr_name = '_{:s}'.format(arg_name)
			response_data['me'][attr_name] = getattr(self, attr_name)

		request.setResponseCode(response_code)
		return self._json_response(request, response_data)

	def _existing_path_or_bust(self, request):
		"""
		Verify that a filesystem location which is contained in *request.path*
		is valid and an existing path.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			path
		Raises:
			ValueError: If contained path value is invalid.
			IOError: If contained path value is not existing.
		"""
		rq_path = urlparse.unquote(request.path)
		if not rq_path.startswith(self._resource_prefix):
			raise ValueError("Invalid Request Path {!r}".format(request.path))

		file_path = os.path.join(
			self._root, rq_path[len(self._resource_prefix) + 1:])
		file_path = re.sub(MANY_SLASHES_REGEX, '/', file_path)

		if not os.path.exists(file_path):
			raise IOError("Not Found {!r}".format(file_path))

		return file_path

	def render_OPTIONS(self, request):
		"""
		Render response for an HTTP OPTIONS request.

		Example request

			curl -iv --noproxy localhost http://localhost:18888/file

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		for key in CORS_DEFAULT:
			request.setHeader(key, CORS_DEFAULT[key])

		return ''

	def render_legacy(self, request):
		"""
		Render response for an HTTP GET request. In order to maintain
		backward compatibility this method emulates the behaviour of the
		legacy method implementation.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return file.FileController().render(request)

	def _glob(self, path, pattern='*'):
		if path == '/':
			glob_me = '/' + pattern
		else:
			glob_me = '/'.join((path, pattern))
		return glob.iglob(glob_me)

	def render_path_listing(self, request, path):
		"""
		Generate a file/folder listing of *path*'s contents.

		Args:
			request (twisted.web.server.Request): HTTP request object
			path: folder location
		Returns:
			HTTP response with headers
		"""
		response_data = {
			'result': True,
			'dirs': [],
			'files': [],
		}

		generator = None
		if "pattern" in request.args:
			generator = self._glob(path, request.args["pattern"][0])

		if generator is None:
			generator = self._glob(path)

		for item in generator:
			if os.path.isdir(item):
				response_data['dirs'].append(item)
			else:
				response_data['files'].append(item)

		return self._json_response(request, response_data)

	def render_file(self, request, path):
		"""
		Return the contents of file *path*.

		Args:
			request (twisted.web.server.Request): HTTP request object
			path: file path
		Returns:
			HTTP response with headers
		"""
		result = twisted.web.static.File(
			path, defaultType="application/octet-stream")
		expires = 3600 * 24 * 30
		if path.lower().endswith('.ts'):
			expires = False
		self._cache(request, expires=expires)
		return result.render(request)

	def render_GET(self, request):
		"""
		HTTP GET request handler returning

			* legacy response if the query *file* or *dir* parameter is set
			* file contents if *request.path* contains a file path
			* directory listing if *request.path* contains a folder path

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		attic_args = {'file', 'dir'}

		if len(attic_args & set(request.args.keys())) >= 1:
			if HAVE_LEGACY_FILE:
				return self.render_legacy(request)
			else:
				return self.error_response(
					request, response_code=http.NOT_IMPLEMENTED)

		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

		try:
			target_path = self._existing_path_or_bust(request)
		except ValueError as vexc:
			return self.error_response(
				request, response_code=http.BAD_REQUEST, message=vexc.message)
		except IOError as iexc:
			return self.error_response(
				request, response_code=http.NOT_FOUND, message=iexc.message)

		if os.path.isdir(target_path):
			return self.render_path_listing(request, target_path)
		else:
			return self.render_file(request, target_path)

	def render_POST(self, request):
		"""
		HTTP POST request handler (currently NOT implemented).

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

		try:
			target_path = self._existing_path_or_bust(request)
		except ValueError as vexc:
			return self.error_response(
				request, response_code=http.BAD_REQUEST, message=vexc.message)
		except IOError as iexc:
			return self.error_response(
				request, response_code=http.NOT_FOUND, message=iexc.message)

		if not os.path.isdir(target_path):
			return self.error_response(
				request, response_code=http.NOT_IMPLEMENTED,
				message="Needs to be an existing path")

		fn_arg = request.args.get("filename", [None])
		filename_raw = fn_arg[0]
		if filename_raw:
			filename = lenient_force_utf_8(filename_raw).split('/')[-1]
		else:
			return self.error_response(
				request, response_code=http.NOT_IMPLEMENTED,
				message="I really need a filename.")

		if not request.args.get('data'):
			return self.error_response(
				request, response_code=http.NOT_IMPLEMENTED,
				message="I really need data to write.")

		target_filename = '/'.join((target_path, filename))

		if os.path.exists(target_filename):
			return self.error_response(
				request, response_code=http.NOT_IMPLEMENTED,
				message="Existing target {!r}".format(target_filename))

		try:
			dump_upload(request, target_filename)
		except Exception as exc:
			return self.error_response(
				request, response_code=http.INTERNAL_SERVER_ERROR,
				message=exc.message)

		response_data = {
			'result': True,
			'filename': target_filename,
		}

		return self._json_response(request, response_data)

	def render_PUT(self, request):
		"""
		HTTP PUT request handler (currently NOT implemented).

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)
		return self.error_response(request, response_code=http.NOT_IMPLEMENTED)

	def render_DELETE(self, request):
		"""
		HTTP DELETE request handler which may try to delete a file if its
		path's prefix is in :py:data:`FileController._delete_whitelist` and
		:py:data:`FileController._do_delete` is True.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

		try:
			target_path = self._existing_path_or_bust(request)
		except ValueError as vexc:
			return self.error_response(
				request, response_code=http.BAD_REQUEST, message=vexc.message)
		except IOError as iexc:
			return self.error_response(
				request, response_code=http.NOT_FOUND, message=iexc.message)

		if os.path.isdir(target_path):
			return self.error_response(
				request, response_code=http.NOT_IMPLEMENTED,
				message='Will not remove folder {!r}'.format(target_path))

		for prefix in self._delete_whitelist:
			if not target_path.startswith(os.path.abspath(prefix)):
				return self.error_response(request,
										   response_code=http.FORBIDDEN)

		response_data = {'result': False}
		try:
			response_data['result'] = True
			if self._do_delete:
				os.unlink(target_path)
				message = 'Removed {!r}'.format(target_path)
			else:
				message = 'WOULD remove {!r}'.format(target_path)
			response_data['message'] = message
		except Exception as eexc:
			response_data['message'] = 'Cannot remove {!r}: {!s}'.format(
				target_path, eexc.message)
			request.setResponseCode(http.INTERNAL_SERVER_ERROR)

		return self._json_response(request, response_data)


if __name__ == '__main__':
	from twisted.web.resource import Resource, EncodingResourceWrapper
	from twisted.web.server import Site, GzipEncoderFactory
	from twisted.internet import reactor

	# standard factory example
	factory_s = Site(FileController(DEFAULT_ROOT_PATH))

	# experimental factory
	root = Resource()
	root.putChild("/", FileController)
	root.putChild("/file", FileController)
	factory_r = Site(root)

	#  experimental factory: enable gzip compression
	wrapped = EncodingResourceWrapper(
		FileController(
			root=DEFAULT_ROOT_PATH,
			# DANGER, WILL ROBINSON! These values allow deletion of ALL files!
			do_delete=True, delete_whitelist=[]
		),
		[GzipEncoderFactory()])
	factory_s_gz = Site(wrapped)

	reactor.listenTCP(18888, factory_s_gz)
	reactor.run()
