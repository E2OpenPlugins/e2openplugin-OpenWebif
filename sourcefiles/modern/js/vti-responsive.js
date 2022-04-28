var standby_status = -1;
var timerFormInitiated = - 1;


$(function () {

	if(!timeredit_initialized)
		$('#editTimerForm').load('ajax/edittimer');

	$('#navbar-collapse').on('show.bs.modal', function (e) {
		$('#navbar-collapse').removeAttr('style');
	});

	$('#navbar-collapse').on('hide.bs.modal', function (e) {
		$('#navbar-collapse').addAttr('style', 'width:100%');
	});

  // $('#TimerModal').modal('show')

	$('#TimerModal').on('show.bs.modal', function (e) {
		if (!$("#TimerModal").data('bs.modal').isShown){
			if (timerFormInitiated !== 1) {
				initTimerEditForm();
      }
      var epgEvent;
      try {
        var dataAttr = 'metadata';
		var meta = e.relatedTarget.closest('[data-' + dataAttr + ']');
        epgEvent = {};
		if (meta != null)
		{
			epgEvent = JSON.parse(e.relatedTarget.closest('[data-' + dataAttr + ']').dataset[dataAttr]);
		}
		else {
			epgEvent.sref = e.relatedTarget.dataset.ref;
			epgEvent.id = e.relatedTarget.dataset.evid;
		}
      } catch (ex) {
		console.log(ex);
        epgEvent = {};
      }
			if (!!epgEvent.sref && !!epgEvent.id) {
				addEditTimerEvent(epgEvent.sref, epgEvent.id);
			} else if (!!epgEvent.sref && !!epgEvent.begin && !!epgEvent.end) {
				editTimer(epgEvent.sref, epgEvent.begin, epgEvent.end);
			} else {
				addTimer();
			}
		
		}
	});

	$('#TimerModal').on('hidden.bs.modal', function (e) {
	});

	autosize($('textarea.auto-growth'));

	$.VTiTools.epgsearch.activate();
	$.VTiTools.moviesearch.activate();
	$(document).keydown(function(e) {
		if ((e.ctrlKey || e.cmdKey) &&  e.keyCode === 70)  {
			e.preventDefault();
			$.VTiTools.epgsearch.showSearchBar();
		}
		if ((e.ctrlKey || e.cmdKey) &&  e.keyCode === 69)  {
			e.preventDefault();
			$.VTiTools.epgsearch.showSearchBar();
		}
		if ((e.ctrlKey || e.cmdKey) &&  e.keyCode === 77)  {
			e.preventDefault();
			$.VTiTools.moviesearch.showSearchBarMovie();
		}
		
	});

	/*
	activateNotificationAndTasksScroll();
	setSkinListHeightAndScroll(true);
	setSettingListHeightAndScroll(true);
	$(window).resize(function () {
		setSkinListHeightAndScroll(false);
		setSettingListHeightAndScroll(false);
	});
	*/
	VTiWebConfig();
  
	setInterval(function () { getStatusInfo(); }, 3000);
});

function initJsTranslationAddon(strings) {
	tstr_timer = strings.timer;
	tstr_loading = strings.loading;
	tstr_add_timer = strings.add_timer;
	tstr_cancel = strings.cancel;
	tstr_close = strings.close;
	tstr_rename = strings.rename;
	tstr_prompt_save_changes = strings.prompt_save_changes;
	tstr_oops = strings.oops;
	tstr_weekday = strings.at_filter_weekday;
	tstr_weekend = strings.at_filter_weekend;
	tstr_at_del = strings.at_del;
	tstr_at_filter_title = strings.at_filter_title;
	tstr_at_filter_short_desc = strings.at_filter_short_desc;
	tstr_at_filter_desc = strings.at_filter_desc;
	tstr_at_filter_day = strings.at_filter_day;
	tstr_at_filter_include = strings.at_filter_include;
	tstr_at_filter_exclude = strings.at_filter_exclude;
	tstrings_no_cancel = strings.no_cancel;
	tstrings_yes_delete = strings.yes_delete;
	tstrings_yes = strings.yes;
	tstrings_deleted = strings.deleted;
	tstrings_cancelled = strings.cancelled;
	tstrings_need_input = strings.need_input;
	tstrings_install_package = strings.install_package;
	tstrings_remove_package = strings.remove_package;
	tstrings_update_package = strings.update_package;
	tstrings_upload_package = strings.upload_package;
	tstrings_upload_error = strings.upload_error;
	tstr_bqe_add_url = strings.bqe_add_url;
	tstr_bqe_name_url = strings.bqe_name_url;
}

function toggleFullRemote() {
	$("#symbolRemoteView").toggle();
	$("#fullRemoteView").toggle();
}

