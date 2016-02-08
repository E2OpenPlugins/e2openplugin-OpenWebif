# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from enigma import eServiceReference, getBestPlayableServiceReference
from ServiceReference import ServiceReference
from info import getInfo
from urllib import unquote, quote
import os
import re
from Components.config import config

def getStream(session, request, m3ufile):
	if "ref" in request.args:
		sRef=unquote(unquote(request.args["ref"][0]).decode('utf-8', 'ignore')).encode('utf-8')
	else:
		sRef = ""

	currentServiceRef = None
	if m3ufile == "streamcurrent.m3u":
		currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()
		sRef = currentServiceRef.toString() 

	if sRef.startswith("1:134:"):
		if currentServiceRef is None:
			currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()
		if currentServiceRef is None:
			currentServiceRef = eServiceReference()
		ref = getBestPlayableServiceReference(eServiceReference(sRef), currentServiceRef)
		if ref is None:
			sRef = ""
		else:
			sRef = ref.toString()

	name = "stream"
	# #EXTINF:-1,%s\n adding back to show service name in programs like VLC
	progopt = ''
	if "name" in request.args:
		name = request.args["name"][0]
		if config.OpenWebif.service_name_for_stream.value:
			progopt="#EXTINF:-1,%s\n" % name
	
	portNumber = config.OpenWebif.streamport.value
	info = getInfo()
	model = info["model"]
	machinebuild = info["machinebuild"]
	transcoder_port = None
	args = ""
	if model in ("Solo4K", "Solo²", "Duo²", "Solo SE", "Quad", "Quad Plus") or machinebuild in ('dags3', 'dags4'):
		try:
			transcoder_port = int(config.plugins.transcodingsetup.port.value)
		except StandardError:
			#Transcoding Plugin is not installed or your STB does not support transcoding
			transcoder_port = None
		if "device" in request.args :
			if request.args["device"][0] == "phone" :
				portNumber = transcoder_port
		if "port" in request.args:
			portNumber = request.args["port"][0]
			
	# INI use dynamic encoder allocation, and each stream can have diffrent parameters 
	if machinebuild in ('inihdp', 'hd2400', 'et10000'):
		transcoder_port = 8001
		if "device" in request.args :
			if request.args["device"][0] == "phone" :
				bitrate = config.plugins.transcodingsetup.bitrate.value
				resolution = config.plugins.transcodingsetup.resolution.value
				(width, height) = tuple(resolution.split('x'))
				framrate = config.plugins.transcodingsetup.framerate.value
				aspectratio = config.plugins.transcodingsetup.aspectratio.value
				interlaced = config.plugins.transcodingsetup.interlaced.value
				args = "?bitrate=%s?width=%s?height=%s?aspectratio=%s?interlaced=%s" % (bitrate, width, height, aspectratio, interlaced)
	if machinebuild in ('ew7356'):
		transcoder_port = 8001
		if "device" in request.args :
			if request.args["device"][0] == "phone" :
				bitrate = config.plugins.transcodingsetup.bitrate.value
				framrate = config.plugins.transcodingsetup.framerate.value
				args = "?bitrate=%s" % (bitrate)

	# When you use EXTVLCOPT:program in a transcoded stream, VLC does not play stream
	if config.OpenWebif.service_name_for_stream.value and sRef != '' and portNumber != transcoder_port:
		progopt="%s#EXTVLCOPT:program=%d\n" % (progopt, int(sRef.split(':')[3],16))

	response = "#EXTM3U \n#EXTVLCOPT--http-reconnect=true \n%shttp://%s:%s/%s%s\n" % (progopt,request.getRequestHostname(), portNumber, sRef, args)
	request.setHeader('Content-Type', 'application/text')
	return response

def getTS(self, request):
	if "file" in request.args:
		filename = unquote(request.args["file"][0]).decode('utf-8', 'ignore').encode('utf-8')
		if not os.path.exists(filename):
			return "File '%s' not found" % (filename)

