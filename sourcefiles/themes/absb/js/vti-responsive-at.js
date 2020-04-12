function toUnixDate(date){
	var d = moment(date, "DD.MM.YY").unix();
	return d;
}

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
		<select class='FM form-control' id='fm" + i.toString() + "' > \
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
			<select class='FS' style='display: none;' id='fs" + i + "' > \
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
}


function initValues () {

	var _sel3 = $('#maxduration');
	var _sel4 = $('#counter');
	var _sel5 = $('#left');
	for (var x=0;x<100;x++)
	{
		var sx=x.toString();
		if(x<10)
			sx='0'+sx;
		_sel4.append($('<option></option>').val(x).html(sx));
		_sel5.append($('<option></option>').val(x).html(sx));
	}
	for (var x=0;x<1000;x++)
	{
		var sx=x.toString();
		if(x<10)
			sx='0'+sx;
		_sel3.append($('<option></option>').val(x).html(sx));
	}
	$('#tafter').val('5');
	$('#tbefore').val('5');
	$('#maxduration').val('70');
	$('#after').datetimepicker({
		format: 'dd.mm.yy',
		initialDate: _dateb,
		autoclose: true,
		minView: 2,
    });
	$('#after').datetimepicker().on('changeDate', function(ev){
		var before = moment($('#before').val(), "DD.MM.YY").unix();
		var after = moment($('#after').val(), "DD.MM.YY").unix();
		if (before < after) {
				showError('AFTER:' + tstr_start_after_end);
			} else
				showError('');
	});
	var _dateb = new Date();
	$('#after').val(moment(_dateb).format('DD.MM.YY'));
	
	var _datea = new Date();
	_datea.setDate(_dateb.getDate()+7);
	$('#from').val('20:15');
	$('#to').val('23:15');
	$('#aefrom').val('20:15');
	$('#aeto').val('23:15');
	$('#before').datetimepicker({
		format: 'dd.mm.yy',
		initialDate: _dateb,
		autoclose: true,
		minView: 2,
	});
	$('#before').datetimepicker().on('changeDate', function(ev){
		var before = moment($('#before').val(), "DD.MM.YY").unix();
		var after = moment($('#after').val(), "DD.MM.YY").unix();
		if (before < after) {
				showError('BEFORE:' + tstr_start_after_end);
			} else
				showError('');
	});
	$('#before').val(moment(_datea).format('DD.MM.YY'));
}


