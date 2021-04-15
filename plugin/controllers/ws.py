# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: wsController
##########################################################################
# Copyright (C) 2021 E2OpenPlugins
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

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource

import voluptuous as vol
import json

class OWFServerProtocol(WebSocketServerProtocol):

	TYPE_RESULT = "result"
	TYPE_AUTH_REQUIRED = "auth_required"
	TYPE_AUTH_OK = "auth_ok"
	TYPE_AUTH = "auth"
	TYPE_PING = "ping"

	REQUEST_BASE_SCHEMA = vol.Schema({
		vol.Required('id'): int,
	})

	BASE_MESSAGE_SCHEMA = REQUEST_BASE_SCHEMA.extend({
		vol.Required('type'): vol.Any(
				TYPE_AUTH,
				TYPE_PING
			)
	}, extra=vol.ALLOW_EXTRA)

	AUTH_MESSAGE_SCHEMA = REQUEST_BASE_SCHEMA.extend({
		vol.Required('type'): TYPE_AUTH,
	})

	server = None

	def __init__(self, *args, **kwargs):
		self._authenticated = True
		self._failedAuthCount = 0
		self._requestID = 0

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {0}".format(code))

	def _disconnect(self, code=3401, reason=u'Authentication failed'):
		self.sendClose(code=code, reason=reason)

	def onConnect(self, request):
		print("Client connecting: {0}".format(request.peer))
		return None

	def onOpen(self):
		self.checkAuth()

	def checkAuth(self):
		if self._authenticated:
			self.sendAuthOk()
			return
		else:
			self.sendAuthRequest()

	def sendAuthOk(self):
		self.sendJSON({"type": self.TYPE_AUTH_OK)

	def sendAuthRequest(self):
		self.sendJSON({"type": self.TYPE_AUTH_REQUIRED})

	def validate(self, msg, validator):
		try:
			return validator(msg)
		except Exception as e:
			self.sendError(msg.get("id", -1), -1, "INVALID CALL! %s" %e)

	def onMessage(self, payload, isBinary):
		if isBinary:
			print"Binary message received: {0} bytes".format(len(payload)))
		else:
			msg = json.loads(payload, 'utf8')
			print("> %s" % (msg))
			self.onJSONMessage(msg)

	def onJSONMessage(self, msg):
		msg = self.validate(msg, self.BASE_MESSAGE_SCHEMA)
		if not msg:
			return
		self._requestID = msg["id"]
		do = 'do_{}'.format(msg['type'])
		getattr(self, do)(msg)

	def sendJSON(self, msg):
		if "id" in msg:
			self._requestID += 1
			msg['id'] = self._requestID
		msg = json.dumps(msg).encode('utf8')
		print("< %s" % (msg))
		self.sendMessage(msg)

	def sendResult(self, id, result=None):
		msg = {
			"id": id,
			"type": self.TYPE_RESULT,
			"success": True,
			"result": result,
		}
		self.sendJSON(msg)

	def sendError(self, id, code, message=None):
		data = {
			"id": id,
			"type": self.TYPE_RESULT,
			"success": False,
			"error": {
				"code": code,
				"message": message,
			}
		}
		self.sendJSON(data)

	def do_ping(self, msg):
		self.sendJSON({"type": self.TYPE_PING})


class OWFWebSocketServer():
	def __init__(self):
		self.session = None
		self._sessions = set()
		self._factory = WebSocketServerFactory(url=None, debug=False, debugCodePaths=False)
		self._factory.setProtocolOptions(autoPingInterval=15, autoPingTimeout=3)
		self._factory.protocol = OWFServerProtocol
		self.root = WebSocketResource(self._factory)
		OWFServerProtocol.server = None

	def addSession(self, session):
		self._sessions.add(session)

	def removeSession(self, session):
		self._sessions.remove(session)

	def checkSession(self, session):
		return session in self._sessions

	def start(self, session):
		self._session = session
		OWFServerProtocol.server = self
		OWFServerProtocol.session = session


webSocketServer = OWFWebSocketServer()
