# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: ATController
##########################################################################
# Copyright (C) 2013 - 2018 jbleyel and E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##########################################################################

from twisted.web import static, resource, http
import os
import json

ATFN = "/tmp/autotimer_backup.tar"  # nosec

class ATUploadFile(resource.Resource):

	def __init__(self, session):
		self.session = session
		resource.Resource.__init__(self)

	def render_POST(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('content-type', 'text/plain')
		request.setHeader('charset', 'UTF-8')
		content = request.args['rfile'][0]
		if not content:
			result = [False, 'Error upload File']
		else:
			fileh = os.open(ATFN, os.O_WRONLY | os.O_CREAT)
			bytes = 0
			if fileh:
				bytes = os.write(fileh, content)
				os.close(fileh)
			if bytes <= 0:
				try:
					os.remove(ATFN)
				except OSError:
					pass
				result = [False, 'Error writing File']
			else:
				result = [True, ATFN]
		return json.dumps({"Result": result})

class AutoTimerDoBackupResource(resource.Resource):
	def render(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		state, statetext = self.backupFiles()
		return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
<e2simplexmlresult>
	<e2state>%s</e2state>
	<e2statetext>%s</e2statetext>
</e2simplexmlresult>""" % ('True' if state else 'False', statetext)

	def backupFiles(self):
		if os.path.exists(ATFN):
			os.remove(ATFN)
		checkfile = '/tmp/.autotimeredit'
		f = os.open(checkfile, os.O_WRONLY | os.O_CREAT)
		if f:
			files = []
			os.write(f, 'created with AutoTimerWebEditor')
			os.close(f)
			files.append(checkfile)
			files.append("/etc/enigma2/autotimer.xml")
			tarFiles = ""
			for arg in files:
				if not os.path.exists(arg):
					return (False, "Error while preparing backup file, %s does not exists." % arg)
				tarFiles += "%s " % arg
			lines = os.popen("tar cvf %s %s" % (ATFN,tarFiles)).readlines()
			os.remove(checkfile)
			return (True, ATFN)
		else:
			return (False, "Error while preparing backup file.")

class AutoTimerDoRestoreResource(resource.Resource):
	def render(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		
		state, statetext = self.restoreFiles()
		
		return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
<e2simplexmlresult>
	<e2state>%s</e2state>
	<e2statetext>%s</e2statetext>
</e2simplexmlresult>""" % ('True' if state else 'False', statetext)

	def restoreFiles(self):
		if os.path.exists(ATFN):
			check_tar = False
			lines = os.popen('tar -tf %s' % ATFN).readlines()
			for line in lines:
				pos = line.find('tmp/.autotimeredit')
				if pos != -1:
					check_tar = True
					break
			if check_tar:
				lines = os.popen('tar xvf %s -C /' % ATFN).readlines()

				from Plugins.Extensions.AutoTimer.plugin import autotimer
				if autotimer is not None:
					try:
						# Force config reload
						autotimer.configMtime = -1
						autotimer.readXml()
					except Exception:
						# TODO: proper error handling
						pass
				
				os.remove(ATFN)
				return (True, "AutoTimer-settings were restored successfully")
			else:
				return (False, "Error, %s was not created with AutoTimerWebEditor..." % ATFN)
		else:
			return (False, "Error, %s does not exists, restore is not possible..." % ATFN)


class ATController(resource.Resource):
	def __init__(self, session):
		resource.Resource.__init__(self)
		self.session = session

		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerDoParseResource, \
				AutoTimerAddOrEditAutoTimerResource, AutoTimerChangeSettingsResource, \
				AutoTimerRemoveAutoTimerResource, AutoTimerSettingsResource, \
				AutoTimerSimulateResource
		except ImportError:
			# print "AT plugin not found"
			return
		self.putChild('parse', AutoTimerDoParseResource())
		self.putChild('remove', AutoTimerRemoveAutoTimerResource())
		self.putChild('edit', AutoTimerAddOrEditAutoTimerResource())
		self.putChild('get', AutoTimerSettingsResource())
		self.putChild('set', AutoTimerChangeSettingsResource())
		self.putChild('simulate', AutoTimerSimulateResource())
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerTestResource
			self.putChild('test', AutoTimerTestResource())
		except ImportError:
			# this is not an error
			pass
		self.putChild('uploadrestore', ATUploadFile(session))
		self.putChild('restore', AutoTimerDoRestoreResource())
		self.putChild('backup', AutoTimerDoBackupResource())
		self.putChild('tmp', static.File('/tmp'))  # nosec

	def render(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			from Plugins.Extensions.AutoTimer.plugin import autotimer
			try:
				if autotimer is not None:
					autotimer.readXml()
					return ''.join(autotimer.getXml())
			except Exception:
				return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>AutoTimer Config not found</e2statetext></e2simplexmlresult>'
		except ImportError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>AutoTimer Plugin not found</e2statetext></e2simplexmlresult>'
