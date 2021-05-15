# -*- coding: utf-8 -*-

# LICENCE
#
# This File is part of the Webbouqueteditor plugin
# and licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported
# License if not stated otherwise in a files head. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
# Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.

from __future__ import print_function
from Plugins.Extensions.OpenWebif.controllers.i18n import _
from enigma import eServiceReference, eServiceCenter, eDVBDB
from Components.Sources.Source import Source
from Screens.ChannelSelection import MODE_TV  #,service_types_tv, MODE_RADIO
from Components.config import config
from os import remove, path, popen
from Screens.InfoBar import InfoBar
from ServiceReference import ServiceReference
from Components.ParentalControl import parentalControl
from re import compile as re_compile
from Components.NimManager import nimmanager


class BouquetEditor(Source):

	ADD_BOUQUET = 0
	REMOVE_BOUQUET = 1
	MOVE_BOUQUET = 2
	ADD_SERVICE_TO_BOUQUET = 3
	REMOVE_SERVICE = 4
	MOVE_SERVICE = 5
	ADD_PROVIDER_TO_BOUQUETLIST = 6
	ADD_SERVICE_TO_ALTERNATIVE = 7
	REMOVE_ALTERNATIVE_SERVICES = 8
	TOGGLE_LOCK = 9
	BACKUP = 10
	RESTORE = 11
	RENAME_SERVICE = 12
	ADD_MARKER_TO_BOUQUET = 13
	IMPORT_BOUQUET = 14

	BACKUP_PATH = "/tmp"  # nosec
	BACKUP_FILENAME = "webbouqueteditor_backup.tar"

	def __init__(self, session, func=ADD_BOUQUET):
		Source.__init__(self)
		self.func = func
		self.session = session
		self.command = None
		self.bouquet_rootstr = ""
		self.result = (False, "one two three four unknown command")

	def handleCommand(self, cmd):
		print("[WebComponents.BouquetEditor] handleCommand with cmd = ", cmd)
		if self.func is self.ADD_BOUQUET:
			self.result = self.addToBouquet(cmd)
		elif self.func is self.MOVE_BOUQUET:
			self.result = self.moveBouquet(cmd)
		elif self.func is self.MOVE_SERVICE:
			self.result = self.moveService(cmd)
		elif self.func is self.REMOVE_BOUQUET:
			self.result = self.removeBouquet(cmd)
		elif self.func is self.REMOVE_SERVICE:
			self.result = self.removeService(cmd)
		elif self.func is self.ADD_SERVICE_TO_BOUQUET:
			self.result = self.addServiceToBouquet(cmd)
		elif self.func is self.ADD_PROVIDER_TO_BOUQUETLIST:
			self.result = self.addProviderToBouquetlist(cmd)
		elif self.func is self.ADD_SERVICE_TO_ALTERNATIVE:
			self.result = self.addServiceToAlternative(cmd)
		elif self.func is self.REMOVE_ALTERNATIVE_SERVICES:
			self.result = self.removeAlternativeServices(cmd)
		elif self.func is self.TOGGLE_LOCK:
			self.result = self.toggleLock(cmd)
		elif self.func is self.BACKUP:
			self.result = self.backupFiles(cmd)
		elif self.func is self.RESTORE:
			self.result = self.restoreFiles(cmd)
		elif self.func is self.RENAME_SERVICE:
			self.result = self.renameService(cmd)
		elif self.func is self.ADD_MARKER_TO_BOUQUET:
			self.result = self.addMarkerToBouquet(cmd)
		elif self.func is self.IMPORT_BOUQUET:
			self.result = self.importBouquet(cmd)
		else:
			self.result = (False, _("one two three four unknown command"))

	def addToBouquet(self, param):
		print("[WebComponents.BouquetEditor] addToBouquet with param = ", param)
		bName = param["name"]
		if bName is None:
			return (False, _("No bouquet name given!"))
		mode = MODE_TV  # init
		if "mode" in param:
			if param["mode"] is not None:
				mode = int(param["mode"])
		return self.addBouquet(bName, mode, None)

	def addBouquet(self, bName, mode, services):
		if config.usage.multibouquet.value:
			mutableBouquetList = self.getMutableBouquetList(mode)
			if mutableBouquetList:
				if mode == MODE_TV:
					bName += " (TV)"
					sref = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.%s.tv\" ORDER BY bouquet' % (self.buildBouquetID(bName, "userbouquet.", mode))
				else:
					bName += " (Radio)"
					sref = '1:7:2:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.%s.radio\" ORDER BY bouquet' % (self.buildBouquetID(bName, "userbouquet.", mode))
				new_bouquet_ref = eServiceReference(sref)
				if not mutableBouquetList.addService(new_bouquet_ref):
					mutableBouquetList.flushChanges()
					eDVBDB.getInstance().reloadBouquets()
					mutableBouquet = self.getMutableList(new_bouquet_ref)
					if mutableBouquet:
						mutableBouquet.setListName(bName)
						if services is not None:
							for service in services:
								if mutableBouquet.addService(service):
									print("add", service.toString(), "to new bouquet failed")
						mutableBouquet.flushChanges()
						self.setRoot(self.bouquet_rootstr)
						return (True, _("Bouquet %s created.") % bName)
					else:
						return (False, _("Get mutable list for new created bouquet failed!"))

				else:
					return (False, _("Bouquet %s already exists.") % bName)
			else:
				return (False, _("Bouquetlist is not editable!"))
		else:
			return (False, _("Multi-Bouquet is not enabled!"))

	def addProviderToBouquetlist(self, param):
		print("[WebComponents.BouquetEditor] addProviderToBouquet with param = ", param)
		refstr = param["sProviderRef"]
		if refstr is None:
			return (False, _("No provider given!"))
		mode = MODE_TV  # init
		if "mode" in param:
			if param["mode"] is not None:
				mode = int(param["mode"])
		ref = eServiceReference(refstr)
		provider = ServiceReference(ref)
		providerName = provider.getServiceName()
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(provider.ref)
		return self.addBouquet(providerName, mode, services and services.getContent('R', True))

	def removeBouquet(self, param):
		print("[WebComponents.BouquetEditor] removeBouquet with param = ", param)
		refstr = sref = param["sBouquetRef"]
		if refstr is None:
			return (False, _("No bouquet name given!"))
		mode = MODE_TV  # init
		if "mode" in param:
			if param["mode"] is not None:
				mode = int(param["mode"])

		if "BouquetRefRoot" in param:
			bouquet_root = param["BouquetRefRoot"]  # only when removing alternative
		else:
			bouquet_root = None
		pos = refstr.find('FROM BOUQUET "')
		filename = None
		if pos != -1:
			refstr = refstr[pos + 14:]
			pos = refstr.find('"')
			if pos != -1:
				filename = '/etc/enigma2/' + refstr[:pos]  # FIXMEEE !!! HARDCODED /etc/enigma2
		ref = eServiceReference(sref)
		bouquetName = self.getName(ref)
		if not bouquetName:
			bouquetName = filename
		if bouquet_root:
			mutableList = self.getMutableList(eServiceReference(bouquet_root))
		else:
			mutableList = self.getMutableBouquetList(mode)

		if ref.valid() and mutableList is not None:
			if not mutableList.removeService(ref):
				mutableList.flushChanges()
				self.setRoot(self.bouquet_rootstr)
			else:
				return (False, _("Bouquet %s removed failed.") % filename)
		else:
			return (False, _("Bouquet %s removed failed, sevicerefence or mutable list is not valid.") % filename)
		try:
			if filename is not None:
				if not path.exists(filename + '.del'):
					remove(filename)
				return (True, _("Bouquet %s deleted.") % bouquetName)
		except OSError:
			return (False, _("Error: Bouquet %s could not deleted, OSError.") % filename)

	def moveBouquet(self, param):
		print("[WebComponents.BouquetEditor] moveBouquet with param = ", param)
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, _("No bouquet name given!"))
		mode = MODE_TV  # init
		if "mode" in param:
			if param["mode"] is not None:
				mode = int(param["mode"])
		position = None
		if "position" in param:
			if param["position"] is not None:
				position = int(param["position"])
		if position is None:
			return (False, _("No position given!"))
		mutableBouquetList = self.getMutableBouquetList(mode)
		if mutableBouquetList is not None:
			ref = eServiceReference(sBouquetRef)
			mutableBouquetList.moveService(ref, position)
			mutableBouquetList.flushChanges()
			self.setRoot(self.bouquet_rootstr)
			return (True, _("Bouquet %s moved.") % self.getName(ref))
		else:
			return (False, _("Bouquet %s can not be moved.") % self.getName(ref))

	def removeService(self, param):
		print("[WebComponents.BouquetEditor] removeService with param = ", param)
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, _("No bouquet given!"))
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]
		if sRef is None:
			return (False, _("No service given!"))
		ref = eServiceReference(sRef)
		if ref.flags & eServiceReference.isGroup:  # check if  service is an alternative, if so delete it with removeBouquet
			new_param = {}
			new_param["sBouquetRef"] = sRef
			new_param["mode"] = None  # of no interest when passing BouquetRefRoot
			new_param["BouquetRefRoot"] = sBouquetRef
			returnValue = self.removeBouquet(new_param)
			if returnValue[0]:
				return (True, _("Service %s removed.") % self.getName(ref))
		else:
			bouquetRef = eServiceReference(sBouquetRef)
			mutableBouquetList = self.getMutableList(bouquetRef)
			if mutableBouquetList is not None:
				if not mutableBouquetList.removeService(ref):
					mutableBouquetList.flushChanges()
					self.setRoot(sBouquetRef)
					return (True, _("Service %s removed from bouquet %s.") % (self.getName(ref), self.getName(bouquetRef)))
		return (False, _("Service %s can not be removed.") % self.getName(ref))

	def moveService(self, param):
		print("[WebComponents.BouquetEditor] moveService with param = ", param)
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, _("No bouquet given!"))
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]
		if sRef is None:
			return (False, _("No service given!"))
		position = None
		if "position" in param:
			if param["position"] is not None:
				position = int(param["position"])
		if position is None:
			return (False, _("No position given!"))
		mutableBouquetList = self.getMutableList(eServiceReference(sBouquetRef))
		if mutableBouquetList is not None:
			ref = eServiceReference(sRef)
			mutableBouquetList.moveService(ref, position)
			mutableBouquetList.flushChanges()
			self.setRoot(sBouquetRef)
			return (True, _("Service %s moved.") % self.getName(ref))
		return (False, _("Service can not be moved."))

	def addServiceToBouquet(self, param):
		print("[WebComponents.BouquetEditor] addService with param = ", param)
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, _("No bouquet given!"))
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]
		sRefUrl = False
		sName = None
		if "Name" in param:
			if param["Name"] is not None:
				sName = param["Name"]
		if sRef is None and "sRefUrl" in param:
			# check IPTV
			if param["sRefUrl"] is not None and sName is not None:
				sRef = param["sRefUrl"]
				sRefUrl = True
		elif sRef is None:
			return (False, _("No service given!"))
		sRefBefore = eServiceReference()
		if "sRefBefore" in param:
			if param["sRefBefore"] is not None:
				sRefBefore = eServiceReference(param["sRefBefore"])
		bouquetRef = eServiceReference(sBouquetRef)
		mutableBouquetList = self.getMutableList(bouquetRef)
		if mutableBouquetList is not None:
			if sRefUrl:
				ref = eServiceReference(4097, 0, sRef)
			else:
				ref = eServiceReference(sRef)
			if sName:
				ref.setName(sName)
			if not mutableBouquetList.addService(ref, sRefBefore):
				mutableBouquetList.flushChanges()
				self.setRoot(sBouquetRef)
				return (True, _("Service %s added.") % self.getName(ref))
			else:
				bouquetName = self.getName(bouquetRef)
				return (False, _("Service %s already exists in bouquet %s.") % (self.getName(ref), bouquetName))
		return (False, _("This service can not be added."))

	def addMarkerToBouquet(self, param):
		print("[WebComponents.BouquetEditor] addMarkerToBouquet with param = ", param)
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, _("No bouquet given!"))
		name = None
		if "Name" in param:
			if param["Name"] is not None:
				name = param["Name"]
		if name is None:
			if "SP" not in param:
				return (False, _("No marker-name given!"))
		sRefBefore = eServiceReference()
		if "sRefBefore" in param:
			if param["sRefBefore"] is not None:
				sRefBefore = eServiceReference(param["sRefBefore"])
		bouquet_ref = eServiceReference(sBouquetRef)
		mutableBouquetList = self.getMutableList(bouquet_ref)
		cnt = 0
		while mutableBouquetList:
			if name is None:
				service_str = '1:832:D:%d:0:0:0:0:0:0:' % cnt
			else:
				service_str = '1:64:%d:0:0:0:0:0:0:0::%s' % (cnt, name)
			ref = eServiceReference(service_str)
			if not mutableBouquetList.addService(ref, sRefBefore):
				mutableBouquetList.flushChanges()
				self.setRoot(sBouquetRef)
				return (True, _("Marker added."))
			cnt += 1
		return (False, _("Internal error!"))

	def renameService(self, param):
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]
		if sRef is None:
			return (False, _("No service given!"))
		sName = None
		if "newName" in param:
			if param["newName"] is not None:
				sName = param["newName"]
		if sName is None:
			return (False, _("No new servicename given!"))
		sBouquetRef = None
		if "sBouquetRef" in param:
			if param["sBouquetRef"] is not None:
				sBouquetRef = param["sBouquetRef"]
		cur_ref = eServiceReference(sRef)
		if cur_ref.flags & eServiceReference.mustDescent:
			# bouquets or alternatives can be renamed with setListName directly
			mutableBouquetList = self.getMutableList(cur_ref)
			if mutableBouquetList:
					mutableBouquetList.setListName(sName)
					mutableBouquetList.flushChanges()
					if sBouquetRef:  # BouquetRef is given when renaming alternatives
						self.setRoot(sBouquetRef)
					else:
						mode = MODE_TV  # mode is given when renaming bouquet
						if "mode" in param:
							if param["mode"] is not None:
								mode = int(param["mode"])
						if mode == MODE_TV:
							bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
						else:
							bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'
						self.setRoot(bouquet_rootstr)
					return (True, _("Bouquet renamed successfully."))
		else:  # service
			# services can not be renamed directly, so delete the current and add it again with new servicename
			sRefBefore = None
			if "sRefBefore" in param:
				if param["sRefBefore"] is not None:
					sRefBefore = param["sRefBefore"]
			new_param = {}
			new_param["sBouquetRef"] = sBouquetRef
			new_param["sRef"] = sRef
			new_param["Name"] = sName
			new_param["sRefBefore"] = sRefBefore
			returnValue = self.removeService(new_param)
			if returnValue[0]:
				returnValue = self.addServiceToBouquet(new_param)
				if returnValue[0]:
					return (True, _("Service renamed successfully."))
		return (False, _("Service can not be renamed."))

	def addServiceToAlternative(self, param):
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, "No bouquet given!")
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]  # service to add to the alternative
		if sRef is None:
			return (False, _("No service given!"))
		sCurrentRef = param["sCurrentRef"]  # alternative service
		if sCurrentRef is None:
			return (False, _("No current service given!"))
		cur_ref = eServiceReference(sCurrentRef)
		# check if  service is already an alternative
		if not (cur_ref.flags & eServiceReference.isGroup):
			# sCurrentRef is not an alternative service yet, so do this and add itself to new alternative liste
			mode = MODE_TV  # init
			if "mode" in param:
				if param["mode"] is not None:
					mode = int(param["mode"])
			mutableBouquetList = self.getMutableList(eServiceReference(sBouquetRef))
			if mutableBouquetList:
				cur_service = ServiceReference(cur_ref)
				name = cur_service.getServiceName()
				if mode == MODE_TV:
					sref = '1:134:1:0:0:0:0:0:0:0:FROM BOUQUET \"alternatives.%s.tv\" ORDER BY bouquet' % (self.buildBouquetID(name, "alternatives.", mode))
				else:
					sref = '1:134:2:0:0:0:0:0:0:0:FROM BOUQUET \"alternatives.%s.radio\" ORDER BY bouquet' % (self.buildBouquetID(name, "alternatives.", mode))
				new_ref = eServiceReference(sref)
				if not mutableBouquetList.addService(new_ref, cur_ref):
					mutableBouquetList.removeService(cur_ref)
					mutableBouquetList.flushChanges()
					eDVBDB.getInstance().reloadBouquets()
					mutableAlternatives = self.getMutableList(new_ref)
					if mutableAlternatives:
						mutableAlternatives.setListName(name)
						if mutableAlternatives.addService(cur_ref):
							print("add", cur_ref.toString(), "to new alternatives failed")
						mutableAlternatives.flushChanges()
						self.setRoot(sBouquetRef)
						sCurrentRef = sref  # currentRef is now an alternative (bouquet)
					else:
						return (False, _("Get mutable list for new created alternative failed!"))
				else:
					return (False, _("Alternative %s created failed.") % name)
			else:
				return (False, _("Bouquetlist is not editable!"))
		# add service to alternative-bouquet
		new_param = {}
		new_param["sBouquetRef"] = sCurrentRef
		new_param["sRef"] = sRef
		returnValue = self.addServiceToBouquet(new_param)
		if returnValue[0]:
			cur_ref = eServiceReference(sCurrentRef)
			cur_service = ServiceReference(cur_ref)
			name = cur_service.getServiceName()
			service_ref = ServiceReference(sRef)
			service_name = service_ref.getServiceName()
			return (True, _("Added %s to alternative service %s.") % (service_name, name))
		else:
			return returnValue

	def removeAlternativeServices(self, param):
		print("[WebComponents.BouquetEditor] removeAlternativeServices with param = ", param)
		sBouquetRef = param["sBouquetRef"]
		if sBouquetRef is None:
			return (False, _("No bouquet given!"))
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]
		if sRef is None:
			return (False, _("No service given!"))
		cur_ref = eServiceReference(sRef)
		# check if service is an alternative
		if cur_ref.flags & eServiceReference.isGroup:
			cur_service = ServiceReference(cur_ref)
			list = cur_service.list()
			first_in_alternative = list and list.getNext()
			if first_in_alternative:
				mutableBouquetList = self.getMutableList(eServiceReference(sBouquetRef))
				if mutableBouquetList is not None:
					if mutableBouquetList.addService(first_in_alternative, cur_service.ref):
						print("couldn't add first alternative service to current root")
				else:
					print("couldn't edit current root")
			else:
				print("remove empty alternative list")
		else:
			return (False, _("Service is not an alternative."))
		new_param = {}
		new_param["sBouquetRef"] = sRef
		new_param["mode"] = None  # of no interest when passing BouquetRefRoot
		new_param["BouquetRefRoot"] = sBouquetRef
		returnValue = self.removeBouquet(new_param)
		if returnValue[0]:
			self.setRoot(sBouquetRef)
			return (True, _("All alternative services deleted."))
		else:
			return returnValue

	def toggleLock(self, param):
		if not config.ParentalControl.configured.value:
			return (False, _("Parent Control is not activated."))
		sRef = None
		if "sRef" in param:
			if param["sRef"] is not None:
				sRef = param["sRef"]
		if sRef is None:
			return (False, _("No service given!"))
		if "setuppinactive" in list(config.ParentalControl.dict().keys()) and config.ParentalControl.setuppinactive.value:
			password = None
			if "password" in param:
				if param["password"] is not None:
					password = param["password"]
			if password is None:
				return (False, _("No Parent Control Setup Pin given!"))
			else:
				if password.isdigit():
					if int(password) != config.ParentalControl.setuppin.value:
						return (False, _("Parent Control Setup Pin is wrong!"))
				else:
					return (False, _("Parent Control Setup Pin is wrong!"))
		cur_ref = eServiceReference(sRef)
		protection = parentalControl.getProtectionLevel(cur_ref.toCompareString())
		if protection:
			parentalControl.unProtectService(cur_ref.toCompareString())
		else:
			parentalControl.protectService(cur_ref.toCompareString())
		if cur_ref.flags & eServiceReference.mustDescent:
			serviceType = "Bouquet"
		else:
			serviceType = "Service"
		if protection:
			if config.ParentalControl.type.value == "blacklist":
				if sRef in parentalControl.blacklist:
					if "SERVICE" in (sRef in parentalControl.blacklist):
						protectionText = _("Service %s is locked.") % self.getName(cur_ref)
					elif "BOUQUET" in (sRef in parentalControl.blacklist):
						protectionText = _("Bouquet %s is locked.") % self.getName(cur_ref)
					else:
						protectionText = _("%s %s is locked.") % (serviceType, self.getName(cur_ref))
			else:
				if hasattr(parentalControl, "whitelist") and sRef in parentalControl.whitelist:
					if "SERVICE" in (sRef in parentalControl.whitelist):
						protectionText = _("Service %s is unlocked.") % self.getName(cur_ref)
					elif "BOUQUET" in (sRef in parentalControl.whitelist):
						protectionText = _("Bouquet %s is unlocked.") % self.getName(cur_ref)
		return (True, protectionText)

	def backupFiles(self, param):
		filename = param
		if not filename:
			filename = self.BACKUP_FILENAME
		invalidCharacters = re_compile(r'[^A-Za-z0-9_. ]+|^\.|\.$|^ | $|^$')
		tarFilename = "%s.tar" % invalidCharacters.sub('_', filename)
		backupFilename = path.join(self.BACKUP_PATH, tarFilename)
		if path.exists(backupFilename):
			remove(backupFilename)
		checkfile = path.join(self.BACKUP_PATH, '.webouquetedit')
		f = open(checkfile, 'w')
		if f:
			files = []
			f.write('created with WebBouquetEditor')
			f.close()
			files.append(checkfile)
			files.append("/etc/enigma2/bouquets.tv")
			files.append("/etc/enigma2/bouquets.radio")
			# files.append("/etc/enigma2/userbouquet.favourites.tv")
			# files.append("/etc/enigma2/userbouquet.favourites.radio")
			files.append("/etc/enigma2/lamedb")
			for xml in ("/etc/tuxbox/cables.xml", "/etc/tuxbox/terrestrial.xml", "/etc/tuxbox/satellites.xml", "/etc/tuxbox/atsc.xml", "/etc/enigma2/lamedb5"):
				if path.exists(xml):
					files.append(xml)
			if config.ParentalControl.configured.value:
				if config.ParentalControl.type.value == "blacklist":
					files.append("/etc/enigma2/blacklist")
				else:
					files.append("/etc/enigma2/whitelist")
			files += self.getPhysicalFilenamesFromServicereference(eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
			files += self.getPhysicalFilenamesFromServicereference(eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
			tarFiles = ""
			for arg in files:
				if not path.exists(arg):
					return (False, _("Error while preparing backup file, %s does not exists.") % arg)
				tarFiles += "%s " % arg
			lines = popen("tar cvf %s %s" % (backupFilename, tarFiles)).readlines()  # nosec
			remove(checkfile)
			return (True, tarFilename)
		else:
			return (False, _("Error while preparing backup file."))

	def getPhysicalFilenamesFromServicereference(self, ref):
		files = []
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(ref)
		servicelist = services and services.getContent("S", True)
		for service in servicelist:
			sref = service
			pos = sref.find('FROM BOUQUET "')
			filename = None
			if pos != -1:
				sref = sref[pos + 14:]
				pos = sref.find('"')
				if pos != -1:
					filename = '/etc/enigma2/' + sref[:pos]  # FIXMEEE !!! HARDCODED /etc/enigma2
					files.append(filename)
					files += self.getPhysicalFilenamesFromServicereference(eServiceReference(service))
		return files

	def restoreFiles(self, param):
		tarFilename = param
		backupFilename = tarFilename  # path.join(self.BACKUP_PATH, tarFilename)
		if path.exists(backupFilename):
			check_tar = False
			lines = popen('tar -tf %s' % backupFilename).readlines()  # nosec
			for line in lines:
				pos = line.find('tmp/.webouquetedit')
				if pos != -1:
					check_tar = True
					break
			if check_tar:
				eDVBDB.getInstance().removeServices()
				files = []
				files += self.getPhysicalFilenamesFromServicereference(eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
				files += self.getPhysicalFilenamesFromServicereference(eServiceReference('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
				for bouquetfiles in files:
					if path.exists(bouquetfiles):
						remove(bouquetfiles)
				lines = popen('tar xvf %s -C / --exclude tmp/.webouquetedit' % backupFilename).readlines()  # nosec
				nimmanager.readTransponders()
				eDVBDB.getInstance().reloadServicelist()
				eDVBDB.getInstance().reloadBouquets()
				infoBarInstance = InfoBar.instance
				if infoBarInstance is not None:
					servicelist = infoBarInstance.servicelist
					root = servicelist.getRoot()
					currentref = servicelist.getCurrentSelection()
					servicelist.setRoot(root)
					servicelist.setCurrentSelection(currentref)
				remove(backupFilename)
				return (True, _("Bouquet-settings were restored successfully"))
			else:
				return (False, _("Error, %s was not created with WebBouquetEditor...") % backupFilename)
		else:
			return (False, _("Error, %s does not exists, restore is not possible...") % backupFilename)

	def getMutableBouquetList(self, mode):
		if mode == MODE_TV:
			self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
		else:
			self.bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'
		return self.getMutableList(eServiceReference(self.bouquet_rootstr))

	def getMutableList(self, ref):
		serviceHandler = eServiceCenter.getInstance()
		return serviceHandler.list(ref).startEdit()

	def setRoot(self, bouquet_rootstr):
		infoBarInstance = InfoBar.instance
		if infoBarInstance is not None:
			servicelist = infoBarInstance.servicelist
			root = servicelist.getRoot()
			if bouquet_rootstr == root.toString():
				currentref = servicelist.getCurrentSelection()
				servicelist.setRoot(root)
				servicelist.setCurrentSelection(currentref)

	def buildBouquetID(self, str, prefix, mode):
		tmp = str.lower()
		name = ''
		for c in tmp:
			if (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9'):
				name += c
			else:
				name += '_'
		# check if file is unique
		suffix = ""
		if mode == MODE_TV:
			suffix = ".tv"
		else:
			suffix = ".radio"
		filename = '/etc/enigma2/' + prefix + name + suffix
		if path.exists(filename):
			i = 1
			while True:
				filename = "/etc/enigma2/%s%s_%d%s" % (prefix, name, i, suffix)
				if path.exists(filename):
					i += 1
				else:
					name = "%s_%d" % (name, i)
					break
		return name

	def getName(self, ref):
		serviceHandler = eServiceCenter.getInstance()
		info = serviceHandler.info(ref)
		if info:
			name = info.getName(ref)
		else:
			name = ""
		return name

	def importBouquet(self, param):
		if config.usage.multibouquet.value:
			import json
			ret = [False, 'json format error']
			mode = MODE_TV
			try:
				bqimport = json.loads(param["json"][0])
				filename = bqimport["filename"]
				_mode = bqimport["mode"]
				overwrite = bqimport["overwrite"]
				lines = bqimport["lines"]
			except (ValueError, KeyError):
				return ret

			if _mode == 1:
				mode = MODE_RADIO

			fullfilename = '/etc/enigma2/' + filename

			if mode == MODE_TV:
				sref = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"%s\" ORDER BY bouquet' % (filename)
			else:
				sref = '1:7:2:0:0:0:0:0:0:0:FROM BOUQUET \"%s\" ORDER BY bouquet' % (filename)

			if not path.exists(fullfilename):
				new_bouquet_ref = eServiceReference(str(sref))
				mutableBouquetList = self.getMutableBouquetList(mode)
				mutableBouquetList.addService(new_bouquet_ref)
				mutableBouquetList.flushChanges()

			if overwrite == 1:
				f = open(fullfilename, 'w')
			else:
				f = open(fullfilename, 'a')
			if f:
				for line in lines:
					f.write(line)
					f.write("\n")
				f.close()
			else:
				return [False, 'error creating bouquet file']

			eDVBDB.getInstance().reloadBouquets()
			return [True, 'bouquet added']
		else:
			return [False, _("Multi-Bouquet is not enabled!")]
