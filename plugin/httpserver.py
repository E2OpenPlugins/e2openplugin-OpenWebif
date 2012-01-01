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
from twisted.internet.error import CannotListenError

from controllers.root import RootController


global http_running
http_running = ""

def buildRootTree(session):
	root = RootController(session)
	return root

def HttpdStart(session):
	if config.OpenWebif.enabled.value == True:
		global http_running
		port = config.OpenWebif.port.value


		root = buildRootTree(session)
		if config.OpenWebif.auth.value == True:	
			root = AuthResource(session, root)
		site = server.Site(root)
		
		try:
			http_running = reactor.listenTCP(port, site)
			print "[OpenWebif] started on %i"% (port)
		except CannotListenError:
			print "[OpenWebif] failed to listen on Port %i" % (port)

#Streaming requires listening on 127.0.0.1:80		
		if port != 80:
			root = buildRootTree(session)
			site = server.Site(root)
			try:
				d = reactor.listenTCP(80, site, interface='127.0.0.1')
				print "[OpenWebif] started stream listening on port 80"
			except CannotListenError:
				print "[OpenWebif] port 80 busy"



def HttpdStop(session):
	if (http_running is not None) and (http_running != ""):
		godown = http_running.stopListening()
		try:
			godown.addCallback(HttpdDoStop)
		except AttributeError:
			pass

def HttpdDoStop(session):
	http_running = ""
	print "[OpenWebif] stopped"

def HttpdRestart(session):
	if (http_running is not None) and (http_running != ""):
		godown = http_running.stopListening()
		try:
			godown.addCallback(HttpdDoRestart, session)
		except AttributeError:
			HttpdStart(session)
	else:
		HttpdStart(session)

def HttpdDoRestart(ign, session):
	http_running = ""
	HttpdStart(session)

class AuthResource(resource.Resource):
	def __init__(self, session, root):
		resource.Resource.__init__(self)
		self.resource = root
		

	def render(self, request):
		if request.getClientIP() == "127.0.0.1":
			return self.resource.render(request)
			
		if self.login(request.getUser(), request.getPassword()) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = error.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
			return errpage.render(request)
		else:
			return self.resource.render(request)


	def getChildWithDefault(self, path, request):
		if request.getClientIP() == "127.0.0.1":
			return self.resource.getChildWithDefault(path, request)
			
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
