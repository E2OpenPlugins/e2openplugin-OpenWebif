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
from Screens.MessageBox import MessageBox
from Components.config import config
from Tools.Directories import fileExists
from twisted.internet import reactor, ssl
from twisted.web import server, http, static, resource, error, version
from twisted.internet.error import CannotListenError

from controllers.root import RootController
from sslcertificate import SSLCertificateGenerator, KEY_FILE, CERT_FILE, CA_FILE
from socket import gethostname, has_ipv6

from OpenSSL import SSL
from twisted.internet.protocol import Factory, Protocol

import os
import imp
import re

global listener, server_to_stop
listener = []

def verifyCallback(connection, x509, errnum, errdepth, ok):
	if not ok:
		print '[OpenWebif] Invalid cert from subject: ', x509.get_subject()
		return False
	else:
		print '[OpenWebif] Successful cert authed as: ', x509.get_subject()
	return True

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
			open(origwebifpath + "/__init__.py", "w").close()
 			open(origwebifpath + "/WebChilds/__init__.py", "w").close()
 			open(origwebifpath + "/WebChilds/External/__init__.py", "w").close()

			os.symlink(hookpath, origwebifpath + "/WebChilds/Toplevel.py")

		# import modules
#		print "[OpenWebif] loading external plugins..."
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
#				print "[OpenWebif] plugin '%s' loaded on path '/%s'" % (plugin[2], plugin[0])
		else:
			print "[OpenWebif] no plugins to load"
	return root

def HttpdStart(session):
	if config.OpenWebif.enabled.value == True:
		global listener
		port = config.OpenWebif.port.value

		temproot = buildRootTree(session)
		root = temproot
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

		if config.OpenWebif.https_clientcert.value == True and not os.path.exists(CA_FILE):
			# Disable https
			config.OpenWebif.https_enabled.value = False
			config.OpenWebif.https_enabled.save()
			# Inform the user
			session.open(MessageBox, "Cannot read CA certs for HTTPS access\nHTTPS access is disabled!", MessageBox.TYPE_ERROR)

		if config.OpenWebif.https_enabled.value == True:
			httpsPort = config.OpenWebif.https_port.value
			installCertificates(session)
			# start https webserver on port configured port
			try:
				try:
					context = ssl.DefaultOpenSSLContextFactory(KEY_FILE, CERT_FILE)
				except:
					# THIS EXCEPTION IS ONLY CATCHED WHEN CERT FILES ARE BAD (look below for error)
					print "[OpenWebif] failed to get valid cert files. (It could occure bad file save or format, removing...)"
					# removing bad files
					if os.path.exists(KEY_FILE):
						os.remove(KEY_FILE)
					if os.path.exists(CERT_FILE):
						os.remove(CERT_FILE)
					# regenerate new ones
					installCertificates(session)
					context = ssl.DefaultOpenSSLContextFactory(KEY_FILE, CERT_FILE)

				if config.OpenWebif.https_clientcert.value == True:
					ctx = context.getContext()
					ctx.set_verify(
						SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
						verifyCallback
						)
					ctx.load_verify_locations(CA_FILE)

				sslroot = temproot
				if config.OpenWebif.https_auth.value == True:
					sslroot = AuthResource(session, sslroot)
				sslsite = server.Site(sslroot)

				if has_ipv6 and fileExists('/proc/net/if_inet6') and version.major >= 12:
					# use ipv6
					listener.append( reactor.listenSSL(httpsPort, sslsite, context, interface='::') )
				else:
					# ipv4 only
					listener.append( reactor.listenSSL(httpsPort, sslsite, context) )
				print "[OpenWebif] started on", httpsPort
				BJregisterService('https',httpsPort)
			except CannotListenError:
				print "[OpenWebif] failed to listen on Port", httpsPort
			except:
				print "[OpenWebif] failed to start https, disabling..."
				# Disable https
				config.OpenWebif.https_enabled.value = False
				config.OpenWebif.https_enabled.save()

		#Streaming requires listening on 127.0.0.1:80
		if port != 80:
			try:
				if has_ipv6 and fileExists('/proc/net/if_inet6') and version.major >= 12:
					# use ipv6
					# Dear Twisted devs: Learning English, lesson 1 - interface != address
					listener.append( reactor.listenTCP(80, site, interface='::1') )
					listener.append( reactor.listenTCP(80, site, interface='::ffff:127.0.0.1') )
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
		host = request.getHost().host

		if (host == "localhost" or host == "127.0.0.1" or host == "::ffff:127.0.0.1") and not config.OpenWebif.auth_for_streaming.value:
			return self.resource.render(request)
		if self.login(request.getUser(), request.getPassword(), request.transport.socket.getpeername()[0]) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = resource.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
			return errpage.render(request)
		else:
			return self.resource.render(request)

	def getChildWithDefault(self, path, request):
		session = request.getSession().sessionNamespaces
		host = request.getHost().host

		if ((host == "localhost" or host == "127.0.0.1" or host == "::ffff:127.0.0.1") and not config.OpenWebif.auth_for_streaming.value) or request.uri == "/web/getipv6":
			return self.resource.getChildWithDefault(path, request)
		if "logged" in session.keys() and session["logged"]:
			return self.resource.getChildWithDefault(path, request)
		if self.login(request.getUser(), request.getPassword(), request.transport.socket.getpeername()[0]) == False:
			request.setHeader('WWW-authenticate', 'Basic realm="%s"' % ("OpenWebif"))
			errpage = resource.ErrorPage(http.UNAUTHORIZED,"Unauthorized","401 Authentication required")
			return errpage
		else:
			session["logged"] = True
			return self.resource.getChildWithDefault(path, request)

	def login(self, user, passwd, peer):
		if user=="root" and config.OpenWebif.no_root_access.value:
			# Override "no root" for logins from local network
			match=re.match("(::ffff:|)(192\.168|10\.\d{1,3})\.\d{1,3}\.\d{1,3}", peer)
			if match is None:
				return False
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
