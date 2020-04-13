//******************************************************************************
//* openwebif.js: openwebif base module
//* Version 1.2.20
//******************************************************************************
//* Copyright (C) 2011-2020 E2OpenPlugins
//*
//* V 1.0   - Initial Version
//* V 1.1   - add movie move and rename
//* V 2.0   - movie sort object, spinner, theme support, ...
//* V 2.1   - support timer conflicts / fix IE cache issue
//* V 2.2   - remove sync requests
//* V 2.3   - prepare web tv / better timer conflicts
//* V 2.4   - improve movie sort
//* V 2.5   - improve settings
//* V 2.6   - getallservices public function
//* V 2.7   - getallservices cache / improve bool values / improve screenshots
//* V 1.1.1 - epg fixes / change version numbering to match OWIF versioning
//* V 1.2.1 - fix multiepg
//* V 1.2.2 - improve epgsearch
//* V 1.2.3 - fix add at from multiepg
//* V 1.2.4 - fix screenshot refresh
//* V 1.2.5 - improve remote control #603
//* V 1.2.6 - improve full channel list and edit timer
//* V 1.2.7 - improve movie rename/delete, fix timer channel selection #612
//* V 1.2.8 - improve save config #620
//* V 1.2.9 - improve timer #624
//* V 1.2.10 - improve screenshot refresh #625
//* V 1.2.11 - improve visual feedback for adding timer in multiepg
//* V 1.2.12 - improve timer edit
//* V 1.2.13 - fix repeating timer edit #631
//* V 1.2.14,15,16 - fix json parse
//* V 1.2.17 - allow timers for IPTV #715, added LCD, PiP into screenshots
//* V 1.2.18 - rename stream.m3u8 to <channelname>.m3u8
//* V 1.2.19 - fixed missing <channelname> when requesting a transcoding stream m3u8
//* V 1.2.20 - timer pipzap option
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
var theme='original',loadspinner = "<div id='spinner'><div class='fa fa-spinner fa-spin'></div></div>",mutestatus = 0,lastcontenturl = null,screenshotMode = 'all',MessageAnswerCounter=0,shiftbutton = false,grabTimer = 0,at2add = null,_location = [],_tags = [],current_ref=null,current_name=null;

$(function() {
	
	SetSpinner();
	
// no execption on popup window
try {
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
	setInterval( function() { getStatusInfo(); }, 15000);

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

	_locations = loadLocations();
	_tags = loadTags();

}
catch(err) {}

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
	tstr_reboot_box = strings.reboot_box;
	tstr_rec_status = strings.rec_status;
	tstr_restart_gui = strings.restart_gui;
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
	
	tstr_timer = strings.timer;
	tstr_timerlist = strings.timer_list;
	tstr_timerpreview = strings.timer_preview;
	tstr_timernewname = strings.timer_newname;
	
	tstr_open_in_new_window = strings.open_in_new_window;
	tstr_error_load_page = strings.tstr_error_load_page;
	tstr_timer_added = strings.tstr_timer_added;
	tstr_event_not_found = strings.tstr_event_not_found;
	
	tstr_channel = strings.channel;
	tstr_end = strings.begin;
	tstr_begin = strings.end;

}

function wait_for_openwebif() {
	var restartCheck = window.setInterval(function() {
		webapi_execute('/api/statusinfo',
			function() {
				window.clearInterval(restartCheck);
				$("#modaldialog").dialog('close');
				location.reload();
			});
	}, 2000);
}

function handle_power_state_dialog(new_power_state) {
	var timeout = 0;
	var sp = loadspinner.replace("'spinner'","'spinner1'");
	$("#modaldialog").dialog('close');
	if ( new_power_state === 2 ) {
		load_reboot_dialog(sp,tstr_reboot_box);
		wait_for_openwebif();
		timeout = 1000 ;
	} else if ( new_power_state === 3 ) {
		load_reboot_dialog(sp,tstr_restart_gui);
		wait_for_openwebif();
		timeout = 1000 ;
	}
	setTimeout(function () {
		webapi_execute('api/powerstate?newstate=' + new_power_state);
	}, timeout);
}

function load_reboot_dialog(data,title){

	$("#modaldialog").html(data).dialog({
		modal:true,
		title:title,
		autoOpen:true,
		width:'auto',
		height:'auto',
		open: function (event, ui) {
			$('#modaldialog').css('overflow', 'hidden'); 
		},
		close: function(event, ui) { 
			$(this).dialog('destroy');
			$("#modaldialog").html('');
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
		create: function(event, ui) {
			$(event.target).parent().css('position', 'fixed');
		},
		close: function(event, ui) { 
			$(this).dialog('destroy');
			$("#modaldialog").html('');
		},
		open: function() {
		$.ajax({
			url: url,
			success: function(data) {
				$("#modaldialog").html(data);
			},
			error: function(){
				$("#modaldialog").html(tstr_error_load_page);
			}
		});
		$(this).siblings('.ui-dialog-buttonpane').find('button:eq(0)').focus(); 
		}
	});
}

function load_dm(url,title,w,h){
	var buttons = {};
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
					$("#modaldialog").html('');
				},
				open: function() {
					$(this).siblings('.ui-dialog-buttonpane').find('button:eq(0)').focus(); 
				}
			});
		},error: function(){
			alert(tstr_error_load_page);
		}
		
	});
}

