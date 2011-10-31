##############################################################################
#                         <<< ow_tpl >>>                           
#                                                                            
#                        2011 E2OpenPlugins          
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################




def tv_Tabs_Tpl():
	return """
<div id="content_main">
<div id="tabs">
	<ul>
		<li><a href="ajax/current.html">Current</a></li>
		<li><a href="ajax/bouquets.html">Bouquets</a></li>
		<li><a href="ajax/providers.html">Providers</a></li>
		<li><a href="ajax/satellites.html">Satellites</a></li>
		<li><a href="ajax/all.html">All</a></li>
	</ul>
</div>
</div>
"""
def hddinfo_Tpl(model, capacity, free):
# For some strange reason string substitution doesn't work here
	out = "<tr><td width='100%'><table cellspacing='0' class='infomain' ><tr><th colspan='2' class='infoHeader'>Hard disk model: " 
	out += model +"</th></tr><tr><td class='infoleft'>Capacity:</td><td class='inforight'>"
	out += capacity + "</td></tr><tr><td class='infoleft'>Free:</td><td class='inforight'>" 
	out += free + "</td></tr></table></td></tr>"
	return out

def tunersinfo_Tpl(typ, model):
	return """
<tr>
	<td class='infoleft'>%s:</td>
	<td class='inforight'>%s</td>
</tr>"
""" % (typ, model)

def current_tab_Tpl(name, provider, width, height):
	return """
This tab is work in progress:<br />
<br />
Current service: %s <br />
Provider: %s <br />
Resolution: %s x %s
<br /><br /><br />
""" % (name, provider, width, height)

def bouquet_link_Tpl(idx, bouquet):
	return """
<a href='ajax/bouquets_chan.html?id=%s'><img border='0' src='css/images/folder.png' alt='' />&nbsp;&nbsp;%s</a><br />
""" % (idx, bouquet)

def bouquet_chan_Tpl():
	return """
		<script type="text/javascript">
		var $tabs = $('#tabs').tabs();
		$('#cur-tab-link').click(function() {
    		$tabs.tabs('select', 0); // Fixme: dirty hack to refresh tab. If someone find a better way please fix.
		$tabs.tabs('select', 1); // Fixme
    		return false;
		});
		</script>
	<p><a href="#" id="cur-tab-link"><img border='0' src='css/images/go-up.png' alt='' />  ... Back to Bouquets</a></p><hr />
"""


def provider_link_Tpl(idx, provider):
	return """
<a href='ajax/providers_chan.html?id=%s'><img border='0' src='css/images/folder.png' alt='' />&nbsp;&nbsp;%s</a><br />
""" % (idx, provider)

def provider_chan_Tpl():
	return """
		<script type="text/javascript">
		var $tabs = $('#tabs').tabs();
		$('#prov-tab-link').click(function() {
    		$tabs.tabs('select', 0); // Fixme: dirty hack to refresh tab. If someone find a better way please fix.
		$tabs.tabs('select', 2); // Fixme
    		return false;
		});
		</script>
	<p><a href="#" id="prov-tab-link"><img border='0' src='css/images/go-up.png' alt='' />  ... Back to Providers</a></p><hr />
"""

def satellite_chan_Tpl():
	return """
		<script type="text/javascript">
		var $tabs = $('#tabs').tabs();
		$('#sat-tab-link').click(function() {
    		$tabs.tabs('select', 0); // Fixme: dirty hack to refresh tab. If someone find a better way please fix.
		$tabs.tabs('select', 3); // Fixme
    		return false;
		});
		</script>
	<p><a href="#" id="sat-tab-link"><img border='0' src='css/images/go-up.png' alt='' />  ... Back to Satellites</a></p><hr />
"""

def satellite_link_Tpl(idx, satellite):
	return """
<a href='ajax/satellites_chan.html?id=%s'><img border='0' src='css/images/folder.png' alt='' />&nbsp;&nbsp;%s</a><br />
""" % (idx, satellite)

def channels_link_Tpl(channel):
	return """
<a href='#' onClick=\"alert('Sorry, Zap function not yet implemented.');return false\">%s</a><br />
""" % (channel)