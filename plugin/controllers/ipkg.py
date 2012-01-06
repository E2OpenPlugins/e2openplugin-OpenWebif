##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from enigma import eConsoleAppContainer
from twisted.web import static, resource, http, server

class IpkgController(resource.Resource):

	IPKG_PATH = "/usr/bin/opkg"

	SIMPLECMDS = ( "list", "list_installed", "list_upgradable", "update", "upgrade" )
	PACKAGECMDS = ( "info", "status", "install", "remove" )
	FILECMDS = ( "search", )

	def render(self, request):
		self.args = request.args
		self.command = self.getArg("command")

		if self.command is not None:
			if self.command in IpkgController.SIMPLECMDS:
				return self.execSimpleCmd(request)
			elif self.command in IpkgController.PACKAGECMDS:
				return self.execPackageCmd(request)
			elif self.command in IpkgController.FILECMDS:
				return self.execFileCmd(request)
			else:
				return self.doErrorPage(request, "Unknown command: "+ self.command)
		else:
			return self.doIndexPage(request)

	def buildCmd(self, parms=[]):
		cmd = [IpkgController.IPKG_PATH, "ipkg", self.command] + parms
		print "[ipkg.py] cmd: %s" % cmd
		return cmd

	def fakeAnswer(self, request):
		request.setResponseCode(http.OK)
		fakeresult = "<html><body>"
		fakeresult += "Package: enigma2-plugin-extensions-webinterface<br>"
		fakeresult += "Version: experimental-git3735+5cdadeb-r6<br>"
		fakeresult += "Depends: python-twisted-web, python-pyopenssl, python-crypt, python-unixadmin, aio-grab"
		fakeresult += "Provides:"
		fakeresult += "Status: install user installed"
		fakeresult += "Section: base"
		fakeresult += "Architecture: x"
		fakeresult += "Maintainer: Felix Domke"
		fakeresult += "MD5Sum: 577a05fd3b2ae71693a8377d753fdff6"
		fakeresult += "Size: 415942"
		fakeresult += "Filename: enigma2-plugin-extensions-webinterface_experimental-git3735+5cdadeb-r6_x.ipk"
		fakeresult += "Source: unknown"
		fakeresult += "Description: Control enigma2 with your Browser"
		fakeresult += "Installed-Time: 1325212945"
		fakeresult += "</body></html>"
		request.write(fakeresult)
		request.finish()
		return server.NOT_DONE_YET

	def execCmd(self, request, parms=[]):
		cmd = self.buildCmd(parms)
		request.setResponseCode(http.OK)
		IPKGConsoleStream(request, cmd)
		return server.NOT_DONE_YET

	def execSimpleCmd(self, request):
		 return self.execCmd(request)

	def execPackageCmd(self, request):
		package = self.getArg("package")
		if package is not None:
			if package == "enigma2-plugin-extensions-webinterface":
				return self.fakeAnswer(request)
			else:
				return self.execCmd(request, [package])
		else:
			return self.doErrorPage(request, "Missing parameter: package")

	def execFileCmd(self, request):
		file = self.getArg("file")
		if file is not None:
			return self.execCmd(request, [file])
		else:
			return self.doErrorPage("Missing parameter: file")

	def doIndexPage(self, request):
		html = "<html><body>"
		html += "<h1>Interface to OPKG</h1>"
		html += "update, ?command=update<br>"
		html += "upgrade, ?command=upgrade<br>"
		html += "list_installed, ?command=list_installed<br>"
		html += "list_upgradable, ?command=list_upgradable<br>"
		html += "list, ?command=list<br>"
		html += "search, ?command=search&file=&lt;filename&gt;<br>"
		html += "info, ?command=info&package=&lt;packagename&gt;<br>"
		html += "status, ?command=status&package=&lt;packagename&gt;<br>"
		html += "install, ?command=install&package=&lt;packagename&gt;<br>"
		html += "remove, ?command=remove&package=&lt;packagename&gt;<br>"
		html += "</body></html>"

		request.setResponseCode(http.OK)
		request.write(html)
		request.finish()

		return server.NOT_DONE_YET

	def doErrorPage(self, request, errormsg):
		request.setResponseCode(http.OK)
		request.write(errormsg)
		request.finish()

		return server.NOT_DONE_YET

	def getArg(self, key):
		if key in self.args:
			return self.args[key][0]
		else:
			return None

class IPKGConsoleStream:
	def __init__(self, request, cmd):
		self.request = request
		self.request.write("<html><body>\n")		
		if hasattr(self.request, 'notifyFinish'):
			self.request.notifyFinish().addErrback(self.connectionLost)
		self.container = eConsoleAppContainer()
		self.lastdata = None
		self.stillAlive = True

		self.container.dataAvail.append(self.dataAvail)
		self.container.appClosed.append(self.cmdFinished)

		self.container.execute(*cmd)

	def connectionLost(self, err):
		self.stillAlive = False

	def cmdFinished(self, data):
		if self.stillAlive:
			self.request.write("</body></html>\n")
			self.request.finish()

	def dataAvail(self, data):
		if data != self.lastdata or self.lastdata is None and self.stillAlive:
			self.lastdata = data
			self.request.write(data.replace("\n", "<br>\n"))
