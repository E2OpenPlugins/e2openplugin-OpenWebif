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
from Tools.DreamboxHardware import getFPVersion
from Tools.Directories import fileExists
from os import popen
from ow_tpl import hddinfo_Tpl, tunersinfo_Tpl


def get_Info_content():
# Todo: implement Etxxx brand and model (i have not)
# Todo: add network infos

	owinfo = {}

	brand = "Dream Multimedia"
	model = "unknown"
	chipset = "unknown"
	
	if fileExists("/proc/stb/info/vumodel"):
		brand = "Vuplus"
		f = open("/proc/stb/info/vumodel",'r')
 		model = "Vu+ " + f.readline().strip()
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
	
	owinfo['tuners'] = ""
	for nim in nimmanager.nimList():
		parts = nim.split(':')
		owinfo['tuners'] += tunersinfo_Tpl(parts[0], parts[1])
	
	owinfo['hdd'] = ""
	for hdd in harddiskmanager.hdd:
		model = "%s" % (hdd.model())
		capacity = "%s" % (hdd.capacity())
		if hdd.free() <= 1024:
			free = "%i MB" % (hdd.free())
		else:
			free = float(hdd.free()) / float(1024)
			free = "%.3f GB" % free
		owinfo['hdd'] +=  hddinfo_Tpl(model, capacity, free)
		
	
	return owinfo
