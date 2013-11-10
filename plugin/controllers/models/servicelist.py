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

def reloadLameDB(self):
		self.eDVBDB.reloadServicelist()

def reloadUserBouquets(self):
		self.eDVBDB.reloadBouquets()

def reloadServicesLists(self, request):
	self.eDVBDB = eDVBDB.getInstance()
	res = "False"
	msg = "missing or wrong parameter mode [0=both, 1=lamedb only, 2=userbouqets only"

	if "mode" in request.args:
		mode = unquote(request.args["mode"][0])
	else:
		mode = ""

	if mode == "0":
		reloadLameDB(self)
		reloadUserBouquets(self)
		res = True
		msg = "reloaded both"
	elif mode == "1":
		reloadLameDB(self)
		res = True
		msg = "reloaded lamedb"
	elif mode == "2":
		reloadUserBouquets(self)
		res = True
		msg = "reloaded bouquets"

	return {
		"result" : res,
		"message" : msg
	}

