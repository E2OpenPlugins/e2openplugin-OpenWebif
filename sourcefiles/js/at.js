//******************************************************************************
//* at.js: openwebif Autotimer plugin
//* Version 2.11
//******************************************************************************
//* Copyright (C) 2014-2021 Joerg Bleyel
//* Copyright (C) 2014-2021 E2OpenPlugins
//*
//* V 1.0 - Initial Version
//* V 1.1 - Support translation, small ui fixes
//* V 1.2 - Optimize bouquets/channels selector
//* V 1.3 - Allow alternatives as channel, small js fixes
//* V 1.4 - fix timespan, offset, support series plugin
//* V 1.5 - autotimer settings
//* V 1.6 - sort autotimer list
//* V 1.7 - fix autotimer filter
//* V 1.8 - use textfield for offset
//* V 1.9 - error handling
//* V 2.0 - theme support
//* V 2.1 - update status label
//* V 2.2 - use public getallservices
//* V 2.3 - fix afterevent
//* V 2.4 - fix simulate
//* V 2.5 - add test api / fix counter
//* V 2.6 - add rec+zap timer support
//* V 2.7 - backup / restore
//* V 2.8 - fix #960
//* V 2.9 - fix #1028
//* V 2.10 - iptv, lastscanned filter
//* V 2.11 - improve getallservices
//*
//* Authors: Joerg Bleyel <jbleyel # gmx.net>
//* 		 plnick
//*			 rdamas
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************

// TODO: some error handler

function toUnixDate(date){
	var datea = date.split('.');
	var d = new Date();
	d.setFullYear(datea[2],datea[1]-1,datea[0]);
	d.setHours( 0 );
	d.setMinutes( 0 );
	d.setSeconds( 0 );
	return Math.floor(d.getTime() / 1000);
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
	var _dateb = new Date();
	var _db = $.datepicker.formatDate('dd.mm.yy', _dateb);
	$('#after').val(_db);
	var _datea = new Date();
	_datea.setDate(_dateb.getDate()+7);
	_db = $.datepicker.formatDate('dd.mm.yy', _datea);
	$('#before').val(_db);
	$('#from').val('20:15');
	$('#to').val('23:15');
	$('#aefrom').val('20:15');
	$('#aeto').val('23:15');
	$('#after').datepicker({
		closeText: tstr_done,
		monthNames: [tstr_january, tstr_february, tstr_march, tstr_april, tstr_may, tstr_june, tstr_july, tstr_august, tstr_september, tstr_october, tstr_november, tstr_december],
		dayNames: [tstr_sunday, tstr_monday, tstr_tuesday, tstr_wednesday, tstr_thursday, tstr_friday, tstr_saturday, tstr_sunday],
		dayNamesMin: [tstr_su, tstr_mo, tstr_tu, tstr_we, tstr_th, tstr_fr, tstr_sa, tstr_su],
		dateFormat: 'dd.mm.yy',
		onClose: function(dateText, inst) {
			if ($('#after').val() != '' && $(this).datepicker('getDate') < $('#before').datepicker('getDate')) {
				showError(tstr_start_after_end);
			} else
				showError('');
		}
	});
	$('#before').datepicker({
		closeText: tstr_done,
		monthNames: [tstr_january, tstr_february, tstr_march, tstr_april, tstr_may, tstr_june, tstr_july, tstr_august, tstr_september, tstr_october, tstr_november, tstr_december],
		dayNames: [tstr_sunday, tstr_monday, tstr_tuesday, tstr_wednesday, tstr_thursday, tstr_friday, tstr_saturday, tstr_sunday],
		dayNamesMin: [tstr_su, tstr_mo, tstr_tu, tstr_we, tstr_th, tstr_fr, tstr_sa, tstr_su],
		dateFormat: 'dd.mm.yy',
		onClose: function(dateText, inst) {
			if ($('#before').val() != '' && $(this).datepicker('getDate') > $('#after').datepicker('getDate')) {
				showError(tstr_start_after_end);
			}
			else
				showError('');
		}
	});
	$('.date').each(function(index,element){
		$('<span style="display: inline-block">').addClass('ui-icon ui-icon-calendar').insertAfter(element).position({
			of: element,
			my: 'right top',
			at: 'right top+2'
		});
	});
	$('.time').each(function(index,element){
		$('<span style="display: inline-block">').addClass('ui-icon ui-icon-clock').insertAfter(element).position({
			of: element,
			my: 'right top',
			at: 'right top+2'
		});
	});
	$("#bouquets").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#bouquets").chosen().change( function() {$("#bouquets").val($(this).val());});
	$("#channels").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#channels").chosen().change( function() {$("#channels").val($(this).val());});
	$("#tags").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#tags").chosen().change( function() {$("#tags").val($(this).val());});
	
	$(".chosen-container .chosen-drop").addClass('ui-widget-content');
	if (theme == 'eggplant' || theme == 'vader')
	{
		$(".chosen-container .chosen-drop").css('background-image','none');
	}
	
}

