# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from urllib import unquote
from enigma import eDVBDB
from Components.NimManager import nimmanager
import Components.ParentalControl

def reloadLameDB(self):
	self.eDVBDB.reloadServicelist()

def reloadUserBouquets(self):
	self.eDVBDB.reloadBouquets()

def reloadTransponders(self):
	nimmanager.readTransponders()

def reloadParentalControl(self):
	Components.ParentalControl.parentalControl.open()

def clearAllServices(self):
	satList = []
	satellites = {}
	transponders = {}
	self.eDVBDB.readSatellites(satList, satellites, transponders)
	positions = [x[0] for x in satList] 
	for pos in positions: # sat
		self.eDVBDB.removeServices(-1, -1, -1, pos)
	self.eDVBDB.removeServices(0xFFFF0000 - 0x100000000) # cable
	self.eDVBDB.removeServices(0xEEEE0000 - 0x100000000) # terrestrial

def reloadServicesLists(self, request):
	self.eDVBDB = eDVBDB.getInstance()
	res = "False"
	msg = "missing or wrong parameter mode [0=both, 1=lamedb only, 2=userbouqets only, 3=transponders, 4=parentalcontrol white-/blacklist]"

	if "mode" in request.args:
		mode = unquote(request.args["mode"][0])
	else:
		mode = ""

	if mode == "0":
		clearAllServices(self)
		reloadLameDB(self)
		reloadUserBouquets(self)
		res = True
		msg = "reloaded both"
	elif mode == "1":
		clearAllServices(self)
		reloadLameDB(self)
		res = True
		msg = "reloaded lamedb"
	elif mode == "2":
		reloadUserBouquets(self)
		res = True
		msg = "reloaded bouquets"
	elif mode == "3":
		reloadTransponders(self)
		res = True
		msg = "reloaded transponders"
	elif mode == "4":
		reloadParentalControl(self)
		res = True
		msg = "reloaded parentalcontrol white-/blacklist"

	return {
		"result" : res,
		"message" : msg
	}
