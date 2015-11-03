//******************************************************************************
//* openwebif.js: openwebif base module
//* Version 1.0
//******************************************************************************
//* Copyright (C) 2011-2014 E2OpenPlugins
//*
//* V 1.0 - Initial Version
//* V 1.1 - add movie move and rename
//*
//* Authors: skaman <sandro # skanetwork.com>
//* 		 meo
//* 		 Homey-GER
//* 		 Cimarast
//* 		 Joerg Bleyel <jbleyel # gmx.net>
//* 		 Schimmelreiter
//* 		 plnick
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************

$.fx.speeds._default = 1000;
var loadspinner = "<div id='spinner' ><img src='../images/spinner.gif' alt='loading...' /></div>",mutestatus = 0,lastcontenturl = null,screenshotMode = 'all',MessageAnswerCounter=0,shiftbutton = false,grabTimer = 0,at2add = null;

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
		if (mutestatus === 0) {
			mutestatus = 1;
			$("#volimage").attr("src","/images/volume_mute.png");
		} else  {
			mutestatus = 0;
			$("#volimage").attr("src","/images/volume.png");
		}
		$.ajax("web/vol?set=mute");
	});
	
	getStatusInfo();
	setInterval("getStatusInfo()", 15000);

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
			var jqxhr = $.ajax( "web/vol?set=set" + ui.value );
			return false;
		}
	});
	$( "#amount" ).val( $( "#slider" ).slider( "value" ) );
	
	$( ".epgsearch button:first" ).button({
		icons: {
				primary: "ui-icon-search"
				}
		});
});


(function($) {
	var defaults = {height: 500,width: 500,toolbar: false,scrollbars: false,status: false,resizable: false,left: 0,top: 0,center: true,createNew: true,location: false,menubar: false,onUnload: null};

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

	if (win && win.focus) { win.focus(); }
		return win;
	};
})(jQuery);

function initJsTranslation(strings) {
	tstr_add_timer = strings.add_timer;
	tstr_cancel = strings.cancel;
	tstr_close = strings.close;
	tstr_del_timer = strings.delete_timer_question;
	tstr_del_autotimer = strings.at_delete_autotimer_question;
	tstr_del_recording = strings.delete_recording_question;
	tstr_ren_recording = strings.rename_recording_question;
	tstr_done = strings.done;
	tstr_edit_timer = strings.edit_timer;
	tstr_hour = strings.hour;
	tstr_save = strings.save;
	tstr_minute = strings.minute;
	tstr_nothing_play = strings.nothing_play;
	tstr_now = strings.now;
	tstr_on = strings.on;
	tstr_reboot_box = strings.reboot_box
	tstr_rec_status = strings.rec_status;
	tstr_restart_gui = strings.restart_gui
	tstr_standby = strings.standby;
	tstr_start_after_end = strings.start_after_end;
	tstr_time = strings.time;
	tstr_zap_to = strings.zap_to;
	
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
	
	tstr_loading = strings.loading;
	tstr_stream = strings.stream;
	tstr_transcoded = strings.transcoded;
	
	tstr_send_message = strings.send_message;
	tstr_sent_wait = strings.sent_wait;
	tstr_epgsearch = strings.epgsearch;
	
	tstr_bqe_del_channel_question = strings.bqe_del_channel_question;
	tstr_bqe_del_bouquet_question = strings.bqe_del_bouquet_question;
	tstr_bqe_name_bouquet = strings.bqe_name_bouquet;
	tstr_bqe_name_marker = strings.bqe_name_marker;
	tstr_bqe_rename_bouquet = strings.bqe_rename_bouquet;
	tstr_bqe_rename_marker = strings.bqe_rename_marker;
	tstr_bqe_filename = strings.bqe_filename;
	tstr_bqe_restore_question = strings.bqe_restore_question;
	
	tstr_timerlist = strings.timer_list;
	tstr_timerpreview = strings.timer_preview;
	tstr_timernewname = strings.timer_newname;
	
	tstr_open_in_new_window = strings.open_in_new_window;
}

function wait_for_openwebif() {
	var restartCheck = window.setInterval(function() {
		$.getJSON('/api/statusinfo').success(function() {
			window.clearInterval(restartCheck);
			$("#modaldialog").dialog('close');
			location.reload();
		});
	}, 2000);
}

