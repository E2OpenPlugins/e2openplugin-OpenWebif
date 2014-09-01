//******************************************************************************
//* epgr.js: openwebif EPGRefresh plugin
//* Version 1.0
//******************************************************************************
//* Copyright (C) 2014 Joerg Bleyel
//* Copyright (C) 2014 E2OpenPlugins
//*
//* V 1.0 - Initial Version
//*
//* Authors: Joerg Bleyel <jbleyel # gmx.net>
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************

var epgxml;
var binterval_in_seconds=true;
var er_hasAutoTimer = false;
var er_bqchchanged = false;

function toUnixDate(date){
	var datea = date.split('.');
	var d = new Date();
	d.setFullYear(datea[2],datea[1]-1,datea[0]);
	d.setHours( 0 );
	d.setMinutes( 0 );
	d.setSeconds( 0 );
	return Math.floor(d.getTime() / 1000);
}
function isInArray(array, search) { return (array.indexOf(search) >= 0) ? true : false; }
function addZero(i) { if (i < 10) { i = "0" + i; } return i; }
function isBQ(sref) {return ((sref.indexOf("FROM BOUQUET") > -1) && (sref.indexOf("1:134:1") != 0));}
function isAlter(sref) {return (sref.indexOf("1:134:1") == 0);}

function saveEPGR()
{
	var reqs = "/epgrefresh/set?&enabled=";
	reqs += $('#er_enabled').is(':checked') ? "true":"";
	reqs += "&enablemessage=";
	reqs += $('#er_enablemessage').is(':checked') ? "true":"";
	if($('#er_ebegin').is(':checked'))
		reqs += "&begin=" + toUnixDate($('#er_begin').val());
	if($('#er_eend').is(':checked'))
		reqs += "&end=" + toUnixDate($('#er_end').val());
	reqs += "&delay_standby=" + $('#er_delay_standby').val();
	reqs += "&afterevent=";
	reqs += $('#er_afterevent').is(':checked') ? "true":"";
	reqs += "&force=";
	reqs += $('#er_force').is(':checked') ? "true":"";
	reqs += "&wakeup=";
	reqs += $('#er_wakeup').is(':checked') ? "true":"";
	reqs += "&adapter=" + $('#er_adapter').val();

	if(er_hasAutoTimer) {
		reqs += "&inherit_autotimer=";
		reqs += $('#er_inherit_autotimer').is(':checked') ? "true":"";
		reqs += "&parse_autotimer=" + $('#er_parse_autotimer').val();
	}
	
	if(binterval_in_seconds)
		reqs += "&interval_seconds=" + $('#er_interval').val();
	else
		reqs += "&interval=" + $('#er_interval').val();
	
	$.ajax({
		type: "GET", url: reqs,
		dataType: "xml",
		success: function (xml)
		{
			var state=$(xml).find("e2state").first();
			var txt=$(xml).find("e2statetext").first();
			showError(txt.text(),state.text());
			if(state)
				SaveCHBQ();
		},
		error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}

function SaveCHBQ()
{
	if(er_bqchchanged === false)
		return;
	
	var reqs = "";
	var Bouquets = $("#bouquets").chosen().val();
	var Channels = $("#channels").chosen().val();

	if(Channels && Channels.length > 0) {
		$.each( Channels, function( index, value ){
			if(isAlter(value)) {
				reqs += "&sref=" + value;
			}
			else {
				reqs += "&sref=" + encodeURIComponent(value);
			}
		});
	}

	if(Bouquets && Bouquets.length > 0) {
		$.each( Bouquets, function( index, value ){
			reqs += "&sref=" + value;
		});
	}

	var reqss = "/epgrefresh/add?multi=1";
	
	if (reqs!="")
		reqss+= reqs;
	else
		return;

	$.ajax({
		type: "GET", url: reqss,
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

function readEPGR2(chbq)
{
	var begin;
	var end;
	er_hasAutoTimer = false;

	$.ajax({
		type: "GET", url: "/epgrefresh/get",
		dataType: "xml",
		success: function (xml)
		{
			var settings = [];
			$(xml).find("e2setting").each(function () {
				var name = $(this).find("e2settingname").text();
				var val = $(this).find("e2settingvalue").text();
				if(name.indexOf("config.plugins.epgrefresh.") === 0)
				{
					name = name.substring(26);
					if(val === "True")
						$('#er_'+name).prop('checked',true);
					else if(val === "False")
						$('#er_'+name).prop('checked',false);
					else if(name === "begin")
						begin = val;
					else if(name === "end")
						end = val;
					else if(name == "interval_seconds") {
						binterval_in_seconds = true;
						$("#er_interval").val(val);
					}
					else if(name == "interval") {
						binterval_in_seconds = false;
						$("#er_interval").val(val);
					}
					else
						$('#er_'+name).val(val);
				}
				else {
					if(name === "hasAutoTimer" && val === "True")
						er_hasAutoTimer = true;
				}
			});
			
			UpdateCHBQ(chbq,begin,end);
			
		},error: function (request, status, error) {
			showError(request.responseText);
		}
	});
}

function UpdateCHBQ(chbq,begin,end)
{
	var _i=parseInt(begin);
	var _date = new Date(_i*1000);
	var h = addZero(_date.getHours());
	var m = addZero(_date.getMinutes());
	
	$("#er_begin").val(h+":"+m);
	
	_i=parseInt(end);
	_date = new Date(_i*1000);
	h = addZero(_date.getHours());
	m = addZero(_date.getMinutes());
	$("#er_end").val(h+":"+m);

	var _c = [];
	var _b = [];
	
	$(chbq).find("e2service").each(function () {
		var ref = $(this).find("e2servicereference").text();
		if (isBQ(ref)) {
			_b.push(encodeURIComponent(ref));
		}
		else if (isAlter(ref)) {
			_c.push(encodeURIComponent(ref));
		}
		else {
			_c.push(ref);
		}
	});
	
	var Channels = _c.slice();
	var Bouquets = _b.slice();
	
	$('#channels').val(null);
	$('#bouquets').val(null);
	$.each(Bouquets, function(index, value) {
		$('#bouquets option[value="' + value + '"]').prop("selected", true);
	});
	$.each(Channels, function(index, value) {
		$('#channels option[value="' + value + '"]').prop("selected", true);
	});
	$('#bouquets').trigger("chosen:updated");
	$('#channels').trigger("chosen:updated");

	er_bqchchanged = false;
	
	if(binterval_in_seconds) {
		$('#lbls').show();
		$('#lblm').hide();
	}
	else
	{
		$('#lblm').show();
		$('#lbls').hide();
	}
	
	if(er_hasAutoTimer) {
		$('#er_hasAT').show();
	} else {
		$('#er_hasAT').hide();
	}
}

function readEPGR()
{
	$.ajax({
		type: "GET", url: "/epgrefresh",
		dataType: "xml",
		success: function (xml)
		{
			readEPGR2(xml);
		},error: function (request, status, error) {
			showError(request.responseText);
			// TODO : error handling
		}
	});
}

function reloadEPGR()
{
	showError("");
	readEPGR();
}

function getAllServices()
{
	// TODO: Errorhandling
	$.getJSON( "/api/getallservices", function( data ) {
		var bqs = data['services'];
		var options = "";
		var boptions = "";
		var refs = [];
		$.each( bqs, function( key, val ) {
			var ref = val['servicereference']
			var name = val['servicename'];
			boptions += "<option value='" + encodeURIComponent(ref) + "'>" + val['servicename'] + "</option>";
			var slist = val['subservices'];
			var items = [];
			$.each( slist, function( key, val ) {
				var ref = val['servicereference']
				if (!isInArray(refs,ref)) {
					refs.push(ref);
					if(ref.substring(0, 4) == "1:0:")
						items.push( "<option value='" + ref + "'>" + val['servicename'] + "</option>" );
					if(ref.substring(0, 7) == "1:134:1")
						items.push( "<option value='" + encodeURIComponent(ref) + "'>" + val['servicename'] + "</option>" );
				}
			});
			if (items.length>0) {
				options += "<optgroup label='" + name + "'>" + items.join("") + "</optgroup>";
			}
		});
		$("#channels").append( options);
		$('#channels').trigger("chosen:updated");
		$("#bouquets").append( boptions);
		$('#bouquets').trigger("chosen:updated");
		reloadEPGR();
	});
}

function initValues () {
	$('#er_begin').val('22:30');
	$('#er_end').val('6:30');
	$('#er_begin').timepicker();
	$('#er_end').timepicker();
	$("#bouquets").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#bouquets").chosen().change( function() {$("#bouquets").val($(this).val());er_bqchchanged = true;});
	$("#channels").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#channels").chosen().change( function() {$("#channels").val($(this).val());er_bqchchanged = true;});
}

function InitPage() {
	initValues ();
	getAllServices();
	$("#actions").buttonset();
	$("#epgrbutton0").click(function () { reloadEPGR(); });
	$("#epgrbutton0").button({icons: { primary: "ui-icon-arrowrefresh-1-w"}});
	$("#epgrbutton1").click(function () { saveEPGR(); });
	$("#epgrbutton1").button({icons: { primary: "ui-icon-disk"}});
	$("#epgrbutton2").click(function () { DoRefresh(); });
	// TODO: icons
	$('#errorbox').hide();
}


function DoRefresh()
{
	$.ajax({
		type: "GET", url: "/epgrefresh/refresh",
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
	$('#success').text("");
	$('#error').text("");
	if(st === "True")
		$('#success').text(txt);
	else
		$('#error').text(txt);
	if(txt!=="")
		$('#errorbox').show();
	else
		$('#errorbox').hide();
}

