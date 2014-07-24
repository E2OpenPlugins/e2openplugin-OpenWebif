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
var mutestatus = 0;
var lastcontenturl = null;

$(function() {
	
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

	$('#volimage').click(function(){
		if (mutestatus == 0) {
			mutestatus = 1;
			$("#volimage").attr("src","/images/volume_mute.png");
		} else  {
			mutestatus = 0;
			$("#volimage").attr("src","/images/volume.png");
		}
		$.ajax("web/vol?set=mute")
	});
	
	getStatusInfo();
	setInterval("getStatusInfo()", 15000);
});

$(function() {
	$( "#slider" ).slider({
		
		range: "min",
		min: 0,
		max: 100,
		value: 40,
		slide: function( event, ui ) {
			$( "#amount" ).val( ui.value );
		},
		stop: function( event, ui ) {	
			if ( ui.value == 0) {
				$("#volimage").attr("src","/images/volume_mute.png");
			} else  {
				$("#volimage").attr("src","/images/volume.png");
			} 
			var url = "web/vol?set=set" + ui.value;
			var jqxhr = $.ajax( url )
			return false;
		}
	});
	$( "#amount" ).val( $( "#slider" ).slider( "value" ) );
});


(function($) {
    var defaults = {
        height: 500,
        width: 500,
        toolbar: false,
        scrollbars: false,
        status: false,
        resizable: false,
        left: 0,
        top: 0,
        center: true,
        createNew: true,
        location: false,
        menubar: false,
        onUnload: null
    };

    $.popupWindow = function(url, opts) {
        var options = $.extend({}, defaults, opts);
        if (options.center) {
            options.top = ((screen.height - options.height) / 2) - 50;
            options.left = (screen.width - options.width) / 2;
        }

        var params = [];
        params.push('location=' + (options.location ? 'yes' : 'no'));
        params.push('menubar=' + (options.menubar ? 'yes' : 'no'));
        params.push('toolbar=' + (options.toolbar ? 'yes' : 'no'));
        params.push('scrollbars=' + (options.scrollbars ? 'yes' : 'no'));
        params.push('status=' + (options.status ? 'yes' : 'no'));
        params.push('resizable=' + (options.resizable ? 'yes' : 'no'));
        params.push('height=' + options.height);
        params.push('width=' + options.width);
        params.push('left=' + options.left);
        params.push('top=' + options.top);

        var random = new Date().getTime();
        var name = options.createNew ? 'popup_window_' + random : 'popup_window';
        var win = window.open(url, name, params.join(','));

        if (options.onUnload && typeof options.onUnload === 'function') {
            var unloadInterval = setInterval(function() {
                if (!win || win.closed) {
                    clearInterval(unloadInterval);
                    options.onUnload();
                }
            }, 250);
        }

        if (win && win.focus) win.focus();

        return win;
    };
})(jQuery);


$(function() {
	$( ".epgsearch button:first" ).button({
            icons: {
                primary: "ui-icon-search"
            }
        })
});

function initJsTranslation(strings) {
	tstr_add_timer = strings.add_timer;
	tstr_close = strings.cancel;
	tstr_del_timer = strings.delete_timer_question;
	tstr_del_movie = strings.delete_movie_question;
	tstr_done = strings.done;
	tstr_edit_timer = strings.edit_timer;
	tstr_hour = strings.hour;
	tstr_save = strings.save;
	tstr_minute = strings.minute;
	tstr_nothing_play = strings.nothing_play;
	tstr_now = strings.now;
	tstr_on = strings.on
	tstr_rec_status = strings.rec_status
	tstr_standby = strings.standby
	tstr_start_after_end = strings.start_after_end;
	tstr_time = strings.time;
	tstr_zap_to = strings.zap_to
	
	tstr_january = strings.month_01;
	tstr_february = strings.month_02;
	tstr_march = strings.month_03;
	tstr_april = strings.month_04;
	tstr_may = strings.month_05;
	tstr_june = strings.month_06;
	tstr_july = strings.month_07;
	tstr_august = strings.month_08;
	tstr_september = strings.month_09;
	tstr_october = strings.month_10;
	tstr_november = strings.month_11;
	tstr_december = strings.month_12;
	
	tstr_monday = strings.monday;
	tstr_tuesday = strings.tuesday;
	tstr_wednesday = strings.wednesday;
	tstr_thursday = strings.thursday;
	tstr_friday = strings.friday;
	tstr_saturday = strings.saturday;
	tstr_sunday = strings.sunday;
	
	tstr_mo = strings.mo;
	tstr_tu = strings.tu;
	tstr_we = strings.we;
	tstr_th = strings.th;
	tstr_fr = strings.fr;
	tstr_sa = strings.sa;
	tstr_su = strings.su;
}

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
	if (lastcontenturl != url) {
		$("#content_container").load(url);
		lastcontenturl = url
	}
	return false;
}

