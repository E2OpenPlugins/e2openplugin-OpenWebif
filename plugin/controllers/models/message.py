# -*- coding: utf-8 -*-

##############################################################################
#                        2022 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Screens.MessageBox import MessageBox
from Plugins.Extensions.OpenWebif.controllers.i18n import _

lastreply = None

MessageMapping = {
	0 : MessageBox.TYPE_YESNO,
	1 : MessageBox.TYPE_INFO,
	2 : MessageBox.TYPE_WARNING,
	3 : MessageBox.TYPE_ERROR
}


def messageReply(reply):
	global lastreply
	lastreply = reply


def sendMessage(session, message, ttype, timeout):
	global lastreply
	ttype = MessageMapping.get(ttype, MessageBox.TYPE_INFO)

	if ttype == MessageBox.TYPE_YESNO:
		lastreply = None
		session.openWithCallback(messageReply, MessageBox, message, type=ttype, timeout=timeout)
	else:
		session.open(MessageBox, message, type=ttype, timeout=timeout)

	return {
		"result": True,
		"message": _('Message sent successfully!')
	}


def getMessageAnswer():
	global lastreply
	reply = lastreply

	if reply is None:
		return {
			"result": False,
			"message": _('No answer in time')
		}

	return {
		"result": True,
		"message": _('Answer is YES!') if reply else _('Answer is NO!')
	}
