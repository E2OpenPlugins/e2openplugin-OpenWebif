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


from twisted.internet import reactor
from twisted.web import server, http, static, resource

global http_running
http_running = ""
#class OutputPage(resource.Resource):
#	def __init__(self, session):
#		resource.Resource.__init__(self)
#		isLeaf = True
		
#    	def getChild(self, name, request):
#        	if name == '':
#            		return self
#        	return Resource.getChild(self, name, request)

#	def render_GET(self, request):
#        	return "Hello, world! I am located at %r." % (request.prepath,)

def buildRootTree(session):
	basepath = get_BasePath()
	root = static.File(basepath + "/www/html")
	return root

def HttpdStart(session):
	global http_running
	port = 8088
#	out = OutputPage(session)
	root = buildRootTree(session)
	site = server.Site(root)
	http_running = reactor.listenTCP(port, site)

	print "[OpenWebif] started on %i"% (port)

def HttpdStop(session):
	global http_running
	if http_running:
		http_running.stopListening()

def get_BasePath():
	return "/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif"