function timeFrameAfterCheck() {

	if ($('#timeFrameAfter').is(':checked') === true) {
		var _da = moment($('#after').val(), "DD.MM.YY").toDate();
		var _datea = new Date(_da);
		var _dateb = new Date();
		_dateb.setDate(_datea.getDate()+7);
		_da =  moment(_dateb).format('DD.MM.YY');
		$('#before').val(_da);
		$('#beforeE').show();
	}
	else {
		var _datea = new Date(2038,0,1);
		var _da = moment(_datea).format('DD.MM.YY');
		$('#before').val(_da);
		$('#beforeE').hide();
	}

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
		this.from = xml.attr("from");
		this.to = xml.attr("to");
		this.timeSpan = true;
	}

	this.maxduration=null;
	if(xml.attr("maxduration")) 
		this.maxduration=xml.attr("maxduration");
	
	if(xml.attr("after") && xml.attr("before"))
	{
		var _i = parseInt(xml.attr("after"));
		var _date = new Date(_i*1000);
		this.after = moment(_date).format('DD.MM.YY');

		_i=parseInt(xml.attr("before"));
		_date = new Date(_i*1000);
		this.before = moment(_date).format('DD.MM.YY');
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
			this.aftereventfrom = _ae.attr("from");
			this.aftereventto = _ae.attr("to");
		}
		else
		{
			this.aftereventfrom=null;
			this.aftereventto=null;
		}
	}

	var _c = [];
	var _b = [];
	xml.find("e2service").each(function () {
		var ref = $(this).find("e2servicereference").text();
		if (isBQ(ref))
			_b.push(encodeURIComponent(ref));
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
	$('#filterlist').empty();
	$('#enabled').prop('checked', this.enabled); 
	$('#name').val(this.name);
	$('#match').val(this.match);
	$('#searchType').val(this.searchType);
	$('#searchType').selectpicker('refresh');
	$('#searchCase').val(this.searchCase);
	$('#searchCase').selectpicker('refresh');
	$('#justplay').val(this.justplay);
	$('#overrideAlternatives').prop('checked', this.overrideAlternatives); 
	$('#timeSpan').prop('checked',this.timeSpan);
	$('#at_name').html("(" + this.name +")");
	if(this.timeSpan)
	{
		$('#from').val(this.from);
		$('#to').val(this.to);
	}
	if(this.maxduration)
	{
		$('#maxDuration').prop('checked',true);
		$('#maxduration').val(this.maxduration);
	}
	else
		$('#maxDuration').prop('checked',false);
	$('#timeFrame').prop('checked',this.timeFrame);
	if(this.timeFrame)
	{
		$('#after').val(this.after);
		$('#before').val(this.before);
		var _dateb = moment($('#before').val(), "DD.MM.YY").toDate();
		var _maxd = new Date(2038,0,1);
		if (_dateb < _maxd) {
			$('#timeFrameAfter').prop('checked',true);
			$('#beforeE').show();
		}
		else {
			$('#timeFrameAfter').prop('checked',false);
			$('#beforeE').hide();
		}
	}
	$("#avoidDuplicateDescription").val(this.avoidDuplicateDescription);
	$('#avoidDuplicateDescription').selectpicker('refresh');
	
	if(this.location) {
		$('#location').val(this.location);
		if(this.location !== $('#location').val()) {
			current_location = "<option value='" + this.location + "'>" + this.location + "</option>";
			$('#location').append(current_location);
			$('#location').val(this.location);
		}
		$('#location').selectpicker('refresh');
		$('#Location').prop('checked',true);
	}
	else
		$('#Location').prop('checked',false);
	$('#timerOffset').prop('checked',this.timerOffset);
	if(this.timerOffset)
	{
		$('#tafter').val(this.timerOffsetAfter);
		$('#tbefore').val(this.timerOffsetBefore);
	}
	$('#timeSpanAE').prop('checked',false);
	$('#afterevent').val("");
	if(this.afterevent) {
		$('#afterevent').val(this.afterevent);
		if(this.aftereventfrom && this.aftereventto) {
			$('#aefrom').val(this.aftereventfrom);
			$('#aeto').val(this.aftereventto);
			$('#timeSpanAE').prop('checked',true);
		}
	}
	$('#afterevent').selectpicker('refresh');
	$('#channels').val(null);
	$('#bouquets').val(null);
	$.each(this.Bouquets, function(index, value) {
		$('#bouquets option[value="' + value + '"]').prop("selected", true);
	});
	$.each(this.Channels, function(index, value) {
		$('#channels option[value="' + value + '"]').prop("selected", true);
	});
	$('#bouquets').selectpicker('refresh');
	$('#channels').selectpicker('refresh');
	$('#Bouquets').prop('checked',(this.Bouquets.length>0));
	$('#Channels').prop('checked',(this.Channels.length>0));
	$('#tags').val(null);
	$.each(this.Tags, function(index, value) {
		$('#tags option[value="' + value + '"]').prop("selected", true);
	});
	$('#tags').selectpicker('refresh');
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
	$.AdminBSB.select.activate();
	$('#Filter').prop('checked',(c>0));
	$('#counter').val(this.counter);
	$('#left').val(this.left);
	$('#counterFormat').val(this.counterFormat);
	$('#vps').prop('checked',this.vps);
	$('#vpssm').prop('checked',!this.vpso);
	$('#series_labeling').prop('checked',this.series_labeling);
	$('#autoadjust').prop('checked',this.autoadjust);
	$('#allow_duplicate').prop('checked',this.allow_duplicate);
	$('#avoidDuplicateMovies').prop('checked', this.avoidDuplicateMovies);
	checkValues();
};

function saveAT()
{
	// TODO: set mustsave
	if(CurrentAT) // && CurrentAT.MustSave)
	{

		var reqs = "/autotimer/edit?";
		CurrentAT.enabled = $('#enabled').is(':checked');
		CurrentAT.name = $('#name').val();
		CurrentAT.match = $('#match').val();
		CurrentAT.searchType = $('#searchType').val();
		CurrentAT.searchCase = $('#searchCase').val();
		CurrentAT.justplay = $('#justplay').val();
		CurrentAT.overrideAlternatives = $('#overrideAlternatives').is(':checked');
		CurrentAT.timeSpan = $('#timeSpan').is(':checked');
		CurrentAT.avoidDuplicateDescription = $('#avoidDuplicateDescription').val();
		CurrentAT.timeSpan = $('#timeSpan').is(':checked');
		CurrentAT.from = $('#from').val();
		CurrentAT.to = $('#to').val();
		CurrentAT.timerOffset = $('#timerOffset').is(':checked');
		CurrentAT.before = $('#before').val();
		CurrentAT.after = $('#after').val();

		if($('#maxDuration').is(':checked')) {
			CurrentAT.maxduration = $('#maxduration').val();
		}
		else
			CurrentAT.maxduration = null;

		if($('#Location').is(':checked'))
			CurrentAT.location = $('#location').val();
		else
			CurrentAT.location = null;

		CurrentAT.timeFrame = $('#timeFrame').is(':checked');
		CurrentAT.timerOffsetBefore = $('#tbefore').val();
		CurrentAT.timerOffsetAfter = $('#tafter').val();
		CurrentAT.afterevent = $('#afterevent').val();
		CurrentAT.aftereventfrom = $('#aefrom').val();
		CurrentAT.aftereventto = $('#aeto').val();
		CurrentAT.Bouquets = $("#bouquets").val();
		CurrentAT.Channels = $("#channels").val();
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
		CurrentAT.Filters = _f.slice();
		CurrentAT.Tags = $("#tags").val();
		CurrentAT.counter = $('#counter').val();
		CurrentAT.left = $('#left').val();
		CurrentAT.counterFormat = $('#counterFormat').val();
		CurrentAT.vps = $('#vps').is(':checked');
		CurrentAT.vpso = !$('#vpssm').is(':checked');
		CurrentAT.series_labeling = $('#series_labeling').is(':checked');
		CurrentAT.allow_duplicate = $('#allow_duplicate').is(':checked');
		CurrentAT.autoadjust = $('#autoadjust').is(':checked');
		CurrentAT.avoidDuplicateMovies = $('#avoidDuplicateMovies').is(':checked');
		reqs += "match=" + encodeURIComponent(CurrentAT.match);
		reqs += "&name=" + encodeURIComponent(CurrentAT.name);
		reqs += "&enabled=";
		reqs += (CurrentAT.enabled) ? "1" : "0";
		if(CurrentAT.justplay=="2")
		{
			reqs += "&justplay=0&always_zap=1";
		}
		else
			reqs += "&justplay=" + CurrentAT.justplay;

		reqs += "&setEndtime=";
		reqs += (CurrentAT.setEndtime) ? "1" : "0";
		reqs += "&searchCase=" + CurrentAT.searchCase;
		reqs += "&overrideAlternatives=";
		reqs += (CurrentAT.overrideAlternatives) ? "1" : "0";
		reqs += "&avoidDuplicateDescription=" + CurrentAT.avoidDuplicateDescription;
		// TODO:
		//	reqs += "&searchForDuplicateDescription=" + CurrentAT.searchForDuplicateDescription;
		if(CurrentAT.location)
			reqs += "&location=" + encodeURIComponent(CurrentAT.location);
		reqs += "&searchType=" + CurrentAT.searchType;
		reqs += "&maxduration=";
		if(CurrentAT.maxduration && CurrentAT.maxduration > -1)
			reqs += CurrentAT.maxduration;

		if(CurrentAT.counter!='0')
		{
			reqs += "&counter=" + CurrentAT.counter;
			reqs += "&counterFormat=" + CurrentAT.counterFormat;
		}
		
		if(CurrentAT.timerOffset) {
			if(CurrentAT.timerOffsetAfter > -1 && CurrentAT.timerOffsetBefore > -1)
				reqs += "&offset=" + CurrentAT.timerOffsetBefore + "," + CurrentAT.timerOffsetAfter;
			else
				reqs += "&offset=";
		}
		else
			reqs += "&offset=";

		if(CurrentAT.timeSpan)
			reqs += "&timespanFrom=" + CurrentAT.from + "&timespanTo=" + CurrentAT.to;
		else
			reqs += "&timespanFrom=&timespanTo=";

		if(CurrentAT.timeFrame)
			reqs += "&before=" + toUnixDate(CurrentAT.before) + "&after=" + toUnixDate(CurrentAT.after);
		else
			reqs += "&before=&after=";

		if(CurrentAT.Tags && CurrentAT.Tags.length > 0) {
			$.each( CurrentAT.Tags, function( index, value ){
				reqs += "&tag=" + value;
			});
		} else
			reqs += "&tag=";

		reqs += "&services=";
		if(CurrentAT.Channels && CurrentAT.Channels.length > 0) {
			var _s = [];
			$.each( CurrentAT.Channels, function( index, value ){
				_s.push(encodeURIComponent(value));
			});
			reqs += _s.join(',');
		}

		reqs += "&bouquets=";
		if(CurrentAT.Bouquets && CurrentAT.Bouquets.length > 0) {
			reqs += CurrentAT.Bouquets.join(',');
		}

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
				reqs += fr;
			});
		}

		reqs += "&autoadjust=";
		reqs += (CurrentAT.autoadjust) ? "1" : "0";
		reqs += "&allow_duplicate=";
		reqs += (CurrentAT.allow_duplicate) ? "1" : "0";
		reqs += "&avoidDuplicateMovies=";
		reqs += (CurrentAT.avoidDuplicateMovies) ? "1" : "0";
		
		if(!CurrentAT.vps)
			CurrentAT.vpo=false;

		reqs += "&vps_enabled=";
		reqs += (CurrentAT.vps) ? "1" : "0";
		reqs += "&vps_overwrite=";
		reqs += (CurrentAT.vpso) ? "1" : "0";
		reqs += "&series_labeling=";
		reqs += (CurrentAT.series_labeling) ? "1" : "0";
		var _ae = CurrentAT.afterevent;
		if (_ae == "") {
			_ae = "default";
		} else if (_ae == "none") {
			_ae = "nothing";
		} else if (_ae == "shutdown") {
			_ae = "deepstandby";
		}
		reqs += "&afterevent=" + _ae;
		if (_ae !== "default") {
			reqs += "&aftereventFrom=" + CurrentAT.aftereventfrom;
			reqs += "&aftereventTo=" + CurrentAT.aftereventto;
		}

		if(!CurrentAT.isNew) {
			reqs += "&id=" + CurrentAT.id;
		}

		$.ajax({
			type: "GET", url: reqs,
			dataType: "xml",
			success: function (xml)
			{
				var state=$(xml).find("e2state").first();
				var txt=$(xml).find("e2statetext").first();
				showError(txt.text(),state.text());
				readAT($('#atlist').val());
			},
			error: function (request, status, error) {
				showError(request.responseText);
			}
		});
		$('#filterlist').empty();
	}
}