function SetSpinner()
{
	/*jshint multistr: true */
	loadspinner = " \
	<div class='page-loader-wrapper'> \
		<div class='loader'> \
			<div class='preloader'> \
				<div class='spinner-layer pl--skinned'> \
					<div class='circle-clipper left'> \
						<div class='circle'></div> \
					</div> \
					<div class='circle-clipper right'> \
						<div class='circle'></div> \
					</div> \
				</div> \
			</div> \
			<p>" + tstr_loading + "...</p> \
		</div> \
	</div>";
}

function listTimers()
{
	$("#timerdlgcont").html(loadspinner).load('ajax/timers #timers');
}

function set_epg_modal_content(data) {
	$('#editTimerForm').load('ajax/edittimer');
	$("#epgmodalcontent").html($( data ).find( '#epgcards' ).html());
}

function open_epg_dialog(sRef,Name) {
	$("#epgmodalcontent").html(loadspinner);
	var url = "ajax/epgdialog?sref=" + encodeURIComponent(sRef);
	$.get(url, set_epg_modal_content);
}

function load_channelsepg(url) {
	$("#channel_epg_container").load(url);
	return false;
}

function load_subcontent(url) {
	$("[id^=sub_content_container]").load(url);
	return false;
}

function loadtvcontent(url) {
	$("[id^=tvcontent]").load(url);
	return false;
}

function load_maincontent(url) {
	if (lastcontenturl != url || ( url.indexOf('screenshot') > -1 ) || ( url.indexOf('boxinfo') > -1 )) {
		$("#content_container").load(url);
		lastcontenturl = url;
	}
	return false;
}

function load_maincontent_spin_force(url) {
	var sp = '<div id="content_main">'+loadspinner+'</div>';
	$("#content_container").html(sp).load(url);
	lastcontenturl = url;
	return false;
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
	});
}

var SSHelperObj = function () {
	var self;
	var screenshotInterval = false;
	var ssr_i = 30;
	var ssr_hd = true;

	return {
		setup: function()
		{
			self = this;
			clearInterval(self.screenshotInterval);
			self.ssr_i = parseInt($('#ssr_i').val());
			self.ssr_hd = $('#ssr_hd').is(':checked');

			$("#dropdown").click(function() {testPipStatus();});
			$('#screenshotbutton0').click(function(){testPipStatus(); grabScreenshot('all');});
			$('#screenshotbutton1').click(function(){testPipStatus(); grabScreenshot('video');});
			$('#screenshotbutton2').click(function(){testPipStatus(); grabScreenshot('osd');});
			$('#screenshotbutton3').click(function(){testPipStatus(); grabScreenshot('pip');});
			$('#screenshotbutton4').click(function(){testPipStatus(); grabScreenshot('lcd');});
			$("button").click(function() {testPipStatus();});

			$('#ssr_i').val(self.ssr_i);
			$('#screenshotspinner').addClass(GetLSValue('spinner','fa-spinner'));
			$('#ssr_hd').change(function() {
				testPipStatus();
				self.ssr_hd = $('#ssr_hd').is(':checked');
				webapi_execute("/api/setwebconfig?screenshot_high_resolution=" + ( self.ssr_hd ? "true" : "false"));
				grabScreenshot('auto');
			});
			$('#ssr_i').change(function() {
				testPipStatus();
				var t = $('#ssr_i').val();
				webapi_execute("/api/setwebconfig?screenshot_refresh_time=" + t);
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
				webapi_execute("/api/setwebconfig?screenshot_refresh_auto=" + (v ? "true":"false"));
			});
		
			screenshotMode = 'all'; // reset on page reload
			grabScreenshot(screenshotMode);

			if($('#ssr_s').is(':checked')) {
				self.setSInterval();
			}

		},setSInterval: function()
		{
			self.screenshotInterval = setInterval( function() {testPipStatus(); grabScreenshot('auto');}, (self.ssr_i+1)*1000);
		}
	};
};

var SSHelper = new SSHelperObj();


function load_reboot_dialog(data,title){
	var sp = loadspinner.replace("<p>" + tstr_loading + "...</p>","<p>" + tstr_loading + "...</p><p>" + title + "</p>");
	$("#responsivespinner").html(sp);
}


function toggleLeftSideBar() {
	var $body = $('body');
	var height = $body.height();
	var $maincontent = $('#fullmaincontent');
	
	if ($('body').hasClass('ls-closed-manual')) {
		$maincontent.addClass('content');
		$maincontent.removeClass('contentfull');
		$body.removeClass('ls-closed-manual');
		$("#epgcard").height(($("#leftsidemenu").height() - 30) + "px");
		$('#topmenuheader,#mainfooter').show();
		$('#togglefullscreen').html('fullscreen');
		setTimeout(function(){load_tvcontent('ajax/multiepg?epgmode=tv');}, 500);
	} else {
		$body.addClass('ls-closed-manual');
		$maincontent.removeClass('content');
		$maincontent.addClass('contentfull');
		$('#epgcard').height(height + "px");
		$('#topmenuheader,#mainfooter').hide();
		$('#togglefullscreen').html('fullscreen_exit');
		setTimeout(function(){load_tvcontent('ajax/multiepg?epgmode=tv');}, 500);
	}
}

