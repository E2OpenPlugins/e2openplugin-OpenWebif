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

def get_Ajax_Tabs():
	return """
<div id="content_main">
<div id="tabs">
	<ul>
		<li><a href="ajax/current.html">Current</a></li>
		<li><a href="ajax/bouquets.html">Bouquets</a></li>
		<li><a href="ajax/providers.html">Providers</a></li>
		<li><a href="ajax/satellites.html">Satellites</a></li>
		<li><a href="ajax/all.html">All</a></li>
	</ul>
</div>
</div>
"""

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
		owinfo['tuners'] += "<tr><td class='infoleft'>" + parts[0] + ":</td><td class='inforight'>" + parts[1] + "</td></tr>"
	
	owinfo['hdd'] = ""
	for hdd in harddiskmanager.hdd:
		model = "%s" % (hdd.model())
		capacity = "%s" % (hdd.capacity())
		if hdd.free() <= 1024:
			free = "%i MB" % (hdd.free())
		else:
			free = float(hdd.free()) / float(1024)
			free = "%.3f GB" % free
		owinfo['hdd'] += "<tr><td width='100%'><table cellspacing='0' class='infomain' ><tr><th colspan='2' class='infoHeader'>Hard disk model: " 
		owinfo['hdd'] += model +"</th></tr><tr><td class='infoleft'>Capacity:</td><td class='inforight'>"
		owinfo['hdd'] += capacity + "</td></tr><tr><td class='infoleft'>Free:</td><td class='inforight'>" 
		owinfo['hdd'] += free + "</td></tr></table></td></tr>"
	
	return owinfo
