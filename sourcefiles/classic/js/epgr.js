//******************************************************************************
//* epgr.js: openwebif EPGRefresh plugin
//* Version 1.3
//******************************************************************************
//* Copyright (C) 2016 Joerg Bleyel
//* Copyright (C) 2016 E2OpenPlugins
//*
//* V 1.0 - Initial Version
//* V 1.1 - Theme Support
//* V 1.2 - Refactor
//* V 1.3 - use public getallservices
//*
//* Authors: Joerg Bleyel <jbleyel # gmx.net>
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************

//var epgxml;

function toUnixDate(date){
	var datea = date.split('.');
	var d = new Date();
	d.setFullYear(datea[2],datea[1]-1,datea[0]);
	d.setHours( 0 );
	d.setMinutes( 0 );
	d.setSeconds( 0 );
	return Math.floor(d.getTime() / 1000);
}
function addZero(i) { if (i < 10) { i = "0" + i; } return i; }
function isBQ(sref) {return ((sref.indexOf("FROM BOUQUET") > -1) && (sref.indexOf("1:134:1") != 0));}
function isAlter(sref) {return (sref.indexOf("1:134:1") == 0);}

(function() {

	var EPGR = function () {
		// keep reference to object.
		var self;
		var er_bqchchanged = false;
		var er_hasAutoTimer = false;
		var binterval_in_seconds=true;

		return {

			setup: function () {
				self = this;

				$('#er_begin').val('22:30');
				$('#er_end').val('6:30');
				$('#er_begin').timepicker();
				$('#er_end').timepicker();
				$("#bouquets").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "100%"});
				$("#bouquets").chosen().change( function() {$("#bouquets").val($(this).val());self.er_bqchchanged = true;});
				$("#channels").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "100%"});
				$("#channels").chosen().change( function() {$("#channels").val($(this).val());self.er_bqchchanged = true;});
			
				$(".chosen-container .chosen-drop").addClass('ui-widget-content');
				if (theme == 'eggplant' || theme == 'vader')
				{
					$(".chosen-container .chosen-drop").css('background-image','none');
				}
				
				self.getAllServices();
				$("#actions").buttonset();
				$("#epgrbutton0").click(function () { self.reloadEPGR(); });
				$("#epgrbutton0").button({icons: { primary: "ui-icon-arrowrefresh-1-w"}});
				$("#epgrbutton1").click(function () { self.saveEPGR(); });
				$("#epgrbutton1").button({icons: { primary: "ui-icon-disk"}});
				$("#epgrbutton2").click(function () { self.DoRefresh(); });
				// TODO: icons
				$('#statuscont').hide();

			}, getAllServices: function () {
			
				GetAllServices(function ( options , boptions) {
					$("#channels").append( options);
					$('#channels').trigger("chosen:updated");
					$("#bouquets").append( boptions);
					$('#bouquets').trigger("chosen:updated");
					self.reloadEPGR();
				});
			
			}, reloadEPGR: function () {

				self.showError("");
				$.ajax({
					type: "GET", url: "/epgrefresh",
					dataType: "xml",
					success: function (xml)
					{
						self.readEPGR2(xml);
					},error: function (request, status, error) {
						self.showError(request.responseText);
						// TODO : error handling
					}
				});

			}, readEPGR2: function (chbq) {
			
				var begin;
				var end;
				self.er_hasAutoTimer = false;
			
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
									self.binterval_in_seconds = true;
									$("#er_interval").val(val);
								}
								else if(name == "interval") {
									self.binterval_in_seconds = false;
									$("#er_interval").val(val);
								}
								else
									$('#er_'+name).val(val);
							}
							else {
								if(name === "hasAutoTimer" && val === "True")
									self.er_hasAutoTimer = true;
							}
						});
						
						self.UpdateCHBQ(chbq,begin,end);
						
					},error: function (request, status, error) {
						self.showError(request.responseText);
					}
				});

			}, UpdateCHBQ: function (chbq,begin,end) {

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
			
				self.er_bqchchanged = false;
				
				if(self.binterval_in_seconds) {
					$('#lbls').show();
					$('#lblm').hide();
				}
				else
				{
					$('#lblm').show();
					$('#lbls').hide();
				}
				
				if(self.er_hasAutoTimer) {
					$('#er_hasAT').show();
				} else {
					$('#er_hasAT').hide();
				}

			}, saveEPGR: function() {

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
			
				if(self.er_hasAutoTimer) {
					reqs += "&inherit_autotimer=";
					reqs += $('#er_inherit_autotimer').is(':checked') ? "true":"";
					reqs += "&parse_autotimer=" + $('#er_parse_autotimer').val();
				}
				
				if(self.binterval_in_seconds)
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
						self.showError(txt.text(),state.text());
						if(state)
							self.SaveCHBQ();
					},
					error: function (request, status, error) {
						self.showError(request.responseText);
					}
				});

			}, SaveCHBQ: function() {

				if(self.er_bqchchanged === false)
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
						self.showError(txt.text(),state.text());
					},
					error: function (request, status, error) {
						self.showError(request.responseText);
					}
				});
				
			}, DoRefresh: function() {

				$.ajax({
					type: "GET", url: "/epgrefresh/refresh",
					dataType: "xml",
					success: function (xml)
					{
						var state=$(xml).find("e2state").first();
						var txt=$(xml).find("e2statetext").first();
						self.showError(txt.text(),state.text());
					},
					error: function (request, status, error) {
						self.showError(request.responseText);
					}
				});
	
			}, showError: function(txt,st) {
				st = typeof st !== 'undefined' ? st : 'False';
				$('#statustext').text('');
			
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
		 };
	};

	var epgr = new EPGR();
	epgr.setup();

})();