function load_message_dm(url,title){
	var buttons = {};
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
					$("#modaldialog").html('');
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
	if (lastcontenturl != url || ( url.indexOf('screenshot') > -1 ) || ( url.indexOf('timer') > -1 ) || ( url.indexOf('boxinfo') > -1 )) {
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
	var jqxhr = $.ajax({ url: url, cache: false, async: false}).done(function() { 
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
	
	var buttons = {};
	buttons[tstr_close] = function() { $(this).dialog("close");};
	buttons[tstr_open_in_new_window] = function() { $(this).dialog("close"); open_epg_pop(sRef);};
	
	load_dm_spinner(url,Name,w,h,buttons);
}

function open_epg_search_dialog() {
	var spar = $("#epgSearch").val();
	var full = GetLSValue('epgsearchtype',false) ? '&full=1' : '';
	var bouquetsonly = GetLSValue('epgsearchbouquetsonly',false) ? '&bouquetsonly=1' : '';
	var url = "ajax/epgdialog?sstr=" + encodeURIComponent(spar) + full + bouquetsonly;
	$("#epgSearch").val("");
	
	var w = $(window).width() -100;
	var h = $(window).height() -100;
	
	var buttons = {};
	buttons[tstr_close] = function() { $(this).dialog("close");};
	buttons[tstr_open_in_new_window] = function() { $(this).dialog("close"); open_epg_search_pop(spar,full);};
	
	load_dm_spinner(url,tstr_epgsearch,w,h,buttons);
}

function _epg_pop(url) {
	$.popupWindow(url, {
		height: $(window).height(),
		width: $(window).width(),
		toolbar: false,
		scrollbars: true
	});	
}

function open_epg_search_pop(spar,full) {
	_epg_pop("ajax/epgpop?sstr=" + encodeURIComponent(spar) + full);
}

function open_epg_pop(sRef) {
	_epg_pop('ajax/epgpop?sref=' + escape(sRef));
}

function TimerConflict(conflicts,sRef, eventId, justplay)
{
	// !!! TODO !!!
	// the first conflict entry is the new timer but this new timer don't exits
	// If there is a deactivate button we need to create the new timer again
	// sRef, eventId, justplay are needed to create the new timer
	var SplitText = "<div class='tbltc'><div><div>Name</div><div>"+tstr_channel+"</div><div>"+tstr_end+"</div><div>"+tstr_begin+"</div></div>";
	conflicts.forEach(function(entry) {
		SplitText +="<div><div>"+entry.name+"</div><div>"+entry.servicename+"</div><div>"+entry.realbegin+"</div><div>"+entry.realend+"</div></div>";
	});

	SplitText +="</div>";
	var buttons = {};
	buttons[tstr_close] = function() { $(this).dialog("close");};
	$('<div></div>').dialog({
		modal: true,
		height: 500,
		width: 600,
		autoOpen:true,
		title: "Timer Conflicts",
		open: function () {
			$(this).html(SplitText);
		}, buttons: buttons
	});
}

function webapi_execute_result(url, callback) {
	$.ajax({
		async: false,
		url: url,
		cache : false,
		dataType: "json",
		success: function(result) {
			if (typeof callback !== 'undefined') {
				if(result)
					callback(result.result,result.message,result.conflicts);
				else
					callback(false,'error');
			}
		}
	});
}

function cbAddTimerEvent(state) {
	if (state.state) {
		$('.event[data-id='+state.eventId+'][data-ref="'+state.sRef+'"] .timer').remove();
		$('.event[data-id='+state.eventId+'][data-ref="'+state.sRef+'"] div:first').append('<div class="timer">'+tstr_timer+'</div>');
	}
}

function addTimerEvent(sRef, eventId, justplay, callback) {

	var url = "/api/timeraddbyeventid?sRef=" + sRef + "&eventid=" + eventId;
	if(justplay)
		url += "&eit=0&disabled=0&justplay=1&afterevent=3";

	webapi_execute_result(url,
		function(state,txt,conflicts) {
			if (!state && conflicts) {
				TimerConflict(conflicts,sRef,eventId,justplay);
			} else if (typeof callback !== 'undefined') {
				callback({
					sRef: sRef, 
					eventId: eventId, 
					justplay: justplay,
					state: state,
					txt: txt
				});
			} else {
				alert( state ? tstr_timer_added : txt );
			}
		}
	);
}

/*
function addTimerEventPlay(sRef, eventId) {
	webapi_execute_result("/api/timeraddbyeventid?sRef=" + sRef + "&eventid=" + eventId + "&eit=0&disabled=0&justplay=1&afterevent=3",
		function(state,txt,conflicts) {
			if (!state && conflicts)
				TimerConflict(conflicts,sRef,eventId,True);
			else
				alert( state ? tstr_timer_added : txt );
		}
	);
}
*/

function addEditTimerEvent(sRef, eventId) {
	var url="/api/event?sref=" + sRef + "&idev=" + eventId;
	$.ajax({
		url: url,
		dataType: "json",
		success: function(result) { 
			if (typeof result !== 'undefined' && typeof result.event !== 'undefined') {
				addTimer(result.event);
			}
			else
				alert(tstr_event_not_found);
		},
		error: function(data) {}
	});
}

function htmlEscape(str) {
	return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function addAutoTimerEvent(sRef, sname, title ,begin, end) {
	
		at2add = {
			"name" : htmlEscape(title),
			"from" : begin,
			"to" : end,
			"sref" : sRef,
			"sname" : sname
		};

		lastcontenturl = '';
		
		if ($("#compressmepg").is(":visible"))
			CompressMEPG();

		if ($("#modaldialog").hasClass('ui-dialog-content')) {
			$("#modaldialog").dialog('destroy');
			$("#modaldialog").html('');
		}

		if ($("#eventdescription").hasClass('ui-dialog-content')) {
			$("#eventdescription").dialog('destroy');
			$("#eventdescription").html('');
		}
		
		load_maincontent('ajax/at');
}

function delTimerEvent(sRef,eventId) {

	var url="/api/event?sref=" + sRef + "&idev=" + eventId;
	$.ajax({
		url: url,
		dataType: "json",
		success: function(result) { 
			if (typeof result !== 'undefined' && typeof result.event !== 'undefined') {
				// FIXME : this will not work if the timer is modified
				var begin = result.event.begin - 60 * result.event.recording_margin_before;
				var end = result.event.begin + result.event.duration + 60 * result.event.recording_margin_after;
				var t = decodeURIComponent(result.event.title);
				if (confirm(tstr_del_timer + ": " + t) === true) {
					webapi_execute("/api/timerdelete?sRef=" + sRef + "&begin=" + begin + "&end=" + end, 
						function() { $('.event[data-id='+eventId+'] .timer').remove(); } 
					);
				}
			}
			else
				alert(tstr_event_not_found);
		},
		error: function(data) {}
	});

}

function toggleTimerStatus(sRef, begin, end) {
	var url="/api/timertogglestatus?";
	var data = { sRef: sRef, begin: begin, end: end };
	
	$.ajax({
		url: url,
		dataType: "json",
		data:data,
		success: function(result) { 
			
			$('#img-'+begin+'-'+end + ' > i').each( function (){ 
				if( $(this).data("ref") == sRef) {
					$(this).removeClass("fa-square-o");
					$(this).removeClass("fa-check-square-o");
					$(this).addClass(result['disabled'] ? "fa-square-o" : "fa-check-square-o");
				}
			});
		},
		error: function(data) {}
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

function webapi_execute_movie(url,callback)
{
	$.ajax({
		async: false,
		url: url,
		cache : false,
		dataType: "json",
		success: function(result) {
			if(result) {
				if (!result.result)
					alert(result.message);
				if (typeof callback !== 'undefined') 
					callback(result.result);
			}
		}
	});
}

function renameMovie(sRef, title) {
	var newname=prompt(tstr_ren_recording, title);
	if (newname && newname!=title){
		webapi_execute_movie("/api/movierename?sRef=" + sRef+"&newname="+newname);
		// TODO reload if success
	}
}

function deleteMovie(sRef, divid, title) {
	if (confirm(tstr_del_recording + ": " + title) === true) {
		webapi_execute_movie("/api/moviedelete?sRef=" + sRef,
			function (state) {
				if(state) 
					$('#' + divid).remove();
			}
		);
	}
}

function playRecording(sRef) {
	var sr = sRef.replace(/-/g,'%2D').replace(/_/g,'%5F').replace(/\//g,'%2F');
	// for debugging 
	console.debug(sr);
	var url = '/api/zap?sRef=' + sr;
	
	webapi_execute(url,
	function() {
		$("#osd").html(" ");
		$("#osd_bottom").html(" ");
	});
}

function zapChannel(sRef, sname) {
	var url = '/api/zap?sRef=' + escape(sRef);
	webapi_execute(url,
	function() {
		$("#osd").html(tstr_zap_to + ': ' + sname);
		$("#osd_bottom").html(" ");
	});
}

function toggleStandby() {
	var sh = (shiftbutton) ? '&shift=1':'';
	webapi_execute('api/powerstate?newstate=0'+sh);
	setTimeout(getStatusInfo, 1500);
}

function setOSD( statusinfo )
{

	var sref = current_ref = statusinfo['currservice_serviceref'];
	var station = current_name = statusinfo['currservice_station'];
	
	if (station) {
		var stream = "<div id='osdicon'>";
		var streamtitle = tstr_stream + ": " + station + "'><i class='fa fa-desktop'></i></a>";
		var streamtitletrans = tstr_stream + " (" + tstr_transcoded + "): " + station + "'><i class='fa fa-mobile'></i></a>";
		var _osdch = "<span class='osdch'>" + station + "</span></a>&nbsp;&nbsp;";
		var _beginend = _osdch + statusinfo['currservice_begin'] + " - " + statusinfo['currservice_end'] + "&nbsp;&nbsp;";
		
		if ((sref.indexOf("1:0:1") !== -1) || (sref.indexOf("1:134:1") !== -1)) {
			if (statusinfo['transcoding']) {
				stream += "<a href='#' onclick=\"jumper8001('" + sref + "', '" + station + "')\"; title='" + streamtitle;
				stream += "<a href='#' onclick=\"jumper8002('" + sref + "', '" + station + "')\"; title='" + streamtitletrans;
			} else {
				stream += "<a target='_blank' href='/web/stream.m3u?ref=" + sref + "&name=" + station + "&fname=" + station + "' title='" + streamtitle;
			}
			stream +="</div>";
			$("#osd").html(stream + "<a href='#' onClick='load_maincontent(\"ajax/tv\");return false;'>" + _beginend + "<a style='text-decoration:none;' href=\"#\" onclick=\"open_epg_pop('" + sref + "')\" title='" + statusinfo['currservice_fulldescription'] + "'>" + statusinfo['currservice_name'] + "</a>");
		} else if ((sref.indexOf("1:0:2") !== -1) || (sref.indexOf("1:134:2") !== -1)) {
			stream += "<a target='_blank' href='/web/stream.m3u?ref=" + sref + "&name=" + station + "&fname=" + station + "' title='" + streamtitle;
			stream +="</div>";
			$("#osd").html(stream + "<a href='#' onClick='load_maincontent(\"ajax/radio\");return false;'>" + _beginend + "<a style='text-decoration:none;' href=\"#\" onclick=\"open_epg_pop('" + sref + "')\" title='" + statusinfo['currservice_fulldescription'] + "'>" + statusinfo['currservice_name'] + "</a>");
		} else if (sref.indexOf("1:0:0") !== -1) {
			if (statusinfo['transcoding']) {
				stream += "<a href='#' onclick=\"jumper80('" + statusinfo['currservice_filename'] + "')\"; title='" + streamtitle;
				stream += "<a href='#' onclick=\"jumper8003('" + statusinfo['currservice_filename'] + "')\"; title='" + streamtitletrans;
			} else {
				stream += "<a target='_blank' href='/web/ts.m3u?file=" + statusinfo['currservice_filename'] + "' title='" + streamtitle;
			}
			stream +="</div>";
			$("#osd").html(stream + _beginend + statusinfo['currservice_name']);
		} else {
			$("#osd").html(_beginend + statusinfo['currservice_name']);
		}
		$("#osd_bottom").html(statusinfo['currservice_description']);
	} else {
		$("#osd").html(tstr_nothing_play);
		$("#osd_bottom").html('');
	}

}

function getStatusInfo() {

	$.ajax({
		url: '/api/statusinfo',
		dataType: "json",
		cache: false,
		success: function(statusinfo) { 
		// Set Volume
		$("#slider").slider("value", statusinfo['volume']);
		$("#amount").val(statusinfo['volume']);

// TODO: remove images
		
		// Set Mute Status
		if (statusinfo['muted'] == true) {
			mutestatus = 1;
			$("#volimage").attr("src","/images/volume_mute.png");
		} else {
			mutestatus = 0;
			$("#volimage").attr("src","/images/volume.png");
		}
		
		setOSD(statusinfo);
		
		var sb = '';
		var tit = tstr_standby;
		if (statusinfo['inStandby'] !== 'true') {
			sb=' checked';
			tit = tstr_on;
		}

		var status = "";
		if (statusinfo['isRecording'] == 'true') {
			status = "<a href='#' onClick='load_maincontent(\"ajax/timers\"); return false;'><div title='" + tstr_rec_status + statusinfo['Recording_list'] + "' class='led-box'><div class='led-red'></div></div></a>";
		}
		
		//status += "<div class='pwrbtncontout'><div class='pwrbtncont' title='" + tit + "'><label class='label pwrbtn'><input type='checkbox' "+sb+" id='pwrbtn' onchange='toggleStandby();return true;' /><div class='pwrbtn-control'></div></label></div></div>";
		
		status += "<a href='#' onClick='toggleStandby();return false'><img src='../images/ico_";
		if (statusinfo['inStandby'] == 'true') {
			status += "standby.png' title='" + tstr_on + "' alt='" + tstr_standby;
		} else {
			status += "on.png' title='" + tstr_standby + "' alt='" + tstr_on;
		}
		status += "' width='56' height='29' /></a>";
		
		$("#osd_status").html(status);
	} , error: function() {
		$("#osd, #osd_bottom").html("");
	}
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
	if (GetLSValue('ssr_hd',false)){
		$('#screenshotimage').attr("src",'/grab?format=jpg&mode=' + mode + '&t=' + timestamp);
	} else {
		$('#screenshotimage').attr("src",'/grab?format=jpg&r=720&mode=' + mode + '&t=' + timestamp);
	}
	if (mode == "lcd") {
		$('#screenshotimage').attr("width", 'auto');
	} else {
		$('#screenshotimage').attr("width",720);
	}
}

function getMessageAnswer() {
	$.ajax({
		url: '/api/messageanswer',
		dataType: "json",
		cache: false,
		success: function(result) { 
			$('#messageSentResponse').html(result['message']);
		}
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

	$.ajax({
		url: '/api/message?text=' + text + '&type=' + type + '&timeout=' + timeout,
		dataType: "json",
		cache: false,
		success: function(result) { 
			$('#messageSentResponse').html(result['message']);
			if(type==0)
			{
				MessageAnswerCounter=timeout;
				setTimeout(countdowngetMessage, 1000);
			}
		}
	});
}

function toggleMenu(name) {
	var expander_id = "#leftmenu_expander_" + name;
	var container_id = "#leftmenu_container_" + name;
	if ($(expander_id).hasClass("ui-icon-caret-1-w")) {
		$(expander_id).removeClass("ui-icon-caret-1-w");
		$(expander_id).addClass("ui-icon-caret-1-s");
		$(container_id).show('fast');
		webapi_execute("/api/expandmenu?name=" + name);
	}
	else {
		$(expander_id).addClass("ui-icon-caret-1-w");
		$(expander_id).removeClass("ui-icon-caret-1-s");
		$(container_id).hide('fast');
		webapi_execute("/api/collapsemenu?name=" + name);
	}
}

// keep checkboxes syncronized
$(function() {
	$('.remotegrabscreen').click(function(evt) {
		$('.remotegrabscreen').prop('checked', evt.currentTarget.checked);
		SetLSValue('remotegrabscreen',evt.currentTarget.checked);
	});
	$('.remotegrabscreen').prop('checked',GetLSValue('remotegrabscreen',true));

	$('input[name=epgsearchtype]').click(function(evt) {
		$('input[name=epgsearchtype]').prop('checked', evt.currentTarget.checked);
		SetLSValue('epgsearchtype',evt.currentTarget.checked);
	});
	if (typeof $('input[name=epgsearchtype]') !== 'undefined') {
		$('input[name=epgsearchtype]').prop('checked',GetLSValue('epgsearchtype',false));
	} else {
		SetLSValue('epgsearchtype',false);
	}
	
	$('input[name=epgsearchbouquetsonly]').click(function(evt) {
		$('input[name=epgsearchbouquetsonly]').prop('checked', evt.currentTarget.checked);
		SetLSValue('epgsearchbouquetsonly',evt.currentTarget.checked);
	});
	if (typeof $('input[name=epgsearchbouquetsonly]') !== 'undefined') {
		$('input[name=epgsearchbouquetsonly]').prop('checked',GetLSValue('epgsearchbouquetsonly',false));
	} else {
		SetLSValue('epgsearchbouquetsonly',false);
	}
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
	testPipStatus();
	if(GetLSValue('remotegrabscreen',true))
	{
		if (lastcontenturl == 'ajax/screenshot') {
			grabScreenshot(screenshotMode);
		} else {
			load_maincontent('ajax/screenshot');
		}
	}
}

function pressMenuRemote(code) {
	
	var url = "/api/remotecontrol?" + ((shiftbutton) ? "type=long&" : "") + "command=" + code;
	webapi_execute(url);
	
	if (grabTimer > 0) {
		clearTimeout(grabTimer);
	}
	grabTimer = setTimeout(function() { callScreenShot(); }, (code > 1 && code < 12) ? 1500:1000);
}

function toggleFullRemote() {
	$("#menucontainer").toggle();
	$("#remotecontainer").toggle();
}

function saveConfig(key, value) {
	$.ajax({ url: "/api/saveconfig?key=" + escape(key) + "&value=" + escape(value), cache: false, async: true, type: "POST"}).done(function() { 
		if (key == "config.usage.setup_level") {
			// TODO: refresh the menu box with new sections list
			$("#content_container").load(lastcontenturl);
		}
	});
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

function initTimerBQ(radio, callback) {

	$('#bouquet_select').find('optgroup').remove().end();
	$('#bouquet_select').find('option').remove().end();
	GetAllServices(function ( options , boptions) {
		$("#bouquet_select").append( options);
		if(current_ref) {
			$("#bouquet_select").val( current_ref );
		}
		$('#bouquet_select').trigger("chosen:updated");
		callback();
	} , radio);

}

function initTimerEdit(radio, callback) {

	var bottomhalf = function() {
		$('#dirname').find('option').remove().end();
		$('#dirname').append($("<option></option>").attr("value", "None").text("Default"));
		for (var id in _locations) {
			var loc = _locations[id];
			$('#dirname').append($("<option></option>").attr("value", loc).text(loc));
		}

		$('#tagsnew').html('');
		for (var id in _tags) {
			var tag = _tags[id];
			$('#tagsnew').append("<input type='checkbox' name='"+tag+"' value='"+tag+"' id='tag_"+tag+"'/><label for='tag_"+tag+"'>"+tag+"</label>");
		}

		$("#tagsnew > input").checkboxradio({icon: false});

		timeredit_initialized = true;
		callback();
	};

	initTimerBQ(radio, bottomhalf);
}

function loadLocations()
{
	_locations = [];
	$.ajax({
		url: "/api/getlocations",
		dataType: "json",
		success: function(loc) {
			if (loc.result)
				_locations = loc.locations;
		}
	});
}

function loadTags()
{
	_tags = [];
	$.ajax({
		url: "/api/gettags",
		dataType: "json",
		success: function(tag) {
			if (tag.result)
				_tags = tag.tags;
		}
	});
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
	
	var radio = false;
	if (typeof serviceref !== 'undefined') {
		radio = ( serviceref.substring(0,6) == '1:0:2:');
	}
	
	$('#cbtv').prop('checked',!radio);
	$('#cbradio').prop('checked',radio);
	
	var bottomhalf = function() {
	
	if (timeredit_begindestroy) {
		initTimerEditBegin();
		timeredit_begindestroy=false;
	}

	$.ajax({
		url: "/api/timerlist",
		dataType: "json",
		success: function(timers) {
			if (timers.result) {
				for (var id in timers.timers) {
					timer = timers.timers[id];
					if (timer.serviceref == serviceref &&
						Math.round(timer.begin) == Math.round(begin) &&
						Math.round(timer.end) == Math.round(end)) {
							$('#timername').val(timer.name);
							$('#description').val(timer.description);
							$('#bouquet_select').val(timer.serviceref);
							$('#bouquet_select').trigger("chosen:updated");
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
								$('#day'+i).prop('checked', ((flags & 1)==1)).checkboxradio("refresh");
								flags >>= 1;
							}
							
							$('#tagsnew > input').prop('checked',false).checkboxradio("refresh");
							
							var tags = timer.tags.split(' ');
							for (var j=0; j<tags.length; j++) {
								var tag = tags[j].replace(/\(/g,'_').replace(/\)/g,'_').replace(/\'/g,'_');
								if (tag.length>0)
								{
									if($('#tag_'+tag).length)
									{
										$('#tag_'+tag).prop('checked', true).checkboxradio("refresh");
									}
									else
									{
										$('#tagsnew').append("<input type='checkbox' checked='checked' name='"+tag+"' value='"+tag+"' id='tag_"+tag+"'/><label for='tag_"+tag+"'>"+tag+"</label>");
							}
								}
							}
							$("#tagsnew > input").checkboxradio({icon: false});
							
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
								//$('#always_zap1').show();
								$('#always_zap').prop("checked", timer.always_zap==1);
								$('#justplay').prop("disabled",timer.always_zap==1);
							} else {
								//$('#always_zap1').hide();
								$('#always_zap').prop("disabled", true);
							}

							if (typeof timer.pipzap !== 'undefined')
							{
								$('#pipzap').prop("disabled",false);
								$('#pipzap').prop("checked", timer.pipzap==1);
							} else {
								$('#pipzap').prop("disabled",true);
							}

							if (typeof timer.allow_duplicate !== 'undefined')
							{
								$('#allow_duplicate').prop("checked", timer.allow_duplicate==1);
								autoadjust: ($('#autoadjust').is(':checked')?"1":"0"),
							}
							if (typeof timer.autoadjust !== 'undefined')
							{
								$('#autoadjust').prop("checked", timer.autoadjust==1);
							}

							openTimerDlg(tstr_edit_timer + " - " + timer.name);
							
							break;
						}
				}
			}
		}
	});
	};
	
	if (!timeredit_initialized) {
		initTimerEdit(radio, bottomhalf);
	}
	else
	{
		var _chsref=$("#bouquet_select option:last").val();
		if(radio && _chsref.substring(0,6) !== '1:0:2:') {
			initTimerEdit(radio, bottomhalf);
		} else if(!radio && _chsref.substring(0,6) == '1:0:2:') {
			initTimerEdit(radio, bottomhalf);
		} else {
			bottomhalf();
		} 
	}
	
}

function addTimer(evt,chsref,chname,top,isradio) {
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

	var lch=$('#bouquet_select > optgroup').length;

	var radio = false;
	if (typeof isradio !== 'undefined')
		radio = true;
	
	if (typeof chsref !== 'undefined') {
		radio = ( chsref.substring(0,6) == '1:0:2:');
	}

	$('#cbtv').prop('checked',!radio);
	$('#cbradio').prop('checked',radio);

	var bottomhalf = function() {
	if (typeof chsref !== 'undefined' && typeof chname !== 'undefined') {
		serviceref = chsref;
		title = chname;
		if ($('#bouquet_select').val(chsref) === 'undefined') {
			$('#bouquet_select').append($("<option></option>").attr("value", serviceref).text(chname));
		}
	}

	$('#timername').val(title);
	$('#description').val(desc);
	$('#dirname').val("None");
	$('#enabled').prop("checked", true);
	$('#justplay').prop("checked", false);
	$('#allow_duplicate').prop("checked", true);
	$('#autoadjust').prop("checked", false);
	$('#afterevent').val(3);
	$('#errorbox').hide();

	for (var i=0; i<7; i++) {
		$('#day'+i).prop('checked', false).checkboxradio('refresh');
	}
	
	$('#tagsnew > input').prop('checked',false).checkboxradio("refresh");

	var begindate = begin !== -1 ? new Date( (Math.round(begin) - margin_before*60) * 1000) : new Date();
	$('#timerbegin').datetimepicker('setDate', begindate);
	var enddate = end !== -1 ? new Date( (Math.round(end) + margin_after*60) * 1000) : new Date(begindate.getTime() + (60*60*1000));
	$('#timerend').datetimepicker('setDate', enddate);

	$('#bouquet_select').val(serviceref);
	$('#bouquet_select').trigger("chosen:updated");
	
	// TODO :check if needed
	/*
	 if (serviceref !== $('#bouquet_select').val() && typeof servicename !== 'undefined' && servicename != '') {
		$('#bouquet_select').append($("<option></option>").attr("value", serviceref).text(servicename));
		$('#bouquet_select').val(serviceref);
	}
	*/

	openTimerDlg(tstr_add_timer);
	};
	
	if (!timeredit_initialized || lch < 2) {
		initTimerEdit(radio, bottomhalf);
	}
	else
	{
		var _chsref=$("#bouquet_select option:last").val();
		if(radio && _chsref.substring(0,6) !== '1:0:2:') {
			initTimerEdit(radio, bottomhalf);
		} else if(!radio && _chsref.substring(0,6) == '1:0:2:') {
			initTimerEdit(radio, bottomhalf);
		} else {
			bottomhalf();
		}
	}

}

function openTimerDlg(title)
{
	$('#editTimerForm').dialog("open");
	$('#editTimerForm').dialog("option", "title", title);

}

/* Timer management end */

function InitAccordeon(obj)
{
	// init accordeon for jquery UI 1.8.x
	/*
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
	*/
	// init accordeon for jquery UI 1.11.x
	
	$(obj).accordion({
		active: true,
		animate: false,
		activate: function(event, ui) {
			ui.oldPanel.empty();
			ui.oldPanel.html(tstr_loading + " ...");
			ui.newPanel.load(ui.newHeader.find('a').attr('id'));
		},
		heightStyle: "content",
		collapsible: true
	});
	
}

function RefreshMEPG(mode)
{
	var full = ($("#compressmepg").is(":visible"));
	var bq = '';
	var lbq=GetLSValue('lastmbq_'+mode,'');
	if(lbq!='')
		bq= "&bref=" + lbq;
	$("#tvcontent").html(loadspinner).load('ajax/multiepg?epgmode=' + mode + bq,function() {
		if(full)
			ExpandMEPG();
	});
}

function ExpandMEPG()
{
	$("#expandmepg").hide();
	$("#compressmepg").show();
	$("#refreshmepg2").show();
	$("#header").hide();
	$("#leftmenu").hide();
	$('#content').css('margin-left', '5px');
	$('#tvcontentmain > #toolbar-header').hide();
	$("#tbl1body").height('100%');
	$("#tvcontent").css('height','100%');
	$("#tvcontentmain").css('height','950px');
	fixTableHeight();
}

function CompressMEPG()
{
	$("#refreshmepg").show();
	$("#expandmepg").show();
	$("#compressmepg").hide();
	$("#refreshmepg").show();
	$("#refreshmepg2").hide();
	$("#header").show();
	$("#leftmenu").show();
	$('#content').css('margin-left', '185px');
	$('#tvcontentmain > #toolbar-header').show();
	$("#tvcontent").css('height','730px');
	$("#tvcontentmain").css('height','800px');
	fixTableHeight();
}

//$(window).resize(function(){ mainresize(); });

function mainresize()
{
	console.log("WH" + $( window ).height() + "TVH" + $("#tvcontentmain").height());

	if($("#tvcontentmain")) {
		//$("#tvcontentmain").height($( window ).height()-220);
		try {fixTableHeight(); } catch(err) {}
	}
}

var mepgdirect=0;

function InitTVRadio(epgmode)
{

	var mode = (epgmode == 'radio') ? '?stype=radio':'';
	
	$('#btn0').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/current" +mode);
	});

	$('#btn5').click(function(){
		var bq = '';
		var lbq=GetLSValue('lastmbq_'+epgmode,'');
		if(lbq!='')
			bq= "&bref=" + lbq;
		$("#tvcontent").html(loadspinner).load('ajax/multiepg?epgmode='+epgmode+bq);
		$("#expandmepg").show();
		$("#refreshmepg").show();
	});

	$('#btn1').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/bouquets" + mode);
	});
	$('#btn2').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/providers" + mode);
	});
	$('#btn3').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").load("ajax/satellites" + mode);
	});
	$('#btn4').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/channels" + mode);
	});
	
	$("#tvbutton").buttonset();

	var link = "ajax/bouquets" + mode;

	if (tv===true) {
		var parts=window.location.href.toLowerCase().split("#");
		window.location.hash="";
		if (parts[1] == 'tv') {
			if(parts[2] == 'mepg' || parts[2] == 'mepgfull')
			{
				mepgdirect=0;
				if(parts[2] == 'mepgfull')
					mepgdirect=1;
				$("#btn5").click();
				return;
			}
			else if (parts[2] == 'current')
			{
				$("#btn0").click();
				return;
			}
		}
	}
	
	$("#tvcontent").load("ajax/bouquets" + mode);
	
	if (theme == 'pepper-grinder')
		$("#tvcontent").addClass('ui-state-active');

}

function InitBouquets(tv)
{
	var mode="";
	if (tv===true) {
		$('#btn0').click(function(){
			$("#expandmepg").hide();
			$("#refreshmepg").hide();
			$("#tvcontent").html(loadspinner).load("ajax/current");
		});
	}
	else {
		mode= "?stype=radio";
		$('#btn0').click(function(){
			$("#expandmepg").hide();
			$("#refreshmepg").hide();
			$("#tvcontent").html(loadspinner).load("ajax/current"+ mode);
		});
	}
	
	$('#btn5').click(function(){
		var emode = (tv===true) ? 'tv':'radio';
		var bq = '';
		var lbq=GetLSValue('lastmbq_'+emode,'');
		if(lbq!='')
			bq= "&bref=" + lbq;
		$("#tvcontent").html(loadspinner).load('ajax/multiepg?epgmode='+emode+bq);
		$("#expandmepg").show();
		$("#refreshmepg").show();
	});
	
	$('#btn1').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/bouquets" + mode);
	});
	$('#btn2').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/providers" + mode);
	});
	$('#btn3').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").load("ajax/satellites" + mode);
	});
	$('#btn4').click(function(){
		$("#expandmepg").hide();
		$("#refreshmepg").hide();
		$("#tvcontent").html(loadspinner).load("ajax/channels" + mode);
	});
	
	$("#tvbutton").buttonset();

	var link = "ajax/bouquets" + mode;

	if (tv===true) {
		var parts=window.location.href.toLowerCase().split("#");
		window.location.hash="";
		if (parts[1] == 'tv') {
			if(parts[2] == 'mepg' || parts[2] == 'mepgfull')
			{
				mepgdirect=0;
				if(parts[2] == 'mepgfull')
					mepgdirect=1;
				$("#btn5").click();
				return;
			}
			else if (parts[2] == 'current')
			{
				$("#btn0").click();
				return;
			}
		}
	}
	
	$("#tvcontent").load("ajax/bouquets" + mode);
	
	if (theme == 'pepper-grinder')
		$("#tvcontent").addClass('ui-state-active');
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
	document.portForm.fname.value = sname;
	document.portForm.device.value = "phone";
	document.portForm.submit();
}