function handle_power_state_dialog(new_power_state) {
	var timeout = 0;
	$("#modaldialog").dialog('close');
	if ( new_power_state === 2 ) {
		load_info_dialog('ajax/rebootdialog',tstr_reboot_box);
		wait_for_openwebif();
		timeout = 1000 ;
	} else if ( new_power_state === 3 ) {
		load_info_dialog('ajax/rebootdialog',tstr_restart_gui);
		wait_for_openwebif();
		timeout = 1000 ;
	}
	setTimeout(function () {
		webapi_execute('api/powerstate?newstate=' + new_power_state);
	}, timeout);
}

function load_info_dialog(url,title,w,h){
	var width = 'auto',height='auto';
	if (typeof w !== 'undefined')
		width = w;
	if (typeof h !== 'undefined')
		height = h;

	$.ajax({
		url: url,
		success: function(data) {
			$("#modaldialog").html(data).dialog({
				modal:true,
				title:title,
				autoOpen:true,
				width:width,
				height:height,
				close: function(event, ui) { 
					$(this).dialog('destroy');
				},
			});
		},error: function(){
			alert('error! Loading Page');
		}
		
	});
}


function load_dm_spinner(url,title,w,h,buttons){
	var width = 'auto',height='auto';
	if (typeof w !== 'undefined')
		width = w;
	if (typeof h !== 'undefined')
		height = h;

	$("#modaldialog").html(loadspinner).dialog({
		modal:true,
		title:title,
		autoOpen:true,
		width:width,
		height:height,
		buttons:buttons,
		close: function(event, ui) { 
			$(this).dialog('destroy');
		},
		open: function() {
		$.ajax({
			url: url,
			success: function(data) {
				$("#modaldialog").html(data);
			}
			,error: function(){
				$("#modaldialog").html("error! Loading Page");
			}
		});
		$(this).siblings('.ui-dialog-buttonpane').find('button:eq(0)').focus(); 
		}
	});
}

function load_dm(url,title,w,h){
	var buttons = {}
	buttons[tstr_close] = function() { $(this).dialog("close");};
	var width = 'auto',height='auto';
	if (typeof w !== 'undefined')
		width = w;
	if (typeof h !== 'undefined')
		height = h;

	$.ajax({
		url: url,
		success: function(data) {
			$("#modaldialog").html(data).dialog({
				modal:true,
				title:title,
				autoOpen:true,
				width:width,
				height:height,
				buttons:buttons,
				close: function(event, ui) { 
					$(this).dialog('destroy');
				},
				open: function() {
					$(this).siblings('.ui-dialog-buttonpane').find('button:eq(0)').focus(); 
				}
			});
		},error: function(){
			alert('error! Loading Page');
		}
		
	});
}

function load_message_dm(url,title){
	var buttons = {}
	buttons[tstr_send_message] = function() { sendMessage();};
	buttons[tstr_cancel] = function() { $(this).dialog("close");};

	$.ajax({
		url: url,
		success: function(data) {
			$("#modaldialog").html(data).dialog({
				modal:true,
				title:title,
				autoOpen:true,
				width:'auto',
				buttons: buttons,
				close: function(event, ui) { 
					$(this).dialog('destroy');
				}
			});
		}
	});
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
		lastcontenturl = url;
	}
	return false;
}

function load_maincontent_spin(url) {
	if (lastcontenturl != url) {
		var sp = '<div id="content_main" style="min-height: 500px;">'+loadspinner+'</div>';
		$("#content_container").html(sp).load(url);
		lastcontenturl = url;
	}
	return false;
}

function webapi_execute(url, callback) {
	var jqxhr = $.ajax( url ).done(function() { 
    		if (typeof callback !== 'undefined') {
    			callback();
    		}
    	});
	return false;
}

function toggle_chan_des(evId, sRef, idp) {
	var url = 'ajax/eventdescription?sref=' + escape(sRef) + '&idev=' + evId;
	var iddiv = "#" + idp;
	$(iddiv).load(url);
	$(iddiv).slideToggle(200);
}

function open_epg_dialog(sRef,Name) {
	var url = "ajax/epgdialog?sref=" + escape(sRef);
	
	var w = $(window).width() -100;
	var h = $(window).height() -100;
	
	var buttons = {}
	buttons[tstr_close] = function() { $(this).dialog("close");};
	buttons[tstr_open_in_new_window] = function() { $(this).dialog("close"); open_epg_pop(sRef);};
	
	load_dm_spinner(url,Name,w,h,buttons);
}