function grabScreenshot(mode) {
	$('#screenshotimage').load(function(){
	  $('#responsivespinnerscreenshot').hide();
	});
	if (mode != "auto") {
		screenshotMode = mode;
	} else {
		mode = screenshotMode;
	}
	timestamp = new Date().getTime();
	if (SSHelper.ssr_hd){
		$('#screenshotimage').attr("src",'/grab?format=jpg&mode=' + mode + '&t=' + timestamp);
	} else {
		$('#screenshotimage').attr("src",'/grab?format=jpg&r=720&mode=' + mode + '&t=' + timestamp);
	}
	$('#screenshotimage').attr("style",'max-height:60vh;');
	if (mode == "lcd") {
		$('#screenshotimage').attr("class",'img-responsive center-block');
	}
	else{
		$('#screenshotimage').attr("class",'img-responsive img-rounded center-block');
	}
}

getStatusInfo = function(){
  // redefine classic version of same function
	$("#osd__connection").toggle(!navigator.onLine);

  navigator.onLine && owif.api.getStatusInfo().then(function(statusinfo) { 
		var responsive_mute_status = '';
		if (statusinfo['muted'] == true) {
			mutestatus = 1;
			responsive_mute_status = "<a href='#' onclick='toggleMute(); return false;'><i class='material-icons'>volume_off</i></a>";
		} else {
			mutestatus = 0;
			responsive_mute_status = "<a href='#' onclick='toggleMute(); return false;'><i class='material-icons'>volume_up</i></a>";
		}
		$("#responsive_mute_status").html(responsive_mute_status);
		
		setOSD(statusinfo);
		
		if (statusinfo['isRecording'] == 'true') {
			var recs = statusinfo['Recording_list'];
			var rec_array = recs.split("\n");
			var recordingCount = 0;
			var tmp = '';
			for (var rec in rec_array) {
				if (rec_array[rec] != '') {
					recordingCount += 1;
					tmp += "<li> <a href='/#timers' onclick='load_maincontent(\"ajax/timers\");' data-dismiss='modal'>" + rec_array[rec] + "</a></li><hr />";
					
				}
			}
			$("#recmodalcontent").html(tmp);
			$("#osd__active-recordings .label-count").text(recordingCount).parent().show();
		} else {
			$("#osd__active-recordings").hide();
		}
		
		if (statusinfo['isStreaming'] == 'true') {
			var streams = statusinfo['Streaming_list'];
			var stream_array = streams.split("\n");
			var streamCount = 0;
			var tmp = '';
			for (var stream in stream_array) {
				if (stream_array[stream] != '') {
					streamCount += 1;
					tmp += "<li>" + stream_array[stream] + "</li><hr/>";
				}
			}
			$("#streammodalcontent").html(tmp);
			$("#osd__active-streams .label-count").text(streamCount).parent().show();
		} else {
			$("#osd__active-streams").hide();
		}

		$('body').toggleClass('standby-mode', statusinfo['inStandby'] === 'true');
	});
}

