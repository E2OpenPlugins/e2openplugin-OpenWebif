#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESTful API for configuration data
----------------------------------

TODO:

	* implementation of GET/POST/.... request handling
	* extend OpenAPI specification in swagger.json
	* add documentation about the purpose of this module et al.

"""

from rest import json_response
from rest import CORS_DEFAULT_ALLOW_ORIGIN, RESTControllerSkeleton


class ConfigurationApiController(RESTControllerSkeleton):
	def __init__(self, *args, **kwargs):
		RESTControllerSkeleton.__init__(self, *args, **kwargs)

	def render_GET(self, request):
		"""
		HTTP GET implementation.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

		# TODO: retrieve configuration data implementation

		data = {
			"_controller": self.__class__.__name__,
			"request_postpath": request.postpath,
			"method": request.method,
			"request_path": request.path,
		}

		return json_response(request, data)

	def render_POST(self, request):
		"""
		HTTP POST implementation.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader(
			'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

		# TODO: alter configuration data implementation

		data = {
			"_controller": self.__class__.__name__,
			"request_postpath": request.postpath,
			"method": request.method,
			"request_path": request.path,
		}

		return json_response(request, data)
