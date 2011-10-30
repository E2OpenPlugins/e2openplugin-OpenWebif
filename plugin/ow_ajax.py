##############################################################################
#                         <<< ow_ajax >>>                           
#                                                                            
#                        2011 E2OpenPlugins          
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from enigma import eServiceCenter, eServiceReference, iServiceInformation
from ow_tpl import current_tab_Tpl, bouquet_link_Tpl, bouquet_chan_Tpl, bouq_chan_link_Tpl, provider_link_Tpl, \
provider_chan_Tpl, prov_chan_link_Tpl


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



def get_Ajax_current(session):
	info = session.nav.getCurrentService().info()
	name = info.getName()
	provider = getServiceInfoString(info, iServiceInformation.sProvider)
	width = getServiceInfoString(info, iServiceInformation.sVideoWidth)
	height = getServiceInfoString(info, iServiceInformation.sVideoHeight)
	return current_tab_Tpl(name, provider, width, height)


def get_Ajax_bouquets():
	out = ""
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(s_type)))
	bouquets = services and services.getContent("SN", True)
	count = 0	
	for bouquet in bouquets:
		out += bouquet_link_Tpl(str(count), bouquet[1])
		count += 1
	return out

def get_Ajax_bouquets_chan(idb):
	out = bouquet_chan_Tpl()
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(s_type)))
	bouquets = services and services.getContent("SN", True)
	bouquet = bouquets[int(idb)]
	services = serviceHandler.list(eServiceReference(bouquet[0]))
	channels = services and services.getContent("SN", True)	
	for channel in channels:
		out += bouq_chan_link_Tpl(channel[1])
	return out

def get_Ajax_providers():
	out = ""
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name'%(s_type)))
	providers = services and services.getContent("SN", True)
	count = 0	
	for provider in providers:
		out += provider_link_Tpl(str(count), provider[1])
		count += 1
	
	return out

def get_Ajax_providers_chan(idb):
	out = provider_chan_Tpl()
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name'%(s_type)))
	providers = services and services.getContent("SN", True)
	provider = providers[int(idb)]
	services = serviceHandler.list(eServiceReference(provider[0]))
	channels = services and services.getContent("SN", True)	
	for channel in channels:
		out += prov_chan_link_Tpl(channel[1])
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
		
