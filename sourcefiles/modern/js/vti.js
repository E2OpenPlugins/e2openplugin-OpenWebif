
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
	
	if (theme == 'pepper-grinder')
		$("#tvcontent").addClass('ui-state-active');
	
}

function myEPGSearch() {
	var spar = $("#epgSearchTVRadio").val();
	var full = $("#myepgbtn0").is(":checked") ? '&full=1' : '';
	var bouquetsonly = $("#myepgbtn1").is(":checked") ? '&bouquetsonly=1' : '';
	var url = "ajax/epgdialog?sstr=" + encodeURIComponent(spar) + full + bouquetsonly;
	
	var w = $(window).width() -100;
	var h = $(window).height() -100;
	
	var buttons = {};
	buttons[tstr_close] = function() { $(this).dialog("close");};
	buttons[tstr_open_in_new_window] = function() { $(this).dialog("close"); open_epg_search_pop(spar,full);};
	
	load_dm_spinner(url,tstr_epgsearch,w,h,buttons);
}