function load_maincontent_spin(url) {
	if (lastcontenturl != url) {
		$("#content_container").html(loadspinner).load(url);
		lastcontenturl = url
	}
	return false;
}

function webapi_execute(url, callback) {
	var jqxhr = $.ajax( url )
    	.done(function() { 
    		if (typeof callback !== 'undefined') {
    			callback();
    		}
    		// alert(jqxhr.responseXml); 
    	});
	return false;
}

function toggle_chan_des(evId, sRef, idp) {
	var url = 'ajax/eventdescription?sref=' + escape(sRef) + '&idev=' + evId;
	var iddiv = "#" + idp;
	$(iddiv).load(url);
	$(iddiv).slideToggle(200);
}

function open_epg_pop(sRef) {
	var url = 'ajax/epgpop?sref=' + escape(sRef);
	$.popupWindow(url, {
		height: 500,
		width: 900,
		toolbar: false,
		scrollbars: true,
	});	
}

function open_epg_search_pop() {
	var spar = $("#epgSearch").val();
	var url = "ajax/epgpop?sstr=" + encodeURIComponent(spar);
	url=url.replace(/%C3%BC/g,'%FC').replace(/%C3%9C/g,'%FC').replace(/%C3%A4/g,'%E4').replace(/%C3%84/g,'%E4').replace(/%C3%B6/g,'%F6').replace(/%C3%96/g,'%F6').replace(/%C3%9F/g,'%DF');
	$.popupWindow(url, {
		height: 500,
		width: 900,
		toolbar: false,
		scrollbars: true,
	});
	$("#epgSearch").val("");
}

function addTimerEvent(sRef, eventId) {
	webapi_execute("/api/timeraddbyeventid?sRef=" + sRef + "&eventid=" + eventId);
}

function toggleTimerStatus(sRef, begin, end) {
	var url="/api/timertogglestatus?";
	var data = { sRef: sRef, begin: begin, end: end };
	$.getJSON(url, data, function(result){
		$('#img-'+begin+'-'+end).attr("src", result['disabled'] ? "/images/ico_disabled.png" : "/images/ico_enabled.png");
	});
}

function deleteTimer(sRef, begin, end, title) {
	var answer = confirm(tstr_del_timer + ": " + title);
	if (answer == true) {
		webapi_execute("/api/timerdelete?sRef=" + sRef + "&begin=" + begin + "&end=" + end, 
			function() { $('#'+begin+'-'+end).remove(); } 
		);
	}
}

function cleanupTimer() {
	webapi_execute("/api/timercleanup", function() { load_maincontent('/ajax/timers'); });
}

function deleteMovie(sRef, divid, title) {
	var answer = confirm(tstr_del_movie + ": " + title);
	if (answer == true) {
		webapi_execute("/api/moviedelete?sRef=" + sRef);
		// TODO: check the api result first
		$('#' + divid).remove();
	}
}

function zapChannel(sRef, sname) {
	var url = '/api/zap?sRef=' + escape(sRef);
	$.getJSON(url, function(result){
		$("#osd").html(tstr_zap_to + ': ' + sname);
		$("#osd_bottom").html(" ");
	});
}

function toggleStandby() {
	webapi_execute('api/powerstate?newstate=0');
	setTimeout(getStatusInfo, 1500);
}

