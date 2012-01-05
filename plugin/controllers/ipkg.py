##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http

class IpkgController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def render(self, request):
		action =''
		package = ''

		if "command" in request.args:
			action = request.args["command"][0]

		if "package" in request.args:
			package = request.args["package"][0]

		if action == "info" and package == "enigma2-plugin-extensions-webinterface":
			response = "Package: enigma2-plugin-extensions-webinterface\nVersion: experimental-git3735+5cdadeb-r6\n" 
			return response

		return "not implemented"
