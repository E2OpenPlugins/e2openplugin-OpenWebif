//******************************************************************************
//* bqe.js: openwebif Bouqueteditor plugin
//* Version 1.0
//******************************************************************************
//* Copyright (C) 2014 Joerg Bleyel
//* Copyright (C) 2014 E2OpenPlugins
//*
//* Authors: Joerg Bleyel <jbleyel # gmx.net>
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************
// TODO: alternatives

var Mode=0;
var cType=1;
var currentBQ=null;
var currentProv=null;

var srccl=[];
var dstbl=[];
var dstcl=[];
var seldstbl=[];
var seldstcl=[];
var selsrccl=[];
var markerstr = "<span style='float:right'>(M)</span>";
var rootreqstr = "/bouqueteditor/api/";

function buildRefStr(type)
{
	var r = (Mode===0) ? '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) || (type == 22) ' : '1:7:2:0:0:0:0:0:0:0:(type == 2) ';
	if(type===0) {
		r+='FROM BOUQUET "bouquets.';
		r+=(Mode===0) ? 'tv' : 'radio';
		r+='" ORDER BY bouquet';
	}
	if(type===1)
		r+='FROM PROVIDERS ORDER BY name';
	if(type===2)
		r+='FROM SATELLITES ORDER BY satellitePosition';
	if(type===3)
		r+='ORDER BY name';

	console.log(r);
	return encodeURIComponent(r);
}

function BQELoadTVR(nmode)
{
	var rl=false;
	if(nmode!==Mode || nmode===3) {
		rl=true;
	}
	
	if(nmode>1) {
		Mode=0;
		rl=true;
	}
	else
		Mode=nmode;
	
	if(cType===0)
		BQELoadSatellites();
	if(cType===1)
		BQELoadProvider();
	if(cType===2)
		BQELoadAll();

	if(rl) 
		BQELoadBQ();
}

function BQELoadSatellites()
{
	cType = 0;
	$("#sel0").show();
	$("#channels").empty();
	srccl=[];
	selsrccl=[];
	SetCHButtons();

	var ref = buildRefStr(2);
	var options = "";

	$.getJSON( "/api/getsatellites?sRef=" + ref, function( data ) {
		var s = data['satellites'];
		$.each( s, function( key, val ) {
			var sref = val['service'];
			var name = val['name'];
			options += "<li class='ui-widget-content' id='"+encodeURIComponent(sref)+"'>"+name+"</li>";
		});
		$("#provider").empty();
		$("#provider").append( options);
		$("#provider").selectable().children().first().addClass('ui-selected');
		var id = $("#provider").selectable().children().first().attr('id');
		changeProvider(id);
	});
	

}
function BQELoadProvider()
{
	cType = 1;
	$("#sel0").show();
	$("#channels").empty();
	srccl=[];
	selsrccl=[];
	SetCHButtons();

	var ref = buildRefStr(1);
	var options = "";

	$.getJSON( "/api/getservices?sRef=" + ref, function( data ) {
		var s = data['services'];
		$.each( s, function( key, val ) {
			var sref = val['servicereference']
			var name = val['servicename']
			options += "<li class='ui-widget-content' id='"+encodeURIComponent(sref)+"'>"+name+"</li>";
		});
		$("#provider").empty();
		$("#provider").append( options);
		$("#provider").selectable().children().first().addClass('ui-selected');
		var id = $("#provider").selectable().children().first().attr('id');
		changeProvider(id);
	});

}

function BQELoadBQ()
{

	var ref = buildRefStr(0);
	var options = "";

	dstbl=[];
	seldstbl=[];
	SetBQButtons();
	
	$.getJSON( rootreqstr + "getservices?sRef=" + ref, function( data ) {
		var s = data['services'];
		var idx=0;
		$.each( s, function( key, val ) {
			dstbl.push(val); 
			var name = val['servicename'];
			options += "<li class='ui-widget-content' id='"+idx+"'><div class='handle'><span class='ui-icon ui-icon-carat-2-n-s'></span></div>"+name+"</li>";
			idx++;
		});
		$("#bql").empty();
		$("#bql").append( options);
		$("#bql").selectable().children().first().addClass('ui-selected');
		var id = $("#bql").selectable().children().first().attr('id');
		SetBQButtons();
		changeBQidx(id);
	});
}

