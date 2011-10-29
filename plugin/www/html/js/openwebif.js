/*  OpenWebif JavaScript 
 *  2011 E2OpenPlugins
 *
 *  This file is open source software; you can redistribute it and/or modify  
 *    it under the terms of the GNU General Public License version 2 as      
 *              published by the Free Software Foundation.                  
 *
 *--------------------------------------------------------------------------*/

$.fx.speeds._default = 1000;
$(function() {
	$( "#tabs" ).tabs({
		ajaxOptions: {
			cache: false,
			error: function( xhr, status, index, anchor ) {
				$( anchor.hash ).html(
					"[Ow_debug].... this tab is loading slowly" );
			}
		},
		load: function(event, ui) {
        		$('a', ui.panel).click(function() {
				var splittedURL = this.href.split(/\/+/g); var path = splittedURL[splittedURL.length-1];
				if (path == 'box_info.html') {
	            			$(ui.panel).load(this.href);
        	    			return false;
				}
        		});
    		}
		
	});
	$( "#dialog" ).dialog({
		autoOpen: false,
		show: "fade",
		hide: "explode",
		buttons: {
			"Ok": function() { 
				$(this).dialog("close");
			} 
		}
	});
	// Dialog Link
	$('#dialog_link').click(function(){
		$('#dialog').dialog('open');
		return false;
	});


});