# -*- coding: utf-8 -*-

from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.PluginComponent import plugins

def reloadPlugins():
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
	return {
		"result": True,
		"message": "List of Plugins has been read"
	}