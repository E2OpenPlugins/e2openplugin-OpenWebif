# -*- coding: utf-8 -*-
from time import localtime, strftime
from six.moves.urllib.parse import quote
from Plugins.Extensions.OpenWebif.controllers.i18n import tstrings


class renderEvtBlock:

    def __init__(self):
        self.template = """
        <div class="event" data-ref="{ref}" data-id="{id}">
            <div style="width:40px; float:left; padding: 0 3px">{hourmin}{evtsymbol}</div>
            <div style="width:144px; float:left">
                <div class="title">{title}</div>{shortdesc}
            </div>
            <div style="clear:left;height:2px;{timerbar}"></div>
        </div>
        """

    def render(self, event):
        if event['title'] != event['shortdesc']:
            shortdesc = '<div class="desc">%s</div>' % (event['shortdesc'])
        else:
            shortdesc = ''

        if event['timerStatus'] != '':
            text = event['timer']['text']
            timerEventSymbol = '<div class="%s">%s</div>' % (event['timerStatus'], text)
            timerbar = "background-color:red;"
        else:
            timerEventSymbol = ''
            timerbar = ''

        return self.template.format(
            ref=quote(event['ref'], safe=' ~@#$&()*!+=:;,.?/\''),
            id=event['id'],
            hourmin=strftime("%H:%M", localtime(event['begin_timestamp'])),
            evtsymbol=timerEventSymbol,
            title=event['title'],
            shortdesc=shortdesc, 
            timerbar=timerbar)
