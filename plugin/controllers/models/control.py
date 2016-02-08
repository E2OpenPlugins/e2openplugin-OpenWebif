# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Components.config import config
from enigma import eServiceReference, eActionMap, eServiceCenter
from urllib import unquote
from services import getProtection
from Screens.InfoBar import InfoBar, MoviePlayer

def zapInServiceList(service):
	InfoBar_Instance = InfoBar.instance
	servicelist = InfoBar_Instance.servicelist
	if config.usage.multibouquet.value:
		rootstrings = ('1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet', '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet')
	else:
		rootstrings = ('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195) FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet', '1:7:2:0:0:0:0:0:0:0:(type == 2) || (type == 10) FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet')
	bouquet_found = False
	for bouquet_rootstr in rootstrings:
		servicelist.bouquet_root = eServiceReference(bouquet_rootstr)
		if bouquet_rootstr.find('radio') != -1:
			servicelist.setModeRadio()
		else:
			servicelist.setModeTv()
		bouquets = servicelist.getBouquetList()
		for bouquet in bouquets:
			reflist = [ ]
			reflist = eServiceCenter.getInstance().list(bouquet[1])
			if reflist:
				while True:
					new_service = reflist.getNext()
					if not new_service.valid(): #check if end of list
						break
					if new_service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
						continue
					if new_service == service:
						bouquet_found = True
						break
			if bouquet_found:
				break
		if bouquet_found:
			break
	if bouquet_found:
		bouquet = bouquet[1]
		if servicelist.getRoot() != bouquet:
			servicelist.clearPath()
			if servicelist.bouquet_root != bouquet:
				servicelist.enterPath(servicelist.bouquet_root)
			servicelist.enterPath(bouquet)
	else:
		servicelist.clearPath()
		servicelist.enterPath(service)
	servicelist.setCurrentSelection(service) #select the service in servicelist
	servicelist.zap()

def zapService(session, id, title = ""):
	# Must NOT unquote id here, breaks zap to streams
	service = eServiceReference(id)

	if len(title) > 0:
		service.setName(title)
	else:
		title = id

	# TODO: check standby

	isRecording = service.getPath()
	isRecording = isRecording and isRecording.startswith("/")

	if not isRecording:
		if config.ParentalControl.servicepinactive.value and config.OpenWebif.parentalenabled.value:
			if getProtection(service.toString()) != "0":
				return {
					"result": False,
					"message": "Service '%s' is blocked by parental Control" % title
				}

	# use mediaplayer for recording
	if isRecording:
		if isinstance(session.current_dialog, InfoBar):
			session.open(MoviePlayer, service)
		else:
			session.nav.playService(service)
	else:
		if isinstance(session.current_dialog, MoviePlayer):
			session.current_dialog.lastservice = service
			session.current_dialog.close()
		zapInServiceList(service)

	return {
		"result": True,
		"message": "Active service is now '%s'" % title
	}

def remoteControl(key, type = "", rcu = ""):
	# TODO: do something better here
	if rcu == "standard":
		remotetype = "dreambox remote control (native)"
	elif rcu == "advanced":
		remotetype = "dreambox advanced remote control (native)"
	elif rcu == "keyboard":
		remotetype = "dreambox ir keyboard"
	else:
		if config.misc.rcused.value == 0:
			remotetype = "dreambox advanced remote control (native)"
		else:
			remotetype = "dreambox remote control (native)"
		try:
			from Tools.HardwareInfo import HardwareInfo
			if HardwareInfo().get_device_model() in ("xp1000", "formuler1", "formuler3", "et9000", "et9200", "hd1100", "hd1200"):
				remotetype = "dreambox advanced remote control (native)"
		except:
			print "[OpenWebIf] wrong hw detection"

	amap = eActionMap.getInstance()
	if type == "long":
		amap.keyPressed(remotetype, key, 0)
		amap.keyPressed(remotetype, key, 3)
	elif type == "ascii":
		amap.keyPressed(remotetype, key, 4)
	else:
		amap.keyPressed(remotetype, key, 0)

	amap.keyPressed(remotetype, key, 1)
	return {
		"result": True,
		"message": "RC command '%s' has been issued" % str(key)
	}

def setPowerState(session, state):
	from Screens.Standby import Standby, TryQuitMainloop, inStandby
	state = int(state)

	if state == 0: # Toggle StandBy
		if inStandby == None:
			session.open(Standby)
		else:
			inStandby.Power()
	elif state == 1: # DeepStandBy
		session.open(TryQuitMainloop, state)
	elif state == 2: # Reboot
		session.open(TryQuitMainloop, state)
	elif state == 3: # Restart Enigma
		session.open(TryQuitMainloop, state)
	elif state == 4: # Wakeup
		if inStandby != None:
			inStandby.Power()
	elif state == 5: # Standby
		if inStandby == None:
			session.open(Standby)

	elif state == 6:
		print "HAHA"

	return {
		"result": True,
		"instandby": inStandby != None
	}

def getStandbyState(session):
	from Screens.Standby import inStandby
	return {
		"result": True,
		"instandby": inStandby != None
	}
