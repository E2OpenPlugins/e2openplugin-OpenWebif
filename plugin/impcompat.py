# -*- coding: utf-8 -*-
# Replacement for the parts of the "imp" module OpenWebif uses.
# "imp" was removed in Python 3.12.

import importlib.machinery
import importlib.util
import sys


def _load(name, path, loader):
	spec = importlib.util.spec_from_file_location(name, path, loader=loader)
	module = importlib.util.module_from_spec(spec)
	sys.modules[name] = module
	loader.exec_module(module)
	return module


def load_source(name, path):
	return _load(name, path, importlib.machinery.SourceFileLoader(name, path))


def load_compiled(name, path):
	return _load(name, path, importlib.machinery.SourcelessFileLoader(name, path))
