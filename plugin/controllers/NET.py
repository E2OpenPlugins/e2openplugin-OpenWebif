# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: NetController
##########################################################################
# Copyright (C) 2018-2020 jbleyel and E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##########################################################################

from twisted.web import server, http, resource
import json
import six
from re import sub as re_sub
from Plugins.SystemPlugins.NetworkBrowser.AutoMount import iAutoMount


class NetController(resource.Resource):
	def __init__(self, session, path=""):
		resource.Resource.__init__(self)
		self.path = six.ensure_text(path)
		self.callback = None
		self.session = session
		self.result = {}
		self.result["result"] = False
		self.result["message"] = "unknown Error"

	def getChild(self, path, request):
		return self.__class__(self.session, path)

	def parsecallback(self):
		self.request.setResponseCode(http.OK)
		self.request.write(json.dumps(self.result))
		self.request.finish()

	def render(self, request):
		func = getattr(self, "P_" + self.path, None)
		self.request = request
		if callable(func):
			request.setResponseCode(http.OK)
			request.setHeader("content-type", "application/json")
			func()
			request.write(json.dumps(self.result))
			request.finish()
		else:
			func = getattr(self, "PC_" + self.path, None)
			if callable(func):
				self.callback = self.parsecallback
				func()
			else:
				request.setHeader("content-type", "text/plain")
				request.write("")
				request.finish()
		return server.NOT_DONE_YET

	def buildCommand(self, ids):
		args = self.request.args
		paramlist = ids.split(",")
		list = {}
		for key in paramlist:
			if key in args:
				k = six.ensure_binary(key)
				list[key] = six.ensure_text(args[k][0])
			else:
				list[key] = None
		return list

	def failed(self, text):
		self.result["message"] = text

	def P_listmounts(self):
		list = []
		mounts = iAutoMount.getMountsList()
		for sharename in list(mounts.keys()):
			mountentry = iAutoMount.automounts[sharename]
			list.append(mountentry)
		self.result["result"] = True
		self.result["mounts"] = list

# Todo: check result
	def removeCallback(self, data):
		if data is True:
			iAutoMount.writeMountsConfig()
			self.result["result"] = True
			self.result["message"] = "mount removed"
		if self.callback is not None:
			self.callback()

	def PC_removemount(self):
		param = self.buildCommand('sharename')
		sharename = param["sharename"]
		if sharename is None:
			self.failed("No sharename given!")
		else:
			mounts = iAutoMount.getMountsList()
			if sharename not in mounts:
				self.failed("No sharename not exists")
			else:
				iAutoMount.removeMount(sharename, self.removeCallback)
				return
		self.callback()

	def P_updatemount(self):
		self.insertupdatemount(False)

	def P_addmount(self):
		self.insertupdatemount(True)

	def P_renamemount(self):
		param = self.buildCommand('sharename,newsharename')
		sharename = param["sharename"]
		if sharename is None:
			return self.failed("No sharename given!")
		newsharename = param["newsharename"]
		if newsharename is None:
			return self.failed("No newsharename given!")

		mounts = iAutoMount.getMountsList()

		if newsharename in mounts:
			return self.failed("newsharename already exists")

		if sharename in mounts:
			try:
				iAutoMount.setMountsAttribute(sharename, "sharename", newsharename)
				iAutoMount.writeMountsConfig()
				self.result["result"] = True
				self.result["message"] = "mount changed"
			except Exception as error:
				self.result["message"] = "mount not changed"
				self.result["error"] = error
		else:
			return self.failed("sharename not exists")

	def insertupdatemount(self, addnew):

		param = self.buildCommand('sharedir,sharename,mounttype,ip,username,active,username,password,hdd_replacement,options,mountusing')
		ip = param["ip"]
		if ip is None:
			return self.failed("No ip given!")
		sharedir = param["sharedir"]
		if sharedir is None:
			return self.failed("No sharedir given!")
		sharename = param["sharename"]
		if sharename is None:
			return self.failed("No sharename given!")
		mounttype = param["mounttype"]
		if mounttype is None:
			mounttype = "nfs"
		if mounttype not in ('cifs', 'nfs'):
			return self.failed("wrong mounttype given!")

		options = param["options"]
		if options is None:
			if mounttype == "nfs":
				options = "rw,nolock,soft"
			else:
				options = "rw,utf8"
		mountusing = param["mountusing"]
		if mountusing is None:
			mountusing = "autofs"
		hdd_replacement = param["hdd_replacement"]
		if hdd_replacement is None:
			hdd_replacement = False
		if hdd_replacement == 'True':
			hdd_replacement = True
		active = param["active"]
		if active is None:
			active = False
		username = param["username"]
		if username is None:
			username = ""
		password = param["password"]
		if password is None:
			password = ""

		mounts = iAutoMount.getMountsList()

		if addnew is True:
			if sharename in mounts:
				return self.failed("sharename already exists")
			else:
				try:
					data = {'isMounted': False}
					data['active'] = active
					data['ip'] = ip
					data['sharename'] = re_sub("\\W", "", sharename)
					if sharedir.startswith("/"):
						data['sharedir'] = sharedir[1:]
					else:
						data['sharedir'] = sharedir
					data['options'] = options
					data['mounttype'] = mounttype
					data['username'] = username
					data['password'] = password
					data['hdd_replacement'] = hdd_replacement
					data['mountusing'] = mountusing
					iAutoMount.automounts[sharename] = data
					iAutoMount.writeMountsConfig()
					self.result["result"] = True
					self.result["message"] = "mount added"
				except Exception as error:
					self.result["message"] = "mount not added"
					self.result["error"] = error
		else:
			if sharename in mounts:
				try:
					iAutoMount.setMountsAttribute(sharename, "active", active)
					iAutoMount.setMountsAttribute(sharename, "ip", ip)
					iAutoMount.setMountsAttribute(sharename, "sharedir", sharedir)
					iAutoMount.setMountsAttribute(sharename, "mounttype", mounttype)
					iAutoMount.setMountsAttribute(sharename, "options", options)
					iAutoMount.setMountsAttribute(sharename, "username", username)
					iAutoMount.setMountsAttribute(sharename, "password", password)
					iAutoMount.setMountsAttribute(sharename, "hdd_replacement", hdd_replacement)
					iAutoMount.setMountsAttribute(sharename, "mountusing", mountusing)
					iAutoMount.writeMountsConfig()
					self.result["result"] = True
					self.result["message"] = "mount changed"
				except Exception as error:
					self.result["message"] = "mount not changed"
					self.result["error"] = error
			else:
				return self.failed("sharename not exists")
