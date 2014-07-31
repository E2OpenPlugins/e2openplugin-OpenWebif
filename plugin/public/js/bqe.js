/* Bouqueteditor plugin for openwebif v1.0 | (c) 2014 E2OpenPlugins | License GPL V2 , https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt */

// TODO: markers, alternatives


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

function buildRefStr(type)
{
	var r = (Mode===0) ? '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) ' : '1:7:2:0:0:0:0:0:0:0:(type == 2) ';
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
			var sref = val['service']
			var name = val['name']
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
	cType = 1
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
	
	$.getJSON( "/bouqueteditor/api/getservices?sRef=" + ref, function( data ) {
		var s = data['services'];
		var idx=0;
		$.each( s, function( key, val ) {
			dstbl.push(val); 
			var name = val['servicename']
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
//	console.log(ref);
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

	$.getJSON( "/bouqueteditor/api/getservices?sRef=" + encodeURIComponent(bref), function( data ) {
		var s = data['services'];
		currentCH=null;
		var idx=0;
		$.each( s, function( key, val ) {
			dstcl.push(val); 
			var name = val['servicename']
			options += "<li class='ui-widget-content' id='"+idx+"'><div class='handle'><span class='ui-icon ui-icon-carat-2-n-s'></span></div>"+name+"</li>";
			idx++;
		});
		$("#bqs").empty();
		$("#bqs").append( options);
		$("#bqs").selectable().children().first().addClass('ui-selected');
		var id = $("#bqs").selectable().children().first().attr('id');
		seldstcl.push(id);
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
	$.getJSON( "/bouqueteditor/api/addprovidertobouquetlist?sProviderRef=" + encodeURIComponent(currentProv) + '&mode=' + Mode, function( data ) {
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

	var deferreds = [];
	var dstref = "";
	
	if (seldstcl.length>0) {
		var si = seldstcl[0];
		var i = parseInt(si);
		dstref = dstcl[i].servicereference;
	}
	
	$.each( srefs, function( key, val ) {
		deferreds.push($.getJSON("/bouqueteditor/api/addservicetobouquet?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + encodeURIComponent(val) + '&sRefBefore=' + encodeURIComponent(dstref), function() {}));
	});

	if(deferreds.length !== 0) {
		$.when.apply($, deferreds).then(function() {
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

	$.getJSON( "/bouqueteditor/api/addservicetoalternative?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sCurrentRef=" + encodeURIComponent(currentCH) + "&sRef=" + encodeURIComponent(sref) + "&mode=" + Mode, function( data ) {
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

	var deferreds = [];
	$.each( cmd, function( key, val ) {
		deferreds.push($.getJSON("/bouqueteditor/api/moveservice?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + val , function() {}));
	});

	if(deferreds.length !== 0) {
		$.when.apply($, deferreds).then(function() {
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

	var deferreds = [];
	$.each( cmd, function( key, val ) {
		deferreds.push($.getJSON("/bouqueteditor/api/movebouquet?sBouquetRef=" + val , function() {}));
	});

	if(deferreds.length !== 0) {
		$.when.apply($, deferreds).then(function() {
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
	if(confirm("Do you really want to delete the channel(s)\n" + snamesstr + " ?") === false)
		return;

	var deferreds = [];
	$.each( srefs, function( key, val ) {
		deferreds.push($.getJSON("/bouqueteditor/api/removeservice?sBouquetRef=" + encodeURIComponent(currentBQ) + "&sRef=" + encodeURIComponent(val) + "&mode=" + Mode, function() {}));
	});

	if(deferreds.length !== 0) {
		$.when.apply($, deferreds).then(function() {
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

	if(confirm("Do you really want to delete the bouquet\n" + sname + " ?") === false)
		return;

	$.getJSON( "/bouqueteditor/api/removebouquet?sBouquetRef=" + encodeURIComponent(sref) + "&mode=" + Mode, function( data ) {
		// check result
		BQELoadBQ();
	});

}

function addbq()
{
	var newname=prompt("Name of the Bouquet:");
	if (newname.length){
		$.getJSON( "/bouqueteditor/api/addbouquet?name=" + encodeURIComponent(newname) + "&mode=" + Mode , function( data ) {
		// check result
			BQELoadBQ();
		});
	}
}



function renbq()
{
	if(seldstbl.length!==1)
		return;
	var pos=parseInt(seldstbl[0]);
	var sname = dstbl[pos].servicename;
	var sref = dstbl[pos].servicereference
	var newname=prompt('Enter new name for the bouquet:', sname);
	if (newname && newname!=sname){
		$.getJSON( "/bouqueteditor/api/renameservice?sRef=" + encodeURIComponent(sref) + "&mode=" + Mode + "&newName=" + encodeURIComponent(newname), function( data ) {
		// check result
			BQELoadBQ();
		});
	}
}

function SetDestCHButtons() {
	var e = (seldstcl.length > 0)
	$('#btncdel').prop( "disabled", !e );
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


function InitPage() {

	$('#btn0').click(function(){ BQELoadTVR(0);});
	$('#btn1').click(function(){ BQELoadTVR(1);});

	$('#btn2').click(function(){ BQELoadSatellites();});
	$('#btn3').click(function(){ BQELoadProvider();});
	$('#btn4').click(function(){ BQELoadAll();});

	$('#btn5').click(function(){ BQELoadBQ();});
	$('#btn6').click(function(){ NOTI();});
	$('#btn7').click(function(){ NOTI();});

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

	BQELoadTVR(3);
}