function open_epg_pop(sRef) {
	var url = 'ajax/epgpop?sref=' + escape(sRef);
	$.popupWindow(url, {
		height: 500,
		width: 900,
		toolbar: false,
		scrollbars: true
	});	
}

function open_epg_search_dialog() {
	var spar = $("#epgSearch").val();
	var url = "ajax/epgdialog?sstr=" + encodeURIComponent(spar);
	$("#epgSearch").val("");
	
	var w = $(window).width() -100;
	var h = $(window).height() -100;
	
	var buttons = {}
	buttons[tstr_close] = function() { $(this).dialog("close");};
	buttons[tstr_open_in_new_window] = function() { $(this).dialog("close"); open_epg_search_pop(spar);};
	
	load_dm_spinner(url,tstr_epgsearch,w,h,buttons);
}

function open_epg_search_pop(spar) {
	var url = "ajax/epgpop?sstr=" + encodeURIComponent(spar);
	$.popupWindow(url, {
		height: 500,
		width: 900,
		toolbar: false,
		scrollbars: true
	});
}

function addTimerEvent(sRef, eventId) {
	webapi_execute("/api/timeraddbyeventid?sRef=" + sRef + "&eventid=" + eventId,
		function() {
			alert("Timer Added"); 
		} 
	);
}
function addTimerEventPlay(sRef, eventId) {
	webapi_execute("/api/timeraddbyeventid?sRef=" + sRef + "&eventid=" + eventId + "&eit=0&disabled=0&justplay=1&afterevent=3",
		function() {
			alert("Timer Added"); 
		} 
	);
}

function addEditTimerEvent(sRef, eventId) {
	var url="/api/event?sref=" + sRef + "&idev=" + eventId;
	$.getJSON(url, function(result){
		if (typeof result !== 'undefined' && typeof result.event !== 'undefined') {
			addTimer(result.event);
		}
		else
			alert("Event not found");
	});
}

function addAutoTimerEvent(sRef, sname, title ,begin, end) {
	at2add = {
			"name" : title,
			"from" : begin,
			"to" : end,
			"sref" : sRef,
			"sname" : sname
		};
		
		var atd=$('#atdialog');
		if (atd != 'undefined')
		{
			$("#content_container").load('/ajax/at', function() { 
				$("#atdialog").show(200).draggable();
			});
		}
		else {
		
		// open the autotimer edit view with a new autotimer
		load_maincontent('ajax/at');
		
		}
		$("#modaldialog").dialog('destroy');
		
}

function delTimerEvent(obj) {
	// TODO: get timerinfo from event
}

function toggleTimerStatus(sRef, begin, end) {
	var url="/api/timertogglestatus?";
	var data = { sRef: sRef, begin: begin, end: end };
	$.getJSON(url, data, function(result){
		var obj = $('#img-'+begin+'-'+end);
		obj.removeClass("ow_i_disabled");
		obj.removeClass("ow_i_enabled");
		obj.addClass(result['disabled'] ? "ow_i_disabled" : "ow_i_enabled");
	});
}

function deleteTimer(sRef, begin, end, title) {
	var t = decodeURIComponent(title);
	if (confirm(tstr_del_timer + ": " + t) === true) {
		webapi_execute("/api/timerdelete?sRef=" + sRef + "&begin=" + begin + "&end=" + end, 
			function() { $('#'+begin+'-'+end).remove(); } 
		);
	}
}

function cleanupTimer() {
	webapi_execute("/api/timercleanup", function() { load_maincontent('/ajax/timers'); });
}

function renameMovie(sRef, title) {
	var newname=prompt(tstr_ren_recording, title);
	if (newname && newname!=title){
		webapi_execute("/api/movierename?sRef=" + sRef+"&newname="+newname);
		// TODO: check the api result first
	}
}

function deleteMovie(sRef, divid, title) {
	if (confirm(tstr_del_recording + ": " + title) === true) {
		webapi_execute("/api/moviedelete?sRef=" + sRef);
		// TODO: check the api result first
		$('#' + divid).remove();
	}
}


