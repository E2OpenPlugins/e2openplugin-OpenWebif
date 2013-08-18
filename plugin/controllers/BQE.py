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
		try:
			self.withMainTemplate = False
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.ADD_BOUQUET)
			bqe.handleCommand(self.buildCommand('name,mode',request.args))
			return self.returnResult(request, bqe.result)
		except ImportError:
			return self.returnResult(request, [False, 'BouquetEditor plugin not found'])

	def P_removebouquet(self, request):
		try:
			self.withMainTemplate = False
			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
			bqe = BouquetEditor(self.session, func=BouquetEditor.REMOVE_BOUQUET)
			bqe.handleCommand(self.buildCommand('sBouquetRef,mode',request.args))
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

#class BQEController(resource.Resource):
#	def __init__(self, session, path = ""):
#		resource.Resource.__init__(self)
#		self.session = session
#		try:
#			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
#		except ImportError:
#			print "BQE plugin not found"
#			return

#	def render(self, request):
#		request.setResponseCode(http.OK)
#		request.setHeader('Content-type', 'application/xhtml+xml')
#		request.setHeader('charset', 'UTF-8')
#		return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>BouquetEditor Plugin not found</e2statetext></e2simplexmlresult>'


#class BouquetEditorWebScreen(WebScreen):
#	def __init__(self, session, request):
#		WebScreen.__init__(self, session, request)
#		from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
#		self["AddBouquet"] = BouquetEditor(session, func=BouquetEditor.ADD_BOUQUET)
#		self["RemoveBouquet"] = BouquetEditor(session, func=BouquetEditor.REMOVE_BOUQUET)
#		self["MoveBouquet"] = BouquetEditor(session, func=BouquetEditor.MOVE_BOUQUET)
#		self["MoveService"] = BouquetEditor(session, func=BouquetEditor.MOVE_SERVICE)
#		self["RemoveService"] = BouquetEditor(session, func=BouquetEditor.REMOVE_SERVICE)
#		self["AddServiceToBouquet"] = BouquetEditor(session, func=BouquetEditor.ADD_SERVICE_TO_BOUQUET)
#		self["AddProviderToBouquetlist"] = BouquetEditor(session, func=BouquetEditor.ADD_PROVIDER_TO_BOUQUETLIST)
#		self["AddServiceToAlternative"] = BouquetEditor(session, func=BouquetEditor.ADD_SERVICE_TO_ALTERNATIVE)
#		self["RemoveAlternativeServices"] = BouquetEditor(session, func=BouquetEditor.REMOVE_ALTERNATIVE_SERVICES)
#		self["ToggleLock"] = BouquetEditor(session, func=BouquetEditor.TOGGLE_LOCK)
#		self["Backup"] = BouquetEditor(session, func=BouquetEditor.BACKUP)
#		self["Restore"] = BouquetEditor(session, func=BouquetEditor.RESTORE)
#		self["RenameService"] = BouquetEditor(session, func=BouquetEditor.RENAME_SERVICE)
#		self["AddMarkerToBouquet"] = BouquetEditor(session, func=BouquetEditor.ADD_MARKER_TO_BOUQUET)

