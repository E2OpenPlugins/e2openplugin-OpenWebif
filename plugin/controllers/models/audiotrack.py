# -*- coding: utf-8 -*-

from Tools.ISO639 import LanguageCodes

def getAudioTracks(session):
	service = session.nav.getCurrentService()
	audio = service and service.audioTracks()
	ret = { "tracklist": [], "result": False }
	if audio is not None and service is not None:
		current = audio.getCurrentTrack()
		for i in range(0, audio.getNumberOfTracks()):
			track = audio.getTrackInfo(i)
			languages = track.getLanguage().split('/')
			language = ""
			for lang in languages:
				if len(language) > 0:
					language += " / "

				if LanguageCodes.has_key(lang):
					language += LanguageCodes[lang][0]
				else:
					language += lang

			description = track.getDescription()
			if description:
				description += " (" + language + ")"
			else:
				description = language

			ret["result"] = True
			ret["tracklist"].append({
				"description": description,
				"index": i,
				"pid": track.getPID(),
				"active": i == current
			})

	return ret

def setAudioTrack(session, id):
	service = session.nav.getCurrentService()
	audio = service and service.audioTracks()
	if audio is not None and service is not None:
		if audio.getNumberOfTracks() > id and id >= 0:
			audio.selectTrack(id)
			return { "result": True }

	return { "result": False }
