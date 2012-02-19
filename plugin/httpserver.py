##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from enigma import eEnv
from Components.config import config
from Tools.Directories import fileExists
from twisted.internet import reactor
from twisted.web import server, http, static, resource, error
from twisted.internet.error import CannotListenError

from controllers.root import RootController

import os
import imp

global http_running
http_running = ""

def isOriginalWebifInstalled():
	pluginpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/WebInterface/plugin.py')
	if fileExists(pluginpath) or fileExists(pluginpath + "o") or fileExists(pluginpath + "c"):
		return True
		
	return False

def buildRootTree(session):
	root = RootController(session)
	
	if not isOriginalWebifInstalled():
		# this is an hack! any better idea?
		origwebifpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/WebInterface')
		hookpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenWebif/pluginshook.src')
		if not os.path.islink(origwebifpath + "/WebChilds/Toplevel.py"):
			print "[OpenWebif] hooking original webif plugins"
			
			cleanuplist = [
				"/__init__.py",
				"/__init__.pyo",
				"/__init__.pyc",
				"/WebChilds/__init__.py",
				"/WebChilds/__init__.pyo",
				"/WebChilds/__init__.pyc",
				"/WebChilds/External/__init__.py",
				"/WebChilds/External/__init__.pyo",
				"/WebChilds/External/__init__.pyc",
				"/WebChilds/Toplevel.py",
				"/WebChilds/Toplevel.pyo"
				"/WebChilds/Toplevel.pyc"
			]
			
			for cleanupfile in cleanuplist:
				if fileExists(origwebifpath + cleanupfile):
					os.remove(origwebifpath + cleanupfile)
				
			if not os.path.exists(origwebifpath + "/WebChilds/External"):
				os.makedirs(origwebifpath + "/WebChilds/External")
			open(origwebifpath + "/__init__.py", "w")
			open(origwebifpath + "/WebChilds/__init__.py", "w")
			open(origwebifpath + "/WebChilds/External/__init__.py", "w")
			
			os.symlink(hookpath, origwebifpath + "/WebChilds/Toplevel.py")
			
		# import modules
		print "[OpenWebif] loading external plugins..."
		from Plugins.Extensions.WebInterface.WebChilds.Toplevel import loaded_plugins
		if len(loaded_plugins) == 0:
			externals = os.listdir(origwebifpath + "/WebChilds/External")
			loaded = []
			for external in externals:
				if external[-3:] == ".py":
					modulename = external[:-3]
				elif external[-4:] == ".pyo" or external[-4:] == ".pyc":
					modulename = external[:-4]
				else:
					continue
					
				if modulename == "__init__":
					continue
					
				if modulename in loaded:
					continue
					
				loaded.append(modulename)
				try:
					imp.load_source(modulename, origwebifpath + "/WebChilds/External/" + modulename + ".py")
				except Exception, e:
					# maybe there's only the compiled version
					imp.load_compiled(modulename, origwebifpath + "/WebChilds/External/" + external)
					
		if len(loaded_plugins) > 0:
			for plugin in loaded_plugins:
				root.putChild(plugin[0], plugin[1])
				print "[OpenWebif] plugin '%s' loaded on path '/%s'" % (plugin[2], plugin[0])
		else:
			print "[OpenWebif] no plugins to load"
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
			if not isOriginalWebifInstalled():
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
		session = request.getSession().sessionNamespaces
		
		if request.getClientIP() == "127.0.0.1":
			return self.resource.getChildWithDefault(path, request)
			
		if "logged" in session.keys() and session["logged"]:
			return self.resource.getChildWithDefault(path, request)
			
		if self.login(request.getUser(), request.getPassword()) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = error.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
			return errpage
		else:
			session["logged"] = True
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