function playRecording(sRef) {
	var sr = sRef.replace(/-/g,'%2D').replace(/_/g,'%5F').replace(/\//g,'%2F');
	// for debugging 
	console.debug(sr);
	var url = '/api/zap?sRef=' + sr;
	$.getJSON(url, function(result){
		$("#osd").html(" ");
		$("#osd_bottom").html(" ");
	});
}

function zapChannel(sRef, sname) {
	var url = '/api/zap?sRef=' + escape(sRef);
	$.getJSON(url, function(result){
		$("#osd").html(tstr_zap_to + ': ' + sname);
		$("#osd_bottom").html(" ");
	});
}

function toggleStandby() {
	if (shiftbutton) {
		webapi_execute('api/set_powerup_without_waking_tv');
	}
	webapi_execute('api/powerstate?newstate=0');
	setTimeout(getStatusInfo, 1500);
}

function getStatusInfo() {
	$.ajaxSetup({ cache: false });
	$.getJSON('/api/statusinfo').success(function(statusinfo) {
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

		if ((statusinfo['currservice_station']) && ((statusinfo['currservice_serviceref'].indexOf("1:0:1") !== -1) || (statusinfo['currservice_serviceref'].indexOf("1:134:1") !== -1))) {
			var stream = "";
			if (statusinfo['transcoding']) {
				stream += "<a href='#' onclick=\"jumper8001('" + statusinfo['currservice_serviceref'] + "', '" + statusinfo['currservice_station'] + "')\"; title='" + tstr_stream + ": " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream.png'></img></a>&nbsp;";
				stream += "<a href='#' onclick=\"jumper8002('" + statusinfo['currservice_serviceref'] + "', '" + statusinfo['currservice_station'] + "')\"; title='" + tstr_stream + " (" + tstr_transcoded + "): " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream02.png'></img></a>&nbsp;";
			} else {
				stream += "<a target='_blank' href='/web/stream.m3u?ref=" + statusinfo['currservice_serviceref'] + "&name=" + statusinfo['currservice_station'] + "' title='" + tstr_stream + ": " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream.png'></img></a>&nbsp;";
			}
			$("#osd").html(stream + "<span style='color:#EA7409;font-weight:bold'><a style='color:#EA7409;font-weight:bold;text-decoration:none;' href='#' onClick='load_maincontent(\"ajax/tv\");return false;'>" + statusinfo['currservice_station'] + "</a></span>&nbsp;&nbsp;" + statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + "&nbsp;&nbsp;" + "<a style='color:#ffffff;text-decoration:none;' href=\"#\" onclick=\"open_epg_pop('" + statusinfo['currservice_serviceref'] + "')\" title='" + statusinfo['currservice_fulldescription'] + "'>" + statusinfo['currservice_name'] + "</a>");
			$("#osd_bottom").html(statusinfo['currservice_description']);
		} else if ((statusinfo['currservice_station']) && ((statusinfo['currservice_serviceref'].indexOf("1:0:2") !== -1) || (statusinfo['currservice_serviceref'].indexOf("1:134:2") !== -1))) {
			var stream = "";
			stream += "<a target='_blank' href='/web/stream.m3u?ref=" + statusinfo['currservice_serviceref'] + "&name=" + statusinfo['currservice_station'] + "' title='" + tstr_stream + ": " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream.png'></img></a>&nbsp;";
			$("#osd").html(stream + "<span style='color:#EA7409;font-weight:bold;'>" + "<a style='color:#EA7409;font-weight:bold;text-decoration:none;' href='#' onClick='load_maincontent(\"ajax/radio\");return false;'>" + statusinfo['currservice_station'] + "</a></span>&nbsp;&nbsp;" + statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + "&nbsp;&nbsp;" + "<a style='color:#ffffff;text-decoration:none;' href=\"#\" onclick=\"open_epg_pop('" + statusinfo['currservice_serviceref'] + "')\" title='" + statusinfo['currservice_fulldescription'] + "'>" + statusinfo['currservice_name'] + "</a>");
			$("#osd_bottom").html(statusinfo['currservice_description']);
		} else if ((statusinfo['currservice_station']) && ((statusinfo['currservice_serviceref'].indexOf("1:0:0") !== -1))) {
			var stream = "";
			if (statusinfo['transcoding']) {
				stream += "<a href='#' onclick=\"jumper80('" + statusinfo['currservice_filename'] + "')\"; title='" + tstr_stream + ": " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream.png'></img></a>&nbsp;";
				stream += "<a href='#' onclick=\"jumper8003('" + statusinfo['currservice_filename'] + "')\"; title='" + tstr_stream + " (" + tstr_transcoded + "): " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream02.png'></img></a>&nbsp;";
			} else {
				stream += "<a target='_blank' href='/web/ts.m3u?file=" + statusinfo['currservice_filename'] + "' title='" + tstr_stream + ": " + statusinfo['currservice_station'] + "'><img src='../images/ico_stream.png'></img></a>&nbsp;";
			}
			$("#osd").html(stream + "<span style='color:#EA7409;font-weight:bold;'>" + statusinfo['currservice_station'] + "</span>&nbsp;&nbsp;" + statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + "&nbsp;&nbsp;" + statusinfo['currservice_name']);
			$("#osd_bottom").html(statusinfo['currservice_description']);
		} else if (statusinfo['currservice_station']) {
			$("#osd").html("<span style='color:#EA7409;font-weight:bold;'>" + statusinfo['currservice_station'] + "</span>&nbsp;&nbsp;" + statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + "&nbsp;&nbsp;" + statusinfo['currservice_name']);
			$("#osd_bottom").html(statusinfo['currservice_description']);
		} else {
			$("#osd").html(tstr_nothing_play);
			$("#osd_bottom").html('');
		}
		var status = "";
		if (statusinfo['isRecording'] == 'true') {
			var timercall = "load_maincontent('ajax/timers'); return false;";
			status = "<a href='#' onClick='load_maincontent(\"ajax/timers\"); return false;'><img src='../images/ico_rec.png' title='" + tstr_rec_status + statusinfo['Recording_list'] + "' alt='" + tstr_rec_status + "' /></a>";
		}
		status += "<a href='#' onClick='toggleStandby();return false'><img src='../images/ico_";
		if (statusinfo['inStandby'] == 'true') {
			status += "standby.png' title='" + tstr_on + "' alt='" + tstr_standby;
		} else {
			status += "on.png' title='" + tstr_standby + "' alt='" + tstr_on;
		}
		status += "' width='58' height='24' /></a>";
		$("#osd_status").html(status);
	}).error(function() {
		$("#osd, #osd_bottom").html("");
	});
}

function grabScreenshot(mode) {
	$('#screenshotspinner').show();
	
	$('#screenshotimage').load(function(){
	  $('#screenshotspinner').hide();
	});

	if (mode != "auto") {
		screenshotMode = mode;
	} else {
		mode = screenshotMode;
	}
	timestamp = new Date().getTime();
	if (($('#screenshotRefreshHD').is(':checked'))){
		$('#screenshotimage').attr("src",'/grab?format=jpg&mode=' + mode + '&timestamp=' + timestamp);
	} else {
		$('#screenshotimage').attr("src",'/grab?format=jpg&r=700&mode=' + mode + '&timestamp=' + timestamp);
	}
	$('#screenshotimage').attr("width",700);
}

function getMessageAnswer() {
	$.getJSON('/api/messageanswer', function(result){
		$('#messageSentResponse').html(result['message']);
	});
}

function countdowngetMessage() {
	MessageAnswerCounter--;
// TODO: the default answer is yes and for this case we stop the timeout two seconds before
// Bad Workaround but it works
	if(MessageAnswerCounter<3) { 
		getMessageAnswer();
		return;
	}
	$('#messageSentResponse').html(tstr_sent_wait + ' ' + MessageAnswerCounter);
	setTimeout(countdowngetMessage, 1000);
}

function sendMessage() {
	var text = $('#messageText').val();
	var type = $('#messageType').val();
	var timeout = $('#messageTimeout').val();

	$.getJSON('/api/message?text=' + text + '&type=' + type + '&timeout=' + timeout, function(result){
		$('#messageSentResponse').html(result['message']);
		if(type==0)
		{
			MessageAnswerCounter=timeout;
			setTimeout(countdowngetMessage, 1000);
		}
	});
	
}

function toggleMenu(name) {
	var expander_id = "#leftmenu_expander_" + name;
	var container_id = "#leftmenu_container_" + name;
	if ($(expander_id).hasClass("leftmenu_icon_collapse")) {
		$(expander_id).removeClass("leftmenu_icon_collapse");
		$(container_id).show('fast');
		webapi_execute("/api/expandmenu?name=" + name);
	}
	else {
		$(expander_id).addClass("leftmenu_icon_collapse");
		$(container_id).hide('fast');
		webapi_execute("/api/collapsemenu?name=" + name);
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

$(function() {
	$("input[name=epgsearchtype]").click(function(evt) {
		$('input[name=epgsearchtype]').attr('checked', evt.currentTarget.checked);
		webapi_execute("/api/epgsearchtype?checked=" + evt.currentTarget.checked);
	});
});

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
		if (lastcontenturl == 'ajax/screenshot') {
			grabScreenshot(screenshotMode);
		} else {
			load_maincontent('ajax/screenshot');
		}
	}
}

function pressMenuRemote(code) {
	if (shiftbutton) {
		webapi_execute("/api/remotecontrol?type=long&command=" + code);
	} else {
		webapi_execute("/api/remotecontrol?command=" + code);
	}
	if (grabTimer > 0) {
		clearTimeout(grabTimer);
	}
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
	if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9) {
		return;
	}
	if ((event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105)) {
		event.preventDefault();
	}
}

