# -*- coding: utf-8 -*-

##############################################################################
#                        2013 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http, server
from enigma import eServiceCenter, eServiceReference, iServiceInformation
from base import BaseController
from Screens.ChannelSelection import service_types_tv
from Components.config import config
from Components.ParentalControl import parentalControl
import os
import json

class BQEWebController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
	
	def returnResult(self, req, result):
		if self.isJson:
			return { "Result": result }
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
			if key in args:
				list[key] = args[key][0]
			else:
				list[key] = None
		return list

	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")

	def P_addbouquet(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_BOUQUET)
			bqe.handleCommand(self.buildCommand('name,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removebouquet(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_movebouquet(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.MOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode,position',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addmarkertobouquet(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_MARKER_TO_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,Name,sRefBefore',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addservicetobouquet(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_SERVICE_TO_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,sRefBefore',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addprovidertobouquetlist(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_PROVIDER_TO_BOUQUETLIST)
			bqe.handleCommand(self.buildCommand('sProviderRef,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addservicetoalternative(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_SERVICE_TO_ALTERNATIVE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sCurrentRef,sRef,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_moveservice(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.MOVE_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,mode,position',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removeservice(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_renameservice(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.RENAME_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,sRefBefore,newName,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_Removealternativeservices(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_ALTERNATIVE_SERVICES)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_togglelock(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.TOGGLE_LOCK)
			bqe.handleCommand(self.buildCommand('sRef,password',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_backup(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.BACKUP)
			bqe.handleCommand(request.args['Filename'][0])
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_restore(self, request):
		self.withMainTemplate = False
		try:
			from BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.RESTORE)
			bqe.handleCommand(request.args['Filename'][0])
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_getservices(self, request):
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]
		else:
			sRef = ""
		services = []

		if sRef == "":
			sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)

		serviceHandler = eServiceCenter.getInstance()
		serviceslist = serviceHandler.list(eServiceReference(sRef))
		fulllist = serviceslist and serviceslist.getContent("RN", True)

		for item in fulllist:
			sref = item[0].toString()
			if not int(sref.split(":")[1]) & 512:	# 512 is hidden service on sifteam image. Doesn't affect other images
				service = {}
				service['servicereference'] = sref
				service['servicename'] = item[1]
				service['isgroup'] = '0'
				if item[0].flags & eServiceReference.isGroup:
					service['isgroup'] = '1'
				service['ismarker'] = '0'
				if item[0].flags & eServiceReference.isMarker:
					service['ismarker'] = '1'
				service['isprotected'] = '0'
				if config.ParentalControl.configured.value and config.ParentalControl.servicepinactive.value:
					sref = item[0].toCompareString()
					protection = parentalControl.getProtectionLevel(sref)
					if protection != -1:
						if config.ParentalControl.type.value == "blacklist":
							if parentalControl.blacklist.has_key(sref):
								if "SERVICE" in parentalControl.blacklist[sref]:
									service['isprotected'] = '1'
								elif "BOUQUET" in parentalControl.blacklist[sref]:
									service['isprotected'] = '2'
								else:
									service['isprotected'] = '3'
						elif config.ParentalControl.type.value == "whitelist":
							if not parentalControl.whitelist.has_key(sref):
								if item[0].flags & eServiceReference.isGroup:
									service['isprotected'] = '5'
								else:
									service['isprotected'] = '4'
				services.append(service)
		return { "services": services }

	def P_getprotectionsettings(self, request):
		configured = config.ParentalControl.configured.value
		if configured:
			if config.ParentalControl.type.value == "blacklist":
				type = "0"
			else:
				type = "1"
			setuppin = "setuppin" in config.ParentalControl.dict().keys() and config.ParentalControl.setuppin.value or -1
			setuppinactive = "setuppin" in config.ParentalControl.dict().keys() and config.ParentalControl.setuppinactive.value
		else:
			type = ""
			setuppin = ""
			setuppinactive = ""

		ps = {}
		ps['Configured'] = configured
		ps['Type'] = type
		ps['SetupPinActive'] = setuppinactive
		ps['SetupPin'] = setuppin
		return { "ps": ps }

class BQEUploadFile(resource.Resource):
	FN = "/tmp/bouquets_backup.tar"
	def __init__(self, session):
		self.session = session
		resource.Resource.__init__(self)

	def render_POST(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('content-type', 'text/plain')
		request.setHeader('charset', 'UTF-8')
		content = request.args['rfile'][0]
		if not content:
			result = [False,'Error upload File']
		else:
			fileh = os.open( self.FN, os.O_WRONLY|os.O_CREAT )
			bytes = 0
			if fileh:
				bytes = os.write(fileh, content)
				os.close(fileh)
			if bytes <= 0:
				try:
					os.remove(FN)
				except OSError, oe:
					pass
				result = [False,'Error writing File']
			else:
				result = [True,self.FN]
		return json.dumps({"Result": result })

class BQEApiController(BQEWebController):
	def __init__(self, session, path = ""):
		BQEWebController.__init__(self, session, path)

	def prePageLoad(self, request):
		self.isJson = True

class BQEController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		self.putChild("web", BQEWebController(session))
		self.putChild("api", BQEApiController(session))
		self.putChild('tmp', static.File('/tmp'))
		self.putChild('uploadrestore', BQEUploadFile(session))

