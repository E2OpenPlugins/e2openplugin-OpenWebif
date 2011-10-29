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
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from Components.About import about
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Tools.DreamboxHardware import getFPVersion
from Tools.Directories import fileExists
from os import popen
from enigma import eServiceCenter, eServiceReference, iServiceInformation


# FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
# FROM BOUQUET "bouquets.radio" ORDER BY bouquet'
# FROM PROVIDERS ORDER BY name'
# FROM SATELLITES ORDER BY satellitePosition'
# ORDER BY name'

def getServiceInfoString(info, what):
	v = info.getInfo(what)
	if v == -1:
		return "N/A"
	if v == -2:
		return info.getInfoString(what)
	return v


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

def get_Ajax_current(session):
	info = session.nav.getCurrentService().info()
	name = info.getName()
	provider = getServiceInfoString(info, iServiceInformation.sProvider)
	width = getServiceInfoString(info, iServiceInformation.sVideoWidth)
	height = getServiceInfoString(info, iServiceInformation.sVideoHeight)
	return """
This tab is work in progress:<br />
<br />
Current service: %s <br />
Provider: %s <br />
Resolution: %s x %s
<br /><br /><br />
""" % (name, provider, width, height)

def get_Ajax_bouquets():
	out = ""
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(s_type)))
	bouquets = services and services.getContent("SN", True)
		
	for bouquet in bouquets:
		out += bouquet[1] + "<br />"
	
	return out

def get_Ajax_providers():
	out = ""
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name'%(s_type)))
	providers = services and services.getContent("SN", True)
		
	for provider in providers:
		out += provider[1] + "<br />"
	
	return out

def get_Ajax_satellites():
# <a href="box_info.html">qui</a>
	out = ""
	s_type = service_types_tv
	refstr = '%s FROM SATELLITES ORDER BY satellitePosition'%(s_type)
	ref = eServiceReference(refstr)
	serviceHandler = eServiceCenter.getInstance()
	servicelist = serviceHandler.list(ref)
	if not servicelist is None:
		while True:
			service = servicelist.getNext()
			if not service.valid():
				break
			unsigned_orbpos = service.getUnsignedData(4) >> 16
			orbpos = service.getData(4) >> 16
			if orbpos < 0:
				orbpos += 3600
			if service.getPath().find("FROM PROVIDER") != -1:
				service_type = _("Providers")
			elif service.getPath().find("flags == %d" %(FLAG_SERVICE_NEW_FOUND)) != -1:
				service_type = _("New")
			else:
				service_type = _("Services")
			try:
				service_name = str(nimmanager.getSatDescription(orbpos))
			except:
				if unsigned_orbpos == 0xFFFF: #Cable
					service_name = _("Cable")
				elif unsigned_orbpos == 0xEEEE: #Terrestrial
					service_name = _("Terrestrial")
				else:
					if orbpos > 1800: # west
						orbpos = 3600 - orbpos
						h = _("W")
					else:
						h = _("E")
					service_name = ("%d.%d" + h) % (orbpos / 10, orbpos % 10)
			service.setName("%s - %s" % (service_name, service_type))
			s = service.toString()
			out += service.getName() + "<br />"
	return out	
		



def get_Ajax_all():
	out = ""
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s ORDER BY name'%(s_type)))
	channels = services and services.getContent("SN", True)			
	for channel in channels:
		if not channel[0].startswith("1:64:"):
			out += channel[1] + "<br />"
	
	return out


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
