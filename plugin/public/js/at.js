/* Autotimer plugin for openwebif v1.0 | (c) 2014 E2OpenPlugins | License GPL V2 , https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt */

// TODO: finish at list selector and fill form fields
// TODO: fix / add checks
// TODO: add save / delete
// TODO: add parse / preview
// TODO: add backup / restore

function initValues () {

	var _sel1 = $('#oafter');
	var _sel2 = $('#obefore');
	var _sel3 = $('#maxduration');
	var _sel4 = $('#counter');
	var _sel5 = $('#left');

	for (x=0;x<100;x++)
	{
		var sx=x.toString();
		if(x<10)
			sx='0'+sx;
		_sel1.append($('<option></option>').val(x).html(sx));
		_sel2.append($('<option></option>').val(x).html(sx));
		_sel4.append($('<option></option>').val(x).html(sx));
		_sel5.append($('<option></option>').val(x).html(sx));
	}

	for (x=0;x<1000;x++)
	{
		var sx=x.toString();
		if(x<10)
			sx='0'+sx;
		_sel3.append($('<option></option>').val(x).html(sx));
	}
	$('#oafter').val('5');
	$('#obefore').val('5');
	$('#maxduration').val('70');

	var _dateb = new Date();
	var _db = $.datepicker.formatDate('dd.mm.yy', _dateb);
	$('#before').val(_db);

	var _datea = new Date();
	_datea.setDate(_dateb.getDate()+7);
	var _da = $.datepicker.formatDate('dd.mm.yy', _datea);
	$('#after').val(_da);
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
				$('#error').text(tstr_start_after_end);
				$('#errorbox').show();
			} else
				$('#errorbox').hide();
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
				$('#error').text(tstr_start_after_end);
				$('#errorbox').show();
			}
			else
				$('#errorbox').hide();
		}
	});

	$('.date').each(function(index,element){
		$('<span style="display: inline-block">').addClass('ui-icon ui-icon-calendar').insertAfter(element).position({
			of: element
			,my: 'right top'
			,at: 'right top+2'
		});
	});

	$('.time').each(function(index,element){
		$('<span style="display: inline-block">').addClass('ui-icon ui-icon-clock').insertAfter(element).position({
			of: element
			,my: 'right top'
			,at: 'right top+2'
		});
	});

	$("#bouquets").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#bouquets").chosen().change( function() {$("#bouquets").val($(this).val());});
	$("#channels").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "80%"});
	$("#channels").chosen().change( function() {$("#channels").val($(this).val());});

// TODO : other time/date picker fields

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

function checkValues () {

	if ($('#timeSpan').is(':checked') == true)
		$('#timeSpanE').show();
	else
		$('#timeSpanE').hide();

	if ($('#timeSpanAE').is(':checked') == true)
		$('#timeSpanAEE').show();
	else
		$('#timeSpanAEE').hide();

	if ($('#timeFrame').is(':checked') == true)
		$('#timeFrameE').show();
	else
		$('#timeFrameE').hide();

	if ($('#timerOffset').is(':checked') == true)
		$('#timerOffsetE').show();
	else
		$('#timerOffsetE').hide();

	if ($('#maxDuration').is(':checked') == true)
		$('#maxDurationE').show();
	else
		$('#maxDurationE').hide();

	if ($('#Location').is(':checked') == true)
		$('#LocationE').show();
	else
		$('#LocationE').hide();

	if ($('#Bouquets').is(':checked') == true)
		$('#BouquetsE').show();
	else
		$('#BouquetsE').hide();

	if ($('#Channels').is(':checked') == true)
		$('#ChannelsE').show();
	else
		$('#ChannelsE').hide();

	if ($('#Filter').is(':checked') == true)
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

}

function InitPage() {

	$('#timeSpan').click(function() { checkValues();});
	$('#timeSpanAE').click(function() { checkValues();});
	$('#timeFrame').click(function() { checkValues();});
	$('#timerOffset').click(function() { checkValues();});
	$('#maxDuration').click(function() { checkValues();});
	$('#Location').click(function() { checkValues();});
	$('#Bouquets').click(function() { checkValues();});
	$('#Channels').click(function() { checkValues();});
	$('#Filter').click(function() { checkValues();});
	$("#AddFilter").click(function(){AddFilter("","","");});
	$('#afterevent').change(function () {checkValues();});
	$('#counter').change(function () {checkValues();});
	
	initValues ();
	checkValues();
	readAT();

	$( "#atlist" ).selectable({
		selected: function( event, ui ) {
			var ids = $('#atlist .ui-selected').map(function() {
				FillAT($(this).data('id'));
			});
		}
	});

	getData();

	$( "#actions" ).buttonset();
	$("#atbutton0").click(function () { addAT(); });
	$("#atbutton0" ).button({icons: { primary: "ui-icon-plus"}});
	$("#atbutton1").click(function () { delAT(); });
	$("#atbutton1" ).button({icons: { primary: "ui-icon-minus"}});
	$("#atbutton2").click(function () { reloadAT(); });
	$("#atbutton2").button({icons: { primary: "ui-icon-arrowrefresh-1-w"}});
	$("#atbutton3").click(function () { saveAT(); });
	$("#atbutton3").button({icons: { primary: "ui-icon-disk"}});
	$("#atbutton4").click(function () { parseAT(); });
	// TODO: parse icon
	//$("#atbutton4").button({icons: { primary: "ui-icon-disk"}});

	$('#errorbox').hide();
}

