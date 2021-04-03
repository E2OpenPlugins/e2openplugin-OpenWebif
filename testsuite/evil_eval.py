#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
Unit Test for Code Trying to Mitigate a Remote Code Execution Vulnerability
(CVE-2017-9807).

.. highlight:: bash

    root@heart-of-gold:~# curl --noproxy localhost http://localhost/api/saveconfig --data "value=1&key=config.__class__.__name__ == 1 or (open('you lost your mind? according to my last psych EVALuation, yes', 'wb') and config or config)"
    root@heart-of-gold:~# ls $HOME/you*
    /home/root/you lost your mind? according to my last psych EVALuation, yes

    root@heart-of-gold:~# curl --noproxy localhost http://localhost/api/saveconfig --data "value=1&key=config.__class__ == 42 or (__import__('os').system('id > pwned') and config or config)"
    {"result": false}
    root@heart-of-gold:~# cat $HOME/pwned
    uid=0(root) gid=0(root)

"""
import os
import sys
import unittest
import pickle

# hack: alter include path in such ways that utilities library is included
sys.path.append(os.path.join(os.path.dirname(__file__), '../plugin'))

from controllers.utilities import get_config_attribute

SOME_BAD_KEY = "config.__class__.__name__ == 1 or (open('you lost your mind?" \
			   " according to my last psych EVALuation, yes', 'wb') " \
			   "and config or config)"

SOME_OLD_BAD_KEY = "config.__class__ == 1 or (__import__('os').system(" \
				   "'touch ' + chr(47) + 'tmp' + chr(47) + 'py100 &')) " \
				   "and config or config)"

KEY_RIGHT = 123456


class ConfigObjectMockup(object):
	"""
	Mock implementation of :py:class:`Components.config.Config`.
	"""

	def __init__(self, value=None):
		self._value = value

	def save(self):
		return True

	def handleKey(self, key):
		return key

	def get_saved_value(self):
		return self._value

	saved_value = property(get_saved_value)

	def pickle(self):
		return pickle.dumps(self)

	def __eq__(self, other):
		return self._value == other


def is_invalid_key(key):
	"""
	Vulnerable key validation as implemented in
	:py:meth:`controllers.WebController.P_saveconfig`.

	Args:
		key: configuration member access key
	Returns:
		True if key appears to be valid
	"""
	if "/" not in key and "%" not in key and "." in key:
		keys = key.split('.')
		if len(keys) in (3, 4, 5) and keys[0] == 'config':
			return False
	return True


def get_config_attribute_insane(path):
	"""
	Determine attribute to be accessed by *path* using :py:func:`eval`.

	Args:
		path: character string specifying which attribute is to be accessed

	Returns:
		Attribute of object described by *path*
	"""
	if not is_invalid_key(path):
		return eval(path)
	raise ValueError("invalid path {!r}".format(path))


class EvilEvalTestCase(unittest.TestCase):
	def setUp(self):
		"""
		Create a :py:class:`Components.config.Config` object like the one
		described in Components/config.py.

		.. highlight:: python

			config.bla = ConfigSubsection()
			config.bla.test = ConfigYesNo()
			config.nim = ConfigSubList()
			config.nim.append(ConfigSubsection())
			config.nim[0].bla = ConfigYesNo()
			config.nim.append(ConfigSubsection())
			config.nim[1].bla = ConfigYesNo()
			config.nim[1].blub = ConfigYesNo()
			config.arg = ConfigSubDict()
			config.arg["Hello"] = ConfigYesNo()

			config.arg["Hello"].handleKey(KEY_RIGHT)
			config.arg["Hello"].handleKey(KEY_RIGHT)

			config.saved_value

			configfile.save()
			config.save()
			print(config.pickle())

		"""
		global config
		self.config_obj = ConfigObjectMockup()
		self.config_obj.bla = ConfigObjectMockup()
		self.config_obj.bla.test = ConfigObjectMockup(True)
		self.config_obj.nim = list()
		self.config_obj.nim.append(ConfigObjectMockup())
		self.config_obj.nim[0].bla = ConfigObjectMockup(True)
		self.config_obj.nim.append(ConfigObjectMockup())
		self.config_obj.nim[1].bla = ConfigObjectMockup(True)
		self.config_obj.nim[1].blub = ConfigObjectMockup(True)
		self.config_obj.arg = dict()
		self.config_obj.arg["Hello"] = ConfigObjectMockup(True)
		self.config_obj.arg["Hello"].handleKey(KEY_RIGHT)
		config = self.config_obj

	def testMockup(self):
		self.assertTrue(self.config_obj.bla.test)
		self.assertTrue(self.config_obj.nim[0].bla)
		self.assertTrue(self.config_obj.nim[1].bla)
		self.assertTrue(self.config_obj.nim[1].blub)
		self.assertEqual(2, len(self.config_obj.nim))
		self.assertTrue(self.config_obj.arg['Hello'])
		self.assertEqual(KEY_RIGHT,
						 self.config_obj.arg['Hello'].handleKey(KEY_RIGHT))

		mockie_messer = ConfigObjectMockup("Und der Haifisch")
		self.assertEqual("Und der Haifisch", mockie_messer.saved_value)
#		self.assertEqual(
#			"ccopy_reg\n_reconstructor\np0\n(c__main__\nConfigObjectMockup\np1"
#			"\nc__builtin__\nobject\np2\nNtp3\nRp4\n(dp5\nS'_value'\np6\nS'Und"
#			" der Haifisch'\np7\nsb.", mockie_messer.pickle())

	def testAtticSanitation(self):
		# D-OH! EPIC FAIL :)
		self.assertFalse(is_invalid_key(SOME_BAD_KEY))

	def testAtticSanitation2(self):
		# D-OH! EPIC FAIL :)
		self.assertFalse(is_invalid_key(SOME_OLD_BAD_KEY))

	def testBraveNewSanitation(self):
		with self.assertRaises(ValueError) as context:
			get_config_attribute(SOME_BAD_KEY, self.config_obj)
		self.assertTrue('private member' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			get_config_attribute('__class__', self.config_obj)
		self.assertTrue('Invalid path length' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			get_config_attribute('config.__class__..', self.config_obj)
		self.assertTrue('private member' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			get_config_attribute('config.nim.__class__.__name__',
								 self.config_obj)
		self.assertTrue('private member' in str(context.exception))

		with self.assertRaises(ValueError) as context:
			get_config_attribute('config.nim................', self.config_obj)
		self.assertTrue('empty attr_name' in str(context.exception))

		with self.assertRaises(AttributeError) as context:
			get_config_attribute('config.nim', None)
		self.assertTrue(
			"'NoneType' object has no attribute 'nim'" in str(context.exception))

	def testMockupAccess(self):
		self.assertTrue(get_config_attribute_insane('config.bla.test'))
		self.assertTrue(get_config_attribute_insane('config.nim[0].bla'))
		self.assertTrue(get_config_attribute_insane('config.nim[1].bla'))
		self.assertTrue(get_config_attribute_insane('config.nim[1].blub'))

		# accessing the following members is not implemented:
		# self.assertEqual(2, len(get_config_value_insane('config.nim')))
		# self.assertTrue(get_config_value_insane("config.arg['Hello']"))
		# self.assertEqual(KEY_RIGHT, get_config_value_insane(
		# "config.arg['Hello']").handleKey(KEY_RIGHT))

		with self.assertRaises(AttributeError) as context:
			get_config_attribute_insane('config.hats.net')
		self.assertTrue(
			"'ConfigObjectMockup' object has no attribute 'hats'" in str(context.exception))

		with self.assertRaises(IndexError) as context:
			get_config_attribute_insane('config.nim[2].bla')
		self.assertTrue("list index out of range" in str(context.exception))

		with self.assertRaises(AttributeError) as context:
			get_config_attribute_insane('config.nim.nosuchnumber')
		self.assertTrue(
			"'list' object has no attribute 'nosuchnumber'" in str(context.exception))

	def testMockupBraveNewAccess(self):
		with self.assertRaises(ValueError) as context:
			get_config_attribute('KONFIG.nim.nosuchnumber', self.config_obj)

		self.assertTrue(
			"Head is 'KONFIG', expected 'config'" in str(context.exception))

		self.assertTrue(
			get_config_attribute('config.bla.test', self.config_obj))
		self.assertTrue(
			get_config_attribute('config.nim[0].bla', self.config_obj))
		self.assertTrue(
			get_config_attribute('config.nim[1].bla', self.config_obj))
		self.assertTrue(
			get_config_attribute('config.nim[1].blub', self.config_obj))
		self.assertEqual(
			2,
			len(get_config_attribute('config.nim', self.config_obj)))
		self.assertTrue(
			get_config_attribute("config.arg['Hello']", self.config_obj))
		self.assertEqual(
			KEY_RIGHT,
			get_config_attribute(
				"config.arg['Hello']",
				self.config_obj).handleKey(KEY_RIGHT))

		with self.assertRaises(AttributeError) as context:
			get_config_attribute('config.hats.net', self.config_obj)
		self.assertTrue(
			"'ConfigObjectMockup' object has no attribute 'hats'" in str(context.exception))

		with self.assertRaises(IndexError) as context:
			get_config_attribute('config.nim[2].bla', self.config_obj)
		self.assertTrue("list index out of range" in str(context.exception))

		with self.assertRaises(AttributeError) as context:
			get_config_attribute('config.nim.nosuchnumber', self.config_obj)
		self.assertTrue(
			"'list' object has no attribute 'nosuchnumber'" in str(context.exception))


if __name__ == '__main__':
	unittest.main()