function getStatusInfo() {
	$.ajaxSetup({ cache: false });
	$.getJSON('/api/statusinfo')
	.success(function(statusinfo) {
		// Set Volume
		$("#slider").slider("value", statusinfo['volume']);
		$("#amount").val(statusinfo['volume']);
		
		// Set Mute Status
		if (statusinfo['muted'] == true) {
			mutestatus = 1;
			$("#volimage").attr("src","/images/volume_mute.png");
		} else {
			mutestatus = 0;
			$("#volimage").attr("src","/images/volume.png");
		}

		if (statusinfo['currservice_station']) {
			$("#osd").html("<span style='color:#EA7409;font-weight:bold;'>" + statusinfo['currservice_station'] + "</span>&nbsp;&nbsp;" + statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + "&nbsp;&nbsp;" + statusinfo['currservice_name']);
			$("#osd_bottom").html(statusinfo['currservice_description']);
		} else {
			$("#osd").html(tstr_nothing_play);
			$("#osd_bottom").html('');
		}
		var status = "";
		if (statusinfo['isRecording'] == 'true') {
			var timercall = "load_maincontent('ajax/timers'); return false;";
			status = "<a href='#' onClick='load_maincontent(\"ajax/timers\"); return false;'><img src='../images/ico_rec.png' title='" + tstr_rec_status + "' alt='" + tstr_rec_status + "' /></a>";
		}
		if (statusinfo['inStandby'] == 'true') {
			status = status + "<a href='#' onClick='toggleStandby();return false'><img src='../images/ico_standby.png' title='" + tstr_on + "' alt='" + tstr_standby + "'/></a>";
		} else {
			status = status + "<a href='#' onClick='toggleStandby();return false'><img src='../images/ico_on.png' title='" + tstr_standby + "' alt='" + tstr_on + "'/></a>";
		}
		$("#osd_status").html(status);
	})
	.error(function() {
		$("#osd, #osd_bottom").html("");
	});
}

var screenshotMode = 'all';

function grabScreenshot(mode) {
	$('#screenshotspinner').show();
	$('#screenshotimage').hide();
	
	$('#screenshotimage').load(function(){
	  $('#screenshotspinner').hide();
	  $('#screenshotimage').show();
	});

	if (mode != "auto")
		screenshotMode = mode;
	else
		mode = screenshotMode;
	
	timestamp = new Date().getTime();
	if (($('#screenshotRefreshHD').is(':checked')))
		$('#screenshotimage')
			.attr("src",'/grab?format=jpg&mode=' + mode + '&timestamp=' + timestamp);
	else
		$('#screenshotimage')
			.attr("src",'/grab?format=jpg&r=700&mode=' + mode + '&timestamp=' + timestamp);
	$('#screenshotimage').attr("width",700);
}

function getMessageAnswer() {
	$.getJSON('/api/messageanswer', function(result){
		$('#messageSentResponse').html(result['message']);
		$('#messageSentResponse_hsa').html(result['message']);
	});
}

var MessageAnswerCounter=0;

function countdowngetMessage() {
	MessageAnswerCounter--;
// TODO: the default answer is yes and for this case we stop the timeout two seconds before
// Bad Workaround but it works
	if(MessageAnswerCounter<3) { 
		getMessageAnswer();
		return;
	}
	$('#messageSentResponse').html('Waiting for Answer...'+MessageAnswerCounter);
	$('#messageSentResponse_hsa').html('Esperando Respuesta... '+MessageAnswerCounter);
	setTimeout(countdowngetMessage, 1000);
}

function sendMessage() {
	var text = $('#messageText').val();
	var type = $('#messageType').val();
	var timeout = $('#messageTimeout').val();

	$.getJSON('/api/message?text=' + text + '&type=' + type + '&timeout=' + timeout, function(result){
		$('#messageSentResponse').html(result['message']);
		$('#messageSentResponse_hsa').html(result['message']);
		if(type==0)
		{
			MessageAnswerCounter=timeout;
			setTimeout(countdowngetMessage, 1000);
		}
	});
	
}

