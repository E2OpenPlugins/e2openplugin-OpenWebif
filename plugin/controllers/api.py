# -*- coding: utf-8 -*-

from web import WebController

class ApiController(WebController):
	def __init__(self, session, path = ""):
		WebController.__init__(self, session, path)

	def prePageLoad(self, request):
		self.isJson = True