function jumper8001( sref, sname ) {
	var deviceType = getDeviceType();
	document.portForm.ref.value = sref;
	document.portForm.name.value = sname;
	document.portForm.fname.value = sname;
	document.portForm.device.value = "etc";
	document.portForm.submit();
}

/* Vu+ Transcoding end*/

// obsolete
function ChangeTheme(theme)
{
	$.ajax({
		url: "api/settheme?theme=" + theme,
		success: function() {
			window.location.hash = '#settings';
			window.location.reload(true);
		}
	});
}

function directlink()
{
	var parts=window.location.href.toLowerCase().split("#");
	var lnk='ajax/tv';
	var p = parts[1];

	switch (p)
	{
		case 'radio':
		case 'movies':
		case 'timer':
		case 'settings':
		case 'at':
		case 'bqe':
		case 'epgr':
			lnk='ajax/' + p;
			break;
	}
	if(p != 'tv') {
		window.location.hash="";
	}
	
	load_maincontent(lnk);
}

function ShowTimers(timers)
{
	if (timers.length > 0)
	{
		$( ".ETV tbody" ).each(function( index ) {
			var parts=$( this ).data('id').split(';');
			if (parts.length == 3)
			{
				var sref = parts[0];
				var begin = parseInt(parts[1]);
				var end = begin + ( parseInt(parts[2]) * 60 );
				var evt = $( this );
				timers.forEach(function(entry) {
					if(entry["sref"] == sref)
					{
						var b = parseInt(entry["begin"]);
						var e = parseInt(entry["end"]);
						
						// event end > timerbegin & event begin < timer end
						if ( end > b && begin < e ) {
							
							var addt = evt.find('.addtimer').first();
							var delt = evt.find('.deltimer').first();
							var pan = evt.find('.timerpanel').first();
							
							if ( begin >= b && end <= e )
							{
								addt.hide();
								delt.show();
								pan.css("background-color", "red");
							}
							else
							{
								pan.css("background-color", "yellow");
							}
						}
					}
				});
			}
			
		});
		
	
	}
}