/* Timer management start */

var current_serviceref;
var current_begin;
var current_end;
var timeredit_initialized = false;
var timeredit_begindestroy = false;

function initTimerEdit() {
	$.ajax({
		async: false,
		url: "/api/getallservices",
		success: function(data) {
			services = $.parseJSON(data);
			if (services.result) {
				$('#bouquet_select').find('option').remove().end();
					
				for (var id in services.services) {
					service = services.services[id];
					for (var id2 in service.subservices) {
						subservice = service.subservices[id2];
						$('#bouquet_select').append($("<option></option>").attr("value", subservice.servicereference).text(subservice.servicename));
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
				$('#dirname').find('option').remove().end();
				$('#dirname').append($("<option></option>").attr("value", "None").text("Default"));
						
				for (var id in locs.locations) {
					loc = locs.locations[id];
					$('#dirname').append($("<option></option>").attr("value", loc).text(loc));
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
					$('#tagsnew').append("<input type='checkbox' name='tagsnew' value='"+tag+"' id='tag_"+tag+"'/><label for='tag_"+tag+"'>"+tag+"</label>");
				}
				$('#tagsnew').buttonset();
			}
		}
	});
	
	timeredit_initialized = true;
}

function checkVPS()
{
	if($('#vpsplugin_enabled').is(':checked')) {
		$('#vpsplugin_safemode').show();
		$('#has_vpsplugin2').show();
	}
	else {
		$('#vpsplugin_safemode').hide();
		$('#has_vpsplugin2').hide();
	}

}

function initTimerEditBegin()
{
	$('#timerbegin').datetimepicker({
		
		timeText: tstr_time,
		hourText: tstr_hour,
		minuteText: tstr_minute,
		currentText: tstr_now,
		closeText: tstr_done,
		monthNames: [tstr_january, tstr_february, tstr_march, tstr_april, tstr_may, tstr_june, tstr_july, tstr_august, tstr_september, tstr_october, tstr_november, tstr_december],
		dayNames: [tstr_sunday, tstr_monday, tstr_tuesday, tstr_wednesday, tstr_thursday, tstr_friday, tstr_saturday, tstr_sunday],
		dayNamesMin: [tstr_su, tstr_mo, tstr_tu, tstr_we, tstr_th, tstr_fr, tstr_sa, tstr_su],
		
		dateFormat: 'dd.mm.yy',
		timeFormat: 'HH:mm',
		onClose: function(dateText, inst) {
			if ($('#timerend').val() != '' &&
				$(this).datetimepicker('getDate') > $('#timerend').datetimepicker('getDate')) {
					$('#error').text(tstr_start_after_end);
					$('#errorbox').show();
			}
			else
				$('#errorbox').hide();
		}
	});
}

function editTimer(serviceref, begin, end) {
	serviceref=decodeURI(serviceref);
	current_serviceref = serviceref;
	current_begin = begin;
	current_end = end;
	
	if (!timeredit_initialized) {
		initTimerEdit();
	}
	
	if (timeredit_begindestroy) {
		initTimerEditBegin();
		timeredit_begindestroy=false;
	}

	
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
							if(timer.serviceref !== $('#bouquet_select').val()) {
								$('#bouquet_select').append($("<option></option>").attr("value", timer.serviceref).text(timer.servicename));
								$('#bouquet_select').val(timer.serviceref);
							}
							$('#dirname').val(timer.dirname);
							if(timer.dirname !== $('#dirname').val()) {
								current_location = "<option value='" + timer.dirname + "'>" + timer.dirname + "</option>";
								$('#dirname').append(current_location);
								$('#dirname').val(timer.dirname);
							}
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
							for (var j=0; j<tags.length; j++) {
								$('#tag_'+tags[j]).attr('checked', true);
							}
							$('#tagsnew').buttonset('refresh');
							
							$('#timerbegin').datetimepicker('setDate', (new Date(Math.round(timer.begin) * 1000)));
							$('#timerend').datetimepicker('setDate', (new Date(Math.round(timer.end) * 1000)));
							
							var r = (timer.state === 2);
							// don't allow edit some fields if running
							if(r) {
								$('#timerbegin').datetimepicker('destroy');
								timeredit_begindestroy=true;
								$('#timerbegin').addClass('ui-state-disabled');
								$('#timername').addClass('ui-state-disabled');
								$("#dirname option").not(":selected").attr("disabled", "disabled");
								$("#bouquet_select option").not(":selected").attr("disabled", "disabled");
							} else {
								$('#timername').removeClass('ui-state-disabled');
								$('#timerbegin').removeClass('ui-state-disabled');
								$("#dirname option").removeAttr('disabled');
								$("#bouquet_select option").removeAttr('disabled');
							}
							$('#timerbegin').prop('readonly', r);
							$('#timername').prop('readonly',r);
							
							if (typeof timer.vpsplugin_enabled !== 'undefined')
							{
								$('#vpsplugin_enabled').prop("checked", timer.vpsplugin_enabled);
								$('#vpsplugin_safemode').prop("checked", !timer.vpsplugin_overwrite);
								$('#has_vpsplugin1').show();
								checkVPS();
							}
							else {
								$('#has_vpsplugin1').hide();
							}
							
							if (typeof timer.always_zap !== 'undefined')
							{
								$('#always_zap1').show();
								$('#always_zap').prop("checked", timer.always_zap==1);
								$('#justplay').prop("disabled",timer.always_zap==1);
							} else {
								$('#always_zap1').hide();
							}
							
							$('#editTimerForm').dialog("open");
							$('#editTimerForm').dialog("option", "title", tstr_edit_timer + " - " + timer.name);
							
							break;
						}
				}
			}
		}
	});
}

