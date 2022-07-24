# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: WOLSetupController, WOLClientController
##########################################################################
# Copyright (C) 2011 - 2022 E2OpenPlugins
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

from six import ensure_binary
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from struct import pack
from twisted.web import resource

from Components.config import config
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg


def createResult(result, resulttext):
	return b'<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>%s</e2state><e2statetext>%s</e2statetext></e2simplexmlresult>' % (b"true" if result else b"false", resulttext)


class WOLSetupController(resource.Resource):

	def __init__(self, session):
		resource.Resource.__init__(self)
		self.session = session

	def render(self, request):
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			wol_active = config.plugins.wolconfig.activate.value
			wol_location = config.plugins.wolconfig.location.value
		except:  # nosec # noqa: E722
			return createResult(False, b"WOLSetup plugin is not installed or your STB does not support WOL")

		if len(request.args):
			config_changed = False
			wol_state = getUrlArg(request, "wol")
			location = getUrlArg(request, "location")
			wol_standby = getUrlArg(request, "wolstandby")
			if wol_state != None:
				wol_state = str(wol_state).lower()
				if wol_state in ('true', '1', 'enabled', 'enable', 'active'):
					config.plugins.wolconfig.activate.value = True
				elif wol_state in ('false', '0', 'disabled', 'disable', 'inactive'):
					config.plugins.wolconfig.activate.value = False
				if wol_active != config.plugins.wolconfig.activate.value:
					config_changed = True
			elif location != None:
				if location not in config.plugins.wolconfig.location.choices:
					location = wol_location
				if location != config.plugins.wolconfig.location.value:
					config.plugins.wolconfig.location.value = location
					config_changed = True
			elif wol_standby != None:
				wol_standby = str(wol_standby).lower()
				if wol_standby in ('true', '1', 'enabled', 'enable', 'active'):
					try:
						from Plugins.SystemPlugins.WOLSetup.plugin import WOLSetup, _deviseWOL, _flagForceEnable, _flagSupportWol, _tryQuitTable, _ethDevice  # noqa: F401
						from Screens.Standby import TryQuitMainloop
					except ImportError:
						return createResult(False, b"WOLSetup plugin is not installed or your STB does not support WOL")
					WOLSetup.ActivateWOL(self.session, writeDevice=True)
					self.session.open(TryQuitMainloop, _tryQuitTable["deepstandby"])
			if config_changed:
				config.plugins.wolconfig.save()

		locations = ""
		for location_available in config.plugins.wolconfig.location.choices:
			locations += location_available + ", "
		locations = locations.rstrip(', ')

		return ensure_binary("""<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
				<e2configs>
					<e2config>
						<e2configname>wol_active</e2configname>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>wol_location</e2configname>
						<e2configchoices>%s</e2configchoices>
						<e2configvalue>%s</e2configvalue>
					</e2config>
				</e2configs>""" % (str(config.plugins.wolconfig.activate.value), locations, str(config.plugins.wolconfig.location.value)))


class WOLClientController(resource.Resource):
	def render(self, request):
		request.setHeader('Content-Type', 'application/xhtml+xml')
		request.setHeader('Charset', 'UTF-8')
		if len(request.args):
			port = 9
			mac = ""
			ip = ""
			man_port = getUrlArg(request, "port")
			if man_port != None:
				try:
					port = int(man_port)
				except ValueError:
					pass
			mac = getUrlArg(request, "mac")
			if mac != None:
				mac = str(mac).lower()
				mac = mac.split(':')
				if len(mac) != 6:
					return createResult(False, b"MAC address invalid see example: AA:BB:CC:DD:EE:FF")
			ip = getUrlArg(request, "ip")
			if ip != None:
				ip = str(ip).lower()
				ip = ip.split('.')
				if len(ip) != 4:
					return createResult(False, b"IP address invalid see example: 192.168.2.10")
				try:
					for digit in ip:
						is_int = int(digit)  # noqa: F841
				except ValueError:
					return createResult(False, b"IP address invalid see example: 192.168.2.10")
				ip = ip[0] + "." + ip[1] + "." + ip[2] + ".255"
			if ip and mac:
				mac_struct = pack('BBBBBB', int(mac[0], 16), int(mac[1], 16), int(mac[2], 16), int(mac[3], 16), int(mac[4], 16), int(mac[5], 16))
				magic = ensure_binary(('\xff' * 6) + str(mac_struct * 16))
				my_socket = socket(AF_INET, SOCK_DGRAM)
				my_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
				my_socket.sendto(magic, (ip, port))
				my_socket.close()
				return createResult(True, ensure_binary("MagicPacket send to IP %s at port %d" % (ip, port)))
		return createResult(False, b"'ip' and 'mac' are mandatory arguments")