var MLHelper;

(function() {

	var MovieListObj = function () {
		var self;
		var _movies = [];
		var currentsort = 'name';
		
		return {
		
			Init: function ( ) {
				self = this;
			},
			Load: function ( newsort) {

				currentsort = newsort;
				$.widget( "custom.iconselectmenu", $.ui.selectmenu, {
					_renderItem: function( ul, item ) {
						var li = $( "<li>" ),
						wrapper = $( "<div>",{ text: item.label } ).prepend (
						$( "<span class='sortimg'>").append (
							$( "<i>", { "class": "fa " + item.element.data("class") })
							)
						);
						return li.append( wrapper ).appendTo( ul );
					}
				});

				$("#moviesort").iconselectmenu({change: function(event, ui) {
					MLHelper.SortMovies(ui.item.value);
					MLHelper.ChangeSort(ui.item.value);
					}
				}).addClass("ui-menu-icons");
				
				self.SetSortImg();
				
				self.ReadMovies();
			},
			SetSortImg: function ()
			{
			
				$("#moviesort option").each(function()
				{
					var simg='';
					if( $(this).val() == $( "#moviesort" ).val() )
					{
						simg=$(this).data("class");
						if (simg) {
							var img = $( "<span class='sortimg'>").append (
								$( "<i>", { "class": "fa " + simg })
								);
							$("#moviesort-button .ui-selectmenu-text").prepend(img);
						}
					}
				});
			},
			SortMovies: function(idx)
			{
				var sorted = self._movies.slice(0);

				if(idx=='name')
				{
					// sort by name
					sorted.sort(function(a,b) {
						var x = a.title.toLowerCase();
						var y = b.title.toLowerCase();
						return x < y ? -1 : x > y ? 1 : 0;
					});
				}
				// sort by name desc
				if(idx=='named')
				{
					sorted.sort(function(a,b){var x = b.title.toLowerCase();var y = a.title.toLowerCase();return x < y ? -1 : x > y ? 1 : 0;});
				}
				if(idx=='date')
				{
					// sort by date
					sorted.sort(function(a,b) {
						return a.start - b.start;
					});
				}
				if(idx=='dated')
				{
					// sort by date desc
					sorted.sort(function(a,b) {
						return b.start - a.start;
					});
				}
				
				$('#movies').empty();
				
				for (var i = 0, len = sorted.length; i < len; i++) {
					$('#movies').append ( 
						sorted[i].html
					);
				}
				
				self.SetSortImg();
				
				return sorted;
			
			},
			ChangeSort : function(nsort)
			{
				$.ajax({
					url: "api/setmoviesort?nsort=" + nsort,
					success: function() {
					}
				});
			}, 
			ReadMovies :function()
			{
				self._movies = [];
				
				$('#movies').children('.tm_row').each(function() { 
				
				var d = $(this).data('start');
				var t = $(this).data('title');
			
				self._movies.push (
					{
					'id':$(this).attr('id'),
					'title':t,
					'start':d,
					'html': $(this)
					}
				);
				});
			
			},
			SetMovies :function(mv)
			{
				self._movies = mv.slice();
			}
		
		};

	};
	
	if (typeof MLHelper == 'undefined') {
		MLHelper = new MovieListObj();
		MLHelper.Init();
	}

})();

