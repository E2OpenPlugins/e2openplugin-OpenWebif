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
		# self.container.dataAvail.append(self.grabData)

	def render(self, request):
		self.request = request
		graboptions = [GRAB_PATH]

		if "format" in request.args.keys():
			self.fileformat = request.args["format"][0]
		else:
			self.fileformat = "jpg"

		if self.fileformat == "jpg":
			graboptions.append("-j")
			graboptions.append("95")
		elif self.fileformat == "png":
			graboptions.append("-p")
		elif self.fileformat != "bmp":
			self.fileformat = "bmp"

		if "r" in request.args.keys():
			size = request.args["r"][0]
			graboptions.append("-r")
			graboptions.append("%d" % int(size))

		if "mode" in request.args.keys():
			mode = request.args["mode"][0]
			if mode == "osd":
				graboptions.append("-o")
			elif mode == "video":
				graboptions.append("-v")

		try:
			ref = self.session.nav.getCurrentlyPlayingServiceReference().toString()
		except:
			ref = None 

		if ref is not None:
			self.sref = '_'.join(ref.split(':', 10)[:10])
		else:
			self.sref = 'screenshot'

		self.filepath = "/tmp/screenshot." + self.fileformat
		graboptions.append(self.filepath)
		self.container.execute(GRAB_PATH, *graboptions)
		return server.NOT_DONE_YET

	def grabData(self, data):
		print "[W] grab:", data,

	def grabFinished(self, retval = None):
		fileformat = self.fileformat
		if fileformat == "jpg":
			fileformat = "jpeg"
		try:
			fd = open(self.filepath)
			data = fd.read()
			fd.close()
			self.request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (self.sref,self.fileformat))
			self.request.setHeader('Content-Type','image/%s' % fileformat)
			self.request.setHeader('Content-Length', '%i' % len(data))
			self.request.write(data)
		except Exception, error:
			self.request.setResponseCode(http.OK)
			self.request.write("Error creating screenshot:\n %s" % error)
		try:
			os.unlink(self.filepath)
		except:
			print "Failed to remove:", self.filepath
		try:
			self.request.finish()
		except RuntimeError, error:
			print "[OpenWebif] grabFinished error: %s" % error
		del self.request
		del self.filepath