function BQELoadAll()
{
	$('#btnaddp').prop( "disabled",true );
	$("#sel0").hide();
	cType = 2
	var ref = buildRefStr(3);
	var options = "";
	srccl=[];
	selsrccl=[];
	SetCHButtons();

	$.getJSON( "/api/getservices?sRef=" + ref, function( data ) {
		var s = data['services'];
		$.each( s, function( key, val ) {
			var name = val['servicename']
			options += "<li class='ui-widget-content'>"+name+"</li>";
			srccl.push(val); 
		});
		$("#channels").empty();
		$("#channels").append( options);
	});

}

function changeBQidx(idx)
{
	var i = parseInt(idx);
	var bref = dstbl[i].servicereference;
	changeBQ(bref);
}

function changeBQ(bref)
{
	var options = "";
	currentBQ=bref;
	dstcl=[];
	seldstcl=[];

	$.getJSON( rootreqstr + "getservices?sRef=" + encodeURIComponent(bref), function( data ) {
		var s = data['services'];
		currentCH=null;
		var idx=0;
		$.each( s, function( key, val ) {
			dstcl.push(val); 
			var name = val['servicename']
			var m = (val['ismarker'] === '1') ? markerstr : "";
			options += "<li class='ui-widget-content' id='"+idx+"'><div class='handle'><span class='ui-icon ui-icon-carat-2-n-s'></span></div>"+name+m+"</li>";
			idx++;
		});
		$("#bqs").empty();
		if (idx>0) {
			$("#bqs").append( options);
			$("#bqs").selectable().children().first().addClass('ui-selected');
			var id = $("#bqs").selectable().children().first().attr('id');
			seldstcl.push(id);
		}
		SetDestCHButtons();
	});

}

function changeCH(obj)
{
	currentCH = obj.value;
}

function changeProvider(sref)
{
	$('#btnaddp').prop( "disabled", (cType!==1) );
	currentProv = sref;
	var options = "";
	srccl=[];
	selsrccl=[];
	SetCHButtons();

	$.getJSON( "/api/getservices?sRef=" + sref, function( data ) {
		var s = data['services'];
		$.each( s, function( key, val ) {
			var name = val['servicename']
			options += "<li class='ui-widget-content'>"+name+"</li>";
			srccl.push(val); 
		});
		$("#channels").empty();
		$("#channels").append( options);
	});

}

function searchChannel(txt)
{
	var t = txt.toLowerCase();
	$( "#channels li").each(function(){
		if($(this).html().toLowerCase().indexOf(t) !== -1)
			$(this).show();
		else
			$(this).hide();
	});
	
	$('#channels .ui-selected').removeClass('ui-selected');
	selsrccl=[];
	SetCHButtons();
}


function addprovider()
{
	$.getJSON( rootreqstr + "addprovidertobouquetlist?sProviderRef=" + currentProv + '&mode=' + Mode, function( data ) {
		var r = data.Result;
		if(r[0])
			showError(r[1],r[0]);
		BQELoadBQ();
	});
}