function reversetheme()
{
	return (theme=='pepper-grinder' || theme=='vader' || theme == 'smoothness' || theme == 'le-frog' || theme == 'mint-choc' || theme == 'humanity' || theme == 'eggplant' || theme == 'dot-luv' || theme == 'black-tie' );
}

function getHoverCls()
{
	return reversetheme() ? 'ui-state-active':'ui-state-hover';
}
function getActiveCls()
{
	return reversetheme() ? 'ui-state-hover':'ui-state-active';
}

function setHover(obj)
{
	var cls=getHoverCls();
	
	$(obj).hover(
		function(){ $(this).addClass(cls); },
		function(){ $(this).removeClass(cls); }
	);
}

function setTMHover()
{
	var cls='ui-state-active';
	if (theme=='pepper-grinder') {
		$('.tm_row').removeClass('ui-state-default');
		$('.tm_row').addClass('ui-state-hover');
	}
	
	$('.tm_row').hover(
		function(){ $(this).addClass(cls); },
		function(){ $(this).removeClass(cls); }
	);
}

// Localstorage

function SetLSValue(t,val)
{
	if(typeof(Storage) !== "undefined") {
		localStorage.setItem(t,val);
	}
}

function GetLSValue(t,def)
{
	var ret = def;
	if(typeof(Storage) !== "undefined") {
		var value = localStorage.getItem(t);
		if (value !== undefined && value !== null)
		{
			if(value === "true")
				return true;
			else if(value === "false")
				return false;
			else
				ret = value;
		}
	}
	return ret;
}

