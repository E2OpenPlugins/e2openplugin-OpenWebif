# -*- coding: utf-8 -*-

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
from ServiceReference import ServiceReference
from Tools.FuzzyDate import FuzzyTime
from os import stat as os_stat, listdir
from os.path import islink, isdir, join, exists, split as os_path_split, realpath, abspath
from Components.config import config
from Components.MovieList import MovieList
from Tools.Directories import fileExists
from time import strftime, localtime
from Screens import MovieSelection

MOVIETAGFILE = "/etc/enigma2/movietags"

def getPosition(cutfile, movie_len):
	cut_list = []
	if movie_len is not None and fileExists(cutfile):
		try:
			import struct
			with open(cutfile) as f:
				data = f.read()
			while len(data) > 0:
				packedCue = data[:12]
				data = data[12:]
				cue = struct.unpack('>QI', packedCue)
				cut_list.append(cue)
		except Exception, ex:
			return 0
	else:
		return 0
	last_end_point = None
	if len(cut_list):
		for (pts, what) in cut_list:
			if what == 3:
				last_end_point = pts/90000 # in seconds
	else:
		return 0
	try:
		movie_len = int(movie_len)
	except ValueError:
		return 0
	if movie_len > 0 and last_end_point is not None:
		play_progress = (last_end_point*100) / movie_len
		if play_progress > 100:
			play_progress = 100
	else:
		play_progress = 0
	return play_progress

def checkParentalProtection(directory):
	if hasattr(config.ParentalControl, 'moviepinactive'):
		if config.ParentalControl.moviepinactive.value:
			directory = os_path_split(directory)[0]
			directory = realpath(directory)
			directory = abspath(directory)
			if directory[-1] != "/":
				directory += "/"
			is_protected = config.movielist.moviedirs_config.getConfigValue(directory, "protect")
			if is_protected is not None and is_protected == 1:
				return True
	return False

def getMovieList(directory=None, tag=None, rargs=None, locations=None):
	movieliste = []

	if directory is None:
		directory = MovieSelection.defaultMoviePath()
	if not directory:
		directory = "/media/"
	elif directory[-1] != "/":
		directory += "/"

	root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + directory)

	bookmarklist=[x for x in listdir(directory) if (x[0] != '.' and (isdir(join(directory, x)) or (islink(join(directory, x)) and exists(join(directory, x)))))]
	bookmarklist.sort()

	folders = []
	folders.append(root)
	if rargs and "recursive" in rargs.keys():
		for f in bookmarklist:
			if f[-1] != "/":
				f += "/"
			ff = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + directory + f)
			folders.append(ff)

	# get all locations
	if locations is not None:
		folders = []
		for f in locations:
			if f[-1] != "/":
				f += "/"
			ff = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + f)
			folders.append(ff)

	if config.OpenWebif.parentalenabled.value:
		dir_is_protected = checkParentalProtection(directory)
	else:
		dir_is_protected = False

	if not dir_is_protected:
		for root in folders:
			movielist = MovieList(None)
			movielist.load(root, None)

			if tag != None:
				movielist.reload(root=root, filter_tags=[tag])
			#??? loadLength = True

			for (serviceref, info, begin, unknown) in movielist.list:
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

				filename = '/'.join(serviceref.toString().split("/")[1:])
				filename = '/'+filename
				pos = getPosition(filename + '.cuts', Len)

				if Len > 0:
					Len = "%d:%02d" % (Len / 60, Len % 60)
				else:
					Len = "?:??"

				sourceERef = info.getInfoString(serviceref, iServiceInformation.sServiceref)
				sourceRef = ServiceReference(sourceERef)
				event = info.getEvent(serviceref)
				ext = event and event.getExtendedDescription() or ""

				servicename = ServiceReference(serviceref).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
				movie = {}
				movie['filename'] = filename
				movie['filename_stripped'] = filename.split("/")[-1]
				movie['eventname'] = servicename
				movie['description'] = info.getInfoString(serviceref, iServiceInformation.sDescription)
				movie['begintime'] = begin_string
				movie['serviceref'] = serviceref.toString()
				movie['length'] = Len
				movie['tags'] = info.getInfoString(serviceref, iServiceInformation.sTags)
				filename = filename.replace("'","\'").replace("%","\%")
				try:
					movie['filesize'] = os_stat(filename).st_size
				except:
					movie['filesize'] = 0
				movie['fullname'] = serviceref.toString()
				movie['descriptionExtended'] = ext
				movie['servicename'] = sourceRef.getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
				movie['recordingtime'] = rtime
				movie['lastseen'] = pos
				movieliste.append(movie)

	if locations == None:
		ml = { "movies": movieliste, "bookmarks": bookmarklist, "directory": directory }
	else:
		ml = { "movies": movieliste, "locations": locations}
	return ml

def getAllMovies():
	locations = config.movielist.videodirs.value[:] or []
	return getMovieList(None, None, None, locations)

def removeMovie(session, sRef):
	service = ServiceReference(sRef)
	result = False
	deleted = False

	if service is not None:
		serviceHandler = eServiceCenter.getInstance()
		offline = serviceHandler.offlineOperations(service.ref)
		info = serviceHandler.info(service.ref)
		name = info and info.getName(service.ref) or "this recording"

	if offline is not None:
		if hasattr(config.usage, 'movielist_trashcan'):
			fullpath = service.ref.getPath()
			srcpath = '/'.join(fullpath.split('/')[:-1]) + '/'
			# TODO: check trash
			# TODO: check enable trash default value
			# TODO: remove jpg
			if '.Trash' not in fullpath and config.usage.movielist_trashcan.value:
				try:
					import Tools.Trashcan
					trash = Tools.Trashcan.createTrashFolder(srcpath)
					if trash:
						res = _moveMovie(session, sRef, destpath=trash)
						result = res['result']
						deleted = result
				except ImportError:
					pass
		if not deleted:
			if not offline.deleteFromDisk(0):
				result = True

	if result == False:
		return {
			"result": False,
			"message": "Could not delete Movie '%s'" % name
			}
	else:
		return {
			"result": True,
			"message": "The movie '%s' has been deleted successfully" % name
			}