function setOSD( statusinfo )
{
	var sref = current_ref = statusinfo['currservice_serviceref'];
	var station = current_name = statusinfo['currservice_station'];
	var streamtitle = tstr_stream + ": " + station + "'><i class='material-icons'>ondemand_video</i></a>";
	var streamtitletrans = tstr_stream + " (" + tstr_transcoded + "): " + station + "'><i class='material-icons'>phone_android</i></a>";
	var responsive_osd_transcoding = '';
	var responsive_osd_stream = '';
	var responsive_osd_current = '';
	var responsive_osd_cur_event = '';

	if (station) {
		if ( (sref.indexOf("1:0:1") !== -1) || (sref.indexOf("1:134:1") !== -1) || (sref.indexOf("1:0:2") !== -1) || (sref.indexOf("1:134:2") !== -1) ) {
			if ( statusinfo['transcoding'] && ( (sref.indexOf("1:0:1") !== -1) || (sref.indexOf("1:134:1") !== -1) ) ) {
				responsive_osd_transcoding = "<a href='#' onclick=\"jumper8002('" + sref + "', '" + station + "')\"; title='" + streamtitletrans;
			}
			$('#osd__current-event__name').html(statusinfo['currservice_name']);
			$('#osd__current-event__time__start').html(statusinfo['currservice_begin']);
			$('#osd__current-event__time__end').html(statusinfo['currservice_end']);
			$('#osd__current-service').html(station);
			$('#osd__current-event__epg').off("click").click(function() {
				open_epg_dialog(sref, station);
			});
			$('#osd__current-event').off("click").click(function() {
				loadeventepg(statusinfo['currservice_id'], sref, '/images/default_picon.png');
			});
		} else if ( (sref.indexOf("4097:0:0") !== -1) || (sref.indexOf("1:0:0") !== -1)) {
			if (statusinfo['currservice_filename'] === '') {
				streamtitle = tstr_stream + ": " + station + "'>" + station + "</a>";
				responsive_osd_stream = "<a href='#' title='" + streamtitle;
			} else {
				var fn = statusinfo['currservice_filename'].replaceAll("'","%27").replaceAll("\"","%22");
				streamtitle = tstr_stream + ": " + station + "'><i class='material-icons'>movie</i></a>";
				responsive_osd_stream = "<a href='/web/ts.m3u?file=" + fn + "' target='_blank' title='" + streamtitle;
				responsive_osd_current = "<a href='/#movies' onclick='load_maincontent(\"ajax/movies\");'><b>" + station + "&nbsp;&nbsp;</b></a>";
				if (statusinfo['transcoding']) {
					responsive_osd_transcoding = "<a href='#' onclick=\"jumper8003('" + fn + "')\"; title='" + streamtitletrans;
				}
			}
		}
	}
	$("#osd__current-event__stream").attr("href", "/web/stream.m3u?ref=" + sref +"&name=" + encodeURIComponent(station));
	$("#volume-slider, #osd__current-volume").val(statusinfo['volume']);
	$("#responsive_osd_transcoding").html(responsive_osd_transcoding);
	$("#responsive_osd_stream").html(responsive_osd_stream);
	$("#responsive_osd_current").html(responsive_osd_current);
	$("#responsive_osd_cur_event").html(responsive_osd_cur_event);
	try {
		$(".channel-list__channel").removeClass("channel--active");
		$("#sref-" + sref.replace(/:/g, '_')).addClass("channel--active");
	} catch(e){}
}


function loadeventepg(id, ref, picon) {
	if (typeof picon !== 'undefined') {
		channelpicon = picon;
	} else {
		channelpicon = null;
	}
	var url = 'ajax/event?idev=' + id + '&sref=' + encodeURIComponent(ref);
	$("#eventdescriptionII").load(url);
}

function loadtimeredit(id, ref) {
	var url = 'ajax/event?idev=' + id + '&sref=' + encodeURIComponent(ref);
	$("#eventdescriptionII").load(url);
}

function initTimerEdit(radio, callback) {
	
	var bottomhalf = function() {
	$('#dirname').find('option').remove().end();
	$('#dirname').append($("<option></option>").attr("value", "None").text("Default"));
	for (var id in _locations) {
		var loc = _locations[id];
		$('#dirname').append($("<option></option>").attr("value", loc).text(loc));
	}
	$("#dirname").selectpicker("refresh");
	$('#tagsnew').html('');
	for (var id in _tags) {
		var tag = _tags[id];
		$('#tagsnew').append("<input type='checkbox' name='"+tag+"' value='"+tag+"' id='tag_"+tag+"'/><label for='tag_"+tag+"'>"+tag+"</label>");
	}
	
	$("#tagsnew > input").checkboxradio({icon: false});
	
	timeredit_initialized = true;
		callback();
	}

	initTimerBQ(radio, bottomhalf);
}

function initTimerEditBegin()
{
	
	$('#timerbegin').datetimepicker({
		format: "dd.mm.yy hh:ii",
		autoclose: true,
		todayHighlight: true,
		todayBtn: 'linked',
		minuteStep: 2,
		language: 'de', // TODO: fix date
	});
	$('#timerbegin').datetimepicker().on('changeDate', function(dateText, inst){
		if ($('#timerend').val() != '' &&
			$(this).datetimepicker('getDate') > $('#timerend').datetimepicker('getDate')) {
				showErrorMain(tstr_start_after_end);
		}
	});
}

function TimerConflict(conflicts, sRef, eventId, justplay)
{
  var SplitText = '';
  conflicts.sort( function(a, b) {
    return (a.begin - b.begin);
  });
  conflicts.forEach(function(entry) {
		SplitText += "<div class='row clearfix conflicting-timer'><div class='col-xs-12'> \
			<div class='card'> \
				<div class='header' style='padding: 10px 20px;'> \
					<div class='row clearfix'> \
						<div class='col-xs-12'> \
              <h2> \
                <span role='button'> \
                  <a href='javascript:void(0);' onclick='toggleTimerStatus(\"" + entry.serviceref + "\", \"" + entry.begin + "\", \"" + entry.end + "\"); this.closest(\".conflicting-timer\").classList.add(\"fade\");' class=\"link--skinned\" title='Disable Timer'> \
                    <i class='material-icons material-icons-centered material-icons-mg-right'>alarm_off</i> \
                  </a> \
                </span> \
							  " +  entry.name + " \
                <span style='opacity: 0.4;'> - " + entry.servicename + "</span> \
              </h2> \
						</div> \
					</div> \
				</div> \
				<div class='body'> \
						<div class='row clearfix'> \
							<div class='col-xs-12' style='margin: 10px 0 0;'> \
                <p>" + entry.realbegin + " - " + entry.realend + "</p> \
              </div> \
						</div> \
					</div> \
				</div> \
			</div> \
		</div></div> \
		"
	});
	$('.modal').modal('hide');
	$('#timerconflictmodal').html(SplitText);
	$('#TimerConflictModal').modal('show');
}