function SetSpinner()
{
	var spin = GetLSValue('spinner','fa-spinner');
	loadspinner = "<div id='spinner'><div class='fa " + spin + " fa-spin'></div></div>";
}

function isInArray(array, search) { return (array.indexOf(search) >= 0) ? true : false; }

function FillAllServices(bqs,callback)
{
	var options = "";
	var boptions = "";
	var refs = [];
	$.each( bqs, function( key, val ) {
		var ref = val['servicereference'];
		var name = val['servicename'];
		boptions += "<option value='" + encodeURIComponent(ref) + "'>" + val['servicename'] + "</option>";
		var slist = val['subservices'];
		var items = [];
		$.each( slist, function( key, val ) {
			var ref = val['servicereference'];
			if (!isInArray(refs,ref)) {
				refs.push(ref);
				if(ref.substring(0, 4) == "1:0:")
					items.push( "<option value='" + ref + "'>" + val['servicename'] + "</option>" );
				if(ref.substring(0, 5) == "4097:")
					items.push( "<option value='" + ref + "'>" + val['servicename'] + "</option>" );
				if(ref.substring(0, 7) == "1:134:1")
					items.push( "<option value='" + encodeURIComponent(ref) + "'>" + val['servicename'] + "</option>" );
			}
		});
		if (items.length>0) {
			options += "<optgroup label='" + name + "'>" + items.join("") + "</optgroup>";
		}
	});
	callback(options,boptions);

}

