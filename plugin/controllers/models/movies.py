##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from time import localtime, strftime
import os
from Components.config import config

def getMovieList(directory="/hdd/movie"):
	movielist = []
	if os.path.exists(directory):
		for filename in os.listdir(directory):
			filename = filename.decode("utf-8", "ignore").encode("utf-8")
			if os.path.isfile(directory + "/" + filename) and filename.endswith(('ts', 'vob', 'mpg', 'mpeg', 'avi', 'mkv', 'dat', 'iso', 'mp4', 'divx', 'mov', 'm2ts', 'm4v', 'f4v', 'flv')) and not filename.endswith(('cuts')):
				movie = {}
				movie['filename'] = filename
				movie['directory'] = directory
				movie['fullname'] = directory + "/" + filename
				movie['eventname'] = ""
				movie['description'] = ""
				movie['begintime'] = ""
				movie['serviceref'] = ""
				
				# Get Event Info from meta file
				if os.path.exists(directory + "/" + filename + ".meta"):
					readmetafile = open(directory + "/" + filename + ".meta", "r")
					movie['serviceref'] = readmetafile.readline()[0:-1]
					movie['eventname'] = readmetafile.readline()[0:-1]
					movie['description'] = readmetafile.readline()[0:-1]
					movie['begintime'] = strftime("%A, %d.%m.%Y %H:%M", (localtime(float(readmetafile.readline()[0:-1]))))
					readmetafile.close()
						
				movielist.append(movie)
	
	# Get Bookmarks
	bookmarklist = []
	for bookmark in config.movielist.videodirs.value:
		bookmarklist.append(bookmark)
			
	return { "movies": movielist, "bookmarks": bookmarklist, "directory": directory }