function toggleMenu(name) {
	var expander_id = "#leftmenu_expander_" + name
	var container_id = "#leftmenu_container_" + name
	if ($(expander_id).hasClass("leftmenu_icon_collapse")) {
		$(expander_id).removeClass("leftmenu_icon_collapse");
		$(container_id).show('fast')
		webapi_execute("/api/expandmenu?name=" + name)
	}
	else {
		$(expander_id).addClass("leftmenu_icon_collapse");
		$(container_id).hide('fast')
		webapi_execute("/api/collapsemenu?name=" + name)
	}
}

// keep checkboxes syncronized
$(function() {
	$("input[name=remotegrabscreen]").click(function(evt) {
		$('input[name=remotegrabscreen]').attr('checked', evt.currentTarget.checked);
		webapi_execute("/api/remotegrabscreenshot?checked=" + evt.currentTarget.checked);
	});
});

$(function() {
	$("input[name=zapstream]").click(function(evt) {
		$('input[name=zapstream]').attr('checked', evt.currentTarget.checked);
		webapi_execute("/api/zapstream?checked=" + evt.currentTarget.checked);
	});
});

var shiftbutton = false;
$(window).keydown(function(evt) {
	if (evt.which == 16) { 
		shiftbutton = true;
	}
}).keyup(function(evt) {
	if (evt.which == 16) { 
		shiftbutton = false;
	}
});

function callScreenShot(){
	if ($('input[name=remotegrabscreen]').is(':checked'))
	{
		if (lastcontenturl == 'ajax/screenshot')
			grabScreenshot(screenshotMode);
		else
			load_maincontent('ajax/screenshot');
	}
}

var grabTimer = 0;
function pressMenuRemote(code) {
	if (shiftbutton)
		webapi_execute("/api/remotecontrol?type=long&command=" + code);
	else
		webapi_execute("/api/remotecontrol?command=" + code);
	if (grabTimer > 0)
		clearTimeout(grabTimer);
	grabTimer = setTimeout("callScreenShot()", 1000);
}

function toggleFullRemote() {
	$("#menucontainer").toggle();
	$("#remotecontainer").toggle();
}

function saveConfig(key, value) {
	webapi_execute("/api/saveconfig?key=" + escape(key) + "&value=" + escape(value));
	if (key == "config.usage.setup_level") {
		// TODO: refresh the menu box with new sections list
		$("#content_container").load(lastcontenturl);
	}
}

function numberTextboxKeydownFilter(event) {
	if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9)
		return;
		
	if ((event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105))
		event.preventDefault();
}

/* Timer management start */

var current_serviceref;
var current_begin;
var current_end;
var timeredit_initialized = false;

function initTimerEdit() {
	$.ajax({
		async: false,
		url: "/api/getallservices",
		success: function(data) {
			services = $.parseJSON(data);
			if (services.result) {
				$('#bouquet_select')
					.find('option')
					.remove()
					.end();
					
				for (var id in services.services) {
					service = services.services[id];
					for (var id2 in service.subservices) {
						subservice = service.subservices[id2];
						$('#bouquet_select')
							.append($("<option></option>")
								.attr("value", subservice.servicereference)
								.text(subservice.servicename));
					}
				}
			}
		}
	});
	
	$.ajax({
		async: false,
		url: "/api/getlocations",
		success: function(data) {
			locs = $.parseJSON(data);
			if (locs.result) {
				$('#dirname')
					.find('option')
					.remove()
					.end();
					
				$('#dirname')
					.append($("<option></option>")
						.attr("value", "None")
						.text("Default"));
						
				for (var id in locs.locations) {
					loc = locs.locations[id];
					$('#dirname')
						.append($("<option></option>")
							.attr("value", loc)
							.text(loc));
				}
			}
		}
	});
	
	$.ajax({
		async: false,
		url: "/api/gettags",
		success: function(data) {
			tags = $.parseJSON(data);
			if (tags.result) {
				for (var id in tags.tags) {
					tag = tags.tags[id];
					$('#tagsnew')
						.append("<input type='checkbox' name='tagsnew' value='"+tag+"' id='tag_"+tag+"'/><label for='tag_"+tag+"'>"+tag+"</label>");
				}
				
				$('#tagsnew').buttonset();

			}
		}
	});
	
	timeredit_initialized = true;
}

