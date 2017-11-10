#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESTful Controller for /api/saveconfig endpoints.
POST requests are proxied through `controllers.web.WebController`.

TODO:

	* sane implementation of POST request handling
	* extend OpenAPI specification in swagger.json
	* add documentation
"""
from web import WebController
from rest import json_response
from rest import CORS_DEFAULT_ALLOW_ORIGIN, RESTControllerSkeleton


class SaveConfigApiController(RESTControllerSkeleton):
	def __init__(self, *args, **kwargs):
		RESTControllerSkeleton.__init__(self, *args, **kwargs)
		session = kwargs.get("session")
		path = kwargs.get("path", "")
		#: web controller instance
		self.web_instance = WebController(session, path)

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

		return json_response(request, {"result": False})

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

		return json_response(request, self.web_instance.P_saveconfig(request))
