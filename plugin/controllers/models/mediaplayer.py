# -*- coding: utf-8 -*-

from Tools.Directories import fileExists, resolveFilename, SCOPE_PLAYLIST
from Components.FileList import FileList
from enigma import eServiceReference

import os 
import fnmatch

def getMpInstance(session):
	try:
		from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer, MyPlayList
	except Exception, e:
		return None

	if isinstance(session.current_dialog, MediaPlayer):
		return session.current_dialog

	for dialog in session.dialog_stack:
		if isinstance(dialog, MediaPlayer):
			return dialog

def getOrCreateMpInstance(session):
	try:
		from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer, MyPlayList
	except Exception, e:
		return None

	mp = getMpInstance(session)
	if mp:
		return mp

	return session.open(MediaPlayer)

def mediaPlayerAdd(session, filename):
	mp = getOrCreateMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not installed"
			}

	if fileExists(filename):
		service = eServiceReference(4097, 0, filename)
	else:
		service = eServiceReference(filename)

	if not service.valid():
		return {
			"result": False,
			"message": "'%s' is neither a valid reference nor a valid file" % filename
		}

	mp.playlist.addFile(service)
	mp.playlist.updateList()

	return {
		"result": True,
		"message": "'%s' has been added to playlist" % filename
	}

def mediaPlayerRemove(session, filename):
	mp = getOrCreateMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not installed"
			}

	service = eServiceReference(filename)
	if not service.valid():
		service = eServiceReference(4097, 0, filename)

	if not service.valid():
		return {
			"result": False,
			"message": "'%s' is neither a valid reference nor a valid file" % filename
		}

	count = 0
	removed = False
	for item in mp.playlist.getServiceRefList():
		if item == service:
			mp.playlist.deleteFile(count)
			removed = True
			break
		count += 1

	if not removed:
		return {
			"result": False,
			"message": "'%s' not found in playlist" % filename
		}

	mp.playlist.updateList()
	return {
		"result": True,
		"message": "'%s' removed from playlist" % filename
	}

def mediaPlayerPlay(session, filename, root):
	mp = getOrCreateMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not installed"
			}

	if fileExists(filename):
		service = eServiceReference(4097, 0, filename)
	else:
		service = eServiceReference(filename)

	if not service.valid():
		return {
			"result": False,
			"message": "'%s' is neither a valid reference nor a valid file" % filename
		}

	if root != "playlist":
		mp.playlist.addFile(service)
		mp.playlist.updateList()

	mp.playServiceRefEntry(service)

	return {
		"result": True,
		"message": "'%s' has been added to playlist" % filename
	}

def mediaPlayerCommand(session, command):
	mp = getMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not active"
			}

	if command == "play":
		mp.playEntry()
	elif command == "pause":
		mp.pauseEntry()
	elif command == "stop":
		mp.stopEntry()
	elif command == "next":
		mp.nextEntry()
	elif command == "previous":
		mp.previousMarkOrEntry()
	elif command == "shuffle":
		mp.playlist.PlayListShuffle()
	elif command == "clear":
		mp.clear_playlist()
	elif command == "exit":
		mp.exit()
	else:
		return {
			"result": False,
			"message": "Unknown parameter %s" % command
			}
	return {
		"result": True,
		"message": "Command '%s' executed" % command
	}

def mediaPlayerCurrent(session):
	mp = getMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not active"
			}
	return {
		"result": True,
		"artist": mp["artist"].getText(),
		"title": mp["title"].getText(),
		"album": mp["album"].getText(),
		"year": mp["year"].getText(),
		"genre": mp["genre"].getText(),
		"coverArt": mp["coverArt"].coverArtFileName
	}

def mediaPlayerList(session, path, types):
	if types == "video":
		mpattern = "(?i)^.*\.(ts|mts|m2ts|e2pls|mpg|vob|avi|divx|m4v|mkv|mp4|dat|flv|mov|dts)"
		mserviceref = True
	elif types == "audio":
		mserviceref = True
		mpattern = "(?i)^.*\.(mp2|mp3|ogg|wav|wave|m3u|pls|e2pls|m4a|flac)"
	elif types == "any" or types == "":
		mserviceref = True
		# complete pattern from mediaplayer
		mpattern = "(?i)^.*\.(mp2|mp3|ogg|ts|mts|m2ts|wav|wave|m3u|pls|e2pls|mpg|vob|avi|divx|m4v|mkv|mp4|m4a|dat|flac|flv|mov|dts)"
	else:
		mserviceref = False
		mpattern = types

	rpath = path
	if rpath == "":
		rpath = None

	if rpath == "playlist":
		mp = getOrCreateMpInstance(session)
		if mp is None:
			return {
				"result": False,
				"files": []
				}
		files = []
		for service in mp.playlist.getServiceRefList():
			files.append({
				"servicereference": service.getPath(),
				"isdirectory": False,
				"root": "playlist"
			})
		return {
			"result": True,
			"files": files
		}
	elif rpath == None or os.path.isdir(rpath):
		files = []
		filelist = FileList(rpath, matchingPattern = mpattern, useServiceRef = mserviceref, additionalExtensions = "4098:m3u 4098:e2pls 4098:pls")
		for item in filelist.getFileList():
			if item[0][1]:
				files.append({
					"servicereference": item[0][0],
					"isdirectory": item[0][1],
					"root": rpath
				})
			elif mserviceref:
				files.append({
					"servicereference": item[0][0].toString(),
					"isdirectory": item[0][1],
					"root": rpath
				})
			else:
				files.append({
					"servicereference": path + item[0][0],
					"isdirectory": item[0][1],
					"root": rpath
				})

		return {
			"result": True,
			"files": files
		}

	return {
		"result": False,
		"files": []
	}

def mediaPlayerLoad(session, filename):
	mp = getOrCreateMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not installed"
			}

	path = resolveFilename(SCOPE_PLAYLIST, filename)
	if not fileExists(path):
		return {
			"result": False,
			"message": "Playlist '%s' does not exist" % path
			}

	mp.PlaylistSelected((filename, path))
	return {
		"result": True,
		"message": "Playlist loaded from '%s'" % path
		}

def mediaPlayerSave(session, filename):
	mp = getOrCreateMpInstance(session)
	if mp is None:
		return {
			"result": False,
			"message": "Mediaplayer not installed"
			}

	path = resolveFilename(SCOPE_PLAYLIST, filename)
	mp.playlistIOInternal.save(path)
	return {
		"result": True,
		"message": "Playlist saved to '%s'" % path
		}

def mediaPlayerFindFile(session, path, pattern):
	rfiles = []
	for root, dirs, files in os.walk(path):
		for filename in fnmatch.filter(files, pattern):
			rfiles.append({
				"name": filename,
				"path": root
			})

	return {
		"result": True,
		"files": rfiles
	}