var atxml;
var BQs;
var CurrentAT = null;
var dencoding = null;

function isBQ(sref)
{
	return (sref.indexOf("FROM BOUQUET") > -1);
}

// parse and create AT List
function Parse() {
	
	$("#atlist").empty();
	$(atxml).find("timer").each(function () {
		$("#atlist").append($("<li></li>").html($(this).attr("name")).addClass('ui-widget-content').data('id',$(this).attr("id")));
	});
	
	var item = $("#atlist").find("li").first();
	if(item) {
		FillAT(item.data('id'));
		item.addClass('ui-selected');
	}
}


function getData()
{

$.getJSON( "/api/getservices", function( data ) {
  var bqs = data['services'];
  BQs = [];
	var options = "";
  $.each( bqs, function( key, val ) {
	var ref = val['servicereference']
	options += "<option value='" + escape(ref) + "'>" + val['servicename'] + "</option>";
	BQs.push(val);
  });
	$("#bouquets").append( options);
	$('#bouquets').trigger("chosen:updated");
	getAllServices();
});

}

function isInArray(array, search) { return (array.indexOf(search) >= 0) ? true : false; }

function getAllServices()
{
$.getJSON( "/api/getallservices", function( data ) {
	var bqs = data['services'];
	var options = "";
	var refs = [];
	$.each( bqs, function( key, val ) {
		var ref = val['servicereference']
		var name = '--';
		jQuery.map(BQs, function(obj) {
			if(obj.servicereference === ref)
				name = obj.servicename;
		});
	
		var slist = val['subservices'];
		var items = [];
		
		$.each( slist, function( key, val ) {
			var ref = val['servicereference']
			if (!isInArray(refs,ref)) {
				refs.push(ref);
				if(ref.substring(0, 4) == "1:0:")
					items.push( "<option value='" + ref + "'>" + val['servicename'] + "</option>" );
			}
		});
		
		if (items.length>0) {
			options += "<optgroup label='" + name + "'>" + items.join("") + "</optgroup>";
		}
	});
	$("#channels").append( options);
	$('#channels').trigger("chosen:updated");

});

}

function FillAT(autotimerid)
{
	var def = $(atxml).find("defaults");
	if(def)
		dencoding=def.attr("encoding");
	if(!dencoding)
		dencoding="UTF-8";

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

	this.searchType = "partical";
	if(xml.attr("searchType"))
		this.searchType=xml.attr("searchType");

	this.searchCase = "insensitive";
	if(xml.attr("searchCase"))
		this.searchCase=xml.attr("searchCase");

	this.justplay = "0";
	if(xml.attr("justplay"))
		this.justplay=xml.attr("justplay");

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
		if (_a) {
			this.timerOffsetAfter=_a;
		} else
			this.timerOffsetAfter=_b;
		this.timerOffsetBefore=_a;
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
			_b.push(escape(ref));
		else
			_c.push(ref);
	});
	
	this.Channels = _c.slice();
	this.Bouquets = _b.slice();

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

	this.encoding = xml.attr("encoding");
	if(!this.encoding) {
		this.encoding = dencoding;
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
	}

	$("#avoidDuplicateDescription").val(this.avoidDuplicateDescription);
	
	if(this.location) {
		$('#location').val(this.location);
		$('#Location').prop('checked',true);
	}
	else
		$('#Location').prop('checked',false);

	$('#timerOffset').prop('checked',this.timerOffset);
	if(this.timerOffset)
	{
		$('#oafter').val(this.timerOffsetAfter);
		$('#obefore').val(this.timerOffsetBefore);
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
	
	$.each(this.Bouquets, function(index, value) {
		$('#bouquets option[value="' + value + '"]').prop("selected", true);
	});
	
	$.each(this.Channels, function(index, value) {
		$('#channels option[value="' + value + '"]').prop("selected", true);
	});

	$('#Bouquets').prop('checked',(this.Bouquets.length>0));
	$('#Channels').prop('checked',(this.Channels.length>0));
	
	if(this.Bouquets.length==0)
		$('#bouquets').val(null);
	if(this.Channels.length==0)
		$('#channels').val(null);

	$('#bouquets').trigger("chosen:updated");
	$('#channels').trigger("chosen:updated");
	
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
	
	// TODO: tags
	
	checkValues();
};

