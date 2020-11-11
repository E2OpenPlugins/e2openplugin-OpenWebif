#!/usr/bin/python
# -*- coding: utf-8 -*-

from time import localtime, strftime
from six.moves.urllib.parse import quote
from Plugins.Extensions.OpenWebif.controllers.i18n import tstrings


class renderEvtBlock:
	def __init__(self):
		self.template = """
		<article onclick="loadeventepg('%s', '%s'); return false;" class="epg__event event %s" data-ref="%s" data-id="%s" data-toggle="modal" data-target="#EventModal">
			<time class="epg__time--start">%s</time>
			<span class="epg__title title">
				%s
				<span class="epg__timer-status">%s</span>
			</span>
			%s
		</article>
		"""

	def render(self, event):
		eventCssClass = ''

		if event['title'] != event['shortdesc']:
			shortdesc = '<summary class="epg__desc desc">%s</summary>' % (
				event['shortdesc']
			)
		else:
			shortdesc = ''

		timer = event['timer']
		if timer:
			eventCssClass = eventCssClass + ' event--has-timer'
			if timer['isEnabled']:
				timerEventSymbol = '<i class="material-icons material-icons-centered">alarm_on</i>'
			else:
				timerEventSymbol = '<i class="material-icons material-icons-centered">alarm_off</i>'
		else:
			timerEventSymbol = ''

		sRef = quote(event['ref'], safe=' ~@#$&()*!+=:;,.?/\'')

		return self.template % (
			event['id'],
			sRef,
			eventCssClass,
			sRef,
			event['id'],
			strftime("%H:%M", localtime(event['begin_timestamp'])),
			event['title'],
			timerEventSymbol,
			shortdesc
		)