function GetAllServices(callback,radio)
{
	if (typeof callback === 'undefined')
		return;
	if (typeof radio === 'undefined')
		radio = false;
	
	var v = "gas-date";
	var vd = "gas-data";
	var ru = "";

	if (radio)
	{
		v += "r";
		vd += "r";
		ru = "&type=radio";
	}
	
	var date = new Date();
	date = date.getFullYear()+"-"+(date.getMonth()+1)+"-"+date.getDate();

	// load allservices only once a day
	var cache = GetLSValue(vd,'');
	if(cache === date) {
		cache = GetLSValue(v,null);
		if(cache != null) {
			var js = JSON.parse(cache);
			var bqs = js['services'];
			FillAllServices(bqs,callback);
			return;
		}
	}
	$.ajax({
		url: '/api/getallservices?renameserviceforxmbc=1'+ru,
		dataType: "json",
		success: function ( data ) {
			var sdata = JSON.stringify(data);
			SetLSValue(v,sdata);
			SetLSValue(vd,date);
			var bqs = data['services'];
			FillAllServices(bqs,callback);
		}
	});
}

function testPipStatus() {
	$.ajax({
		url: "api/pipinfo",
		dataType: "json",
		cache: false,
		success: function(pipinfo) {
			if(pipinfo.pip != pip){
				pip = pipinfo.pip;
                                buttonsSwitcher(pipinfo.pip);
			}
		}
	})
}

