##############################################################################
#                         <<< http_server >>>                           
#                                                                            
#                        2011 E2OpenPlugins          
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################

from Components.config import config
from Tools.Directories import fileExists
from twisted.internet import reactor
from twisted.web import server, http, static, resource, error
from ow_contents import get_Info_content
from ow_ajax import get_Ajax_current, get_Ajax_bouquets, get_Ajax_providers, get_Ajax_satellites, get_Ajax_channel_list
from ow_tpl import tv_Tabs_Tpl

global http_running
http_running = ""

def buildRootTree(session):
	basepath = get_BasePath()
	root = BuildPage(session, basepath + "/www/html")
	root.putChild("ajax", BuildAjaxPage(session, basepath + "/www/html/ajax"))
	root.putChild("js", static.File(basepath + "/www/html/js"))
	root.putChild("css", static.File(basepath + "/www/html/css"))
	root.putChild("media", static.File("/media"))
	return root

def HttpdStart(session):
	if config.OpenWebif.enabled.value == True:
		global http_running
		port = config.OpenWebif.port.value


		root = buildRootTree(session)
		if config.OpenWebif.auth.value == True:	
			root = AuthResource(session, root)
		site = server.Site(root)
		
		http_running = reactor.listenTCP(port, site)

		print "[OpenWebif] started on %i"% (port)
		
def HttpdStop(session):
	if http_running:
		http_running.stopListening().addCallback(HttpdDoStop, session)

def HttpdDoStop(session):
	print "[OpenWebif] stopped"
	
def HttpdRestart(session):
	if http_running:
		http_running.stopListening().addCallback(HttpdDoRestart, session)

def HttpdDoRestart(ign, session):
	HttpdStart(session)

class AuthResource(resource.Resource):
	def __init__(self, session, root):
		resource.Resource.__init__(self)
		self.resource = root
		

	def render(self, request):
		if self.login(request.getUser(), request.getPassword()) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = error.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
			return errpage.render(request)
		else:
			return self.resource.render(request)


	def getChildWithDefault(self, path, request):
		if self.login(request.getUser(), request.getPassword()) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = error.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
			return errpage
		else:
			return self.resource.getChildWithDefault(path, request)
		
		
	def login(self, user, passwd):
		from crypt import crypt
		from pwd import getpwnam
		from spwd import getspnam
		cpass = None
		try:
			cpass = getpwnam(user)[1]
		except:
			return False
		if cpass:
			if cpass == 'x' or cpass == '*':
				try:
					cpass = getspnam(user)[1]
				except:
					return False			
			return crypt(passwd, cpass) == cpass
		return False

class BuildPage(resource.Resource):
	def __init__(self, session, path):
		resource.Resource.__init__(self)

		self.session = session
		self.path = path

	def render(self, request):
		basepath = get_BasePath()
		if fileExists(self.path):
			htmlout = self.loadHtmlSource(basepath + "/www/html/index.html")
			request.setResponseCode(http.OK)
        		OpenWebIfMainBody = self.get_Main_body(self.path)
			request.write(htmlout.format(**locals()))
			request.finish()
		else:
			request.setResponseCode(http.NOT_FOUND)
			request.write("<html><head><title>Open Webif</title></head><body><h1>Error 404: Page not found</h1><br />The requested URL was not found on this server.</body></html>")
			request.finish()
			
		return server.NOT_DONE_YET
		
	def getChild(self, path, request):
		path = self.path + "/" + path
		if path[-1] == "/":
			path += "index.html"
		return BuildPage(self.session, path)

	def loadHtmlSource(self, file):
		out = "not found"
		if fileExists(file):
			f = open(file,'r')
 			out = f.read()
 			f.close()
		return out
		
	def get_Main_body(self, path):
		if path.find('index.html') != -1:
			return tv_Tabs_Tpl()
		elif path.find('box_info.html') != -1:
			htmlout = self.loadHtmlSource(self.path)
			owinfo = get_Info_content()
			return htmlout.format(**owinfo)
		else:
			return self.loadHtmlSource(self.path)
		
		
class BuildAjaxPage(resource.Resource):
	def __init__(self, session, path):
		resource.Resource.__init__(self)

		self.session = session
		self.path = path

	def render_GET(self, request):
		self.args = request.args
		basepath = get_BasePath()
		request.setResponseCode(http.OK)
		htmlout = self.get_body(self.path)
		request.write(htmlout)
		request.finish()

		return server.NOT_DONE_YET
		
		
	def getChild(self, path, request):
		path = self.path + "/" + path
		return BuildAjaxPage(self.session, path)
		
	def get_body(self, path):
		if path.find('current.html') != -1:
			return get_Ajax_current(self.session)
		elif path.find('bouquets.html') != -1:
			return get_Ajax_bouquets()
		elif path.find('bouquets_chan.html') != -1:
			return get_Ajax_channel_list("bouquet", self.args["id"][0])
		elif path.find('providers.html') != -1:
			return get_Ajax_providers()
		elif path.find('providers_chan.html') != -1:
			return get_Ajax_channel_list("provider", self.args["id"][0])
		elif path.find('satellites.html') != -1:
			return get_Ajax_satellites()
		elif path.find('satellites_chan.html') != -1:
			return get_Ajax_channel_list("satellite", self.args["id"][0])
		elif path.find('all.html') != -1:
			return get_Ajax_channel_list("all", "all")
		else:
			return "Error. Page not found."
		
def get_BasePath():
	return "/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif"



