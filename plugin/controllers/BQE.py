# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: BQEController
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
from enigma import eServiceCenter, eServiceReference
from Plugins.Extensions.OpenWebif.controllers.base import BaseController
from Components.config import config
from Components.ParentalControl import parentalControl
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg
from Plugins.Extensions.OpenWebif.controllers.models.services import getPicon
import os
import json
import six

# FIXME:
# remove #from Screens.ChannelSelection import service_types_tv
# because of missing 211

service_types_tv = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 31) || (type == 134) || (type == 195) || (type == 211)'
service_types_radio = '1:7:2:0:0:0:0:0:0:0:(type == 2) || (type == 10)'


class BQEWebController(BaseController):
	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session)

	def returnResult(self, req, result):
		if self.isJson:
			return {"Result": result}
		else:
			state = result[0]
			statetext = result[1]
			req.setResponseCode(http.OK)
			req.setHeader('Content-type', 'application/xhtml+xml')
			req.setHeader('charset', 'UTF-8')

			return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
<e2simplexmlresult>
	<e2state>%s</e2state>
	<e2statetext>%s</e2statetext>
</e2simplexmlresult>""" % ('True' if state else 'False', statetext)

	def buildCommand(self, ids, args):
		paramlist = ids.split(",")
		list = {}
		for key in paramlist:
			k = six.ensure_binary(key)
			if k in args:
				list[key] = six.ensure_str(args[k][0])
			else:
				list[key] = None
		return list

	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")

	def P_addbouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_BOUQUET)
			bqe.handleCommand(self.buildCommand('name,mode', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removebouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_movebouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.MOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode,position', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addmarkertobouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_MARKER_TO_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,Name,sRefBefore,SP', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addservicetobouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_SERVICE_TO_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,sRefBefore,sRefUrl,Name', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addprovidertobouquetlist(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_PROVIDER_TO_BOUQUETLIST)
			bqe.handleCommand(self.buildCommand('sProviderRef,mode', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addservicetoalternative(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_SERVICE_TO_ALTERNATIVE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sCurrentRef,sRef,mode', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_moveservice(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.MOVE_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,mode,position', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removeservice(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_renameservice(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.RENAME_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,sRefBefore,newName,mode', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removealternativeservices(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_ALTERNATIVE_SERVICES)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_togglelock(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.TOGGLE_LOCK)
			bqe.handleCommand(self.buildCommand('sRef,password', request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_backup(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.BACKUP)
			bqe.handleCommand(six.ensure_str(request.args[b'Filename'][0]))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_restore(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.RESTORE)
			bqe.handleCommand(six.ensure_str(request.args[b'Filename'][0]))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

#	def P_calcpos(self, request):
#		type = 0
#		if "type" in request.args.keys():
#			type = request.args["type"][0]
#		bRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)
#		if type == 1:
#			bRef = '%s FROM BOUQUET "bouquets.radio" ORDER BY bouquet' % (service_types_radio)
#
#		serviceHandler = eServiceCenter.getInstance()
#		serviceslist = serviceHandler.list(eServiceReference(bRef))
#		bqlist = serviceslist and serviceslist.getContent("RN", True)
#		pos = 0
#		services = []
#		for bq in bqlist:
#			bqref = bq[0].toString()
#			service = {}
#			service['servicereference'] = bqref
#			service['startpos'] = pos
#			serviceslist = serviceHandler.list(eServiceReference(bqref))
#			fulllist = serviceslist and serviceslist.getContent("RN", True)
#			for item in fulllist:
#				sref = item[0].toString()
#				hs = (int(sref.split(":")[1]) & 512)
#				sp = (sref[:7] == '1:832:D')
#				if not hs or sp:  # 512 is hidden service on sifteam image. Doesn't affect other images
#					pos = pos + 1
#					if not sp and item[0].flags & eServiceReference.isMarker:
#						pos = pos - 1
#			services.append(service)
#		return {"services": services}

	def P_getservices(self, request):
		sRef = getUrlArg(request, "sRef", "")
		includePicon = (getUrlArg(request, "picon", "") == '1')
		services = []

		CalcPos = False

		if sRef == "":
			sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)
			CalcPos = True
		elif ' "bouquets.radio" ' in sRef:
			CalcPos = True
		elif ' "bouquets.tv" ' in sRef:
			CalcPos = True

		serviceHandler = eServiceCenter.getInstance()
		serviceslist = serviceHandler.list(eServiceReference(sRef))
		fulllist = serviceslist and serviceslist.getContent("RN", True)

		pos = 0
		oPos = 0
		for item in fulllist:
			oldoPos = oPos
			if CalcPos:
				sref = item[0].toString()
				serviceslist = serviceHandler.list(eServiceReference(sref))
				sfulllist = serviceslist and serviceslist.getContent("RN", True)
				for sitem in sfulllist:
					sref = sitem[0].toString()
					hs = (int(sref.split(":")[1]) & 512)
					sp = (sref[:7] == '1:832:D')
					if not hs or sp:  # 512 is hidden service on sifteam image. Doesn't affect other images
						oPos = oPos + 1
						if not sp and sitem[0].flags & eServiceReference.isMarker:
							oPos = oPos - 1
			sref = item[0].toString()
			hs = (int(sref.split(":")[1]) & 512)
			sp = (sref[:7] == '1:832:D')
			if not hs or sp:  # 512 is hidden service on sifteam image. Doesn't affect other images
				pos = pos + 1
				service = {}
				if CalcPos:
					service['startpos'] = oldoPos
				service['pos'] = pos
				service['servicereference'] = sref
				service['isgroup'] = '0'
				service['ismarker'] = '0'
				service['isprotected'] = '0'
				if includePicon:
					try:
						service['picon'] = getPicon(sref)
					except:
						service['picon'] = ''
				if sp:
					service['ismarker'] = '2'
					service['servicename'] = ''
				else:
					service['servicename'] = item[1].replace('<', '&lt;').replace('>', '&gt;')
					if item[0].flags & eServiceReference.isGroup:
						gservices = []
						service['isgroup'] = '1'
						# get members of group
						gserviceslist = serviceHandler.list(eServiceReference(sref))
						gfulllist = gserviceslist and gserviceslist.getContent("RN", True)
						for gitem in gfulllist:
							gservice = {}
							gservice['servicereference'] = gitem[0].toString()
							gservice['servicename'] = gitem[1].replace('<', '&lt;').replace('>', '&gt;')
							gservices.append(gservice)
						service['members'] = gservices

					if item[0].flags & eServiceReference.isMarker:
						service['ismarker'] = '1'
						# dont inc the pos for markers
						pos = pos - 1
						service['pos'] = 0
				if not sp and config.ParentalControl.configured.value and config.ParentalControl.servicepinactive.value:
					sref = item[0].toCompareString()
					protection = parentalControl.getProtectionLevel(sref)
					if protection != -1:
						if config.ParentalControl.type.value == "blacklist":
							if sref in parentalControl.blacklist:
								if "SERVICE" in parentalControl.blacklist[sref]:
									service['isprotected'] = '1'
								elif "BOUQUET" in parentalControl.blacklist[sref]:
									service['isprotected'] = '2'
								else:
									service['isprotected'] = '3'
						elif config.ParentalControl.type.value == "whitelist":
							if sref not in parentalControl.whitelist:
								if item[0].flags & eServiceReference.isGroup:
									service['isprotected'] = '5'
								else:
									service['isprotected'] = '4'
				services.append(service)
		return {"services": services}

	def P_getprotectionsettings(self, request):
		configured = config.ParentalControl.configured.value
		if configured:
			if config.ParentalControl.type.value == "blacklist":
				type = "0"
			else:
				type = "1"
			setuppin = "setuppin" in list(config.ParentalControl.dict().keys()) and config.ParentalControl.setuppin.value or -1
			setuppinactive = "setuppin" in list(config.ParentalControl.dict().keys()) and config.ParentalControl.setuppinactive.value
		else:
			type = ""
			setuppin = ""
			setuppinactive = ""

		ps = {}
		ps['Configured'] = configured
		ps['Type'] = type
		ps['SetupPinActive'] = setuppinactive
		ps['SetupPin'] = setuppin
		return {"ps": ps}


class BQEUploadFile(resource.Resource):
	FN = "/tmp/bouquets_backup.tar"  # nosec

	def __init__(self, session):
		self.session = session
		resource.Resource.__init__(self)

	def render_POST(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('content-type', 'text/plain')
		request.setHeader('charset', 'UTF-8')
		content = request.args[b'rfile'][0]
		if not content:
			result = [False, 'Error upload File']
		else:
			fileh = os.open(self.FN, os.O_WRONLY | os.O_CREAT)
			bytes = 0
			if fileh:
				bytes = os.write(fileh, content)
				os.close(fileh)
			if bytes <= 0:
				try:
					os.remove(self.FN)
				except OSError:
					pass
				result = [False, 'Error writing File']
			else:
				result = [True, self.FN]
		return six.ensure_binary(json.dumps({"Result": result}))


class BQEImport(resource.Resource):
	def __init__(self, session):
		self.session = session
		resource.Resource.__init__(self)

	def render_POST(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('content-type', 'text/plain')
		request.setHeader('charset', 'UTF-8')
		result = [False, 'Error upload File']
		if getUrlArg(request, "json") != None:
			try:
				from Plugins.Extensions.OpenWebif.controllers.BouquetEditor import BouquetEditor
				bqe = BouquetEditor(self.session, func=BouquetEditor.IMPORT_BOUQUET)
				bqe.handleCommand(request.args)
				result = bqe.result
			except ImportError:
				result = [False, 'BouquetEditor plugin not found']

		return six.ensure_binary(json.dumps({"Result": result}))


class BQEApiController(BQEWebController):
	def __init__(self, session, path=""):
		BQEWebController.__init__(self, session, path)

	def prePageLoad(self, request):
		self.isJson = True


class BQEController(BaseController):
	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session)
		self.putChild(b"web", BQEWebController(session))
		self.putChild(b"api", BQEApiController(session))
		self.putChild(b"tmp", static.File(b"/tmp"))  # nosec
		self.putChild(b"uploadrestore", BQEUploadFile(session))
		self.putChild(b"import", BQEImport(session))
