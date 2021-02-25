/* BEGIN legacy AutoTimer.js */
function isBQ(sref) {
	return ((sref.indexOf('FROM BOUQUET') > -1) && (sref.indexOf('1:134:1') != 0));
}

function FillAT(autotimerid){
	var def = $(atxml).find('defaults');
	$(atxml).find('timer').each(function () {
		if($(this).attr('id') == autotimerid) {
			CurrentAT = new AutoTimerObj($(this));
			CurrentAT.UpdateUI();
		}
	});
}

function reloadAT() {
	showError('');
	readAT();
	$('#atlist').selectable({
		selected: function( event, ui ) {
			var ids = $('#atlist .ui-selected').map(function() {
				FillAT($(this).data('id'));
			});
		},
		classes: {
			'ui-selected': 'ui-state-active',
		}
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
	this.id = xml.attr("id");
	this.enabled = (xml.attr("enabled") == "yes");

	this.name = xml.attr("name");
	if(!this.name)
		this.name='';

	this.match = xml.attr("match");
	if(!this.match)
		this.match='';

	this.searchType = "partial";
	if(xml.attr("searchType"))
		this.searchType=xml.attr("searchType");

	this.searchCase = "insensitive";
	if(xml.attr("searchCase"))
		this.searchCase=xml.attr("searchCase");


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

	this.overrideAlternatives = (xml.attr("overrideAlternatives") == "1");

	this.timeSpan = false;
	if(xml.attr("from") && xml.attr("to"))
	{
		this.timespanFrom = xml.attr("from");
		this.timespanTo = xml.attr("to");
		this.timeSpan = true;
	}

	this.maxduration=null;
	if(xml.attr("maxduration")) 
		this.maxduration=xml.attr("maxduration");
	
	if(xml.attr("after") && xml.attr("before"))
	{
		var _i = parseInt(xml.attr("after"));
		var _date = new Date(_i*1000);
		this.after = moment(_date).format('YYYY-MM-DD');

		_i=parseInt(xml.attr("before"));
		_date = new Date(_i*1000);
		this.before = moment(_date).format('YYYY-MM-DD');
		this.timeFrame=true;
	}
	else
	{
		this.before=null;
		this.after=null;
		this.timeFrame=false;
	}

	this.avoidDuplicateDescription="0";
	if(xml.attr("avoidDuplicateDescription"))
		this.avoidDuplicateDescription=xml.attr("avoidDuplicateDescription")

	this.location=null;
	if(xml.attr("location")) 
		this.location = xml.attr("location");

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
	
	var _ae = xml.find('afterevent');
	this.afterevent=null;
	if(_ae.text())
	{
		this.afterevent=_ae.text();
		if(_ae.attr("from") && _ae.attr("to"))
		{
			this.aftereventFrom = _ae.attr("from");
			this.aftereventTo = _ae.attr("to");
		}
		else
		{
			this.aftereventFrom = null;
			this.aftereventTo = null;
		}
	}

	var _c = [];
	var _b = [];
	xml.find("e2service").each(function () {
		var ref = $(this).find("e2servicereference").text();
		if (isBQ(ref))
			_b.push(ref);
		else
			_c.push(ref);
	});
	
	this.Channels = _c.slice();
	this.Bouquets = _b.slice();

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

	this.counter = xml.attr("counter");
	if(!this.counter)
		this.counter='0';

	this.left = xml.attr("left");
	if(!this.left)
		this.left='0';

	this.counterFormat = xml.attr("counterFormat");
	if(!this.counterFormat)
		this.counterFormat='';

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

	window.autoTimers.populateForm(this);

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

	// $('#at_name').html("(" + this.name +")");
	
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

	// $('#_timerOffset').prop('checked', this.timerOffset);

	// if(this.timerOffset)
	// {
	// 	$('#tafter').val(this.timerOffsetAfter);
	// 	$('#tbefore').val(this.timerOffsetBefore);
	// }

	// if(this.afterevent) {
	// 	$('#afterevent').val(this.afterevent);
	// 	if (this.aftereventFrom && this.aftereventTo) {
	// 		$('#aftereventFrom').val(this.aftereventFrom);
	// 		$('#aftereventTo').val(this.aftereventTo);
	// 		$('#timeSpanAE').prop('checked',true);
	// 	}
	// }

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

		// keep logic
		// CurrentAT.afterevent = $('#afterevent').val();
		// var _ae = CurrentAT.afterevent;
		// if (_ae !== "default") {
		// 	reqs += "&aftereventFrom=" + CurrentAT.aftereventFrom;
		// 	reqs += "&aftereventTo=" + CurrentAT.aftereventTo;
		// }

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
	$.ajax({
		type: "GET", url: "/autotimer/get",
		dataType: "xml",
		success: function (xml)
		{
			var settings = [];
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
		},error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}


function test_simulateAT(simulate)
{

	$("#simtb").append("<tr><td COLSPAN=6>"+loadspinner+"</td></tr>");

	var link = simulate ? "simulate":"test";
	var tag = simulate ? "e2simulatedtimer":"e2testtimer";
	
	if ( (link === 'test') && (!CurrentAT.isNew) ) {
		link += "?id=" + CurrentAT.id;
	} else {
		link = 'simulate';
		tag = 'e2simulatedtimer';
	}
	console.debug('LINK', link, tag);
	$.ajax({
		type: "GET", url: "/autotimer/" +link,
		dataType: "xml",
		success: function (xml)
		{
			console.debug(xml);
			var lines= [];
			$(xml).find(tag).each(function () {
				var line = '<tr>';
				line += '<td>' + $(this).find('e2state').text() + '</td>';
				line += '<td>' + $(this).find('e2autotimername').text() + '</td>';
				line += '<td>' + $(this).find('e2name').text() + '</td>';
				line += '<td>' + $(this).find('e2servicename').text() + '</td>';
				var startTime = $(this).find('e2timebegin').text();
				line += '<td style="text-align: right">' + owif.utils.getStrftime(startTime) + '</td>';
        var endTime = $(this).find('e2timeend').text();
				line += '<td style="text-align: right">' + owif.utils.getToTimeText(startTime, endTime) + '</td>';
				line += '</tr>';
				console.debug(line);
				lines.push(line);
			});
			
			$("#simtb").empty();
			$(lines).each(function(idx,val) {
				$("#simtb").append(val);
			});
			if(lines.length===0)
				$("#simtb").append("<tr><td COLSPAN=6>NO Timer found</td></tr>");
		},
		error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}

var autoTimerOptions;
function InitPage() {
	reloadAT();

	autoTimerOptions = owif.gui.populateAutoTimerOptions();

	$.AdminBSB.input.activate();
	$.AdminBSB.select.activate();

	if(!timeredit_initialized) {
		$('#editTimerForm').load('ajax/edittimer');
	}
	$('#atlist').on('change', function (e) {
		// var optionSelected = jQuery("option:selected", this);
		var valueSelected = this.value;
		FillAT(valueSelected);
	});
}

function delAT()
{
	if(CurrentAT && !CurrentAT.isNew)
	{
		swal({
			title: tstr_del_autotimer,
			text: CurrentAT.name,
			type: "warning",
			showCancelButton: true,
			confirmButtonColor: "#DD6B55",
			confirmButtonText: tstrings_yes_delete,
			cancelButtonText: tstrings_no_cancel,
			closeOnConfirm: false,
			closeOnCancel: false
		}, function (isConfirm) {
			if (isConfirm) {
				$.ajax({
				type: "GET", url: "/autotimer/remove?id=" + CurrentAT.id,
				dataType: "xml",
				success: function (xml)
				{
					var state=$(xml).find("e2state").first();
					var txt=$(xml).find("e2statetext").first();
					showError(txt.text(),state.text());
					readAT();
				},
				error: function (request, status, error) {
					showError(request.responseText);
				}
			});
			} else {
				swal(tstrings_cancelled, CurrentAT.name, "error");
			}
		});
	}
}

function addAT(evt)
{
	if(CurrentAT && CurrentAT.isNew)
	{
		showError("please save the current autotimer first");
		return;
	}

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
	$.ajax({
		type: "GET", url: "/autotimer",
		dataType: "xml",
		success: function (xml)
		{
			atxml=xml;
			Parse(keepSelection);
		},error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}

// parse and create AT List
function Parse(keepSelection) {
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
