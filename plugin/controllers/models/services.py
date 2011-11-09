##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from enigma import eServiceCenter, eServiceReference, iServiceInformation, eEPGCache
from time import localtime, strftime

def getServiceInfoString(info, what):
	v = info.getInfo(what)
	if v == -1:
		return "N/A"
	if v == -2:
		return info.getInfoString(what)
	return v

def getCurrentService(session):
	try:
		info = session.nav.getCurrentService().info()
		return {
			"result": True,
			"name": info.getName(),
			"namespace": getServiceInfoString(info, iServiceInformation.sNamespace),
			"aspect": getServiceInfoString(info, iServiceInformation.sAspect),
			"provider": getServiceInfoString(info, iServiceInformation.sProvider),
			"width": getServiceInfoString(info, iServiceInformation.sVideoWidth),
			"height": getServiceInfoString(info, iServiceInformation.sVideoHeight),
			"apid": getServiceInfoString(info, iServiceInformation.sAudioPID),
			"vpid": getServiceInfoString(info, iServiceInformation.sVideoPID),
			"pcrpid": getServiceInfoString(info, iServiceInformation.sPCRPID),
			"pmtpid": getServiceInfoString(info, iServiceInformation.sPMTPID),
			"txtpid": getServiceInfoString(info, iServiceInformation.sTXTPID),
			"tsid": getServiceInfoString(info, iServiceInformation.sTSID),
			"onid": getServiceInfoString(info, iServiceInformation.sONID),
			"sid": getServiceInfoString(info, iServiceInformation.sSID)
		}
	except Exception, e:
		return {
			"result": False,
			"name": "",
			"namespace": "",
			"aspect": 0,
			"provider": "",
			"width": 0,
			"height": 0,
			"apid": 0,
			"vpid": 0,
			"pcrpid": 0,
			"pmtpid": 0,
			"txtpid": 0,
			"tsid": 0,
			"onid": 0,
			"sid": 0
		}

def getBouquets():
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet'%(s_type)))
	bouquets = services and services.getContent("SN", True)
	return { "bouquets": bouquets }
	
def getProviders():
	s_type = service_types_tv
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name'%(s_type)))
	providers = services and services.getContent("SN", True)	
	return { "providers": providers }
	

def getSatellites():
	ret = []
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
#				service_type = _("Providers")
				continue
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
			ret.append({
				"service": service.toString(),
				"name": service.getName()
			})

	return { "satellites": ret }
	
	
def getChannels(idb=""):
	ret = []
	s_type = service_types_tv
	epgcache = eEPGCache.getInstance()
	if idb == "":
		idb = '%s ORDER BY name'%(s_type)

	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference(idb))
	channels = services and services.getContent("SN", True)	
	for channel in channels:
		if not channel[0].startswith("1:64:"):
			chan = {}
			chan['ref'] = channel[0]
			chan['name'] = channel[1]
			nowevent = epgcache.lookupEvent(['TBDCIX', (channel[0], 0, -1)])
			if nowevent[0][0] is not None:
				chan['now_title'] = nowevent[0][0]
				chan['now_begin'] =  strftime("%H:%M", (localtime(nowevent[0][1])))
				chan['now_end'] = strftime("%H:%M",(localtime(nowevent[0][1] + nowevent[0][2])))
				chan['now_left'] = int (((nowevent[0][1] + nowevent[0][2]) - nowevent[0][3]) / 60)
				chan['progress'] = int(((nowevent[0][3] - nowevent[0][1]) * 100 / nowevent[0][2]) )
				chan['now_ev_id'] = nowevent[0][4]
				nextevent = epgcache.lookupEvent(['TBDIX', (channel[0], +1, -1)])
				chan['next_title'] = nextevent[0][0]
				chan['next_begin'] =  strftime("%H:%M", (localtime(nextevent[0][1])))
				chan['next_end'] = strftime("%H:%M",(localtime(nextevent[0][1] + nextevent[0][2])))
				chan['next_duration'] = int(nextevent[0][2] / 60)
				chan['next_ev_id'] = nextevent[0][3]
			ret.append(chan)
			
	return { "channels": ret }
		


