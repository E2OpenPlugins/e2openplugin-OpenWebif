# -*- coding: utf-8 -*-

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
from twisted.internet import reactor, ssl
from twisted.web import server, http, static, resource, error, version
from twisted.internet.error import CannotListenError

from controllers.root import RootController
from sslcertificate import SSLCertificateGenerator, KEY_FILE, CERT_FILE
from socket import gethostname, has_ipv6

import os
import imp

global listener, server_to_stop
listener = []

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
		global listener
		port = config.OpenWebif.port.value

		root = buildRootTree(session)
		if config.OpenWebif.auth.value == True:	
			root = AuthResource(session, root)
		site = server.Site(root)
		
		# start http webserver on configured port
		try:
			if has_ipv6 and fileExists('/proc/net/if_inet6') and version.major >= 12:
				# use ipv6
				listener.append( reactor.listenTCP(port, site, interface='::') )
			else:
				# ipv4 only
				listener.append( reactor.listenTCP(port, site) )
			print "[OpenWebif] started on %i"% (port)
			BJregisterService('http',port)
		except CannotListenError:
			print "[OpenWebif] failed to listen on Port %i" % (port)

		if config.OpenWebif.https_enabled.value == True:
			httpsPort = config.OpenWebif.https_port.value
			installCertificates(session)
			# start https webserver on port configured port
			try:
				context = ssl.DefaultOpenSSLContextFactory(KEY_FILE, CERT_FILE)
				if has_ipv6 and fileExists('/proc/net/if_inet6') and version.major >= 12:
					# use ipv6
					listener.append( reactor.listenSSL(httpsPort, site, context, interface='::') )
				else:
					# ipv4 only
					listener.append( reactor.listenSSL(httpsPort, site, context) )
				print "[OpenWebif] started on", httpsPort
				BJregisterService('https',httpsPort)
			except CannotListenError:
				print "[OpenWebif] failed to listen on Port", httpsPort

#Streaming requires listening on 127.0.0.1:80	
		if port != 80:
			if not isOriginalWebifInstalled():
				root = buildRootTree(session)
				site = server.Site(root)
				try:
					if has_ipv6 and fileExists('/proc/net/if_inet6') and version.major >= 12:
						# use ipv6
						listener.append( reactor.listenTCP(80, site, interface='::1') )
					else:
						# ipv4 only
						listener.append( reactor.listenTCP(80, site, interface='127.0.0.1') )
					print "[OpenWebif] started stream listening on port 80"
				except CannotListenError:
					print "[OpenWebif] port 80 busy"


def HttpdStop(session):
	StopServer(session).doStop()

def HttpdRestart(session):
	StopServer(session, HttpdStart).doStop()

class AuthResource(resource.Resource):
	def __init__(self, session, root):
		resource.Resource.__init__(self)
		self.resource = root
		

	def render(self, request):
		if request.getClientIP() == "127.0.0.1":
			return self.resource.render(request)
			
		if self.login(request.getUser(), request.getPassword()) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = resource.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
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
			errpage = resource.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
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

#
# Helper class to stop running web servers; we use a class here to reduce use
# of global variables. Resembles code prior found in HttpdStop et. al.
# 
class StopServer:
	server_to_stop = 0
	
	def __init__(self, session, callback=None):
		self.session = session
		self.callback = callback
	
	def doStop(self):
		global listener
		self.server_to_stop = 0
		for interface in listener:
			print "[OpenWebif] Stopping server on port", interface.port
			deferred = interface.stopListening()
			try:
				self.server_to_stop += 1
				deferred.addCallback(self.callbackStopped)
			except AttributeError:
				pass
		listener = []
		if self.server_to_stop < 1:
			self.doCallback()
	
	def callbackStopped(self, reason):
		self.server_to_stop -= 1
		if self.server_to_stop < 1:
			self.doCallback()
	
	def doCallback(self):
		if self.callback is not None:
			self.callback(self.session)
		
#
# create a self signed SSL certificate if necessary
#
def installCertificates(session):
	certGenerator = SSLCertificateGenerator()
	try:
		certGenerator.installCertificates()
	except IOError, e:
		# Disable https
		config.OpenWebif.https_enabled.value = False
		config.OpenWebif.https_enabled.save()
		# Inform the user
		session.open(MessageBox, "Cannot install generated SSL-Certifactes for https access\nHttps access is disabled!", MessageBox.TYPE_ERROR)
# BJ
def BJregisterService(protocol, port):
	try:
		from Plugins.Extensions.Bonjour.Bonjour import bonjour
		service = bonjour.buildService(protocol, port, 'OpenWebif')
		bonjour.registerService(service, True)
		return True

	except ImportError, e:
		return False

