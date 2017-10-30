#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESTful API access using HTTP
-----------------------------

This controller exposes the application programming interface (API) as
implemented by the ``web`` and ``ajax`` controller.

The generated responses are returned as JSON data with appropriate HTTP headers.
Output will be compressed using gzip if requested by client.

A swagger v2 (https://swagger.io/) compatible API specification will be
returned when accessing the /api/ endpoint. The API specification is consumable
e.g. by a Swagger UI (https://swagger.io/swagger-ui/) instance.
"""
import urlparse
import copy
import os
import json

from twisted.web import http, resource

from web import WebController
from ajax import AjaxController
from rest import json_response, CORS_ALLOWED_METHODS_DEFAULT, CORS_DEFAULT
from rest import CORS_DEFAULT_ALLOW_ORIGIN

SWAGGER_TEMPLATE = os.path.join(
	os.path.dirname(__file__), 'swagger.json')

OWIF_PREFIX = 'P_'


class ApiController(resource.Resource):
	isLeaf = True

	def __init__(self, session, path="", *args, **kwargs):
		#: web controller instance
		self.web_instance = WebController(session, path)
		#: ajax controller instance
		self.ajax_instance = AjaxController(session, path)
		self._resource_prefix = kwargs.get("resource_prefix", '/api')
		self._cors_header = copy.copy(CORS_DEFAULT)
		http_verbs = []

		for verb in CORS_ALLOWED_METHODS_DEFAULT:
			method_name = 'render_{:s}'.format(verb)
			if hasattr(self, method_name):
				http_verbs.append(verb)
		self._cors_header['Access-Control-Allow-Methods'] = ','.join(http_verbs)

	def render_OPTIONS(self, request):
		"""
		Render response for an HTTP OPTIONS request.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		for key in self._cors_header:
			request.setHeader(key, self._cors_header[key])

		return ''

	def _index(self, request):
		"""
		Return a swagger/JSON based description of the implemented interface.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		with open(SWAGGER_TEMPLATE, "rb") as src:
			data = json.load(src)

		return json_response(request, data)

	def render_GET(self, request):
		"""
		HTTP GET implementation.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		# as implemented in BaseController --v
		request.path = request.path.replace('signal', 'tunersignal')
		rq_path = urlparse.unquote(request.path)

		if not rq_path.startswith(self._resource_prefix):
			raise ValueError("Invalid Request Path {!r}".format(request.path))

		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

		# as implemented in BaseController -----------------v
		func_path = rq_path[len(self._resource_prefix) + 1:].replace(".", "")

		if func_path in ("", "index"):
			return self._index(request)

		#: name of OpenWebif method to be called
		owif_func = "{:s}{:s}".format(OWIF_PREFIX, func_path)

		#: callable methods
		funcs = [
			# TODO: add method of *self*
			('web', getattr(self.web_instance, owif_func, None)),
			('ajax', getattr(self.ajax_instance, owif_func, None)),
		]

		#: method to be called
		func = None
		#: nickname for controller instance
		source_controller = None

		# query controller instances for given method - first match wins
		for candidate_controller, candidate in funcs:
			if callable(candidate):
				func = candidate
				source_controller = candidate_controller
				break

		if func is None:
			request.setResponseCode(http.NOT_FOUND)
			data = {
				"method": repr(func_path),
				"result": False
			}
			return json_response(request, data)

		try:
			request.setResponseCode(http.OK)
			data = func(request)
			data['_controller'] = source_controller
			try:
				if "result" not in data:
					data["result"] = True
			except Exception:
				# ignoring exceptions is bad.
				pass

			return json_response(data=data, request=request)
		except Exception as exc:
			request.setResponseCode(http.INTERNAL_SERVER_ERROR)
			data = {
				"exception": repr(exc),
				"result": False
			}

			return json_response(request, data)