function addchannel()
{
	var srefs = [];
	$.each( selsrccl, function( key, val ) {
		var idx = parseInt(val);
		srefs.push(srccl[idx].servicereference);
	});

	var reqjobs = [];
	var dstref = "";
	
	if (seldstcl.length>0) {
		var si = seldstcl[0];
		var i = parseInt(si);
		dstref = dstcl[i].servicereference;
	}
	
	$.each( srefs, function( key, val ) {
		reqjobs.push($.getJSON( rootreqstr + "addservicetobouquet?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + encodeURIComponent(val) + '&sRefBefore=' + encodeURIComponent(dstref), function() {}));
	});

	if(reqjobs.length !== 0) {
		$.when.apply($, reqjobs).then(function() {
			changeBQ(currentBQ);
		});
	}

}

function addalter()
{
	NOTI();
	return;
	var sref = obj.value;
	var options = "";

	$.getJSON( rootreqstr + "addservicetoalternative?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sCurrentRef=" + encodeURIComponent(currentCH) + "&sRef=" + encodeURIComponent(sref) + "&mode=" + Mode, function( data ) {
		// check result
	});

}

function movec(arr)
{
	var cmd = [];
	var m=false;
	
	if((arr.length === 0) || (arr.length !== dstcl.length))
		return;

	for (var i=0;i<arr.length;i++)
	{
		var pos = parseInt(arr[i]);
		if(m && i>pos)
			break;
		if(i!==pos)
		{
			cmd.push( encodeURIComponent(dstcl[pos].servicereference) + "&mode=" + Mode + "&position=" + i);
			m=true;
		}
	}

	var reqjobs = [];
	$.each( cmd, function( key, val ) {
		reqjobs.push($.getJSON(rootreqstr + "moveservice?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + val , function() {}));
	});

	if(reqjobs.length !== 0) {
		$.when.apply($, reqjobs).then(function() {
			changeBQ(currentBQ);
		});
	}

}

function movebq(arr)
{
	var cmd = [];
	var m=false;
	
	if((arr.length === 0) || (arr.length !== dstbl.length))
		return;

	for (var i=0;i<arr.length;i++)
	{
		var pos = parseInt(arr[i]);
		if(m && i>pos)
			break;
		if(i!==pos)
		{
			cmd.push( encodeURIComponent(dstbl[pos].servicereference) + "&mode=" + Mode + "&position=" + i);
			m=true;
		}
	}

	var reqjobs = [];
	$.each( cmd, function( key, val ) {
		reqjobs.push($.getJSON(rootreqstr + "movebouquet?sBouquetRef=" + val , function() {}));
	});

	if(reqjobs.length !== 0) {
		$.when.apply($, reqjobs).then(function() {
			BQELoadBQ();
		});
	}

}

function delc()
{
	if(seldstcl.length<1)
		return;
	var snames = [];
	var srefs = [];
	$.each( seldstcl, function( key, val ) {
		var idx = parseInt(val);
		snames.push(dstcl[idx].servicename);
		srefs.push(dstcl[idx].servicereference);
	});
	var snamesstr = snames.join();
	if(confirm(tstr_bqe_del_channel_question + "\n" + snamesstr + " ?") === false)
		return;

	var reqjobs = [];
	$.each( srefs, function( key, val ) {
		reqjobs.push($.getJSON(rootreqstr + "removeservice?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + encodeURIComponent(val) + "&mode=" + Mode, function() {}));
	});

	if(reqjobs.length !== 0) {
		$.when.apply($, reqjobs).then(function() {
			changeBQ(currentBQ);
		});
	}

}

function delbq()
{
	if(seldstbl.length!==1)
		return;

	var pos=parseInt(seldstbl[0]);
	var sname = dstbl[pos].servicename;
	var sref = dstbl[pos].servicereference

	if(confirm(tstr_bqe_del_bouquet_question + "\n" + sname + " ?") === false)
		return;

	$.getJSON(rootreqstr + "removebouquet?sBouquetRef=" + encodeURIComponent(sref) + "&mode=" + Mode, function( data ) {
		var r = data.Result;
		if(r[0])
			showError(r[1],r[0]);
		BQELoadBQ();
	});

}

function addbq()
{
	var newname=prompt(tstr_bqe_name_bouquet + ":");
	if (newname.length){
		$.getJSON(rootreqstr + "addbouquet?name=" + encodeURIComponent(newname) + "&mode=" + Mode , function( data ) {
			var r = data.Result;
			if(r[0])
				showError(r[1],r[0]);
			BQELoadBQ();
		});
	}
}

function addm()
{
	var newname=prompt(tstr_bqe_name_marker + ":");
	if (newname.length){
	
		var dstref = "";
		
		if (seldstcl.length>0) {
			var si = seldstcl[0];
			var i = parseInt(si);
			dstref = dstcl[i].servicereference;
		}
		
		$.getJSON(rootreqstr + "addmarkertobouquet?sBouquetRef=" + encodeURIComponent(currentBQ) + '&Name=' + encodeURIComponent(newname) +'&sRefBefore=' + encodeURIComponent(dstref) , function( data ) {
			var r = data.Result;
			if(r[0])
				showError(r[1],r[0]);
			changeBQ(currentBQ);
		});
	}
}


function renbq()
{
	if(seldstbl.length!==1)
		return;
	var pos=parseInt(seldstbl[0]);
	var sname = dstbl[pos].servicename;
	var sref = dstbl[pos].servicereference;
	var newname=prompt(tstr_bqe_rename_bouquet + ':', sname);
	if (newname && newname!=sname){
		$.getJSON(rootreqstr + "renameservice?sRef=" + encodeURIComponent(sref) + "&mode=" + Mode + "&newName=" + encodeURIComponent(newname), function( data ) {
			var r = data.Result;
			if(r[0])
				showError(r[1],r[0]);
			BQELoadBQ();
		});
	}
}

function renmg()
{
	// rename marker or group
	if(seldstcl.length!==1)
		return;

	var pos=parseInt(seldstcl[0]);

	// TODO : rename group
	if(dstcl[pos].ismarker === "0")
		return;
	
	var sname = dstcl[pos].servicename;
	var sref = dstcl[pos].servicereference;
	var newname=prompt(tstr_bqe_rename_marker + ':', sname);
	if (newname && newname!=sname){

		var dstref = "";
		pos++;
		if(pos < dstcl.length) {
			dstref = dstcl[pos].servicereference;
		}
		
		$.getJSON(rootreqstr + "renameservice?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + encodeURIComponent(sref) + "&newName=" + encodeURIComponent(newname) + "&sRefBefore=" + encodeURIComponent(dstref), function( data ) {
			var r = data.Result;
			if(r[0])
				showError(r[1],r[0]);
			changeBQ(currentBQ);
		});
	}

	
}

function SetDestCHButtons() {
	var e = (seldstcl.length > 0)
	$('#btncdel').prop( "disabled", !e );
	$('#btnmadd').prop( "disabled", !e );

	e = (seldstcl.length === 1)
	if(e) {
		var idx = seldstcl[0];
		var i = parseInt(idx);
		e = (dstcl[i].ismarker === "1");
	}
	$('#btnmgren').prop( "disabled", !e );

}

function SetCHButtons() {
	var e = (selsrccl.length > 0)
	$('#btnaddc').prop( "disabled", !e );
	$('#btnadda').prop( "disabled", !e );
}

function SetBQButtons() {
	var e = (seldstbl.length === 1)
	$('#btnbren').prop( "disabled", !e );
	$('#btnbdel').prop( "disabled", !e );
}

function NOTI()
{
	alert("NOT implemented YET");
}

function BQEBackup()
{
	var fn=prompt(tstr_bqe_filename + ':', 'bouquets_backup');
	if (fn) {
		$.getJSON(rootreqstr + 'backup?Filename='+fn, function( data ) {
			var r = data.Result;
			if(r[0]===false)
				showError(r[1],r[0]);
			else {
				var url =  "/bouqueteditor/tmp/" + r[1];
				window.open(url,'Download');
			}
		});
	}
}

function BQEDoRestore(fn)
{
	if (fn) {
		$.getJSON(rootreqstr + 'restore?Filename='+fn, function( data ) {
			console.log(data);
			var r = data.Result;
			showError(r[1],r[0]);
		});
	}
}


function BQERestore()
{
	$("#rfile").trigger('click');
}

function prepareRestore(obj){
	var fn = obj.val()
	fn = fn.replace('C:\\fakepath\\','');
	if(confirm(tstr_bqe_restore_question + " ( " + fn + ") ?") === false)
		return;
	
	$('form#uploadrestore').unbind('submit');
	$('form#uploadrestore').submit(function(e)
	{
		var formData = new FormData(this);
		$.ajax({
			url: '/bouqueteditor/uploadrestore',
			type: 'POST',
			data:  formData,
			mimeType:"multipart/form-data",
			contentType: false,
			cache: false,
			processData:false,
			dataType: "json",
			success: function(data, textStatus, jqXHR)
			{
				var r = data.Result;
				if(r[0])
					BQEDoRestore(r[1]);
				else
					showError("Upload File: " + textStatus);
			},
			error: function(jqXHR, textStatus, errorThrown) 
			{
				showError("Upload File Error: " + errorThrown);
			}
		});
		e.preventDefault();
		try {
			e.unbind();
		} catch(e){}
	});
	$('form#uploadrestore').submit();
}

function InitPage() {

	showError("");
	
	$('#btn0').click(function(){ BQELoadTVR(0);});
	$('#btn1').click(function(){ BQELoadTVR(1);});

	$('#btn2').click(function(){ BQELoadSatellites();});
	$('#btn3').click(function(){ BQELoadProvider();});
	$('#btn4').click(function(){ BQELoadAll();});

	$('#btn5').click(function(){ BQELoadBQ();});
	$('#btn6').click(function(){ BQEBackup();});
	$('#btn7').click(function(){ BQERestore();});

	$("#tb1").buttonset();
	$("#tb2").buttonset();
	$("#tb3").buttonset();

	$("#provider").selectable({
		selected: function( event, ui ) {
			$(ui.selected).addClass("ui-selected").siblings().removeClass("ui-selected");
			changeProvider(ui.selected.id);
		}
	});

	$("#channels").selectable({
		stop: function() {
			var _s = [];
			$( ".ui-selected", this ).each(function() {
				var index = $( "#channels li" ).index( this );
				_s.push(index);
			});
			selsrccl=_s;
			SetCHButtons();
		}
	});

	$("#bqs").sortable({
		handle: ".handle",
		update: function( event, ui ) {
			var newsort = $(this).sortable('toArray');
			movec(newsort);
		}
		}).selectable({
		filter: "li",
		cancel: ".handle",
		stop: function() {
			var _s = [];
			$( ".ui-selected", this ).each(function() {
				var index = $( "#bqs li" ).index( this );
				_s.push(index);
			});
			seldstcl = _s;
			console.log(_s);
			SetDestCHButtons();
		}
	});

	$("#bql").sortable({
		handle: ".handle",
		update: function( event, ui ) {
			var newsort = $(this).sortable('toArray');
			movebq(newsort);
		}
		}).selectable({
		filter: "li",
		cancel: ".handle",
		stop: function() {
			var _s = [];
			$( ".ui-selected", this ).each(function() {
				var index = $( "#bql li" ).index( this );
				_s.push(index);
			});
			seldstbl = _s;
			SetBQButtons();
			if(_s.length === 1)
				changeBQidx(_s[0]);
		}
	});


	$('#searchch').focus(function() { 
		if ($(this).val() == "...") {
			$(this).val('');
		}
	});

	$('#searchch').keyup(function(){
		if ($(this).data('val')!=this.value) {
			searchChannel(this.value);
		}
		$(this).data('val', this.value);
	});

	$('#searchch').blur(function(){
		if ($(this).val() == "") {
			$(this).val('...');
		}
	});

	SetBQButtons();

	$('#btnaddc').prop( "disabled", true );
	$('#btnadda').prop( "disabled", true );
	$('#btnaddp').prop( "disabled", true );
	$('#btnmadd').prop( "disabled", true );
	$('#btnmgren').prop( "disabled", true );
	
	BQELoadTVR(3);
	
	$("#rfile").change(function() {
		prepareRestore($(this));
	});
	
}

function showError(txt,st)
{
	st = typeof st !== 'undefined' ? st : "False";
	$('#success').text("");
	$('#error').text("");
	if(st===true)
		st="True";
	if(st === "True")
		$('#success').text(txt);
	else
		$('#error').text(txt);
	if(txt!=="")
		$('#errorbox').show();
	else
		$('#errorbox').hide();
}