function addTimer(evt,chsref,chname) {
	current_serviceref = '';
	current_begin = -1;
	current_end = -1;
	servicename = '';

	var begin = -1;
	var end = -1;
	var serviceref = '';
	var title = '';
	var desc = '';
	var margin_before = 0;
	var margin_after = 0;
	
	if (typeof evt !== 'undefined' && evt != '') {
		begin = evt.begin;
		end = evt.begin+evt.duration;
		serviceref = evt.sref;
		servicename = evt.channel;
		title = evt.title;
		desc = evt.shortdesc;
		margin_before = evt.recording_margin_before;
		margin_after = evt.recording_margin_after;
	}
	
	var lch=$('#bouquet_select > option').length;
	
	if (!timeredit_initialized || lch < 2) {
		initTimerEdit();
	}
	
	if (typeof chsref !== 'undefined' && typeof chname !== 'undefined') {
		// NOT NICE BUT IT WORKS
		// TODO : remove the radio channel from the list after close
		serviceref = chsref;
		title = chname;
		$('#bouquet_select').append($("<option></option>").attr("value", serviceref).text(chname));
	}
	
	$('#timername').val(title);
	$('#description').val(desc);
	$('#dirname').val("None");
	$('#enabled').prop("checked", true);
	$('#justplay').prop("checked", false);
	$('#afterevent').val(3);
	$('#errorbox').hide();

	for (var i=0; i<7; i++) {
		$('#day'+i).attr('checked', false);
	}
	$('#repeatdays').buttonset('refresh');
	
	$('#tagsnew').find('input').attr('checked',false);
	$('#tagsnew').buttonset('refresh');

	var begindate = begin !== -1 ? new Date( (Math.round(begin) - margin_before*60) * 1000) : new Date();
	$('#timerbegin').datetimepicker('setDate', begindate);
	var enddate = end !== -1 ? new Date( (Math.round(end) + margin_after*60) * 1000) : new Date(begindate.getTime() + (60*60*1000));
	$('#timerend').datetimepicker('setDate', enddate);

	$('#bouquet_select').val(serviceref);
	if (serviceref !== $('#bouquet_select').val() && typeof servicename !== 'undefined' && servicename != '') {
		$('#bouquet_select').append($("<option></option>").attr("value", serviceref).text(servicename));
		$('#bouquet_select').val(serviceref);
	}

	$('#editTimerForm').dialog("open");
	$('#editTimerForm').dialog("option", "title", tstr_add_timer);
	$('#editTimerForm').dialog("option", "height", "auto");
}

