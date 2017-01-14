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
from twisted.web import resource, server

GRAB_PATH = '/usr/bin/grab'

class grabScreenshot(resource.Resource):
	def __init__(self, session, path = None):
		resource.Resource.__init__(self)
		self.session = session
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.grabFinished)
		self.container.stdoutAvail.append(self.grabData)
		self.container.setBufferSize(32768)

	def render(self, request):
		self.request = request
		graboptions = [GRAB_PATH, '-q', '-s']

		if "format" in request.args:
			fileformat = request.args["format"][0]
		else:
			fileformat = "jpg"

		if fileformat == "jpg":
			graboptions.append("-j")
			graboptions.append("95")
		elif fileformat == "png":
			graboptions.append("-p")
		elif fileformat != "bmp":
			fileformat = "bmp"

		if "r" in request.args:
			size = request.args["r"][0]
			graboptions.append("-r")
			graboptions.append("%d" % int(size))

		if "mode" in request.args:
			mode = request.args["mode"][0]
			if mode == "osd":
				graboptions.append("-o")
			elif mode == "video":
				graboptions.append("-v")

		self.container.execute(GRAB_PATH, *graboptions)

		try:
			ref = self.session.nav.getCurrentlyPlayingServiceReference().toString()
			sref = '_'.join(ref.split(':', 10)[:10])
		except:
			sref = 'screenshot'

		self.request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (sref, fileformat))
		self.request.setHeader('Content-Type','image/%s' % fileformat)
		return server.NOT_DONE_YET

	def grabData(self, data):
		self.request.write(data)

	def grabFinished(self, retval = None):
		try:
			self.request.finish()
		except RuntimeError, error:
			print "[OpenWebif] grabFinished error: %s" % error
		del self.request
