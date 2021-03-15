/* BEGIN legacy AutoTimer.js */
function setAutoTimerSettings() {
	var reqs = "";
	reqs += "autopoll=" + $('#ats_autopoll').is(':checked') ? "true":"";
	reqs += "&interval=" + $('#ats_interval').val();
	reqs += "&try_guessing=";
	reqs += $('#ats_try_guessing').is(':checked') ? "true":"";
	reqs += "&disabled_on_conflict=";
	reqs += $('#ats_disabled_on_conflict').is(':checked') ? "true":"";
	reqs += "&addsimilar_on_conflict=";
	reqs += $('#ats_addsimilar_on_conflict').is(':checked') ? "true":"";
	reqs += "&show_in_extensionsmenu=";
	reqs += $('#ats_show_in_extensionsmenu').is(':checked') ? "true":"";
	reqs += "&fastscan=";
	reqs += $('#ats_fastscan').is(':checked') ? "true":"";
	reqs += "&notifconflict=";
	reqs += $('#ats_notifconflict').is(':checked') ? "true":"";
	reqs += "&notifsimilar=";
	reqs += $('#ats_notifsimilar').is(':checked') ? "true":"";
	reqs += "&maxdaysinfuture=" + $('#ats_maxdaysinfuture').val();
	var v = $('#ats_add_autotimer_to_tags').is(':checked') ? "true":"";
	reqs += "&add_autotimer_to_tags=" + v;
	v = $('#ats_add_name_to_tags').is(':checked') ? "true":"";
	reqs += "&add_name_to_tags=" + v
	reqs += "&refresh=" + $('#ats_refresh').val();
	reqs += "&editor=" + $('#ats_editor').val();
	
	window.autoTimers.saveSettings(reqs)
		// .then(xml => {
		// 	var state=$(xml).find("e2state").first();
		// 	var txt=$(xml).find("e2statetext").first();
		// 	showError(txt.text(),state.text());
		// });
}
/* END legacy AutoTimer.js */

function getAutoTimerSettings()
{
	window.autoTimers.getSettings()
		// .then(xml => {
		// 	$(xml).find("e2setting").each(function () {
		// 		var name = $(this).find("e2settingname").text();
		// 		var val = $(this).find("e2settingvalue").text();
		// 		if(name.indexOf("config.plugins.autotimer.") === 0)
		// 		{
		// 			name = name.substring(25);
		// 			if(val === "True")
		// 				$('#ats_'+name).prop('checked',true);
		// 			else if(val === "False")
		// 				$('#ats_'+name).prop('checked',false);
		// 			else
		// 				$('#ats_'+name).val(val);
		// 		}
		// 	});
		// })
}

function AutoTimerObj (xml) {

	// justplay 0 = record
	// justplay 1 = zap
	// justplay 2 = reord+zap
	this.justplay = "0";
	if(xml.attr("justplay"))
		this.justplay=xml.attr("justplay");

	if(xml.attr("always_zap"))
	{
		var az = xml.attr("always_zap");
		if(az == "1")
			this.justplay = "2";
	}

	this.timerOffset=false;
	if(xml.attr("offset"))
	{
		var fields = xml.attr("offset").split(',');
		var _b = fields[0];
		var _a = fields[1];
		if (typeof _a === "undefined") {
			this.timerOffsetAfter=_b;
			this.timerOffsetBefore=_b;
		} else {
			this.timerOffsetAfter=_a;
			this.timerOffsetBefore=_b;
		}
		this.timerOffset=true;
	}

	this.vps = false;
	this.vpso = false;
	if(xml.attr("vps_enabled") === "yes") {
		this.vps = true;
		if(xml.attr("vps_overwrite") === "yes") {
			this.vpso = true;
		}
	}
	
	this.series_labeling = false;
	if(xml.attr("series_labeling") === "yes") {
		this.series_labeling = true;
	}
	
	this.autoadjust = false;
	if(xml.attr("autoadjust") === "1") {
		this.autoadjust = true;
	}
	this.allow_duplicate = true;
	if(xml.attr("allow_duplicate") === "0") {
		this.allow_duplicate = false;
	}
	this.avoidDuplicateMovies = false;
	if(xml.attr("avoidDuplicateMovies") === "1") {
		this.avoidDuplicateMovies = true;
	}
}

// AutoTimerObj.prototype.UpdateUI = function(){
	// $('select', '#atform').not('.choices__input').selectpicker('refresh');

	// $('#vps').prop('checked',this.vps);
	// $('#vpssm').prop('checked',!this.vpso);
// };

function saveAT()
{
		var reqs = '';
		var CurrentAT = {};

		CurrentAT.justplay = $('#justplay').val();
		if(CurrentAT.justplay=="2") {
			reqs += "&justplay=0&always_zap=1";
		} else {
			reqs += "&justplay=" + CurrentAT.justplay;
		}

		CurrentAT.vps = $('#vps').is(':checked');
		if (!CurrentAT.vps) {
			CurrentAT.vpo=false;
		}
		reqs += (CurrentAT.vps) ? "1" : "0";

		reqs += "&vps_overwrite=";

		CurrentAT.vpso = !$('#vpssm').is(':checked');
		reqs += (CurrentAT.vpso) ? "1" : "0";
}

function showError(txt,st)
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