/* Timer management end */

function InitAccordeon(obj)
{
	// init accordeon for jquery UI 1.8.x
	$(obj).accordion({
		active: false,
		change: function(event, ui) {
			ui.oldContent.empty();
			ui.oldContent.html(tstr_loading + " ...");
			ui.newContent.load(ui.newHeader.find('a').attr('id'));
		},
		autoHeight: false,
		collapsible: true
	});
	// init accordeon for jquery UI 1.11.x
	/*
	$(obj).accordion({
		active: true,
		activate: function(event, ui) {
			ui.oldPanel.empty();
			ui.oldPanel.html(tstr_loading + " ...");
			ui.newPanel.load(ui.newHeader.find('a').attr('id'));
		},
		heightStyle: "content",
		collapsible: true
	});
	*/
}

function InitBouquets(tv)
{
	var mode="";
	if (tv===true) {
		$('#btn0').click(function(){
			$("#tvcontent").html(loadspinner).load("ajax/current");
		});
		$('#btn5').click(function(){
			$("#tvcontent").html(loadspinner).load('ajax/multiepg');
		});

	} 
	else {
		mode= "?stype=radio";
	}
	$('#btn1').click(function(){
		$("#tvcontent").html(loadspinner).load("ajax/bouquets" + mode);
	});
	$('#btn2').click(function(){
		$("#tvcontent").html(loadspinner).load("ajax/providers" + mode);
	});
	$('#btn3').click(function(){
		$("#tvcontent").load("ajax/satellites" + mode);
	});
	$('#btn4').click(function(){
		$("#tvcontent").html(loadspinner).load("ajax/channels" + mode);
	});
	
	$("#tvbutton").buttonset();
	$("#tvcontent").load("ajax/bouquets" + mode);
	
}