function cbAddTimerEvent(state) {
	if (state.state) {
		$('.event[data-id='+state.eventId+'][data-ref="'+state.sRef+'"] .timer').remove();
		$('.event[data-id='+state.eventId+'][data-ref="'+state.sRef+'"] div:first').append('<div class="timer">'+tstr_timer+'</div>');
		showErrorMain(tstr_timer_added, true);
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
				showErrorMain(state ? tstr_timer_added : txt, true);
			}
		}
	);
}

function addTimer(evt,chsref,chname,top) {
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
	$('#allow_duplicate').prop("checked", true);
	$('#autoadjust').prop("checked", false);
	$('#justplay').prop("checked", false);
	$('#afterevent').val(3);

	for (var i=0; i<7; i++) {
		$('#day'+i).prop('checked', false);
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

	setTimerEditFormTitle(tstr_add_timer);
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

function editTimer(serviceref, begin, end) {
	serviceref = decodeURIComponent(serviceref);
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
							$('#allow_duplicate').prop("checked", timer.allow_duplicate);
							$('#autoadjust').prop("checked", timer.autoadjust);
							$('#justplay').prop("checked", timer.justplay);
							$('#afterevent').val(timer.afterevent);
							var flags=timer.repeated;
							for (var i=0; i<7; i++) {
								$('#day'+i).prop('checked', ((flags & 1)==1));
								//$('#day'+i).prop('checked', ((flags & 1)==1)).checkboxradio("refresh");
								flags >>= 1;
							}
							
							$('#tagsnew > input').prop('checked',false) //.checkboxradio("refresh");
							
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
							
							if (typeof timer.vpsplugin_enabled !== 'undefined' && (!typeof timer.vpsplugin_enabled))
							{
								console.debug(timer.vpsplugin_enabled);
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
							
							setTimerEditFormTitle(tstr_edit_timer + " - " + timer.name);
							
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

function changeMoviesort(sort)
{
	MLHelper.SortMovies(sort);
	MLHelper.ChangeSort(sort);
	MLHelper.ReadMovies();
	lastcontenturl = '';
	load_maincontent_spin('ajax/movies');
}

function changeMoviesortSearch(sort)
{
	MLHelper.SortMovies(sort);
	MLHelper.ChangeSort(sort);
	MLHelper.ReadMovies();
	load_maincontent_spin_force(lastcontenturl);
}

function initTimerEditForm()
{
	if (timerFormInitiated !== 1) {
		timerFormInitiated = 1;
		addTimer();
		element = document.getElementById('editTimerForm');
		$("#timereditmodal").html(element)
	}
}

function setTimerEditFormTitle(title)
{
	$("#timerEditTitle").html(title);
}

function setVolume(value) {
	$.ajax("web/vol?set=set" + value);
	getStatusInfo();
}

function toggleMute() {
	$.ajax("web/vol?set=mute");
	getStatusInfo();
}

function CallEPGResponsive(url)
{
	load_tvcontent_spin(url);
}

function CallEPG()
{
	$('#myepgbtn2').click(function(){
		$("#tvcontent").load("ajax/multiepg?epgmode=radio");
	});
	
	$('#myepgbtn3').click(function(){
		$("#tvcontent").load("ajax/multiepg?epgmode=tv");
	});
	
	$("#tvbutton").buttonset();
	
	$("#tvcontent").load("ajax/multiepg?epgmode=tv");

}

function myEPGSearch() {
	var spar = $("#epgSearchTVRadio").val();
	var full = $("#myepgbtn0").is(":checked") ? '&full=1' : ''
	var bouquetsonly = $("#myepgbtn1").is(":checked") ? '&bouquetsonly=1' : ''
	var url = "ajax/epgdialog?sstr=" + encodeURIComponent(spar) + full + bouquetsonly;
	
	var w = $(window).width() -100;
	var h = $(window).height() -100;
	
	var buttons = {}
	buttons[tstr_close] = function() { $(this).dialog("close");};
	buttons[tstr_open_in_new_window] = function() { $(this).dialog("close"); open_epg_search_pop(spar,full);};
	
	load_dm_spinner(url,tstr_epgsearch,w,h,buttons);
}

$.VTiTools = {};

var $searchBar = $('.search-bar-epg');
var $searchBarMovie = $('.search-bar-movie');
$.VTiTools.epgsearch = {
	activate: function () {
		var _this = this;

		$('.js-search-epg').on('click', function () {
			_this.showSearchBar();
		});

		$searchBar.find('.close-search').on('click', function () {
			_this.hideSearchBar();
		});

		$searchBar.find('.start-search').on('click', function () {
			_this.startSearch();
		});

		$searchBar.find('input[type="text"]').on('keyup', function (e) {
			if (e.keyCode == 27) {
				_this.hideSearchBar();
			} else if (e.keyCode == 13) {
				_this.startSearch();
			}
		});
    },
	showSearchBar: function () {
		$.VTiTools.moviesearch.hideSearchBarMovie();
		$searchBar.addClass('open');
		$searchBar.find('input[type="text"]').focus();
	},
	hideSearchBar: function () {
		$searchBar.removeClass('open');
		$searchBar.find('input[type="text"]').val('');
	},
	startSearch: function() {
		if ($('body').hasClass('ls-closed-manual')) {
			toggleLeftSideBar();
		}
		gotEPGSearch();
		this.hideSearchBar();
	}
}

$.VTiTools.moviesearch = {
	activate: function () {
		var _this = this;

		$('.js-search-movie').on('click', function () {
			console.debug('xlkj');
			_this.showSearchBarMovie();
		});

		$searchBarMovie.find('.close-search').on('click', function () {
			_this.hideSearchBarMovie();
		});

		$searchBarMovie.find('.start-search').on('click', function () {
			_this.startSearchMovie();
		});

		$searchBarMovie.find('input[type="text"]').on('keyup', function (e) {
			if (e.keyCode == 27) {
				_this.hideSearchBarMovie();
			} else if (e.keyCode == 13) {
				_this.startSearchMovie();
			}
		});
    },
	showSearchBarMovie: function () {
		$.VTiTools.epgsearch.hideSearchBar();
		$searchBarMovie.addClass('open');
		$searchBarMovie.find('input[type="text"]').focus();
	},
	hideSearchBarMovie: function () {
		$searchBarMovie.removeClass('open');
		$searchBarMovie.find('input[type="text"]').val('');
	},
	startSearchMovie: function() {
		if ($('body').hasClass('ls-closed-manual')) {
			toggleLeftSideBar();
		}
		gotMovieSearch();
		this.hideSearchBarMovie();
	}
}


function gotEPGSearch() {
	var searchstr = $("#epgsearchtext").val();
	var full = $("#myepgbtn0").is(":checked") ? '&full=1' : ''
	

	var bouquetsonly = $("#myepgbtn1").is(":checked") ? '&bouquetsonly=1' : ''
	var url = "ajax/epgdialog?sstr=" + encodeURIComponent(searchstr) + full + bouquetsonly;
	$("#epgSearch").val("");
	load_maincontent(url);
	lastcontenturl = '';
}

function gotMovieSearch() {
	var searchstr = $("#moviesearchtext").val();
	var shortdesc = $("#mymoviesearchbtn0").is(":checked") ? '&short=1' : ''
	var extendeddesc = $("#mymoviesearchbtn1").is(":checked") ? '&extended=1' : ''
	var url = "ajax/moviesearch?find=" + encodeURIComponent(searchstr) + shortdesc+ extendeddesc;
	$("#epgSearch").val("");
	load_maincontent_spin_force(url);
}

function closeMessageModal() {
	$('#messageSentResponse').html('');
}

function sendModalMessage() {
	var text = $('#messageText').val();
	var type = $('#messageType').val();
	var timeout = $('#messageTimeout').val();
	$.ajax({
		url: '/api/message?text=' + text + '&type=' + type + '&timeout=' + timeout,
		dataType: "json",
		cache: false,
		success: function(result) { 
			$('#messageSentResponse').html('<div class="alert alert-info">' + result['message']+ '</div>');
			if(type==0)
			{
				MessageAnswerCounter=timeout;
				setTimeout(countdowngetMessage, 1000);
			}
		}
	});
	$('#messageText').val('');
	$('#messageType').val(1);
	$('#messageType').selectpicker('refresh');
	$('#messageTimeout').val('30');
	$('#messageTimeout').removeClass('active');
	$('#messageText').addClass('active');
}

function btn_saveTimer() {
				var enddate = moment($('#timerend').val(), "DD.MM.YYYY hh:mm").unix();
				var repeated = 0;
				$('[name="repeated"]:checked').each(function() {
					repeated += parseInt($(this).val());
				});
				var tags = "";
				$('[name="tagsnew"]:checked').each(function() {
					if(tags!="")
						tags+=" ";
					tags += $(this).val();
					
				});
				var urldata = { sRef: $('#bouquet_select').val(),
					end: enddate,
					name: $('#timername').val(),
					description: $('#description').val(),
					disabled: ($('#enabled').is(':checked')?"0":"1"),
					allow_duplicate: ($('#allow_duplicate').is(':checked')?"1":"0"),
					autoadjust: ($('#autoadjust').is(':checked')?"1":"0"),
					afterevent: $('#afterevent').val(),
					tags: tags,
					repeated: repeated };
				
				if($('#always_zap').is(':checked')) {
					urldata["always_zap"] = "1";
					urldata["justplay"] = "0";
				}
				else
					urldata["justplay"] = $('#justplay').is(':checked')?"1":"0";
				
				if ($('#dirname').val() != 'None')
					urldata["dirname"] = $('#dirname').val();
				if (!$('#has_vpsplugin1').is(':hidden'))
				{
					urldata["vpsplugin_enabled"] = ($('#vpsplugin_enabled').is(':checked')?"1":"0");
					urldata["vpsplugin_overwrite"] = ($('#vpsplugin_safemode').is(':checked')?"0":"1");
				}
				if (!timeredit_begindestroy) {
					var begindate = moment($('#timerbegin').val(), "DD.MM.YYYY hh:mm").unix();
					urldata["begin"] = begindate;
				}
				else
					urldata["begin"] = Math.round(current_begin);
				
				var canclose = false;
				if (current_serviceref == "") {
					$.ajax({
						async: false,
			            dataType: "json",
			            cache: false,
						url: "/api/timeradd?",
						data: urldata,
						success: function(result) {
							if (result.result) {
								canclose = true;
							}
							else {
								if(result.conflicts)
								{
									var conftext='Timer Conflicts:<br>';
									result.conflicts.forEach(function(entry) {
										conftext += entry.name+" / "+entry.servicename+" / "+entry.realbegin+" - "+entry.realend+"<br>";
									});
									showErrorMain(conftext);
								} else {
									showErrorMain(result.message);
								}
							}
						}
					});
				}
				else {
					urldata['channelOld'] = current_serviceref;
					urldata['beginOld'] = Math.round(current_begin);
					urldata['endOld'] = Math.round(current_end);
					$.ajax({
						async: false,
			            dataType: "json",
			            cache: false,
						url: "api/timerchange?",
						data: urldata,
						success: function(result) {
							if (result.result) {
								canclose = true;
							}
							else {
								if(result.conflicts)
								{
									var conftext='Timer Conflicts:<br>';
									result.conflicts.forEach(function(entry) {
										conftext += entry.name+" / "+entry.servicename+" / "+entry.realbegin+" - "+entry.realend+"<br>";
									});
									$("#error").text(conftext);
								} else {
									$("#error").text(result.message);
								}
							}
						}
					});
				}
				
				if (canclose) {
					if (reloadTimers) {
							if ( lastcontenturl.startsWith('ajax/timers') ) {
								lastcontenturl = '';
								setTimeout(function(){load_maincontent("ajax/timers")}, 500);
							}
					}
				}
			}

function VTiWebConfig() {
	$('#mymoviesearchbtn0').change(function () {
		var res = $("#mymoviesearchbtn0").is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?moviesearchshort=' + res);
	});
	
	$('#mymoviesearchbtn1').change(function () {
		var res = $("#mymoviesearchbtn1").is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?moviesearchextended=' + res);
	});
	
	$('#myepgbtn0').change(function () {
		var fullsearch = $("#myepgbtn0").is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?fullsearch=' + fullsearch);
	});
	
	$('#myepgbtn1').change(function () {
		var bqonly = $("#myepgbtn1").is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?bqonly=' + bqonly);
	});
	
	$('#remotegrabscreen1').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?rcugrabscreen=' + val);
	});

	$('#remotecontrolview').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?remotecontrolview=' + val);
		toggleFullRemote();
	});

	$('#minmovielist').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?minmovielist=' + val);
		if ( lastcontenturl.startsWith('ajax/movies') ) {
			load_maincontent_spin_force(lastcontenturl);
		}
	});
	$('#mintimerlist').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?mintimerlist=' + val);
		if ( lastcontenturl === 'ajax/timers') {
			lastcontenturl = '';
			load_maincontent('ajax/timers');
		}
	});
	$('#minepglist').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?minepglist=' + val);
	});
	$('#zapstream').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?zapstream=' + val);
	});
	$('#showpicons').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?showpicons=' + val);
		$('#showpiconbackground').prop('disabled', !val);
	});
	$('#showpiconbackground').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?showpiconbackground=' + val);
	});
	$('#showiptvchannelsinselection').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?showiptvchannelsinselection=' + val);
	});

	$('#screenshotchannelname').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?screenshotchannelname=' + val);
	});

	$('#thememodebtn').change(function () {
		var themeMode = $(this).is(":checked") ? $(this).val() : 'supabright';
		$('body').removeClass(function (index, className) {
			return (className.match(/(^|\s)theme--\S+/g) || []).join(' ');
		});
		if ($(this).is(":checked")) {
			$('body').addClass('theme--' + themeMode);
		} else {
			$('body').addClass('theme--' + 'supabright');
		}
		$.get('api/setthememode?themeMode=' + themeMode);
	});
	$('#nownext_columns').change(function () {
		var val = $(this).is(":checked") ? '1' : '0'
		$.get('api/setvtiwebconfig?nownext_columns=' + val);
	});

}
/*
//Skin tab content set height and show scroll
function setSkinListHeightAndScroll(isFirstTime) {
	var height = $(window).height() - ($('.navbar').innerHeight() + $('.right-sidebar .nav-tabs').outerHeight());
	var $el = $('.skin-switcher');

	if (!isFirstTime){
		$el.slimScroll({ destroy: true }).height('auto');
		$el.parent().find('.slimScrollBar, .slimScrollRail').remove();
	}

	$el.slimscroll({
		height: height + 'px',
		color: 'rgba(0,0,0,0.5)',
		size: '6px',
		alwaysVisible: false,
		borderRadius: '0',
		railBorderRadius: '0'
	});
}

//Setting tab content set height and show scroll
function setSettingListHeightAndScroll(isFirstTime) {
	var height = $(window).height() - ($('.navbar').innerHeight() + $('.right-sidebar .nav-tabs').outerHeight());
	var $el = $('.right-sidebar .demo-settings');

	if (!isFirstTime){
		$el.slimScroll({ destroy: true }).height('auto');
		$el.parent().find('.slimScrollBar, .slimScrollRail').remove();
	}

	$el.slimscroll({
		height: height + 'px',
		color: 'rgba(0,0,0,0.5)',
		size: '6px',
		alwaysVisible: false,
		borderRadius: '0',
		railBorderRadius: '0'
	});
}

//Activate notification and task dropdown on top right menu
function activateNotificationAndTasksScroll() {
	$('.navbar-right .dropdown-menu .body .menu').slimscroll({
		height: '254px',
		color: 'rgba(0,0,0,0.5)',
		size: '4px',
		alwaysVisible: false,
		borderRadius: '0',
		railBorderRadius: '0'
	});
}
*/
function showErrorMain(txt,st)
{
	st = typeof st !== 'undefined' ? st : "False";
	var infotype = "error";
	if (st === true || st === 'True' || st === 'true') {
		infotype = "success";
	}
	
	if (txt !== '') {
		swal("", txt, infotype);
	} else {
		$('#statuscont').hide();
	}
	
}

