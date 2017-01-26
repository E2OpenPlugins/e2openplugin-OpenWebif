//******************************************************************************
//* bqe.js: openwebif Bouqueteditor plugin
//* Version 2.5
//******************************************************************************
//* Copyright (C) 2014-2016 Joerg Bleyel
//* Copyright (C) 2014-2016 E2OpenPlugins
//*
//* Authors: Joerg Bleyel <jbleyel # gmx.net>
//*          Robert Damas <https://github.com/rdamas>

//* V 2.0 - complete refactored
//* V 2.1 - theme support
//* V 2.2 - update status label
//* V 2.3 - fix #198
//* V 2.4 - improve search fix #419
//* V 2.5 - prepare support spacers #239

//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************
// TODO: alternatives

(function() {

	var BQE = function () {
		// keep reference to object.
		var self;
		
		// Mode=0: TV, Mode=1: Radio
		var	Mode;
		
		// keep track of which list in left pane is shown.
		// 0: satellites, 1: providers, 2: all channels
		var cType;
		
		// Array of services type markers.
		var sType;

		var hovercls;

		var activecls;
		
		var allChannelsCache;

		var filterChannelsCache;
		
		// used for caching.
		var date;

		return {
			// Callback for display left panel providers list
			// Triggers fetching and displaying dependent services list
			// for selected provider
			showProviders: function (options) {
				$('#sel0').show();
				$('#btn-provider-add')
					.show()
					.prop( 'disabled', (self.cType !==1 ) );
				$('#provider').empty();
				$.each(options, function(k,v) {
					$('#provider').append(v);
				})
				$('#provider').children().first().addClass('ui-selected');
				self.changeProvider(
					$('#provider').children().first().data('sref'),
					self.showChannels
				);
				self.setHover('#provider');
			},
		
			// Callback for display left panel services list
			showChannels: function (options) {
				$('#channels').empty();
				$.each(options, function(k,v) {
					$('#channels').append(v);
				})
				self.setChannelButtons();
				self.setHover('#channels');
			},

			// Callback for display right panel bouquet list
			// Triggers fetching and displaying dependent services list
			// for selected bouquet
			showBouquets: function (options) {
				$('#bql').empty();
				$.each(options, function(k,v) {
					$('#bql').append(v);
				})
				$('#bql').children().first().addClass('ui-selected');
				self.changeBouquet(
					$('#bql').children().first().data('sref'),
					self.showBouquetChannels
				);
				self.setHover('#bql');
			},

			// Callback for display right panel services list
			showBouquetChannels: function (options) {
				$('#bqs').empty();
				$.each(options, function(k,v) {
					$('#bqs').append(v);
				})
				self.setBouquetChannelButtons();
				self.setHover('#bqs');
			},

			// Build ref string for selecting services list
			// @param type int which list to use
			// @return string
			buildRefStr: function (type) {
				var r;
				if (self.Mode === 0) {
					r = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) || (type == 22) || (type == 31) || (type == 211) ';
				} else {
					r = '1:7:2:0:0:0:0:0:0:0:(type == 2) ';
				}
				if (type === 0) {
					r += 'FROM BOUQUET "bouquets.';
					r += (self.Mode === 0) ? 'tv' : 'radio';
					r += '" ORDER BY bouquet';
				} else if (type === 1) {
					r += 'FROM PROVIDERS ORDER BY name';
				} else if (type === 2) {
					r += 'FROM SATELLITES ORDER BY satellitePosition';
				} else if (type === 3) {
					r+='ORDER BY name';
				}
				// console.log("buildref => "+r);
				return r;
			},

			// Callback function for TV/Radio button
			// @param nmode int 
			//        0: TV, 1: Radio, 2: Option, 3: initial setup, triggers reload
			setTvRadioMode: function (nmode) {
				var reload = false;
				if (nmode !== self.Mode || nmode === 3) {
					reload = true;
				}
	
				if (nmode > 1) {
					self.Mode = 0;
				} else {
					self.Mode = nmode;
				}
	
				if (self.cType === 0) {
					self.getSatellites(self.showProviders);
				} else if (self.cType === 1) {
					self.getProviders(self.showProviders);
				} else if (self.cType === 2) {
					$('#sel0').hide();
					self.getChannels(self.showChannels);
				}
			
				if (reload) {
					self.getBouquets(self.showBouquets);
				}
			},

			// Callback function for left pane "satellites" button.
			// Fetches satellites list, param callback displays list.
			// @param callback function
			getSatellites: function (callback) {
				self.cType = 0;
				var ref = self.buildRefStr(2);
				var stype = (self.Mode === 0) ? 'tv' : 'radio';
				$.ajax({
					url: '/api/getsatellites',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: true,
					data: { sRef: ref, stype: stype, date: self.date },
					success: function ( data ) {
						var options = [];
						var s = data['satellites'];
						$.each( s, function ( key, val ) {
							var sref = val['service'];
							var name = val['name'];
							options.push( $("<li/>", {
								class: "ui-widget-content",
								data: { sref: sref }
							}).html(name));
						});
						if (callback) {
							callback(options);
						}
					}
				});
			},

			// Callback function for left pane "providers" button.
			// Fetches provider list, param callback displays list.
			// @param callback function
			getProviders: function (callback) {
				self.cType = 1;
				var ref = self.buildRefStr(1);
				$.ajax({
					url: '/api/getservices',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: true,
					data: { sRef: ref, date: self.date },
					success: function ( data ) {
						var options = [];
						var s = data['services'];
						$.each( s, function ( key, val ) {
							var sref = val['servicereference']
							var name = val['servicename']
							options.push( $('<li/>', {
							    class: "ui-widget-content",
							    data: { sref: sref }
							}).html(name) );
						});
						if (callback) {
							callback(options);
						}
					}
				});
			},

			// Callback function for left pane "channels" button.
			// Fetches channels list, param callback displays list.
			// @param callback function
			getChannels: function (callback) {
				self.cType = 2;
				var ref = self.buildRefStr(3);
				$.ajax({
					url: '/api/getservices?sRef=' + ref,
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: true,
					data: { sRef: ref, date: self.date },
					success: function ( data ) {
						self.allChannelsCache = data['services'];
						self.filterChannelsCache = data['services'];
						self.fillChannels(callback);
					}
				});
			},

			fillChannels: function (callback)
			{
				var options = [];
				$.each( self.filterChannelsCache, function ( key, val ) {
					var sref = val['servicereference'];
					var name = val['servicename'];
					var stype = sref.split(':')[2];
					var m = '<span class="marker">' + (self.sType[stype] || '') + '</span>';
					options.push( $('<li/>', {
						class: "ui-widget-content",
						data: { stype: stype, sref: sref }
					}).html(name+m) );
				});
				if (callback) {
					callback(options);
				}
			},

			// Callback function for fetching right panel bouquets list.
			// @param callback function display bouquets list
			getBouquets: function (callback) {
				var ref = self.buildRefStr(0);
				$.ajax({
					url: '/bouqueteditor/api/getservices',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: false,
					data: { sRef: ref },
					success: function ( data ) {
						var options = [];
						var s = data['services'];
						$.each( s, function ( key, val ) {
							var sref = val['servicereference'];
							var name = val['servicename'];
							options.push( $('<li/>', {
								class: "ui-widget-content",
								data: { sref: sref }
							}).html('<div class="handle"><span class="ui-icon ui-icon-arrow-2-n-s"></span></div>'+name+'</li>') );
						});
						if (callback) {
							callback(options);
						}
					}
				});
			},

			// Callback function for selecting provider in left panel
			// providers list.
			// @param sref string selected provider reference string
			// @param callback function display services list
			changeProvider: function (sref, callback) {
				$.ajax({
					url: '/api/getservices',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: true,
					data: { sRef: sref, date: self.date },
					success: function ( data ) {
						self.allChannelsCache = data['services'];
						self.filterChannelsCache = data['services'];
						self.fillChannels(callback);
					}
				});
			},

			// Callback function for selecting bouquet in right panel
			// bouquets list.
			// @param sref string selected bouquet reference string
			// @param callback function display services list
			changeBouquet: function (sref, callback) {
				$.ajax({
					url: '/bouqueteditor/api/getservices',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: false,
					data: { sRef: sref },
					success: function ( data ) {
						var options = [];
						var s = data['services'];
						$.each( s, function ( key, val ) {
							var sref = val['servicereference'];
							var m = (val['ismarker'] == 1) ? '<span style="float:right">(M)</span>' : '';
							var name=val['servicename'];
							var pos = val['pos'];
							if(val['ismarker'] == 2)
								m= '<span style="float:right">(S)</span>';
							name = pos.toString() + ' - ' + name;
							if(name!='')
								options.push( $('<li/>', {
									class: "ui-widget-content",
									data: {
										ismarker: val['ismarker'],
										sref: sref
									}
								}).html('<div class="handle"><span class="ui-icon ui-icon-arrow-2-n-s"></span></div>'+name+m+'</li>') );
						});
						if (callback) {
							callback(options);
						}
					}
				});
			},

			// Callback function for adding selecting provider in left panel
			// providers list to bouquets list
			addProvider: function () {
				var sref = $('#provider li.ui-selected').data('sref');
				$.ajax({
					url: '/bouqueteditor/api/addprovidertobouquetlist',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: true,
					data: { sProviderRef: sref, mode: self.Mode, date: self.date },
					success: function ( data ) {
						var r = data.Result;
						if (r.length == 2) {
							self.showError(r[1],r[0]);
						}
						self.getBouquets(self.showBouquets);
					}
				});
			},

			// Callback function for moving bouquet in bouquets list
			moveBouquet: function (obj) {
				$.ajax({
					url: '/bouqueteditor/api/movebouquet',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: false,
					data: { sBouquetRef: obj.sBouquetRef, mode: obj.mode, position: obj.position },
					success: function () {}
				});
			},

			// Callback function for bouquet add button in right pane
			// Prompts for bouquet name
			addBouquet: function () {
				var newname = prompt(tstr_bqe_name_bouquet + ':');
				if (newname.length) {
					$.ajax({
						url: '/bouqueteditor/api/addbouquet',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: { name: newname, mode: self.Mode },
						success: function ( data ) {
							var r = data.Result;
							if (r.length == 2) {
								self.showError(r[1],r[0]);
							}
							self.getBouquets(self.showBouquets);
						}
					});
				}
			},

			// Callback function for bouquet rename button in right pane
			// Prompts for new bouquet name
			renameBouquet: function () {
				if ($('#bql li.ui-selected').length !== 1) {
					return;
				}
				var item = $('#bql li.ui-selected');
				var pos = item.index();
				var sname = item.text();
				var sref = item.data('sref');

				var newname=prompt(tstr_bqe_rename_bouquet + ':', sname);
				if (newname && newname!=sname){
					$.ajax({
						url: '/bouqueteditor/api/renameservice',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: { sRef: sref, mode: self.Mode, newName: newname },
						success: function ( data ) {
							var r = data.Result;
							if (r.length == 2) {
								self.showError(r[1],r[0]);
							}
							self.getBouquets(self.showBouquets);
						}
					});
				}
			},

			// Callback function for bouquet delete button in roght panel
			// Prompts for confirmation
			deleteBouquet: function () {
				if ($('#bql li.ui-selected').length !== 1) {
					return;
				}
				var sname = $('#bql li.ui-selected').text();
				var sref = $('#bql li.ui-selected').data('sref');
				if (confirm(tstr_bqe_del_bouquet_question + "\n" + sname + ' ?') === false) {
					return;
				}

				$.ajax({
					url: '/bouqueteditor/api/removebouquet',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: false,
					data: { sBouquetRef: sref, mode: self.Mode },
					success: function ( data ) {
						var r = data.Result;
						if (r.length == 2) {
							self.showError(r[1],r[0]);
						}
						self.getBouquets(self.showBouquets);
					}
				});
			},

			// Disable/enable left pane channel buttons on selection state
			setChannelButtons: function () {
				var enabled = $('#channels li.ui-selected').length == 0;
				$('#btn-channel-add').prop( 'disabled', enabled );
				$('#btn-alternative-add').prop( 'disabled', enabled );
			},

			// Disable/enable right pane channel buttons on selection state
			setBouquetChannelButtons: function () {
				var item = $('#bqs li.ui-selected');
				var state = item.length == 0;
				$('#btn-channel-delete').prop( 'disabled', state );
				$('#btn-marker-add').prop( 'disabled', state );
				$('#btn-spacer-add').prop( 'disabled', state );

				state = item.length != 1 || item.data('ismarker') != 1;
				$('#btn-marker-group-rename').prop( "disabled", state );
			},

			// Callback function for moving service in right pane services list
			moveChannel: function (obj) {
				$.ajax({
					url: '/bouqueteditor/api/moveservice',
					dataType: 'json',
					contentType: "application/json; charset=utf-8",
					cache: false,
					data: {
						sBouquetRef: obj.sBouquetRef,
						sRef: obj.sRef,
						mode: obj.mode,
						position: obj.position
					},
					success:self.renumberChannel
				});
			},

			renumberChannel: function ()
			{
				//TODO
			},

			// Add selected services from left pane channels list to right pane channels list
			// Services will be added before selected service in right pane.
			addChannel: function () {
				var reqjobs = [];
				var bref = $('#bql li.ui-selected').data('sref');
				var dstref = $('#bqs li.ui-selected').data('sref') || '';

				$('#channels li.ui-selected').each(function () {
					reqjobs.push($.ajax({
						url: '/bouqueteditor/api/addservicetobouquet',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: {
							sBouquetRef: bref,
							sRef: $(this).data('sref'),
							sRefBefore: dstref
						},
						success: function () {}
					}));
				});

				if (reqjobs.length !== 0) {
					$.when.apply($, reqjobs).then(function () {
						self.changeBouquet(bref, self.showBouquetChannels);
					});
				}
			},

			// TBD.
			addAlternative: function () {
				alert('NOT implemented YET');
				return;
			},

			// Callback function for right pane delete channel button
			// Deletes selected services, prompts for confirmation.
			deleteChannel: function () {
				if ($('#bqs li.ui-selected').length === 0) {
					return;
				}

				var bref = $('#bql li.ui-selected').data('sref');
				var snames = [];
				var jobs = [];

				$('#bqs li.ui-selected').each(function () {
					snames.push( $(this).text() );
					jobs.push({
						sBouquetRef: bref,
						mode: self.Mode,
						sRef: $(this).data('sref')
					});
				});

				if (confirm(tstr_bqe_del_channel_question + "\n" + snames.join(', ') + ' ?') === false) {
					return;
				}

				var reqjobs = [];
				$.each( jobs, function ( key, jobdata ) {
					reqjobs.push($.ajax({
						url: '/bouqueteditor/api/removeservice',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: jobdata,
						success: function (){}
					}));
				});

				if (reqjobs.length !== 0) {
					$.when.apply($, reqjobs).then(function () {
						self.changeBouquet(bref, self.showBouquetChannels);
					});
				}
			},
			addMarker: function () {
				self._addMarker(false);
			},
			addSpacer: function () {
				self._addMarker(true);
			},
			// Callback function for right pane add marker button
			// Prompts for marker name, marker will be added before selected service
			_addMarker: function (sp) {
				var newname = '';
				if (!sp)
					newname = prompt(tstr_bqe_name_marker + ':');
				if (newname.length || sp) {
					var bref = $('#bql li.ui-selected').data('sref');
					var dstref = $('#bqs li.ui-selected').data('sref') || '';
					var params = { sBouquetRef: bref, Name: newname, sRefBefore: dstref };
					if(sp)
						params = { sBouquetRef: bref, SP: '1', sRefBefore: dstref };
					$.ajax({
						url: '/bouqueteditor/api/addmarkertobouquet',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: params,
						success: function ( data ) {
							var r = data.Result;
							if (r.length == 2) {
								self.showError(r[1],r[0]);
							}
							self.changeBouquet(bref, self.showBouquetChannels);
						}
					});
				}
			},

			// Callback function for right panel rename marker button
			// At the moment only markers will be renamed. Prompts for new marker name.
			renameMarkerGroup: function () {
				// rename marker or group
				var item = $('#bqs li.ui-selected');
				if (item.length !== 1) {
					return;
				}

				// TODO : rename group
				if (item.data('ismarker') == 0) {
					return;
				}

				var pos = item.index()
				var sname = item.text();
				var sref = item.data('sref');
				var bref = $('#bql li.ui-selected').data('sref');
				var dstref = $('#bqs li.ui-selected').next().data('sref') || '';

				var newname = prompt(tstr_bqe_rename_marker + ': ', sname);
				if (newname && newname !== sname) {
					$.ajax({
						url: '/bouqueteditor/api/renameservice',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: { sBouquetRef: bref, sRef: sref, newName: newname, sRefBefore: dstref },
						success: function ( data ) {
							var r = data.Result;
							if (r.length == 2) {
								self.showError(r[1],r[0]);
							}
							self.changeBouquet(bref, self.showBouquetChannels);
						}
					});
				}
			},

			// Callback function for search box in left pane
			// Filters matching services in channels list.
			searchChannel: function (txt) {
				var t = txt.toLowerCase();

				self.filterChannelsCache = [];
				$.each( self.allChannelsCache, function ( key, val ) {
					var name = val['servicename'];
					if (name.toLowerCase().indexOf(t) !== -1)
						self.filterChannelsCache.push({
							servicename: val['servicename'],
							servicereference:val['servicereference']
						});
				});

				self.fillChannels(self.showChannels);
				self.setChannelButtons();
			},

			// Display success and errors for selected ajax functions
			// @param txt string success/error msg
			// @param st bool False: error, True: success
			showError: function (txt, st) {
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
			},

			// Callback function for export button in right pane.
			// Prompts for backup file name
			exportBouquets: function () {
				var fn = prompt(tstr_bqe_filename + ': ', 'bouquets_backup');
				if (fn) {
					$.ajax({
						url: '/bouqueteditor/api/backup',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: { Filename: fn },
						success: function ( data ) {
							var r = data.Result;
							if (r[0] === false) {
								showError(r[1],r[0]);
							} else {
								var url =  "/bouqueteditor/tmp/" + r[1];
								window.open(url,'Download');
							}
						}
					});
				}
			},

			// Callback function for import button in right pane.
			// Triggers file upload dialog.
			importBouquets: function () {
				$("#rfile").trigger('click');
			},

			// Callback function for import button in right pane.
			// Called after file upload dialog. Prompts for confirmation of upload,
			// uploads backup file.
			prepareRestore: function () {
				var fn = $(this).val();
				fn = fn.replace('C:\\fakepath\\','');
				if (confirm(tstr_bqe_restore_question + ' ( ' + fn + ') ?') === false) {
					return;
				}

				$('form#uploadrestore')
					.unbind('submit')
					.submit(function (e)
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
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						success: function (data, textStatus, jqXHR) {
							var r = data.Result;
							if (r[0]) {
								self.doRestore(r[1]);
							} else {
								self.showError("Upload File: " + textStatus);
							}
						},
						error: function (jqXHR, textStatus, errorThrown) {
							self.showError("Upload File Error: " + errorThrown);
						}
					});
					e.preventDefault();
					try {
						e.unbind();
					} catch(e){}
				});
				$('form#uploadrestore').submit();
			},

			// Callback function for restoring uploaded bouquet backup file
			doRestore: function (fn) {
				if (fn) {
					$.ajax({
						url: '/bouqueteditor/api/restore',
						dataType: 'json',
						contentType: "application/json; charset=utf-8",
						cache: false,
						data: { Filename: fn }, 
						success: function ( data ) {
							// console.log(data);
							var r = data.Result;
							if (r.length == 2) {
								self.showError(r[1],r[0]);
							}
						}
					});
				}
			},

			// Setup handlers, trigger building lists.
			// This is the starting point.
			setup: function () {
				self = this;
				self.Mode = 0;
				self.cType = 1;
				self.sType = { '1': '[SD]', '16': '[SD4]', '19': '[HD]', '1F': '[UHD]', 'D3': '[OPT]' };
				self.hovercls = getHoverCls();
				self.activecls = getActiveCls();

				// Styled button sets; #tb1, #tb2 in left pane, #tb3 in right pane
				$('#tb1').buttonset();
				$('#tb2').buttonset();
				$('#tb3').buttonset();

				// Setup callback functions in left pane
				$('#btn-provider-add').click(self.addProvider);
				$('#btn-channel-add').click(self.addChannel);
				$('#btn-alternative-add').click(self.addAlternative);

				// Setup callback functions in right pane
				$('#btn-bouquet-add').click(self.addBouquet);
				$('#btn-bouquet-rename').click(self.renameBouquet);
				$('#btn-bouquet-delete').click(self.deleteBouquet);

				$('#btn-channel-delete').click(self.deleteChannel);
				$('#btn-marker-add').click(self.addMarker);
				$('#btn-spacer-add').click(self.addSpacer);
				$('#btn-marker-group-rename').click(self.renameMarkerGroup);
				
				// Setup selection callback function for left pane providers list
				// Triggers building services list for selected provider
				$('#provider').selectable({
					selected: function ( event, ui ) {
						$(ui.selected).addClass('ui-selected').siblings().removeClass('ui-selected');
						self.changeProvider($(ui.selected).data('sref'), self.showChannels);
					},classes: {
						"ui-selected": self.activecls 
					}
				});

				// Setup selection callback function for left pane channels list
				$('#channels').selectable({
					stop: self.setChannelButtons
					,classes: {
						"ui-selected": self.activecls 
					}
				});

				// Setup callback functions for right pane bouquets list
				// Sorting is done via sortable widget, selection via selectable
				// widget triggers building of channels list for selected bouquet.
				$('#bql').sortable({
					handle: '.handle',
					stop: function ( event, ui ) {
						var sref = $(ui.item).data('sref');
						var position = ui.item.index();
						self.moveBouquet({ sBouquetRef: sref, mode: self.Mode, position: position});
					}
				}).selectable({
					filter: 'li',
					cancel: '.handle',
					selected: function ( event, ui ) {
						$(ui.selected).addClass('ui-selected').siblings().removeClass('ui-selected');
						self.changeBouquet($(ui.selected).data('sref'), self.showBouquetChannels);
					},classes: {
						"ui-selected": self.activecls 
					}
				});

				// Setup callback functions for right pane channels list
				// Sorting is done via sortable widget.
				$('#bqs').sortable({
					handle: '.handle',
					stop: function ( event, ui ) {
						var bref = $('#bql li.ui-selected').data('sref');
						var sref = $(ui.item).data('sref');
						var position = ui.item.index();
						self.moveChannel({ sBouquetRef: bref, sRef: sref, mode: self.Mode, position: position});
					}
				}).selectable({
					filter: 'li',
					cancel: '.handle',
					stop: self.setBouquetChannelButtons,
					classes: {
						"ui-selected": self.activecls 
					}
				});

				// Setup callback functions for left pane toolbar buttons
				$('#toolbar-choose-tv').click(function () { self.setTvRadioMode(0); });
				$('#toolbar-choose-radio').click(function () { self.setTvRadioMode(1); });

				$('#toolbar-choose-satellites').click(function () { self.getSatellites(self.showProviders); });
				$('#toolbar-choose-providers').click(function () { self.getProviders(self.showProviders); });
				$('#toolbar-choose-channels').click(function () { 
					$('#sel0').hide();
					$('#btn-provider-add').hide();
					self.getChannels(self.showChannels); 
				});

				// Setup callback functions for right pane toolbar buttons
				$('#toolbar-bouquets-reload').click(function () { self.getBouquets(self.showBouquets); });
				$('#toolbar-bouquets-export').click(self.exportBouquets);
				$('#toolbar-bouquets-import').click(self.importBouquets);

				// Setup callback function for left pane search box
				$('#searchch').focus(function () { 
					if ($(this).val() === '...') {
						$(this).val('');
					}
				}).keyup(function (){
					if ($(this).data('val') !== this.value) {
						self.searchChannel(this.value);
					}
					$(this).data('val', this.value);
				}).blur(function (){
					$(this).data('val', '');
					if ($(this).val() === '') {
						$(this).val('...');
					}
				});

				// Setup callback function hidden file upload button
				$('#rfile').change(self.prepareRestore);

				// Initially build all lists.
				self.setTvRadioMode(3);
			},setHover : function(obj)
			{
				$(obj + ' li').hover(
					function(){ $(this).addClass(self.hovercls) },
					function(){ $(this).removeClass(self.hovercls) }
				)
			}
		 }
	};

	var bqe = new BQE();
	var date = new Date();
	bqe.date = date.getFullYear()+"-"+(date.getMonth()+1)+"-"+date.getDate();
	bqe.setup();

})();