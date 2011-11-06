##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Components.About import about
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.Network import iNetwork
from Tools.DreamboxHardware import getFPVersion
from Tools.Directories import fileExists

import os
import sys

def formatIp(ip):
	if len(ip) != 4:
		return None
	return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])

def getBasePath():
	path = os.path.dirname(sys.modules[__name__].__file__)
	chunks = path.split("/")
	chunks.pop()
	chunks.pop()
	return "/".join(chunks)
	
def getPublicPath(file = ""):
	return getBasePath() + "/public/" + file
	
def getViewsPath(file = ""):
	return getBasePath() + "/controllers/views/" + file
	
def getInfo():
	# TODO: get webif versione somewhere!
	info = {}

	brand = "Dream Multimedia"
	model = "unknown"
	chipset = "unknown"
	
	if fileExists("/proc/stb/info/vumodel"):
		brand = "Vuplus"
		f = open("/proc/stb/info/vumodel",'r')
 		model = f.readline().strip()
 		f.close()
	elif fileExists("/proc/stb/info/boxtype"):
		brand = "Clarke-Xtrend"
		f = open("/proc/stb/info/boxtype",'r')
 		model = f.readline().strip()
 		f.close()
	else:
		f = open("/proc/stb/info/model",'r')
 		model = f.readline().strip()
 		f.close()

	info['brand'] = brand
	info['model'] = model

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
 		chipset = f.readline().strip()
 		f.close()
		
	info['chipset'] = chipset
	
	f = open("/proc/meminfo",'r')
 	parts = f.readline().split(':')
	info['mem1'] = parts[1].strip()
	parts = f.readline().split(':')
	info['mem2'] = parts[1].strip()
	f.close()
		
	f = os.popen("uptime")
	parts = f.readline().split(',')
	info['uptime'] = parts[0].strip()
	f.close()
		
	if fileExists("/etc/bhversion"):
		f = open("/etc/bhversion",'r')
		imagever = f.readline().strip()
		f.close()
	else:
		imagever = about.getImageVersionString()
		
	info["webifver"] = "0.0.0"
	info['imagever'] = imagever
	info['enigmaver'] = about.getEnigmaVersionString()
	info['kernelver'] = about.getKernelVersionString()
	
	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = 0

	info['fp_version'] = str(fp_version)
	
	info['tuners'] = []
	for i in range(0, nimmanager.getSlotCount()):
		info['tuners'].append({
			"name": nimmanager.getNim(i).getSlotName(),
			"type": nimmanager.getNimName(i) + " (" + nimmanager.getNim(i).getFriendlyType() + ")"
		})

	info['ifaces'] = []
	ifaces = iNetwork.getConfiguredAdapters()
	for iface in ifaces:
		info['ifaces'].append({
			"name": iNetwork.getAdapterName(iface),
			"mac": iNetwork.getAdapterAttribute(iface, "mac"),
			"dhcp": iNetwork.getAdapterAttribute(iface, "dhcp"),
			"ip": formatIp(iNetwork.getAdapterAttribute(iface, "ip")),
			"mask": formatIp(iNetwork.getAdapterAttribute(iface, "netmask")),
			"gw": formatIp(iNetwork.getAdapterAttribute(iface, "gateway"))
		})
			
	info['hdd'] = []
	for hdd in harddiskmanager.hdd:
		if hdd.free() <= 1024:
			free = "%i MB" % (hdd.free())
		else:
			free = float(hdd.free()) / float(1024)
			free = "%.3f GB" % free
		info['hdd'].append({
			"model": hdd.model(),
			"capacity": hdd.capacity(),
			"free": free
		})
	return info
