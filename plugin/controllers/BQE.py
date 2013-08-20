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
from Components.ParentalControl import LIST_BLACKLIST

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
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_BOUQUET)
			bqe.handleCommand(self.buildCommand('name,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removebouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_movebouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.MOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode,position',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addmarkertobouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_MARKER_TO_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,Name,sRefBefore',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addservicetobouquet(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_SERVICE_TO_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,sRefBefore',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addprovidertobouquetlist(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_PROVIDER_TO_BOUQUETLIST)
			bqe.handleCommand(self.buildCommand('sProviderRef,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_addservicetoalternative(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_SERVICE_TO_ALTERNATIVE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sCurrentRef,sRef,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_moveservice(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.MOVE_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,mode,position',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removeservice(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_renameservice(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.RENAME_SERVICE)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef,sRefBefore,newName,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_Removealternativeservices(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_ALTERNATIVE_SERVICES)
			bqe.handleCommand(self.buildCommand('sBouquetRef,sRef',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_togglelock(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.TOGGLE_LOCK)
			bqe.handleCommand(self.buildCommand('sRef,password',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_backup(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.BACKUP)
			bqe.handleCommand(self.buildCommand('Filename',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_restore(self, request):
		self.withMainTemplate = False
		try:
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.RESTORE)
			bqe.handleCommand(self.buildCommand('Filename',request.args))
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

		from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.ServiceList import ServiceList
		from enigma import eServiceReference

		servicelist = ServiceList(eServiceReference(sRef))
		slist = servicelist.getServicesAsList()

		for sitem in slist:
			if not int(sitem[0].split(":")[1]) & 512:	# 512 is hidden service on sifteam image. Doesn't affect other images
				service = {}
				service['servicereference'] = sitem[0]
				service['servicename'] = sitem[1]
				service['isgroup'] = sitem[2]
				service['ismarker'] = sitem[3]
				service['isprotected'] = sitem[4]
				services.append(service)

		return { "services": services }

	def P_getprotectionsettings(self, request):
		configured = config.ParentalControl.configured.value
		if configured:
			if config.ParentalControl.type.value == LIST_BLACKLIST:
				type = "0"
			else:
				type = "1"
			setuppin = config.ParentalControl.setuppin.value
			setuppinactive = config.ParentalControl.setuppinactive.value
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