var SSHelperObj = function () {
	var self;
	var screenshotInterval = false;
	var ssr_i = 30;

	return {
		setup: function()
		{
			self = this;
			clearInterval(self.screenshotInterval);
			self.ssr_i = parseInt(GetLSValue('ssr_i','30'));
			
			$('#screenshotbutton0').click(function(){testPipStatus(); grabScreenshot('all');});
			$('#screenshotbutton1').click(function(){testPipStatus(); grabScreenshot('video');});
			$('#screenshotbutton2').click(function(){testPipStatus(); grabScreenshot('osd');});
			$('#screenshotbutton3').click(function(){testPipStatus(); grabScreenshot('pip');});
			$('#screenshotbutton4').click(function(){testPipStatus(); grabScreenshot('lcd');});
			$("#screenshotrefreshbutton").click(function(){testPipStatus();});

			$('#screenshotbutton').buttonset();
			$('#screenshotrefreshbutton').buttonset();
			$('#ssr_i').val(self.ssr_i);
			$('#ssr_s').prop('checked',GetLSValue('ssr_s',false));
			$('#ssr_hd').prop('checked',GetLSValue('ssr_hd',false));
			$('#screenshotspinner').addClass(GetLSValue('spinner','fa-spinner'));

			$('#ssr_hd').change(function() {
				testPipStatus();
				SetLSValue('ssr_hd',$('#ssr_hd').is(':checked'));
				grabScreenshot('auto');
			});
		
			$('#ssr_i').change(function() {
				testPipStatus();
				var t = $('#ssr_i').val();
				SetLSValue('ssr_i',t);
				self.ssr_i = parseInt(t);
				if($('#ssr_s').is(':checked'))
				{
					clearInterval(self.screenshotInterval);
					self.setSInterval();
				}
			});
			
			$('#ssr_s').change(function() {
				testPipStatus();
				var v = $('#ssr_s').is(':checked');
				if (v) {
					self.setSInterval();
				} else {
					clearInterval(self.screenshotInterval); 
				}
				SetLSValue('ssr_s',v);
			});
		
			screenshotMode = 'all'; // reset on page reload
			grabScreenshot(screenshotMode);

			if(GetLSValue('ssr_s',false))
				self.setSInterval();

		},setSInterval: function()
		{
			self.screenshotInterval = setInterval( function() { testPipStatus(); grabScreenshot('auto'); }, (self.ssr_i+1)*1000);
		}
	};
};

var SSHelper = new SSHelperObj();
