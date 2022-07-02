#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: config
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##########################################################################

from __future__ import print_function
from enigma import eEnv
from Components.SystemInfo import SystemInfo
from Components.config import config
from os import path, listdir
import xml.etree.cElementTree  # nosec

from Plugins.Extensions.OpenWebif.controllers.i18n import _
from Plugins.Extensions.OpenWebif.controllers.utilities import get_config_attribute
from datetime import datetime
import time


def addCollapsedMenu(name):
	tags = config.OpenWebif.webcache.collapsedmenus.value.split("|")
	if name not in tags:
		tags.append(name)

	config.OpenWebif.webcache.collapsedmenus.value = "|".join(tags).strip("|")
	config.OpenWebif.webcache.collapsedmenus.save()

	return {
		"result": True
	}


def removeCollapsedMenu(name):
	tags = config.OpenWebif.webcache.collapsedmenus.value.split("|")
	if name in tags:
		tags.remove(name)

	config.OpenWebif.webcache.collapsedmenus.value = "|".join(tags).strip("|")
	config.OpenWebif.webcache.collapsedmenus.save()

	return {
		"result": True
	}


def getCollapsedMenus():
	return {
		"result": True,
		"collapsed": config.OpenWebif.webcache.collapsedmenus.value.split("|")
	}


def getShowName():
	return {
		"result": True,
		"showname": config.OpenWebif.identifier.value
	}


def getCustomName():
	return {
		"result": True,
		"customname": config.OpenWebif.identifier_custom.value
	}


def getBoxName():
	return {
		"result": True,
		"boxname": config.OpenWebif.identifier_text.value
	}


def getJsonFromConfig(cnf):
	if cnf.__class__.__name__ == "ConfigSelection" or cnf.__class__.__name__ == "ConfigSelectionNumber" or cnf.__class__.__name__ == "TconfigSelection":
		if isinstance(cnf.choices.choices, dict):
			choices = []
			for choice in cnf.choices.choices:
				choices.append((choice, _(cnf.choices.choices[choice])))
		elif isinstance(cnf.choices.choices[0], tuple):
			choices = []
			for choice_tuple in cnf.choices.choices:
				choices.append((choice_tuple[0], _(choice_tuple[1])))
		else:
			choices = []
			for choice in cnf.choices.choices:
				choices.append((choice, _(choice)))

		return {
			"result": True,
			"type": "select",
			"choices": choices,
			"current": str(cnf.value)
		}
	elif cnf.__class__.__name__ == "ConfigBoolean" or cnf.__class__.__name__ == "ConfigEnableDisable" or cnf.__class__.__name__ == "ConfigYesNo":
		return {
			"result": True,
			"type": "checkbox",
			"current": cnf.value
		}
	elif cnf.__class__.__name__ == "ConfigSet":
		return {
			"result": True,
			"type": "multicheckbox",
			"choices": cnf.choices.choices,
			"current": cnf.value
		}

	elif cnf.__class__.__name__ == "ConfigNumber":
		return {
			"result": True,
			"type": "number",
			"current": cnf.value
		}
	elif cnf.__class__.__name__ == "ConfigInteger" or cnf.__class__.__name__ == "TconfigInteger":
		return {
			"result": True,
			"type": "number",
			"current": cnf.value,
			"limits": (cnf.limits[0][0], cnf.limits[0][1])
		}

	elif cnf.__class__.__name__ == "ConfigText":
		return {
			"result": True,
			"type": "text",
			"current": cnf.value
		}
	elif cnf.__class__.__name__ == "ConfigSlider":
		return {
			"result": True,
			"type": "slider",
			"current": cnf.value,
			"increment": cnf.increment,
			"limits": (cnf.min, cnf.max)
		}
	elif cnf.__class__.__name__ == "ConfigNothing":
		return None

	print("[OpenWebif] Unknown class ", cnf.__class__.__name__)
	return {
		"result": False,
		"type": "unknown"
	}


def saveConfig(path, value):
	try:
		cnf = get_config_attribute(path, root_obj=config)
	except Exception as exc:
		print("[OpenWebif] ", exc)
		return {
			"result": False,
			"message": "I'm sorry Dave, I'm afraid I can't do that"
		}

	try:
		if cnf.__class__.__name__ in ("ConfigBoolean", "ConfigEnableDisable", "ConfigYesNo"):
			cnf.value = value == "true"
		elif cnf.__class__.__name__ == "ConfigSet":
			values = cnf.value
			if int(value) in values:
				values.remove(int(value))
			else:
				values.append(int(value))
			cnf.value = values
		elif cnf.__class__.__name__ == "ConfigNumber":
			cnf.value = int(value)
		elif cnf.__class__.__name__ in ("ConfigInteger", "TconfigInteger"):
			cnf_min = int(cnf.limits[0][0])
			cnf_max = int(cnf.limits[0][1])
			cnf_value = int(value)
			if cnf_value < cnf_min:
				cnf_value = cnf_min
			elif cnf_value > cnf_max:
				cnf_value = cnf_max
			cnf.value = cnf_value
		elif cnf.__class__.__name__ in ("ConfigSlider"):
			cnf_min = int(cnf.min)
			cnf_max = int(cnf.max)
			cnf_value = int(value)
			if cnf_value < cnf_min:
				cnf_value = cnf_min
			elif cnf_value > cnf_max:
				cnf_value = cnf_max
			cnf.value = cnf_value
		else:
			cnf.value = value
		cnf.save()
		configfiles.reload()
	except Exception as e:
		print("[OpenWebif] ", e)
		return {
			"result": False
		}

	return {
		"result": True
	}


