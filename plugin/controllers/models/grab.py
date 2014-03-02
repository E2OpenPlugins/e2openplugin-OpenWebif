# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from enigma import eConsoleAppContainer
from twisted.web import static, resource, http, server
import os

GRAB_PATH = '/usr/bin/grab'

class grabScreenshot(resource.Resource):

	def __init__(self,session, path = ""):
		resource.Resource.__init__(self)
		self.session = session
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.grabFinished)

	def render(self, request):
		self.request = request
		graboptions = ""

		if "format" in request.args.keys():
			self.fileformat = request.args["format"][0]
		else:
			self.fileformat = "jpg"

		if self.fileformat == "jpg":
			graboptions += " -j 95"
		elif self.fileformat == "png":
			graboptions += " -p"
		elif self.fileformat != "bmp":
			self.fileformat = "bmp"

		if "r" in request.args.keys():
			size = request.args["r"][0]
			graboptions += " -r %s" % int(size)

		if "mode" in request.args.keys():
			mode = request.args["mode"][0]
			if mode == "osd":
				graboptions += " -o"
			elif mode == "video":
				graboptions += " -v"

		try:
			ref = self.session.nav.getCurrentlyPlayingServiceReference().toString()
		except:
			ref = None 

		if ref is not None:
			self.sref = '_'.join(ref.split(':', 10)[:10])
		else:
			self.sref = 'screenshot'

		self.filepath = "/tmp/screenshot." + self.fileformat
		grabcommand = GRAB_PATH + graboptions + " " + self.filepath

		os.system(grabcommand)
		self.grabFinished()
		return server.NOT_DONE_YET

	def grabFinished(self, data=""):
		fileformat = self.fileformat
		if fileformat == "jpg":
			fileformat = "jpeg"
		try:
			self.request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (self.sref,self.fileformat))
			self.request.setHeader('Content-Type','image/%s' % fileformat)
			self.request.setHeader('Content-Length', '%i' % os.path.getsize(self.filepath))

			file = open(self.filepath)
			self.request.write(file.read())
			file.close()
			self.request.finish()
		except Exception, error:
			self.request.setResponseCode(http.OK)
			self.request.write("Error creating screenshot:\n %s" % error)
			self.request.finish()