/* Vu+ Transcoding begin*/

function getWinSize(win) {
	if(!win) win = window;
	var s = {};
	if(typeof win.innerWidth != "undefined") {
		s.screenWidth = win.screen.width;
		s.screenHeight = win.screen.height;
	} else {
		s.screenWidth = 0;
		s.screenHeight = 0;
	}
	return s;
}

function getDeviceType() {
	var ss = getWinSize();
	var screenLen = ( ss.screenHeight > ss.screenWdith ) ? ss.screenHeight : ss.screenWidth;
	return ( screenLen < 500 ) ? "phone":"tab";
}

function getOSType() {
	var agentStr = navigator.userAgent;

	if(agentStr.indexOf("iPod") > -1 || agentStr.indexOf("iPhone") > -1 || agentStr.indexOf("iPad") > -1 || agentStr.indexOf("ipod") > -1 || agentStr.indexOf("iphone") > -1 || agentStr.indexOf("ipad") > -1)
		return "ios";
	else if(agentStr.indexOf("Android") > -1 || agentStr.indexOf("android") > -1)
		return "android";
	else if(agentStr.indexOf("BlackBerry") > -1 || agentStr.indexOf("blackberry") > -1)
		return "blackberry";
	else
		return "unknown";
}

function jumper80( file ) {
	var deviceType = getDeviceType();
	document.portFormTs.file.value = file;
	document.portFormTs.device.value = "etc";
	document.portFormTs.submit();
}

function jumper8003( file ) {
	var deviceType = getDeviceType();
	document.portFormTs.file.value = file;
	document.portFormTs.device.value = "phone";
	document.portFormTs.submit();
}

function jumper8002( sref, sname ) {
	var deviceType = getDeviceType();
	document.portForm.ref.value = sref;
	document.portForm.name.value = sname;
	document.portForm.device.value = "phone";
	document.portForm.submit();
}

function jumper8001( sref, sname ) {
	var deviceType = getDeviceType();
	document.portForm.ref.value = sref;
	document.portForm.name.value = sname;
	document.portForm.device.value = "etc";
	document.portForm.submit();
}

/* Vu+ Transcoding end*/
