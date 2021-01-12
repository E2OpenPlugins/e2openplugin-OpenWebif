
// TODO minimize js

var isChrome = !!window.chrome;
var isSecure = (window.location.protocol == 'https:');

var PlayerObj = function () {
	var self;
	var _vlc;
	var _html;
	var vxgplayerId = null;
	var currentp;
	var folderoptions;
	var dn;
	var currenturl;
	var pr;
	var pl;
	var hasvlc=false;
	var hasvxg=false;
	return {
		setup: function (vxg,auth,streamingport) {
			self = this;
			self.auth = auth;
			self.hasvlc = self.hasvxg = false;
			self.pl = GetLSValue('webtvplayerl','vlc');
			self.pr = GetLSValue('webtvplayerr','vlc');
			if (isChrome) {
				$('#plbtn_vlc').remove();
				$('#lplbtn_vlc').remove();
			} else
				self.hasvlc=true;
				
			if(vxg)
				self.hasvxg = true;

			if (isChrome && self.hasvxg)
			{
				self.pl = GetLSValue('webtvplayerl','vxg');
				self.pr = GetLSValue('webtvplayerr','vxg');
			}
			else
			{
				$('#plbtn_vxg').remove();
				$('#lplbtn_vxg').remove();
			}

			SetLSValue('webtvplayerl',self.pl);
			SetLSValue('webtvplayerr',self.pr);

			$('#sbtn0').click(function(){
				$('#streamchannels_chosen').css('display','inline-block');
				$('#streamrecordings_chosen').css('display','none');
				$('#moviesort-button').hide();
				self.currentp = self.pl;
				self.setPlayer(self.pl);
				self.CheckPlayer();
			});
			$('#sbtn1').click(function(){
				$('#streamrecordings_chosen').css('display','inline-block');
				$('#streamchannels_chosen').css('display','none');
				$('#moviesort-button').show();
				self.currentp = self.pr;
				self.setPlayer(self.pr);
				self.CheckPlayer();
			});
			
			$("#srcbuttons").buttonset();
			$("#streamchannels").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "400px"});
			$("#streamchannels").chosen().change( 
				function() {
					self.setUrl($("#streamchannels").val(),$("#streamchannels option:selected").text(),true);
					self.play();
				}
			);
			
			$("#streamrecordings").chosen({disable_search_threshold: 10,no_results_text: "Oops, nothing found!",width: "400px"});
			$("#streamrecordings").chosen().change( 
				function() {
					var ref = $("#streamrecordings").val();
					var name = $("#streamrecordings option:selected").text();
					if(ref!='')
					{
						if(ref == name)
						{
							$("#streamrecordings").empty();
							$('#streamrecordings').trigger("chosen:updated");
							$("#moviesort-button .ui-selectmenu-text .sortimg").empty();
							self.getRecordings(ref,function(){
								$('#streamrecordings').trigger("chosen:updated");
							});
						}
						else {
							self.setUrl(ref,name,false);
							self.play();
						}
					}
				}
			);
			
			$("#deinterlace").chosen({disable_search: true,no_results_text: "",width: "150px"});
			$("#deinterlace").chosen().change( 
					function() {
						var dv = $("#deinterlace").val();
						SetLSValue('vlcdeinterlace',dv);
						self.setDeinterlace(dv);
					}
			);
			
			var dv = GetLSValue('vlcdeinterlace','off');
			$("#deinterlace").val( dv );
			$('#deinterlace').trigger("chosen:updated");
			self.setDeinterlace(dv);
			
			if(!isSecure) {
				GetAllServices(function ( options , boptions) {
					$("#streamchannels").append( options);
					if(current_ref) {
						$("#streamchannels").val( current_ref );
					}
					$('#streamchannels').trigger("chosen:updated");
				});
			}

			self.getRecordings('',function(){
				$('#streamrecordings').trigger("chosen:updated");
			});
			
			$(".chosen-container .chosen-drop").addClass('ui-widget-content');
			if (theme == 'eggplant' || theme == 'vader')
			{
				$(".chosen-container .chosen-drop").css('background-image','none');
			}
			
			$('#btnstop').click(function(){
				self.stop();
				$(this).blur();
			});
			$('#btnplay').click(function(){
				self.play();
				$(this).blur();
			});
			
			$('#streamchannels_chosen').css('display','inline-block');
			$('#streamrecordings_chosen').css('display','none');

			if($('#wtranscoding').data('port')!='0')
			{
				$('#wtranscoding').click(function() { 
					SetLSValue('wtranscoding',$('#wtranscoding').is(':checked'));
					$(this).blur();
					self.stop();
					var live = ($('#moviesort-button').css('display') == 'none');
					if(live)
						$("#streamchannels").trigger('change');
					else
						$("#streamrecordings").trigger('change');
				});
				var ap = GetLSValue('wtranscoding',false);
				$('#wtranscoding').prop('checked',ap);
			}
			else
			{
				$('#wtranscoding').hide();
				$('#wtranscodingl').hide();
			}

			$.widget( "custom.iconselectmenu", $.ui.selectmenu, {
				_renderItem: function( ul, item ) {
					var li = $( "<li>" ),
					wrapper = $( "<div>",{ text: item.label } ).prepend (
					$( "<span class='sortimg'>").append (
						$( "<i>", { "class": "fa " + item.element.data("class") })
						)
					);
					return li.append( wrapper ).appendTo( ul );
				}
			});	
			
			var ms = GetLSValue('webtvms','name');
			$('#moviesort').val(ms).change();

			$('#moviesort').iconselectmenu({change: function(event, ui) {
				$("#streamrecordings").empty();
				SetLSValue('webtvms',ui.item.value);
				self.SortMovies();
				}
			}).addClass('ui-menu-icons');

			$('#moviesort-button').hide();
			$('#moviesort-button').css('margin-left','10px');
			$('#wautoplay').checkboxradio();
			$('#wtranscoding').checkboxradio();
			$('#btnstop').button();
			$('#btnplay').button();
			$("#plbuttons").buttonset();
			
			$('#plbtn_vlc').click(function(){
				self.setRecPlayer('vlc');
			});
			$('#plbtn_vxg').click(function(){
				self.setRecPlayer('vxg');
			});
			$('#plbtn_html').click(function(){
				self.setRecPlayer('html');
			});
			
			self.setPlayer(self.pl);
			self.CheckPlayer();
			
			$('#wautoplay').click(function() { 
				SetLSValue('wautoplay',$('#wautoplay').is(':checked'));
				$(this).blur();
			});
			var ap = GetLSValue('wautoplay',false);
			$('#wautoplay').prop('checked',ap);

			if(isSecure) {
				$('#srcbuttons').hide();
				$('#sbtn1').trigger( "click" );
			}
			else
			{
				if(current_ref) {
					self.setUrl(current_ref,current_name,true);
					if (ap)
						self.play();
				}
			}
			
		},setRecPlayer: function (pl) {
			self.currentp = self.pr = pl;
			SetLSValue('webtvplayerr',self.currentp);
			self.setPlayer(self.currentp);
		},SortMovies: function () {

			var idx = GetLSValue('webtvms','name');
			var _mv = MLHelper.SortMovies(idx).slice();

			var options = self.folderoptions;
			var items = [];
			// TODO : format list
			for (var i = 0, len = _mv.length; i < len; i++) {
				items.push (
					"<option value='" + _mv[i].fn + "'>" + _mv[i].title + "&nbsp;/&nbsp;" + _mv[i].bt + "</option>"
				);
			}
			options += "<optgroup label='" + self.dn + "'>" + items.join("") + "</optgroup>";
			$("#streamrecordings").append( options );
			$('#streamrecordings').trigger("chosen:updated");

		},CheckPlayer: function () {
		
			var live = ($('#moviesort-button').css('display') == 'none');
			var pl = self.currentp;
			
			$('#htmlPlayer').toggle(pl == 'html');
			$('#vxgPlayer').toggle(pl == 'vxg');
			$('#vlcPlayer').toggle(pl == 'vlc');

			if (!live) {
				$('#plbtn_html').prop('checked',false).button("refresh");
				if(self.hasvxg)
					$('#plbtn_vxg').prop('checked',false).button("refresh");
				if(self.hasvlc)
					$('#plbtn_vlc').prop('checked',false).button("refresh");
				$('#plbtn_'+pl).prop('checked',true).button("refresh");
			}
			$('#plbuttons').toggle(!live);
			$('#btnstop').toggle(pl != 'html');
			$('#btnplay').toggle(pl != 'html');

		},getRecordings: function(_dirname,callback) {
			var rdata = {fields:'f'};
			if(_dirname != '')
				rdata = {dirname: _dirname,fields:'f'};
			$.ajax({
				url: '/api/movielist',
				dataType: 'json',
				cache: false,
				data: rdata,
				success: function ( data ) {
					var mv = data['movies'];
					self.dn = data['directory'];
					var subdirs = data['bookmarks'];
					var items = [];
					var lastdir = '';
					var dira = self.dn.split('/');
					var options='';
					if(dira.length>1) {
						for (index = 0;index < dira.length - 2; ++index) {
							lastdir += dira[index] + '/';
						}
					}
					if(lastdir!='') {
						options = "<optgroup label='Folders'>";
						options += "<option value='' disabled selected style='display:none;'></option>";
						options += "<option value='" + lastdir + "'>" + lastdir + "</option>";
						for (index = 0;index < subdirs.length; ++index) {
							options += "<option value='" + self.dn + subdirs[index] + "'>" + self.dn + subdirs[index] + "</option>";
						}
						options += "</optgroup>";
					}
					
					self.folderoptions = options;
					
					var _mv = [];
					
					$.each( mv, function( key, val ) {
						var _fn = val['filename'].replace(/'/g, '___');
						_mv.push({ title :  val['eventname'], bt : val['begintime'], start:val['recordingtime'],fn:_fn});
					});
					
					MLHelper.SetMovies(_mv);
					self.SortMovies();
					callback();
				}
			});
		}, setDeinterlace: function(val){
				var modes = ["blend", "bob", "discard", "linear", "mean", "x", "yadif", "yadif2x"];
				try {
					if(val != "off" && modes.indexOf(val) >= 0)
						self._vlc.video.deinterlace.enable(val);
					else
						self._vlc.video.deinterlace.disable();
				} catch (e) { }
		}, setUrl: function(sref,name,live) {

			try {
				if (!live) {
					var fn = sref.split('/').reverse()[0];
					var path = encodeURIComponent(sref.substring(0,sref.length-fn.length));
					fn = fn.replace(/___/g, "'");
					sref = path + escape(fn);
				}
				
				var tp = $('#wtranscoding').data('port');
				var trans = GetLSValue('wtranscoding',false);
				if(tp!='0' && trans)
				{
					url = 'http://' + self.auth + window.location.hostname + ':'+ tp +'/' + sref;
				}
				else
				{
					if (live) {
						url = 'http://' + self.auth + window.location.hostname + ':' + streamingport + '/' + sref;
					} else {
						baseurl = window.location.protocol + '//' + self.auth + window.location.hostname;
						if (window.location.port != "")
							baseurl = baseurl + ':' + window.location.port;
						url = baseurl + '/file?file=' + sref;
					}
				}
				
				if(self._vlc) {
					self._vlc.playlist.clear();
					self._vlc.playlist.add(url);
				}
				if(self._html) {
					self._html.src = url;
				}
				if(self.hasvxg && self.currentp == 'vxg')
					vxgplayer(self.vxgplayerId).src(url);

			} catch (e) {
			}
		}, stop: function() {

			if(self.hasvxg && self.currentp == 'vxg')
				vxgplayer(self.vxgplayerId).stop();
			if(self.currentp == 'vlc')
				try { self._vlc.playlist.stop(); } catch (e) { }
			if(self.currentp == 'html')
				try { self._html.stop(); } catch (e) { }
		}, play: function() {
			if(self.hasvxg && self.currentp == 'vxg')
				vxgplayer(self.vxgplayerId).play();
			if(self.currentp == 'vlc')
				try { self._vlc.playlist.play(); } catch (e) { }
			if(self.currentp == 'html')
				try { self._html.play(); } catch (e) { }
		}, setPlayer : function (pl) {
			self._vlc = null;
			self._html = null;
			self.currentp = pl;

			$('#Deinterlace').toggle(pl == 'vlc');
			$('#vlcPlayer').toggle(pl == 'vlc');
			$('#htmlPlayer').toggle(pl == 'html');
			
			if(pl == 'vlc')
				self._vlc = document.getElementById("vlc");
			
			if(pl == 'html')
				self._html = document.getElementById("htmlp");

			if(self.hasvxg) {
				$('#vxgPlayer').toggle(pl == 'vxg');
				if(pl == 'vxg'){
					if(!self.vxgplayerId)
						self.createVX();
				}
				self.CheckPlayer();
			}
			
		}, createVX: function() {
		
			self.vxgplayerId = 'vxg_media_player1';
			var div = document.createElement('div');
			div.setAttribute("id", self.vxgplayerId);
			div.setAttribute("class", "vxgplayer");
			var _parent = document.getElementById('vxgPlayer');
			_parent.appendChild(div);
			vxgplayer(self.vxgplayerId, {
				nmf_path: 'media_player.nmf',
				nmf_src: '/vxg/media_player.nmf',
				latency: 300000,
				aspect_ratio_mode: 1,
				autohide: 3,
				controls: true,
				avsync: true,
				autoreconnect: 1
			});
		},
	}
};