function AddFilter(a,b,c)
{
	var rc = $('#filterlist tr').length;
	var nf = $("#dummyfilter").clone(true);
	nf.show();
	nf.attr({
	'id': 'f' + rc.toString(),
	'name': 'f' + rc.toString()
	});
	
	if(a!="")
		nf.find(".FT").val(a);
	if(b!="") {
		if(b=="dayofweek") {
			nf.find(".FM").val(b);
			nf.find(".FI").hide();
			nf.find(".FS").show().val(c);
		}
		else {
			nf.find(".FM").val(b);
			nf.find(".FS").hide();
			nf.find(".FI").show().val(c);
		}
	}
	nf.appendTo("#filterlist");
}

function timeFrameAfterCheck() {

	if ($('#timeFrameAfter').is(':checked') === true) {
		var _da = $('#after').datepicker('getDate');
		var _datea = new Date(_da);
		var _dateb = new Date();
		_dateb.setDate(_datea.getDate()+7);
		_da = $.datepicker.formatDate('dd.mm.yy', _dateb);
		$('#before').val(_da);
		$('#beforeE').show();
	}
	else {
		var _datea = new Date(2038,0,1);
		var _da = $.datepicker.formatDate('dd.mm.yy', _datea);
		$('#before').val(_da);
		$('#beforeE').hide();
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
	if ($('#timeFrame').is(':checked') === true)
		$('#timeFrameE').show();
	else
		$('#timeFrameE').hide();
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
	if ($('#Filter').is(':checked') === true)
		$('#FilterE').show();
	else
		$('#FilterE').hide();
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

var ATnoiptv = false;

function InitPage(noiptv) {

	ATnoiptv = noiptv;
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
	$("#AddFilter").click(function(){AddFilter("","","");});
	$('#afterevent').change(function () {checkValues();});
	$('#counter').change(function () {checkValues();});
	$('#vps').change(function () {checkValues();});
	initValues ();
	checkValues();
	getData();
	$("#actions").buttonset();
	$("#atbutton0").click(function () { addAT(); });
	$("#atbutton0" ).button({icons: { primary: "ui-icon-plus"}});
	$("#atbutton1").click(function () { delAT(); });
	$("#atbutton1" ).button({icons: { primary: "ui-icon-minus"}});
	$("#atbutton2").click(function () { reloadAT(); });
	$("#atbutton2").button({icons: { primary: "ui-icon-arrowrefresh-1-w"}});
	$("#atbutton3").click(function () { saveAT(); });
	$("#atbutton3").button({icons: { primary: "ui-icon-disk"}});
	$("#atbutton4").click(function () { parseAT(); });
	$("#atbutton5").click(function () { test_simulateAT(true); });
	$("#atbutton6").click(function () { test_simulateAT(false); });
	$("#atbutton7").click(function () { listTimers(); });
	$("#atbutton8").click(function () { getAutoTimerSettings(); });
	// TODO: icons

	$("#atbutton9").click(function () { exportAT(); });
	$("#atbutton10").click(function () { importAT(); });

	$('#statuscont').hide();
	$("#simdlg").dialog({
		modal : true, 
		overlay: { backgroundColor: "#000", opacity: 0.5 }, 
		autoOpen: false,
		title: tstr_timerpreview,
		width: 600,
		height: 400
	});
	$("#timerdlg").dialog({
		modal : true, 
		overlay: { backgroundColor: "#000", opacity: 0.5 }, 
		autoOpen: false,
		title: tstr_timerlist,
		width: 600,
		height: 400
	});
	
	
	var buttons = {};
	buttons["Save"] = function() {setAutoTimerSettings(); $(this).dialog("close");};
	buttons["Cancel"] = function() {$(this).dialog("close");};
	
	var t = $("#atbutton8").data('title');
	
	$("#atsettingdlg").dialog({
		modal : true, 
		overlay: { backgroundColor: "#000", opacity: 0.5 }, 
		autoOpen: false,
		title: t,
		width: 600,
		height: 400,
		buttons: buttons
	});
	
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
	
	$("#rfile").change(function() {
		prepareRestore($(this));
	});

}

var atxml;
var CurrentAT = null;

function isBQ(sref)
{
	return ((sref.indexOf("FROM BOUQUET") > -1) && (sref.indexOf("1:134:1") != 0));
}

// parse and create AT List
function Parse() {
	$("#atlist").empty();
	
	var atlist = [];
	
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
	
	$(atlist).each(function () {
		$("#atlist").append($("<li></li>").html($(this).attr("name")).data('id',$(this).attr("id")));
	});
	
	if(at2add)
	{
		addAT(at2add);
		at2add=null;
	}
	else
	{
		var item = $("#atlist").find("li").first();
		if(item) {
			FillAT(item.data('id'));
			item.addClass('ui-selected');
			item.addClass(getActiveCls());
		}
		setHover('#atlist li');
	}
	if(atlist.length>0) {
		$("#atbutton5").show();
		$("#atbutton6").show();
	} else {
		$("#atbutton5").hide();
		$("#atbutton6").hide();
	}
}

function getTags()
{
	// TODO: Errorhandling
	$.getJSON( "/api/gettags", function( data ) {
		var bqs = data['tags'];
		var options = "";
		$.each( bqs, function( key, val ) {
			options += "<option value='" + encodeURIComponent(val) + "'>" + val + "</option>";
		});
		$("#tags").append( options);
		$('#tags').trigger("chosen:updated");
	});
}


function ATGetAllServices(callback,radio)
{
	if (typeof callback === 'undefined')
		return;
	if (typeof radio === 'undefined')
		radio = false;
	
	ru = "";
	if (radio)
	{
		v += "r";
		vd += "r";
		ru = "&type=radio";
	}

	niptv = "";
	if(ATnoiptv)
	{
		ru = "&noiptv=1";
	}
	
	$.ajax({
		url: '/api/getallservices?nolastscanned=1'+ ru + niptv,
		dataType: "json",
		success: function ( data ) {
			var sdata = JSON.stringify(data);
			var bqs = data['services'];
			FillAllServices(bqs,callback);
		}
	});
}

function getAllServices()
{
	ATGetAllServices(function ( options , boptions) {
		$("#channels").append( options);
		$('#channels').trigger("chosen:updated");
		$("#bouquets").append( boptions);
		$('#bouquets').trigger("chosen:updated");
		reloadAT();
	});
}

function getData()
{
	getTags();
	getAllServices();
}

function FillAT(autotimerid)
{
	var def = $(atxml).find("defaults");
	$(atxml).find("timer").each(function () {
		if($(this).attr("id")==autotimerid) {
			CurrentAT = new AutoTimerObj($(this));
			CurrentAT.UpdateUI();
		}
	});
	checkValues ();
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
		var _i=parseInt(xml.attr("after"));
		var _date = new Date(_i*1000);
		var _dt = $.datepicker.formatDate('dd.mm.yy', _date);
		this.after = _dt;

		_i=parseInt(xml.attr("before"));
		_date = new Date(_i*1000);
		_dt = $.datepicker.formatDate('dd.mm.yy', _date);
		this.before = _dt;
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
		this.avoidDuplicateDescription=xml.attr("avoidDuplicateDescription");

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
}

AutoTimerObj.prototype.UpdateUI = function(){
	$('#enabled').prop('checked', this.enabled); 
	$('#name').val(this.name);
	$('#match').val(this.match);
	$('#searchType').val(this.searchType);
	$('#searchCase').val(this.searchCase);
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
		var _dateb= $('#before').datepicker('getDate');
		var _maxd=new Date(2038,0,1);
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
	
	if(this.location) {
		$('#location').val(this.location);
		if(this.location !== $('#location').val()) {
			current_location = "<option value='" + this.location + "'>" + this.location + "</option>";
			$('#location').append(current_location);
			$('#location').val(this.location);
		}
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
	$('#channels').val(null);
	$('#bouquets').val(null);
	$.each(this.Bouquets, function(index, value) {
		$('#bouquets option[value="' + value + '"]').prop("selected", true);
	});
	$.each(this.Channels, function(index, value) {
		$('#channels option[value="' + value + '"]').prop("selected", true);
	});
	$('#Bouquets').prop('checked',(this.Bouquets.length>0));
	$('#Channels').prop('checked',(this.Channels.length>0));
	$('#tags').val(null);
	$.each(this.Tags, function(index, value) {
		$('#tags option[value="' + value + '"]').prop("selected", true);
	});
	$('#bouquets').trigger("chosen:updated");
	$('#channels').trigger("chosen:updated");
	$('#tags').trigger("chosen:updated");
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
	$('#Filter').prop('checked',(c>0));
	$('#counter').val(this.counter);
	$('#left').val(this.left);
	$('#counterFormat').val(this.counterFormat);
	$('#vps').prop('checked',this.vps);
	$('#vpssm').prop('checked',!this.vpso);
	$('#series_labeling').prop('checked',this.series_labeling);
	checkValues();
};

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
		$( "#atlist" ).append($('<li></li>').html($(this).attr("name")).data('id',$(this).attr("id")));
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

function delAT()
{
	if(CurrentAT && !CurrentAT.isNew)
	{
		if(confirm(tstr_del_autotimer + " (" + CurrentAT.name + ") ?") === false)
			return;
		$.ajax({
			type: "GET", url: "/autotimer/remove?id=" + CurrentAT.id,
			dataType: "xml",
			success: function (xml)
			{
				var state=$(xml).find("e2state").first();
				var txt=$(xml).find("e2statetext").first();
				showError(txt.text(),state);
				readAT();
			},
			error: function (request, status, error) {
				showError(request.responseText);
			}
		});
		
	}
}

function readAT()
{
	CurrentAT = null;
	$.ajax({
		type: "GET", url: "/autotimer",
		dataType: "xml",
		success: function (xml)
		{
			atxml=xml;
			Parse();
		},error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}

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
		CurrentAT.Bouquets = $("#bouquets").chosen().val();
		CurrentAT.Channels = $("#channels").chosen().val();
		var _f = [];
		$.each($('#filterlist tr'), function(index, value) {
			var tr = $(value);
			if(tr.prop('id') !== "dummyfilter") {
				var FT = tr.find(".FT");
				var FM = tr.find(".FM");
				var FI = tr.find(".FI");
				var FS = tr.find(".FS");
				var FR = tr.find(".FR");
				if (FR.is(':checked') === false){
					if (FM.val() === 'dayofweek'){
						_f.push (
								{ 	"t" : FT.val(),
									"w": FM.val(),
									"v": FS.val()
								}
							); 
					}
					else {
						_f.push (
								{ 	"t" : FT.val(),
									"w": FM.val(),
									"v": FI.val()
								}
							); 

					}
				} else {
					_f.push (
								{ 	"t" :FT.val(),
									"w": FM.val(),
									"v": ""
								}
							); 
				}
			}
		});
		CurrentAT.Filters = _f.slice();
		CurrentAT.Tags = $("#tags").chosen().val();
		CurrentAT.counter = $('#counter').val();
		CurrentAT.left = $('#left').val();
		CurrentAT.counterFormat = $('#counterFormat').val();
		CurrentAT.vps = $('#vps').is(':checked');
		CurrentAT.vpso = !$('#vpssm').is(':checked');
		CurrentAT.series_labeling = $('#series_labeling').is(':checked');
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
		else
			reqs += "&counter=0";
		
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
				readAT();
			},
			error: function (request, status, error) {
				showError(request.responseText);
			}
		});
	}
}

