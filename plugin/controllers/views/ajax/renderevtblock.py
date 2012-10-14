from time import localtime, strftime

class renderEvtBlock:

    def __init__(self):
        self.template = """
        <div class="event" js:ref="%s" js:id="%s">
	    	<div style="width:40px; float:left; padding: 0 3px">%s</div>
	    	<div style="width:144px; float:left">
                <div class="title">%s</div>%s
            </div>
            <div style="clear:left"></div>
        </div>
        """

    def render(self,event):
        if event['title'] != event['shortdesc']:
            shortdesc = '<div class="desc">%s</div>' % (event['shortdesc'])
        else:
            shortdesc = ''
        return self.template % (
            event['ref'],
            event['id'],
            strftime("%H:%M", localtime(event['begin_timestamp'])),
            event['title'],
            shortdesc)
