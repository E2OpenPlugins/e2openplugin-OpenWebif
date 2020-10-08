#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import localtime, strftime
from six.moves.urllib.parse import quote
from Plugins.Extensions.OpenWebif.controllers.i18n import tstrings


class renderEvtBlock:
	def __init__(self):
		self.template = """
		<article class="epg__event event" data-ref="%s" data-id="%s" data-toggle="modal" data-target="#EventModal" onClick="loadeventepg('%s', '%s'); return false;">
			<time class="epg__time--start">%s%s</time>
			<span class="epg__title title">%s</span>
			%s
		</article>
		"""

	def render(self, event):
		if event['title'] != event['shortdesc']:
			shortdesc = '<summary class="epg__desc desc">%s</summary>' % (
				event['shortdesc']
			)
		else:
			shortdesc = ''

		if event['timerStatus'] != '':
			timerEventSymbol = '<span class="epg__timer %s">%s</span>' % (
				event['timerStatus'], tstrings['timer']
			)
		else:
			timerEventSymbol = ''
		return self.template % (
			quote(event['ref'], safe=' ~@#$&()*!+=:;,.?/\''),
			event['id'],
			event['id'],
			quote(event['ref'], safe=' ~@#$&()*!+=:;,.?/\''),
			strftime("%H:%M", localtime(event['begin_timestamp'])),
			timerEventSymbol,
			event['title'],
			shortdesc
		)