function test_simulateAT(simulate)
{

	$("#simdlg").dialog( "open" );
	$("#simtb").append("<tr><td COLSPAN=6>"+loadspinner+"</td></tr>");

	var link = simulate ? "simulate":"test";
	var tag = simulate ? "e2simulatedtimer":"e2testtimer";
	
	$.ajax({
		type: "GET", url: "/autotimer/" +link,
		dataType: "xml",
		success: function (xml)
		{
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

function parseAT()
{
	$.ajax({
		type: "GET", url: "/autotimer/parse",
		dataType: "xml",
		success: function (xml)
		{
			var state=$(xml).find("e2state").first();
			var txt=$(xml).find("e2statetext").first();
			showError(txt.text(),state.text());
		},
		error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}

function reloadAT()
{
	showError("");
	readAT();
	$( "#atlist" ).selectable({
		selected: function( event, ui ) {
			var ids = $('#atlist .ui-selected').map(function() {
				FillAT($(this).data('id'));
			});
		},
		classes: {
			"ui-selected": getActiveCls()
		}
	});
}

function listTimers()
{
	$("#timerdlg").dialog( "open" );
	$("#timerdlgcont").html(loadspinner).load('ajax/timers #timers', function() {
		$("#timerdlgcont #timers .moviecontainer_main .moviecontainer_right div a:first").hide();
	});
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
			$("#atsettingdlg").dialog( "open" );
		},error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}


function setAutoTimerSettings()
{
	var reqs = "/autotimer/set?&autopoll=";
	reqs += $('#ats_autopoll').is(':checked') ? "true":"";
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
	reqs += "&add_name_to_tags=" + v;
	reqs += "&refresh=" + $('#ats_refresh').val();
	reqs += "&editor=" + $('#ats_editor').val();
	
	$.ajax({
		type: "GET", url: reqs,
		dataType: "xml",
		success: function (xml)
		{
			var state=$(xml).find("e2state").first();
			var txt=$(xml).find("e2statetext").first();
			showError(txt.text(),state.text());
		},
		error: function (request, status, error) {
			showError(request.responseText);
		}
	});
	
}

function showError(txt,st)
{
	st = typeof st !== 'undefined' ? st : "False";
	
	if (st === true || st === 'True' || st === 'true') {
		$('#statusbox').removeClass('ui-state-error').addClass('ui-state-highlight');
		$('#statusicon').removeClass('ui-icon-alert').addClass('ui-icon-info');
	} else {
		$('#statusbox').removeClass('ui-state-highlight').addClass('ui-state-error');
		$('#statusicon').removeClass('ui-icon-info').addClass('ui-icon-alert');
	}
	$('#statustext').text(txt);
	
	if (txt !== '') {
		$('#statuscont').show();
	} else {
		$('#statuscont').hide();
	}
	
}

function importAT () {
	$("#rfile").trigger('click');
}

function prepareRestore (ff) {
	var fn = ff.val();
	fn = fn.replace('C:\\fakepath\\','');
	if (confirm(tstr_bqe_restore_question + ' ( ' + fn + ') ?') === false) {
		return;
	}

	$('form#uploadrestore')
		.unbind('submit')
		.submit(function (_e) 
	{
		var formData = new FormData(this);
		$.ajax({
			url: '/autotimer/uploadfile',
			type: 'POST',
			data:  formData,
			mimeType:"multipart/form-data",
			contentType: false,
			cache: false,
			processData:false,
			dataType: 'json',
			success: function (data, textStatus, jqXHR) {
				var r = data.Result;
				if (r[0]) {
					doRestore(r[1]);
				} else {
					showError("Upload File: " + textStatus);
				}
			},
			error: function (jqXHR, textStatus, errorThrown) {
				showError("Upload File Error: " + errorThrown);
			}
		});
		_e.preventDefault();
		try {
			_e.unbind();
		} catch(ex){}
	});
	$('form#uploadrestore').submit();
}

function doRestore (fn) {
	if (fn) {
		$.ajax({
			url: '/autotimer/restore',
			dataType: 'xml',
			cache: false,
			success: function ( xml ) {
				var state=$(xml).find("e2state").first();
				var txt=$(xml).find("e2statetext").first();
				showError(txt.text(),state.text());
			}
		});
	}
}

function exportAT () {
	if (confirm('export AT ?') === false) {
		return;
	}
	$.ajax({
		url: '/autotimer/backup',
		dataType: 'xml',
		cache: false,
		data: { }, 
		success: function ( xml ) {
			var state=$(xml).find("e2state").first();
			if (state.text() == 'false') {
				showError($(xml).find("e2statetext").first().text());
			} else {
				var url = "/autotimer/tmp/autotimer_backup.tar";
				window.open(url,'Download');
			}
		}
	});
}

//# sourceURL=js/at.js