#	ServiceReference is not part of filename so look in the '.ts.meta' file
		sRef = ""
		progopt = ''

		if os.path.exists(filename + '.meta'):
			metafile = open(filename + '.meta', "r")
			name = ''
			seconds = -1 				# unknown duration default
			line = metafile.readline()	# service ref
			if line:
				sRef = eServiceReference(line.strip()).toString()
			line2 = metafile.readline()	# name
			if line2:
				name = line2.strip()
			line3 = metafile.readline()	# description
			line4 = metafile.readline() # recording time
			line5 = metafile.readline() # tags
			line6 = metafile.readline() # length

			if line6:
				seconds = float(line6.strip()) / 90000 # In seconds

			if config.OpenWebif.service_name_for_stream.value:
				progopt="%s#EXTINF:%d,%s\n" % (progopt, seconds, name)

			metafile.close()

		portNumber = None
		proto = 'http'
		info = getInfo()
		model = info["model"]
		machinebuild = info["machinebuild"]
		transcoder_port = None
		args = ""
		if model in ("Solo4K", "Solo²", "Duo²", "Solo SE", "Quad", "Quad Plus"):
			try:
				transcoder_port = int(config.plugins.transcodingsetup.port.value)
			except StandardError:
				#Transcoding Plugin is not installed or your STB does not support transcoding
				transcoder_port = None
			if "device" in request.args :
				if request.args["device"][0] == "phone" :
					portNumber = transcoder_port
		if "port" in request.args:
			portNumber = request.args["port"][0]
			
		# INI use dynamic encoder allocation, and each stream can have diffrent parameters
		if machinebuild in ('inihdp', 'hd2400', 'et10000'):
			if "device" in request.args :
				if request.args["device"][0] == "phone" :
					portNumber = config.OpenWebif.streamport.value
					bitrate = config.plugins.transcodingsetup.bitrate.value
					resolution = config.plugins.transcodingsetup.resolution.value
					(width, height) = tuple(resolution.split('x'))
					framrate = config.plugins.transcodingsetup.framerate.value
					aspectratio = config.plugins.transcodingsetup.aspectratio.value
					interlaced = config.plugins.transcodingsetup.interlaced.value
					args = "?bitrate=%s?width=%s?height=%s?aspectratio=%s?interlaced=%s" % (bitrate, width, height, aspectratio, interlaced)
		elif machinebuild in ('ew7356'):
			if "device" in request.args :
				if request.args["device"][0] == "phone" :
					portNumber = config.OpenWebif.streamport.value
					bitrate = config.plugins.transcodingsetup.bitrate.value
					framrate = config.plugins.transcodingsetup.framerate.value
					args = "?bitrate=%s" % (bitrate)

		# When you use EXTVLCOPT:program in a transcoded stream, VLC does not play stream
		if config.OpenWebif.service_name_for_stream.value and sRef != '' and portNumber != transcoder_port:
			progopt="%s#EXTVLCOPT:program=%d\n" % (progopt, int(sRef.split(':')[3],16))

		if portNumber is None:
			portNumber = config.OpenWebif.port.value
			if request.isSecure():
				portNumber = config.OpenWebif.https_port.value
				proto = 'https'
			ourhost = request.getHeader('host')
			m = re.match('.+\:(\d+)$', ourhost)
			if m is not None:
				portNumber = m.group(1)

		response = "#EXTM3U \n#EXTVLCOPT--http-reconnect=true \n%s%s://%s:%s/file?file=%s%s\n" % ((progopt,proto, request.getRequestHostname(), portNumber, quote(filename), args))
		request.setHeader('Content-Type', 'application/text')
		return response
	else:
		return "Missing file parameter"

def getStreamSubservices(session, request):
	services = []
	currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()

	# TODO : this will only work if sref = current channel
	# the DMM webif can also show subservices for other channels like the current
	# ideas are welcome

	if "sRef" in request.args:
		currentServiceRef = eServiceReference(request.args["sRef"][0])

	if currentServiceRef is not None:
		currentService = session.nav.getCurrentService()
		subservices = currentService.subServices()

		services.append({
			"servicereference": currentServiceRef.toString(),
			"servicename": ServiceReference(currentServiceRef).getServiceName()
			}) 
		if subservices and subservices.getNumberOfSubservices() != 0:
			n = subservices and subservices.getNumberOfSubservices()  
			z = 0
			while z < n:
				sub = subservices.getSubservice(z)
				services.append({
					"servicereference": sub.toString(),
					"servicename": sub.getName()
				}) 
				z += 1
	else:
		services.append =({
			"servicereference": "N/A",
			"servicename": "N/A"
		})

	return { "services": services }