def _moveMovie(session, sRef, destpath=None, newname=None):
	import os
	service = ServiceReference(sRef)
	result = True
	errText = 'unknown Error'

	if destpath is not None and not destpath[-1] == '/':
		destpath = destpath + '/'

	if service is not None:
		serviceHandler = eServiceCenter.getInstance()
		info = serviceHandler.info(service.ref)
		name = info and info.getName(service.ref) or "this recording"
		fullpath = service.ref.getPath()
		srcpath = '/'.join(fullpath.split('/')[:-1]) + '/'
		fullfilename = fullpath.split('/')[-1]
		fileName, fileExt = os.path.splitext(fullfilename)
		if newname is not None:
			newfullpath = srcpath + newname + fileExt

		# TODO: check splitted recording
		def domove():
			exists = os.path.exists
			move = os.rename
			errorlist = []
			if fileExt == '.ts':
				suffixes = ".ts.meta", ".ts.cuts", ".ts.ap", ".ts.sc", ".eit", ".ts", ".jpg"
			else:
				suffixes = "%s.ts.meta" % fileExt, "%s.cuts" % fileExt, fileExt, '.jpg', '.eit'

			for suffix in suffixes:
				src = srcpath + fileName + suffix
				if exists(src):
					try:
						if newname is not None:
							# rename title in meta file
							if suffix == '.ts.meta':
								# todo error handling
								lines = []
								with open(src, "r") as fin:
									for line in fin:
										lines.append(line)
								lines[1]=newname+'\n'
								lines[4]='\n'
								with open(srcpath + newname + suffix, 'w') as fout:
									fout.write(''.join(lines))
								os.remove(src)
							else:
								move(src, srcpath + newname + suffix)
						else:
							move(src, destpath + fileName + suffix)
					except OSError as ose:
						#print "ERR:%s" % str(ose)
						errorlist.append(str(ose))
			return errorlist

		# MOVE
		if newname is None:
			if srcpath == destpath:
				result = False
				errText = 'Equal Source and Destination Path'
			elif not os.path.exists(fullpath):
				result = False
				errText = 'File not exist'
			elif not os.path.exists(destpath):
				result = False
				errText = 'Destination Path not exist'
			elif os.path.exists(destpath + fullfilename):
				errText = 'Destination File exist'
				result = False
		#rename
		else:
			if not os.path.exists(fullpath):
				result = False
				errText = 'File not exist'
			elif os.path.exists(newfullpath):
				result = False
				errText = 'New File exist'

		if result:
			errlist = domove()
			if not errlist:
				result = True
			else:
				result = False

	etxt = "rename"
	if newname is None:
		etxt = "move"
	if result == False:
		return {
			"result": False,
			"message": "Could not %s recording '%s' Err: '%s'" % (etxt,name,errText)
			}
	else:
		return {
			"result": True,
			"message": "The recording '%s' has been %sd successfully" % (name,etxt)
			}

def moveMovie(session, sRef, destpath):
	return _moveMovie (session,sRef,destpath=destpath)

def renameMovie(session, sRef, newname):
	return _moveMovie (session,sRef,newname=newname)

def getMovieTags(sRef = None, addtag = None, deltag = None):
	
	if sRef is not None:
		result = False
		service = ServiceReference(sRef)
		if service is not None:
			fullpath = service.ref.getPath()
			filename = '/'.join(fullpath.split("/")[1:])
			metafilename = '/'+filename + '.meta'
			if fileExists(metafilename):
				lines = []
				with open(metafilename, 'r') as f:
					lines = f.readlines()
				if lines:
					meta = ["","","","","","",""]
					lines = [l.strip() for l in lines]
					le = len(lines)
					meta[0:le] = lines[0:le]
					oldtags = meta[4].split(' ')

					if addtag is not None:
						addtag = addtag.replace(' ','_')
						try:
							oldtags.index(addtag)
						except ValueError:
							oldtags.append(addtag)
					if deltag is not None:
						deltag = deltag.replace(' ','_')
					else:
						deltag = 'dummy'
					newtags = []
					for tag in oldtags:
						if tag != deltag:
							newtags.append(tag)

					lines[4] = ' '.join(newtags)

					with open(metafilename, 'w') as f:
						f.write('\n'.join(lines))

					result = True
					return {
						"result": result,
						"tags" : newtags
					}

		return {
			"result": result,
			"resulttext" : "Recording not found"
		}
	
	tags = []
	wr = False
	if fileExists(MOVIETAGFILE):
		for tag in open(MOVIETAGFILE).read().split("\n"):
			if len(tag.strip()) > 0:
				if deltag != tag:
					tags.append(tag.strip())
				if addtag == tag:
					addtag = None
		if deltag is not None:
			wr = True
	if addtag is not None:
		tags.append(addtag)
		wr = True
	if wr:
		with open(MOVIETAGFILE, 'w') as f:
			f.write("\n".join(tags))
	return {
		"result": True,
		"tags": tags
	}

