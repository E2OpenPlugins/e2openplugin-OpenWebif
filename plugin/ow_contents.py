##############################################################################
#                         <<< ow_contents >>>                           
#                                                                            
#                        2011 E2OpenPlugins          
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################

from Components.About import about
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.Network import iNetwork
from Tools.DreamboxHardware import getFPVersion
from Tools.Directories import fileExists
from os import popen

def format_ip(ip):
	if len(ip) != 4:
		return None
	return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])
	
def get_Info_content():
	owinfo = {}

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

	owinfo['brand'] = brand
	owinfo['model'] = model

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
 		chipset = f.readline().strip()
 		f.close()
		
	owinfo['chipset'] = chipset
	
	f = open("/proc/meminfo",'r')
 	parts = f.readline().split(':')
	owinfo['mem1'] = parts[1].strip()
	parts = f.readline().split(':')
	owinfo['mem2'] = parts[1].strip()
	f.close()
		
	f = popen("uptime")
	parts = f.readline().split(',')
	owinfo['uptime'] = parts[0].strip()
	f.close()
		
	if fileExists("/etc/bhversion"):
		f = open("/etc/bhversion",'r')
		imagever = f.readline().strip()
		f.close()
	else:
		imagever = about.getImageVersionString()
		
	owinfo['imagever'] = imagever
	owinfo['enigmaver'] = about.getEnigmaVersionString()
	owinfo['kernelver'] = about.getKernelVersionString()
	
	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = 0

	owinfo['fp_version'] = str(fp_version)
	
	owinfo['tuners'] = []
	for i in range(0, nimmanager.getSlotCount()):
		owinfo['tuners'].append({
			"name": nimmanager.getNim(i).getSlotName(),
			"type": nimmanager.getNimName(i) + " (" + nimmanager.getNim(i).getFriendlyType() + ")"
		})

	owinfo['ifaces'] = []
	ifaces = iNetwork.getConfiguredAdapters()
	for iface in ifaces:
		owinfo['ifaces'].append({
			"name": iNetwork.getAdapterName(iface),
			"mac": iNetwork.getAdapterAttribute(iface, "mac"),
			"dhcp": iNetwork.getAdapterAttribute(iface, "dhcp"),
			"ip": format_ip(iNetwork.getAdapterAttribute(iface, "ip")),
			"mask": format_ip(iNetwork.getAdapterAttribute(iface, "netmask")),
			"gw": format_ip(iNetwork.getAdapterAttribute(iface, "gateway"))
		})
			
	owinfo['hdd'] = []
	for hdd in harddiskmanager.hdd:
		if hdd.free() <= 1024:
			free = "%i MB" % (hdd.free())
		else:
			free = float(hdd.free()) / float(1024)
			free = "%.3f GB" % free
		owinfo['hdd'].append({
			"model": hdd.model(),
			"capacity": hdd.capacity(),
			"free": free
		})
	return owinfo
