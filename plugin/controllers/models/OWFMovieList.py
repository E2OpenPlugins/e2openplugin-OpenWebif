# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: MovieList / copy of OpenATV MovieList.py
##########################################################################

import os
import struct

from enigma import iServiceInformation, eServiceReference, eServiceCenter

from Tools.FuzzyDate import FuzzyTime
from Components.config import config
from Tools.Directories import resolveFilename
from Screens.LocationBox import defaultInhibitDirs
from ServiceReference import ServiceReference

cutsParser = struct.Struct('>QI')  # big-endian, 64-bit PTS and 32-bit type

# iStaticServiceInformation


class StubInfo:
	def __init__(self):
		pass

	def getName(self, serviceref):
		return os.path.split(serviceref.getPath())[1]

	def getLength(self, serviceref):
		return -1

	def getEvent(self, serviceref, *args):
		return None

	def isPlayable(self):
		return True

	def getInfo(self, serviceref, w):
		try:
			if w == iServiceInformation.sTimeCreate:
				return os.stat(serviceref.getPath()).st_ctime
			if w == iServiceInformation.sFileSize:
				return os.stat(serviceref.getPath()).st_size
			if w == iServiceInformation.sDescription:
				return serviceref.getPath()
		except:
			pass
		return 0

	def getInfoString(self, serviceref, w):
		return ''


justStubInfo = StubInfo()


class MovieList():

	def __init__(self, root, sort_type=None, descr_state=None):
		self.list = []
		self.firstFileEntry = 0
		self.parentDirectory = 0
		self.tags = set()
		self.root = None
		self._char = ''

	def getItem(self, index):
		if self.list:
			if len(self.list) > index:
				return self.list[index] and self.list[index][0]

	def __len__(self):
		return len(self.list)

	def __getitem__(self, index):
		return self.list[index]

	def __iter__(self):
		return self.list.__iter__()

	def load(self, root, filter_tags):
		# this lists our root service, then building a
		# nice list
		del self.list[:]
		serviceHandler = eServiceCenter.getInstance()
		numberOfDirs = 0

		reflist = root and serviceHandler.list(root)
		if reflist is None:
			print("listing of movies failed")
			return
		realtags = set()
		tags = {}
		rootPath = os.path.normpath(root.getPath())
		parent = None
		# Don't navigate above the "root"
		if len(rootPath) > 1 and (os.path.realpath(rootPath) != config.movielist.root.value):
			parent = os.path.split(os.path.normpath(rootPath))[0]
			currentfolder = os.path.normpath(rootPath) + '/'
			if parent and (parent not in defaultInhibitDirs) and not currentfolder.endswith(config.usage.default_path.value):
				# enigma wants an extra '/' appended
				if not parent.endswith('/'):
					parent += '/'
				ref = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + parent)
				ref.flags = eServiceReference.flagDirectory
				self.list.append((ref, None, 0, -1))
				numberOfDirs += 1

		while True:
			serviceref = reflist.getNext()
			if not serviceref.valid():
				break
			info = serviceHandler.info(serviceref)
			if info is None:
				info = justStubInfo
			begin = info.getInfo(serviceref, iServiceInformation.sTimeCreate)
			if serviceref.flags & eServiceReference.mustDescent:
				dirname = info.getName(serviceref)
				if not dirname.endswith('.AppleDouble/') and not dirname.endswith('.AppleDesktop/') and not dirname.endswith('.AppleDB/') and not dirname.endswith('Network Trash Folder/') and not dirname.endswith('Temporary Items/'):
					self.list.append((serviceref, info, begin, -1))
					numberOfDirs += 1
				continue
			# convert space-seperated list of tags into a set
			this_tags = info.getInfoString(serviceref, iServiceInformation.sTags).split(' ')
			name = info.getName(serviceref)

			# OSX put a lot of stupid files ._* everywhere... we need to skip them
			if name[:2] == "._":
				continue

			if this_tags == ['']:
				# No tags? Auto tag!
				this_tags = name.replace(',', ' ').replace('.', ' ').replace('_', ' ').replace(':', ' ').split()
			else:
				realtags.update(this_tags)
			for tag in this_tags:
				if len(tag) >= 4:
					if tag in tags:
						tags[tag].append(name)
					else:
						tags[tag] = [name]
			# filter_tags is either None (which means no filter at all), or
			# a set. In this case, all elements of filter_tags must be present,
			# otherwise the entry will be dropped.
			if filter_tags is not None:
				this_tags_fullname = [" ".join(this_tags)]
				this_tags_fullname = set(this_tags_fullname)
				this_tags = set(this_tags)
				if not this_tags.issuperset(filter_tags) and not this_tags_fullname.issuperset(filter_tags):
# 					print "Skipping", name, "tags=", this_tags, " filter=", filter_tags
					continue

			self.list.append((serviceref, info, begin, -1))

		self.firstFileEntry = numberOfDirs
		self.parentDirectory = 0

		for x in self.list:
			if x[1]:
				tmppath = x[1].getName(x[0])[:-1] if x[1].getName(x[0]).endswith('/') else x[1].getName(x[0])
				if tmppath.endswith('.Trash'):
					self.list.insert(0, self.list.pop(self.list.index(x)))
					break

		if self.root and numberOfDirs > 0:
			rootPath = os.path.normpath(self.root.getPath())
			if not rootPath.endswith('/'):
				rootPath += '/'
			if rootPath != parent:
				# with new sort types directories may be in between files, so scan whole
				# list for parentDirectory index. Usually it is the first one anyway
				for index, item in enumerate(self.list):
					if item[0].flags & eServiceReference.mustDescent:
						itempath = os.path.normpath(item[0].getPath())
						if not itempath.endswith('/'):
							itempath += '/'
						if itempath == rootPath:
							self.parentDirectory = index
							break
		self.root = root
		# finally, store a list of all tags which were found. these can be presented
		# to the user to filter the list
		# ML: Only use the tags that occur more than once in the list OR that were
		# really in the tag set of some file.

		# reverse the dictionary to see which unique movie each tag now references
		rtags = {}
		for tag, movies in list(tags.items()):
			if (len(movies) > 1) or (tag in realtags):
				movies = tuple(movies)  # a tuple can be hashed, but a list not
				item = rtags.get(movies, [])
				if not item:
					rtags[movies] = item
				item.append(tag)
		self.tags = {}
		for movies, tags in list(rtags.items()):
			movie = movies[0]
			# format the tag lists so that they are in 'original' order
			tags.sort(key=movie.find)
			first = movie.find(tags[0])
			last = movie.find(tags[-1]) + len(tags[-1])
			match = movie
			start = 0
			end = len(movie)
			# Check if the set has a complete sentence in common, and how far
			for m in movies[1:]:
				if m[start:end] != match:
					if not m.startswith(movie[:last]):
						start = first
					if not m.endswith(movie[first:]):
						end = last
					match = movie[start:end]
					if m[start:end] != match:
						match = ''
						break
			if match:
				self.tags[match] = set(tags)
				continue
			else:
				match = ' '.join(tags)
				if len(match) > 2:  # Omit small words
					self.tags[match] = set(tags)