function editTimer(serviceref, begin, end) {
	serviceref=decodeURI(serviceref);
	current_serviceref = serviceref;
	current_begin = begin;
	current_end = end;
	
	if (!timeredit_initialized)
		initTimerEdit();
	
	$.ajax({
		async: false,
		url: "/api/timerlist",
		success: function(data) {
			timers = $.parseJSON(data);
			if (timers.result) {
				for (var id in timers.timers) {
					timer = timers.timers[id];
					if (timer.serviceref == serviceref &&
						Math.round(timer.begin) == Math.round(begin) &&
						Math.round(timer.end) == Math.round(end)) {
							$('#timername').val(timer.name);
							$('#description').val(timer.description);
							$('#bouquet_select').val(timer.serviceref);
							$('#dirname').val(timer.dirname);
							$('#enabled').prop("checked", timer.disabled == 0);
							$('#justplay').prop("checked", timer.justplay);
							$('#afterevent').val(timer.afterevent);
							$('#errorbox').hide();

							var flags=timer.repeated;
							for (var i=0; i<7; i++) {
								$('#day'+i).attr('checked', ((flags & 1)==1));
								flags >>= 1;
							}
							$('#repeatdays').buttonset('refresh');
							
							$('#tagsnew').find('input').attr('checked',false);
							var tags = timer.tags.split(' ');
							for (var i=0; i<tags.length; i++) {
								$('#tag_'+tags[i]).attr('checked', true);
							}
							$('#tagsnew').buttonset('refresh');
							
							$('#timerbegin').datetimepicker('setDate', (new Date(Math.round(timer.begin) * 1000)));
							$('#timerend').datetimepicker('setDate', (new Date(Math.round(timer.end) * 1000)));
							
							$('#editTimerForm').dialog("open");
							$('#editTimerForm').dialog("option", "title", tstr_edit_timer + " - " + timer.name);
							break;
						}
				}
			}
		}
	});
}

function addTimer(evt) {
	current_serviceref = '';
	current_begin = -1;
	current_end = -1;

	var begin = -1;
	var end = -1;
	var serviceref = '';
	var title = '';
	var desc = '';
	var margin_before = 0;
	var margin_after = 0;
	
	if (typeof evt !== 'undefined') {
		begin = evt.begin;
		end = evt.begin+evt.duration;
		serviceref = evt.sref;
		title = evt.title;
		desc = evt.shortdesc;
		margin_before = evt.recording_margin_before;
		margin_after = evt.recording_margin_after;
	}
	
	if (!timeredit_initialized)
		initTimerEdit();
		
	$('#timername').val(title);
	$('#description').val(desc);
	$('#dirname').val("None");
	$('#enabled').prop("checked", true);
	$('#justplay').prop("checked", false);
	$('#afterevent').val(3);
	$('#errorbox').hide();

	for (var i=0; i<7; i++) $('#day'+i).attr('checked', false);
	$('#repeatdays').buttonset('refresh');
	
	$('#tagsnew').find('input').attr('checked',false);
	$('#tagsnew').buttonset('refresh');

	var begindate = begin !== -1 ? new Date( (Math.round(begin) - margin_before*60) * 1000) : new Date();
	$('#timerbegin').datetimepicker('setDate', begindate);
	var enddate = end !== -1 ? new Date( (Math.round(end) + margin_after*60) * 1000) : new Date(begindate.getTime() + (60*60*1000));
	$('#timerend').datetimepicker('setDate', enddate);

	$('#bouquet_select').val(serviceref);
	
	$('#editTimerForm').dialog("open");
	$('#editTimerForm').dialog("option", "title", tstr_add_timer);
	$('#editTimerForm').dialog("option", "height", "auto");
}

/* Timer management end */