function addAT()
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

	var name = "New Name";
	var match = "New Name";
	var id = _id.toString();

	var xml = '<timers><timer name="'+name+'" match="'+match+'" enabled="yes" id="'+id+'" encoding="ISO8859-15"></timer></timers>',
	xmlDoc = $.parseXML( xml )
	
	$(xmlDoc).find("timer").each(function () {
		$( "#atlist" ).append($('<li></li>').html($(this).attr("name")).addClass('ui-widget-content').data('id',$(this).attr("id")));
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

		$.ajax({
			type: "GET", url: "/autotimer/remove?id=" + CurrentAT.id,
			dataType: "xml",
			success: function (xml)
			{
			
				var state=$(xml).find("e2state").first();
				var txt=$(xml).find("e2statetext").first();
				
				showError(txt.text());
				
				console.debug(xml);
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
			// TODO : error handling
			alert(request.responseText);
		}
	});
}

function saveAT()
{
	if(CurrentAT) // && CurrentAT.MustSave)
	{

	var reqs = "/autotimer/edit?";

	reqs += "match=" + encodeURIComponent(CurrentAT.match);
	reqs += "&name=" + encodeURIComponent(CurrentAT.name);
	reqs += "&enabled=" + (CurrentAT.enabled) ? 1 : 0;
	reqs += "&justplay=" + (CurrentAT.justplay) ? 1 : 0;
	reqs += "&setEndtime=" + (CurrentAT.setEndtime) ? 1 : 0;
	reqs += "&searchCase=" + CurrentAT.searchCase;
	reqs += "&overrideAlternatives=" + (CurrentAT.overrideAlternatives) ? 1 : 0;
	reqs += "&avoidDuplicateDescription=" + CurrentAT.avoidDuplicateDescription;
	reqs += "&searchForDuplicateDescription=" + CurrentAT.searchForDuplicateDescription;
	reqs += "&location=" + encodeURIComponent(CurrentAT.location);
	reqs += "&searchType=" + CurrentAT.searchType;
	reqs += "&maxduration=" + (CurrentAT.maxduration > -1) ? CurrentAT.maxduration : "";
	reqs += "&encoding=" + encodeURIComponent(CurrentAT.encoding);

	if(CurrentAT.timerOffsetAfter > -1 && CurrentAT.timerOffsetBefore > -1)
		reqs += "&offset=" + CurrentAT.timerOffsetBefore + "," + CurrentAT.timerOffsetAfter;
	else
		reqs += "&offset=";

	if(CurrentAT.timeSpan)
		reqs += "&timespanFrom=" + CurrentAT.from + "&timespanTo=" + CurrentAT.to;
	else
		reqs += "&timespanFrom=&timespanTo=";

	if(this.timeFrame)
		reqs += "&before=" + CurrentAT.before + "&after=" + CurrentAT.after;
	else
		reqs += "&before=&after=";


// TODO: filter , tags , bq , channels
	console.log(this.tags);
	console.log(this.filter);
	console.log(this.Channels);
	console.log(this.Bouquets);
	
	return;
	
	// if change
	if(CurrentAT.id!=-1)
		regs += "&id=" + CurrentAT.id;

		$.ajax({
			type: "GET", url: reqs,
			dataType: "xml",
			success: function (xml)
			{
			
				var state=$(xml).find("e2state").first();
				var txt=$(xml).find("e2statetext").first();
				
				showError(txt.text());
				
				console.debug(xml);
				readAT();
			},
			error: function (request, status, error) {
				showError(request.responseText);
			}
		});
		
	}
}

function parseAT()
{
	if(CurrentAT && CurrentAT.MustSave)
	{
		$.ajax({
			type: "GET", url: "/autotimer/parse",
			dataType: "xml",
			success: function (xml)
			{
			
				var state=$(xml).find("e2state").first();
				var txt=$(xml).find("e2statetext").first();
				
				showError(txt.text());
				
				console.debug(xml);
				readAT();
			},
			error: function (request, status, error) {
				showError(request.responseText);
			}
		});
		
	}
}

function showError(txt)
{
	$('#error').text(txt);
	$('#errorbox').show();
}

