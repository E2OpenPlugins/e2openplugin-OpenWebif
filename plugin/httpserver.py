##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Components.config import config
from twisted.internet import reactor
from twisted.web import server, http, static, resource, error

#from core.info import getBasePath, getWebPublicPath

from controllers.root import RootController
#from path.ajax import AjaxPath
#from path.web import WebPath

global http_running
http_running = ""

def buildRootTree(session):
	#basepath = getBasePath()
	root = RootController(session)
	#root.putChild("ajax", AjaxPath(session))
	#root.putChild("web", WebPath(session))
	#root.putChild("js", static.File(getWebPublicPath() + "/js"))
	#root.putChild("css", static.File(getWebPublicPath() + "/css"))
	#root.putChild("images", static.File(getWebPublicPath() + "/images"))
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