function deleteTimer(sRef, begin, end, title) {
	var t = decodeURIComponent(title);
	swal({
		title: tstr_del_timer,
		text: t,
		type: "warning",
		showCancelButton: true,
		confirmButtonColor: "#DD6B55",
		confirmButtonText: tstrings_yes_delete,
		cancelButtonText: tstrings_no_cancel,
		animation: "none"
	}, function (isConfirm) {
		if (isConfirm) {
			webapi_execute("/api/timerdelete?sRef=" + sRef + "&begin=" + begin + "&end=" + end, 
			function() { $('#'+begin+'-'+end).remove(); });
		}
	});
}

function deleteMovie(sRef, divid, title) {
	
	swal({
		title: tstr_del_recording,
		text: title,
		type: "warning",
		showCancelButton: true,
		confirmButtonColor: "#DD6B55",
		confirmButtonText: tstrings_yes_delete,
		cancelButtonText: tstrings_no_cancel,
		closeOnConfirm: false,
		animation: "none"
	}, function (isConfirm) {
		if (isConfirm) {
			webapi_execute_movie("/api/moviedelete?sRef=" + sRef,
				function (state) {
					if(state){ 
						swal(tstrings_deleted, title, "success");
						$('#' + divid).remove();
					}
				}
			);
		}
	});
}

function renameMovie(sRef, title) {
	swal({
		title: tstr_ren_recording,
		text: title,
		type: "input",
		showCancelButton: true,
		closeOnConfirm: false,
		animation: "none",
		inputPlaceholder: title,
		inputValue: title,
		input: "text"
	}, function (newname) {
		if ( (newname === false) || (newname === title) ) return false;
		if (newname === "") {
			swal.showInputError(tstrings_need_input); return false
		}
		webapi_execute_movie("/api/movierename?sRef=" + sRef+"&newname="+newname);
		showErrorMain(newname, true);
	});
}

function closeSideBar() {
	var $body = $('body');
	var width = $body.width();
	if (width < $.AdminBSB.options.leftSideBar.breakpointWidth) {
		var $openCloseBar = $('#leftsidebarin');
		$body.addClass('ls-closed');
		$openCloseBar.fadeIn();
	} else {
		$body.removeClass('ls-closed');
        //$('.sidebar').hide();
  }
}