/* BEGIN legacy AutoTimer.js */
function FillAT(autotimerid){
	$(atxml).find('timer').each(function () {
		if($(this).attr('id') == autotimerid) {
			CurrentAT = new AutoTimerObj($(this));
			CurrentAT.UpdateUI();
		}
	});
}

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
		.then(xml => {
			var state=$(xml).find("e2state").first();
			var txt=$(xml).find("e2statetext").first();
			showError(txt.text(),state.text());
		});
}
/* END legacy AutoTimer.js */


function AddFilter(a,b,c)
{
	var i = ($('#filterlist tbody tr').length).toString();
	/*jshint multistr: true */
	$('#filterlist').append("<tr id='f" + i + "' style='display:none'> \
	<td class='nopadding'> \
		<select class='FT form-control' id='ft" + i + "' > \
			<option value='include'>" + tstr_at_filter_include + "</option> \
			<option value='exclude'>" + tstr_at_filter_exclude + "</option> \
		</select> \
	</td> \
	<td class='nopadding'> \
		<select class='FM form-control' id='fm" + i + "' > \
			<option value='title' selected=''>" + tstr_at_filter_title + "</option> \
			<option value='shortdescription'>" + tstr_at_filter_short_desc + "</option> \
			<option value='description'>" + tstr_at_filter_desc + "</option> \
			<option value='dayofweek'>" + tstr_at_filter_day + "</option> \
			</select> \
	</td> \
	<td> \
		<div class='form-line inactive' id='filine" + i + "'> \
			<input type='text' class='FI form-control' size='20' value='' style='display: block;' id='fi" + i + "'> \
		</div> \
		<div id='fsline" + i +"'> \
			<select class='FS' id='fs" + i + "' > \
				<option value='0' selected=''>" + tstr_monday + "</option> \
				<option value='1'>" + tstr_tuesday + "</option> \
				<option value='2'>" + tstr_wednesday + "</option> \
				<option value='3'>" + tstr_thursday + "</option> \
				<option value='4'>" + tstr_friday + "</option> \
				<option value='5'>" + tstr_saturday + "</option> \
				<option value='6'>" + tstr_sunday + "</option> \
				<option value='weekend'>" + tstr_weekend + "</option> \
				<option value='weekday'>" + tstr_weekday + "</option> \
			</select> \
		</div> \
	</td> \
	<td> \
		<input type='checkbox' class='FR form-control' id='fr" + i + "'> \
		<label for='fr" + i + "'>" + tstr_at_del + "</label> \
	</td> \
</tr>");

	$('#fsline' + i).hide();

	if(a!="")
		$('#ft' + i).val(a);
	if(b!="") {
		$('#ft' + i).attr("disabled", true);
		$('#fs' + i).attr("disabled", true);
		$('#fm' + i).attr("disabled", true);
		$('#fi' + i).attr("disabled", true);
		if(b=="dayofweek") {
			$('#fm' + i).val(b);
			$('#fi' + i).hide();
			$('#filine' + i).hide();
			$('#fs' + i).val(c);
			$('#fs' + i).show();
		}
		else {
			$('#fm' + i).val(b);
			$('#fs' + i).hide();
			$('#fsline' + i).hide();
			$('#fi' + i).val(c);
			$('#fi' + i).show();
		}
	}
	if ( a === "" && b === "")
		$.AdminBSB.select.activate();
	$('#f' + i).show();

	$('#fm' + i).change(function() {
		if ($(this).val()=="dayofweek") {
			$('#fsline' + i).show();
			$('#filine' + i).hide();
		} else {
			$('#fsline' + i).hide();
			$('#filine' + i).show();
		}
  });
}