def getConfigs(key):
	configs = []
	title = None
	if not len(configfiles.sections):
		configfiles.parseConfigFiles()
	if key in configfiles.section_config:
		config_entries = configfiles.section_config[key][1]
		title = configfiles.section_config[key][0]
	if config_entries:
		for entry in config_entries:
			try:
				data = getJsonFromConfig(eval(entry.text or ""))  # nosec
				if data is None:
					continue
				# print("[OpenWebif] -D- config entry: ", entry.text)
				text = _(entry.get("text", ""))
				if "limits" in data:
					text = "%s (%d - %d)" % (text, data["limits"][0], data["limits"][1])
				configs.append({
					"description": text,
					"path": entry.text or "",
					"data": data
				})
			except Exception:
				pass
	return {
		"result": True,
		"configs": configs,
		"title": title,
		"key": key
	}


def getConfigsSections():
	if not len(configfiles.sections):
		configfiles.parseConfigFiles()
	return {
		"result": True,
		"sections": configfiles.sections
	}


def privSettingValues(prefix, top, result):
	for (key, val) in list(top.items()):
		name = prefix + "." + key
		if isinstance(val, dict):
			privSettingValues(name, val, result)
		elif isinstance(val, tuple):
			result.append((name, val[0]))
		else:
			result.append((name, val))


def getSettings():
	configkeyval = []
	privSettingValues("config", config.saved_value, configkeyval)
	return {
		"result": True,
		"settings": configkeyval
	}


def getUtcOffset():
	now = time.time()
	offset = (datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)).total_seconds()
	hours = round(offset / 3600)
	minutes = (offset - (hours * 3600))
	return {
		"result": True,
		# round minutes to next quarter hour
		"utcoffset": "{:+05}".format(int(hours * 100 + (round(minutes / 900) * 900 / 60)))
	}


class ConfigFiles:
	def __init__(self):
		self.allowedsections = ["usage", "userinterface", "recording", "subtitlesetup", "autolanguagesetup", "avsetup", "harddisk", "keyboard", "timezone", "time", "osdsetup", "epgsetup", "display", "remotesetup", "softcamsetup", "logs", "timeshift", "channelselection", "epgsettings", "softwareupdate", "pluginbrowsersetup"]
		self.setupfiles = []
		self.sections = []
		self.itemstoadd = []
		self.section_config = {}
		self.getConfigFiles()

	def reload(self):
		self.section_config = {}
		self.sections = []
		self.parseConfigFiles()

	def getConfigFiles(self):
		setupfiles = [eEnv.resolve('${datadir}/enigma2/setup.xml')]
		locations = ('SystemPlugins', 'Extensions')
		libdir = eEnv.resolve('${libdir}')
		for location in locations:
			plugins = listdir(('%s/enigma2/python/Plugins/%s' % (libdir, location)))
			for plugin in plugins:
				setupfiles.append(('%s/enigma2/python/Plugins/%s/%s/setup.xml' % (libdir, location, plugin)))
		for setupfile in setupfiles:
			if path.exists(setupfile):
				self.setupfiles.append(setupfile)

	def includeElement(self, element):
		itemLevel = int(element.get("level", 0))
		if itemLevel > config.usage.setup_level.index:  # The item is higher than the current setup level.
			return False
		requires = element.get("requires")
		if requires:
			for require in [x.strip() for x in requires.split(";")]:
				negate = require.startswith("!")
				if negate:
					require = require[1:]
				if require.startswith("config."):
					try:
						result = eval(require)
						result = bool(result.value and str(result.value).lower() not in ("0", "disable", "false", "no", "off"))
					except Exception:
						return False
				else:
					result = SystemInfo.get(requires, False)
				if require and negate == result:  # The item requirements are not met.
					return False
		conditional = element.get("conditional")
		if conditional:
			try:
				if not bool(eval(conditional)):
					return False
			except Exception:
				return False
		return True

	def addItems(self, parentNode, including=True):
		for element in parentNode:
			if not element.tag:
				continue
			if element.tag in ("elif", "else") and including:
				break  # End of succesful if/elif branch - short-circuit rest of children.
			include = self.includeElement(element)
			if element.tag == "item":
				if including and include:
					self.itemstoadd.append(element)
			elif element.tag == "if":
				if including:
					self.addItems(element, including=include)
			elif element.tag == "elif":
				including = include
			elif element.tag == "else":
				including = True

	def parseConfigFiles(self):
		sections = []
		for setupfile in self.setupfiles:
			# print("[OpenWebif] loading configuration file :", setupfile)
			setupfile = open(setupfile, 'r')
			setupdom = xml.etree.cElementTree.parse(setupfile)  # nosec
			setupfile.close()
			xmldata = setupdom.getroot()
			for section in xmldata.findall("setup"):
				configs = []
				requires = section.get("requires")
				if requires and not SystemInfo.get(requires, False):
					continue
				key = section.get("key")
				if key not in self.allowedsections:
					showOpenWebIf = section.get("showOpenWebif") or section.get("showOpenWebIf") or section.get("showOpenWebIF") or "0"
					if showOpenWebIf.lower() in ("1", "showopenwebif", "enabled", "on", "true", "yes"):
						self.allowedsections.append(key)
					else:
						continue
				# print("[OpenWebif] loading configuration section :", key)

				self.itemstoadd = []
				self.addItems(section)
				for entry in self.itemstoadd:
					configs.append(entry)

				if len(configs):
					sections.append({
						"key": key,
						"description": _(section.get("title"))
					})
					title = _(section.get("title", ""))
					self.section_config[key] = (title, configs)
		sections = sorted(sections, key=lambda k: k['description'])
		self.sections = sections


configfiles = ConfigFiles()
