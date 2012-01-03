##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from enigma import eServiceReference, iServiceInformation, eServiceCenter
from Components.Sources.Source import Source
from Components.config import config
from ServiceReference import ServiceReference
from Tools.Directories import resolveFilename, SCOPE_HDD
from Tools.FuzzyDate import FuzzyTime
from os import stat as os_stat
from Components.MovieList import MovieList

def getMovieList(self,directory=resolveFilename(SCOPE_HDD)):

	movieliste = []
	bookmarklist = []
	
	self.root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + directory)

	for bookmark in config.movielist.videodirs.value:
		bookmarklist.append(bookmark)

	self.tagfilter = []
	
	self.movielist = MovieList(self.root)
#	self.movielist.reload(root=self.root, filter_tags=self.tagfilter)
	loadLength = True

	for (serviceref, info, begin, unknown) in self.movielist.list:
		if serviceref.flags & eServiceReference.mustDescent:
				continue

		rtime = info.getInfo(serviceref, iServiceInformation.sTimeCreate)

		if rtime > 0:
			t = FuzzyTime(rtime)
			begin_string = t[0] + ", " + t[1]
		else:
			begin_string = "undefined"

		try:
			Len = info.getLength(serviceref)
		except:
			Len = None

		if Len > 0:
			Len = "%d:%02d" % (Len / 60, Len % 60)
		else:
			Len = "?:??"
		
		sourceERef = info.getInfoString(serviceref, iServiceInformation.sServiceref)
		sourceRef = ServiceReference(sourceERef)

		event = info.getEvent(serviceref)
		ext = event and event.getExtendedDescription() or ""

		filename = '/'.join(serviceref.toString().split("/")[1:])
		servicename = ServiceReference(serviceref).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
		movie = {}
		filename = '/'+filename
		movie['filename'] = filename
		movie['eventname'] = servicename
		movie['description'] = info.getInfoString(serviceref, iServiceInformation.sDescription)
		movie['begintime'] = begin_string
		movie['serviceref'] = serviceref.toString()
		movie['length'] = Len
		movie['tags'] = info.getInfoString(serviceref, iServiceInformation.sTags)
		movie['filesize'] = os_stat(filename)[6]
		movie['fullname'] = serviceref.toString()
		movie['DescriptionExtended'] = ext
		movie['servicename'] = sourceRef.getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
		movie['recordingtime'] = rtime
		
		movieliste.append(movie)
		
	
	return { "movies": movieliste, "bookmarks": bookmarklist, "directory": directory }

