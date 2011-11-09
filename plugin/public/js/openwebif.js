/*  OpenWebif JavaScript 
 *  2011 E2OpenPlugins
 *
 *  This file is open source software; you can redistribute it and/or modify  
 *    it under the terms of the GNU General Public License version 2 as      
 *              published by the Free Software Foundation.                  
 *
 *--------------------------------------------------------------------------*/

$.fx.speeds._default = 1000;
var loadspinner = "<div id='spinner' ><img src='../images/spinner.gif' alt='loading...' /></div>"
$(function() {
	

	$( "#tvbutton" ).buttonset();
	

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
	
	$('#tvbutton0').click(function(){
		 $("#tvcontent").load("ajax/current");
	});
	$('#tvbutton1').click(function(){
		 $("#tvcontent").html(loadspinner).load("ajax/bouquets");
	});
	$('#tvbutton2').click(function(){
		 $("#tvcontent").html(loadspinner).load("ajax/providers");
	});
	$('#tvbutton3').click(function(){
		 $("#tvcontent").load("ajax/satellites");
	});
	$('#tvbutton4').click(function(){
		 $("#tvcontent").html(loadspinner).load("ajax/channels");
	});

});

function dialog_notyet(){
	$('#dialog').dialog('open');
	return false;
}

function load_tvcontent(url) {
	$("#tvcontent").load(url);
	return false;
}

function load_tvcontent_spin(url) {
	$("#tvcontent").html(loadspinner).load(url);
	return false;
}

function load_maincontent(url) {
	$("#content").load(url);
	return false;
}

function webapi_execute(url) {
	var jqxhr = $.ajax( url )
//    	.done(function() { alert(jqxhr.responseXml); })
	return false;
}

function toggle_chan_des(obj, url) {
	var iddiv = "#" + obj;
	$(iddiv).load(url);
	$(iddiv).toggle('blind', '', '500');
	
}


