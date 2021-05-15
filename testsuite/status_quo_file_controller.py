#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import unittest
import uuid

import requests

TARGET_URL_BASE_FMT = 'http://{host}/file'

from movie_files_testsuite import dump_disclaimer
from movie_files_testsuite import ENV_VAR, ENV_VAL_FALLBACK


class TestEnigma2FileAPICalls(unittest.TestCase):
	"""
	This test suite is used to document the behaviour of /file endpoint as
	of 2017-09-08.
	"""

	def setUp(self):
		self.enigma2_host = os.environ.get(ENV_VAR, ENV_VAL_FALLBACK)
		self.file_url = TARGET_URL_BASE_FMT.format(host=self.enigma2_host)

	def test_etc_passwd(self):
		params = {
			"file": "/etc/passwd"
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		self.assertTrue(len(req.text) > 20)
		self.assertEqual(200, req.status_code)  # should this be allowed at all?

	def test_etc_passwd_stream(self):
		params = {
			"file": "/etc/passwd",
			"action": "stream",
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		# print(req.text)
		expected_body = '#EXTM3U\n#EXTVLCOPT--http-reconnect=true\n#EXTINF:-1,stream\nhttp://{netloc}:80/file?action=download&file=/etc/passwd'.format(netloc=self.enigma2_host)
		self.assertEqual(expected_body, req.text)
		self.assertEqual(200, req.status_code)

	def test_etc_passwd_download(self):
		params = {
			"file": "/etc/passwd",
			"action": "download",
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		self.assertTrue(len(req.text) > 20)
		self.assertEqual(200, req.status_code)

	def test_invalid_action(self):
		params = {
			"file": "/etc/passwd",
			"action": "invalid",
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		self.assertEqual("wrong action parameter", req.text)
		self.assertEqual(200, req.status_code)

	def test_nonexisting_file(self):
		randy = uuid.uuid4().hex
		params = {
			"file": randy
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		self.assertEqual("File '/home/root/{:s}' not found".format(randy),
						  req.text)
		self.assertEqual(200, req.status_code)

	def test_nonexisting_path(self):
		randy = uuid.uuid4().hex
		params = {
			"dir": randy
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		minimal_expectation = {"message": "path {:s} not exits".format(randy),
							   "result": False}
		result = req.json()
		for key in minimal_expectation:
			self.assertEqual(minimal_expectation[key], result.get(key))
		self.assertEqual(200, req.status_code)

	def test_empty_glob_result(self):
		randy = uuid.uuid4().hex
		params = {
			"dir": '/etc',
			"pattern": randy
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		minimal_expectation = {"dirs": [], "result": True}
		result = req.json()
		for key in minimal_expectation:
			self.assertEqual(minimal_expectation[key], result.get(key))
		self.assertEqual(200, req.status_code)

	def test_nonempty_glob_result(self):
		params = {
			"dir": '/etc',
			"pattern": 'opkg*'
		}
		req = requests.get(self.file_url, params=params)
		print("Tried to fetch {!r}".format(req.url))
		minimal_expectation = {"dirs": ['/etc/opkg/'], "result": True,
							   "files": []}
		result = req.json()
		for key in minimal_expectation:
			self.assertEqual(minimal_expectation[key], result.get(key))
		self.assertEqual(200, req.status_code)


if __name__ == '__main__':
	dump_disclaimer()
	unittest.main()