function AutoTimerObj (xml) {

	this.isNew = false;
	this.MustSave = false;


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

	// Tags
	_b = [];
	xml.find("e2tags").each(function () {
		var tag = $(this).text();
		_b.push(encodeURIComponent(tag));
	});

	this.Tags = _b.slice();
	
	// Filters
	var _f = [];
	
	xml.find("include").each(function () {
		_f.push (
			{ 	"t" : "include",
				"w": $(this).attr("where"),
				"v": $(this).text()
			}
		); 
	});

	xml.find("exclude").each(function () {
		_f.push (
			{ 	"t" : "exclude",
				"w": $(this).attr("where"),
				"v": $(this).text()
			}
		); 
	});

	this.Filters = _f.slice();

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

AutoTimerObj.prototype.UpdateUI = function(){

	// window.autoTimers.populateForm(this);

	$('#filterlist').empty();
	var rc = $('#filterlist tr').length;
	if(rc>1)
	{
		for(var x=1;x<rc;x++)
			$('#f' + x.toString()).remove();
	}
	var c=0;
	$.each(this.Filters, function(index, value) {
		c++;
		AddFilter(value.t,value.w,value.v);
	});
	$('#_filters').prop('checked',(c>0));

	$.AdminBSB.select.activate();
	$('select', '#atform').not('.choices__input').selectpicker('refresh');

	// if(this.location) {
	// 	$('#location').val(this.location);
	// 	if(this.location !== $('#location').val()) {
	// 		current_location = "<option value='" + this.location + "'>" + this.location + "</option>";
	// 		$('#location').append(current_location);
	// 		$('#location').val(this.location);
	// 	}
	// 	$('#_location').prop('checked', true);
	// }
	// else
	// 	$('#_location').prop('checked', false);

	// $('#vps').prop('checked',this.vps);
	// $('#vpssm').prop('checked',!this.vpso);
};

function saveAT()
{
	// TODO: set mustsave
	if(CurrentAT) // && CurrentAT.MustSave)
	{

		var reqs = '';

		CurrentAT.justplay = $('#justplay').val();
		if(CurrentAT.justplay=="2")
		{
			reqs += "&justplay=0&always_zap=1";
		}
		else
			reqs += "&justplay=" + CurrentAT.justplay;

		CurrentAT.vps = $('#vps').is(':checked');
		if(!CurrentAT.vps)
			CurrentAT.vpo=false;
		reqs += (CurrentAT.vps) ? "1" : "0";

		reqs += "&vps_overwrite=";

		CurrentAT.vpso = !$('#vpssm').is(':checked');
		reqs += (CurrentAT.vpso) ? "1" : "0";

		var _f = [];
		for (i = 0; i < $('#filterlist tr').length; i++) {
			var FT = $("#ft" + i.toString()).val();
			var FM = $("#fm" + i.toString()).val();
			var FI = $("#fi" + i.toString()).val();
			var FS = $("#fs" + i.toString()).val();
			var FR = $("#fr" + i.toString()).is(":checked") ? true : false;
			if (FR === false){
				if (FM === 'dayofweek'){
					_f.push (
							{ 	"t" : FT,
								"w": FM,
								"v": FS
							}
						); 
				}
				else {
					_f.push (
							{ 	"t" : FT,
								"w": FM,
								"v": FI
							}
						); 
					}
			} else {
				_f.push (
							{ 	"t" :FT,
								"w": FM,
								"v": ""
							}
						); 
			}
		}

		var filtersParam = '';
		CurrentAT.Filters = _f.slice();
		if(CurrentAT.Filters && CurrentAT.Filters.length > 0) {
			$.each( CurrentAT.Filters, function( index, value ){
				var fr = "&";
				if(value.t === "exclude")
					fr+="!";
				fr += value.w;
				fr += "=";
				if (value.w === 'dayofweek')
					fr += value.v;
				else
					fr += encodeURIComponent(value.v);
				filtersParam += fr;
			});
		}

		console.log('reqs', reqs);

		window.autoTimers.saveEntry(filtersParam);

		$('#filterlist').empty();
	}
}

function getAutoTimerSettings()
{
	window.autoTimers.getSettings()
		.then(xml => {
			$(xml).find("e2setting").each(function () {
				var name = $(this).find("e2settingname").text();
				var val = $(this).find("e2settingvalue").text();
				if(name.indexOf("config.plugins.autotimer.") === 0)
				{
					name = name.substring(25);
					if(val === "True")
						$('#ats_'+name).prop('checked',true);
					else if(val === "False")
						$('#ats_'+name).prop('checked',false);
					else
						$('#ats_'+name).val(val);
				}
			});
		})
}

var autoTimerOptions;
function InitPage() {
	autoTimerOptions = owif.gui.populateAutoTimerOptions(true);

	$.AdminBSB.input.activate();
	$.AdminBSB.select.activate();

	if(!timeredit_initialized) {
		$('#editTimerForm').load('ajax/edittimer');
	}
}

function addAT(evt)
{
	if(false && CurrentAT && CurrentAT.isNew)
	{
		showError("please save the current autotimer first");
		return;
	}
	console.log('addAT');

	document.getElementById('atform').reset();

	var name = '';
	var id = '';
	var xml = '<timers><timer name="'+name+'" match="'+name+'" enabled="yes" id="'+id+'" justplay="0" overrideAlternatives="1"></timer></timers>';
	if (typeof evt !== 'undefined') 
	{
		xml = '<timers><timer name="'+evt.name+'" match="'+evt.name+'" enabled="yes" id="'+id+'" from="'+evt.timespanFrom+'" to="'+evt.timespanTo+'"';
		xml += ' searchType="exact" searchCase="sensitive" justplay="0" overrideAlternatives="1" ';
		xml += '><e2service><e2servicereference>'+evt.sref+'</e2servicereference><e2servicename>'+evt.sname+'</e2servicename></e2service>';
		xml += '</timer></timers>';
	}
	var xmlDoc = $.parseXML( xml );
	$(xmlDoc).find("timer").each(function () {
		$('#atlist').append($("<option data-id='" + $(this).attr("id") + "' value='" + $(this).attr("id") + "' data-x-selected >" + $(this).attr("name") + "</option>")).selectpicker('refresh');
		CurrentAT = new AutoTimerObj($(this));
		CurrentAT.isNew = true;
		CurrentAT.MustSave = true;
		CurrentAT.UpdateUI();
	});
	$('#atlist').find('li').each(function () {
		if($(this).data('id') == id)
			$(this).addClass('ui-selected');
		else
			$(this).removeClass('ui-selected');
	});
}

function readAT(keepSelection)
{
	CurrentAT = null;
	// window.autoTimers.getAll()
	// 	.then(xml => {
	// 		atxml = xml;
	// 		parseAT(keepSelection);
	// 	})
}

// parse and create AT List
function parseAT(keepSelection) {
	keepSelection = typeof keepSelection !== 'undefined' ? keepSelection : -1;
	$("#atlist").empty();
	$('#filterlist').empty();
	
	var atlist = []
	window.tagList = [];
	
	var state=$(atxml).find("e2state").first();
	if (state.text() == 'false') {
		showError($(atxml).find("e2statetext").first().text());
	}

	$(atxml).find("timer").each(function () {
		atlist.push($(this));

		$(this).find("e2tags").each(function () {
			var tag = $(this).text();
			// var tags = $(this).text().split(' ');
			// tags.forEach(function (tag, index) {
				if (window.tagList.indexOf(tag) < 0) {
					window.tagList.push(tag);
				}
			// });
		});
	});

	atlist.sort(function(a, b){
		var a1= a.attr("name"), b1=b.attr("name");
		if(a1==b1) return 0;
		return a1> b1? 1: -1;
	});
	
	var selectoptions = "<option selected disabled>Select an AutoTimer</option>";
	$(atlist).each(function () {
		var selected = ''
		if ( ( (keepSelection || "").toString() === $(this).attr("id").toString() ) ) {
			selected = 'selected'
		}
		selectoptions += "<option data-id='" + $(this).attr("id") + "' value='" + $(this).attr("id") + "' " + selected + " >" + $(this).attr("name") + "</option>"
	});
	$("#atlist").html(selectoptions).selectpicker('refresh');

	if(at2add)
	{
		addAT(at2add);
		at2add=null;
	}
	else
	{
		var item = $("#atlist").val();
		if(item) {
			FillAT(item);
		} else {
      // init with new entry
      addAT();
    }
	}
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

InitPage();