function checkValues () {
	if ($('#timeSpan').is(':checked') === true)
		$('#timeSpanE').show();
	else
		$('#timeSpanE').hide();
	if ($('#timeSpanAE').is(':checked') === true)
		$('#timeSpanAEE').show();
	else
		$('#timeSpanAEE').hide();
	if ($('#timeFrame').is(':checked') === true) {
		$('#timeFrameE').show();
		$('#timeFrameAfterCheckBox').show();
	}
	else {
		$('#timeFrameE').hide();
		$('#timeFrameAfterCheckBox').hide();
	}
	if ($('#timerOffset').is(':checked') === true)
		$('#timerOffsetE').show();
	else
		$('#timerOffsetE').hide();
	if ($('#maxDuration').is(':checked') === true)
		$('#maxDurationE').show();
	else
		$('#maxDurationE').hide();
	if ($('#Location').is(':checked') === true)
		$('#LocationE').show();
	else
		$('#LocationE').hide();
	if ($('#Bouquets').is(':checked') === true)
		$('#BouquetsE').show();
	else
		$('#BouquetsE').hide();
	if ($('#Channels').is(':checked') === true)
		$('#ChannelsE').show();
	else
		$('#ChannelsE').hide();

	if ($('#Tags').is(':checked') === true) {
		$('#TagsE').show();
	}
	else {
		$('#TagsE').hide();
	}

	if ($('#Filter').is(':checked') === true) {
		$('.FilterE').show();
	}
	else {
		$('.FilterE').hide();
	}
	if ($('#afterevent').val() != "")
		$('#AftereventE').show();
	else
		$('#AftereventE').hide();
	if ($('#counter').val() != "0")
		$('#CounterE').show();
	else
		$('#CounterE').hide();
	if ($('#vps').is(':checked') === true)
		$('#vpsE').show();
	else
		$('#vpsE').hide();
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
				var s = $(this).find('e2timebegin').text();
				var d = new Date(Math.round(s) * 1000);
				var h = d.getHours();
				var m = d.getMinutes();
				var _h = ((h>9) ? '':'0') + h.toString();
				var _m = ((m>9) ? '':'0') + m.toString();
				s = (d.getMonth()+1) + '/' + d.getDate() + '/' + d.getFullYear() + ' ' + _h + ':' + _m;
				line += '<td>' + s + '</td>';
				s = $(this).find('e2timeend').text();
				d = new Date(Math.round(s) * 1000);
				h = d.getHours();
				m = d.getMinutes();
				var _h = ((h>9) ? '':'0') + h.toString();
				var _m = ((m>9) ? '':'0') + m.toString();
				s = (d.getMonth()+1) + '/' + d.getDate() + '/' + d.getFullYear() + ' ' + _h + ':' + _m;
				line += '<td>' + s + '</td>';
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


function InitPage() {

	$('#timeSpan').click(function() { checkValues();});
	$('#timeSpanAE').click(function() { checkValues();});
	$('#timeFrame').click(function() { checkValues();});
	$('#timeFrameAfter').click(function() { timeFrameAfterCheck();});
	$('#timerOffset').click(function() { checkValues();});
	$('#maxDuration').click(function() { checkValues();});
	$('#Location').click(function() { checkValues();});
	$('#Bouquets').click(function() { checkValues();});
	$('#Channels').click(function() { checkValues();});
	$('#Filter').click(function() { checkValues();});
	$('#Tags').click(function() { checkValues();});
	$("#AddFilter").click(function(){AddFilter("","","");});
	$('#afterevent').change(function () {checkValues();});
	$('#counter').change(function () {checkValues();});
	$('#vps').change(function () {checkValues();});
	initValues ();
	checkValues();
	getData();

	$( ".FM" ).change(function() {
	
		var nf = $(this).parent().parent();
		if($(this).val()=="dayofweek") {
			nf.find(".FS").show();
			nf.find(".FI").hide();
		}
		else
		{
			nf.find(".FS").hide();
			nf.find(".FI").show();
		}
	});
}

function delAT()
{
	if(CurrentAT && !CurrentAT.isNew)
	{
		swal({
			title: tstr_del_autotimer + " ?",
			text: CurrentAT.name,
			type: "warning",
			showCancelButton: true,
			confirmButtonColor: "#DD6B55",
			confirmButtonText: tstrings_yes_delete + ' !',
			cancelButtonText: tstrings_no_cancel + ' !',
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
	var _id=1;
	$(atxml).find("timer").each(function () {
		var li = parseInt($(this).attr("id"));
		if(li>=_id)
			_id=li+1;
	});
	var name = tstr_timernewname;
	var id = _id.toString();
	var xml = '<timers><timer name="'+name+'" match="'+name+'" enabled="yes" id="'+id+'" justplay="0" overrideAlternatives="1"></timer></timers>';
	if (typeof evt !== 'undefined') 
	{
		xml = '<timers><timer name="'+evt.name+'" match="'+evt.name+'" enabled="yes" id="'+id+'" from="'+evt.from+'" to="'+evt.to+'"';
		xml += ' searchType="exact" searchCase="sensitive" justplay="0" overrideAlternatives="1" ';
		xml += '><e2service><e2servicereference>'+evt.sref+'</e2servicereference><e2servicename>'+evt.sname+'</e2servicename></e2service>';
		xml += '</timer></timers>';
	}
	var xmlDoc = $.parseXML( xml );
	
	$(xmlDoc).find("timer").each(function () {
		$( "#atlist" ).append($("<option data-id='" + $(this).attr("id") + "' value='" + $(this).attr("id") + "' selected >" + $(this).attr("name") + "</option>"));
		$('#atlist').selectpicker('refresh');
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
	
	var state=$(atxml).find("e2state").first();
	if (state.text() == 'false') {
		showError($(atxml).find("e2statetext").first().text());
	}

	$(atxml).find("timer").each(function () {
		atlist.push($(this));
	});

	atlist.sort(function(a, b){
		var a1= a.attr("name"), b1=b.attr("name");
		if(a1==b1) return 0;
		return a1> b1? 1: -1;
	});
	
	var selectoptions = "";
	var i = 0;
	$(atlist).each(function () {
		var selected = ''
		if ( ( i === 0 && keepSelection === -1) || ( keepSelection.toString() === $(this).attr("id").toString() ) ) {
			selected = 'selected'
		}
		selectoptions += "<option data-id='" + $(this).attr("id") + "' value='" + $(this).attr("id") + "' " + selected + " >" + $(this).attr("name") + "</option>"
		i++;
	});
	$("#atlist").html(selectoptions);
	$("#atlist").selectpicker('refresh');

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
		}
	}
	if(atlist.length>0) {
		$("#atbutton5").show();
		$("#atbutton6").show();
	} else {
		$("#atbutton5").hide();
		$("#atbutton6").hide();
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
