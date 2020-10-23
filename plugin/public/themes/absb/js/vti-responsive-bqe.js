!function(){var e=new function(){var e;return{showProviders:function(t){$("#sel0").show(),$("#btn-provider-add").show().prop("disabled",1!==e.cType),$("#provider").empty(),$.each(t,function(e,t){$("#provider").append(t)}),$("#provider").children().first().addClass("ui-selected"),e.changeProvider($("#provider").children().first().data("sref"),e.showChannels),e.setHover("#provider")},showChannels:function(t){$("#channels").empty(),$.each(t,function(e,t){$("#channels").append(t)}),e.setChannelButtons(),e.setHover("#channels")},showBouquets:function(t){$("#bql").empty(),$.each(t,function(e,t){$("#bql").append(t)}),$("#bql").children().first().addClass("ui-selected"),e.changeBouquet($("#bql").children().first().data("sref"),e.showBouquetChannels),e.setHover("#bql")},showBouquetChannels:function(t){$("#bqs").empty(),$.each(t,function(e,t){$("#bqs").append(t)}),e.setBouquetChannelButtons(),e.setHover("#bqs")},buildRefStr:function(t){var a;return a=0===e.Mode?"1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) || (type == 22) || (type == 31) || (type == 211) ":"1:7:2:0:0:0:0:0:0:0:(type == 2) ",0===t?(a+='FROM BOUQUET "bouquets.',a+=0===e.Mode?"tv":"radio",a+='" ORDER BY bouquet'):1===t?a+="FROM PROVIDERS ORDER BY name":2===t?a+="FROM SATELLITES ORDER BY satellitePosition":3===t&&(a+="ORDER BY name"),a},setTvRadioMode:function(t){var a=!1;t===e.Mode&&3!==t||(a=!0),e.Mode=t>1?0:t,0===e.cType?e.getSatellites(e.showProviders):1===e.cType?e.getProviders(e.showProviders):2===e.cType&&($("#sel0").hide(),e.getChannels(e.showChannels)),a&&e.getBouquets(e.showBouquets)},getSatellites:function(t){e.cType=0;var a=e.buildRefStr(2),s=0===e.Mode?"tv":"radio";$("#searchch").val(""),$("#channels").addClass("loading"),$.ajax({url:"/api/getsatellites",dataType:"json",cache:!0,data:{sRef:a,stype:s,date:e.date},success:function(e){var a=[],s=e.satellites;$.each(s,function(e,t){var s=t.service,n=t.name;n='<span class="icon"><i class="material-icons material-icons-centered">bubble_chart</i></span>'+n,a.push($("<li/>",{data:{sref:s}}).html(n))}),t&&t(a)}})},getProviders:function(t){e.cType=1;var a=e.buildRefStr(1);$("#searchch").val(""),$("#channels").addClass("loading"),$.ajax({url:"/api/getservices",dataType:"json",cache:!0,data:{sRef:a,date:e.date},success:function(e){var a=[],s=e.services;$.each(s,function(e,t){var s=t.servicereference,n=t.servicename;n='<span class="icon"><i class="material-icons material-icons-centered">folder_open</i></span>'+n,a.push($("<li/>",{data:{sref:s}}).html(n))}),t&&t(a)}})},getChannels:function(t){e.cType=2;var a=e.buildRefStr(3);$("#searchch").val(""),$("#channels").addClass("loading"),$.ajax({url:"/api/getservices?sRef="+a+"&provider=1",dataType:"json",cache:!0,data:{date:e.date,picon:1},success:function(a){e.allChannelsCache=a.services,e.filterChannelsCache=a.services,e.fillChannels(t)}})},fillChannels:function(t){var a=[];$.each(e.filterChannelsCache,function(t,s){var n=s.servicereference,o=s.servicename,i=s.provider,r=n.split(":")[2],l=n.split(":")[6],c=e.getNS(l);o='<span class="bqe__picon"><img src="'+s.picon+'"></span>'+o;var u='<span class="pull-right"><span title="'+i+'"> '+(e.sType[r]||"")+" &bull; "+c+'</span>&nbsp;<span class="dd-icon-selected pull-left"><i class="material-icons material-icons-centered">done</i></span></span>';a.push($("<li/>",{data:{stype:r,sref:n}}).html(o+u))}),$("#channels").removeClass("loading"),t&&t(a)},getBouquets:function(t){e.bqStartPositions={};var a=e.buildRefStr(0);$.ajax({url:"/bouqueteditor/api/getservices",dataType:"json",cache:!1,data:{sRef:a},success:function(a){var s=[],n=a.services;$.each(n,function(t,a){e.bqStartPositions[a.servicereference]=a.startpos;var n=a.servicereference,o=a.servicename;s.push($("<li/>",{data:{sref:n}}).html('<span class="handle dd-icon"><i class="material-icons material-icons-centered">list</i>&nbsp;</span>'+o+'<span class="dd-icon-selected pull-right"><i class="material-icons material-icons-centered">done</i></span></li>'))}),t&&t(s)}})},changeProvider:function(t,a){$("#channels").addClass("loading"),$.ajax({url:"/api/getservices",dataType:"json",cache:!0,data:{sRef:t,date:e.date,provider:"1",picon:1},success:function(t){e.allChannelsCache=t.services,e.filterChannelsCache=t.services,e.fillChannels(a)}})},changeBouquet:function(t,a){var s=0;e.bqStartPositions[t]&&(s=e.bqStartPositions[t]),$.ajax({url:"/bouqueteditor/api/getservices",dataType:"json",cache:!1,data:{sRef:t,picon:1},success:function(e){var t=[],n=e.services;$.each(n,function(e,a){var n=a.servicereference,o=1==a.ismarker?'<span style="float:right">(M)</span>':"",i=a.servicename,r=s+a.pos,l=a.picon;2==a.ismarker&&(o='<span style="float:right">(S)</span>'),""!=(i=r.toString()+" - "+i)&&t.push($("<li/>",{data:{ismarker:a.ismarker,sref:n}}).html('<span class="handle dd-icon"><i class="material-icons material-icons-centered">list</i>&nbsp;</span><span class="bqe__picon"><img src="'+l+'"></span>'+i+o+'<span class="dd-icon-selected pull-right"><i class="material-icons material-icons-centered">done</i></span></li>'))}),a&&a(t)}})},addProvider:function(){var t=$("#provider li.ui-selected").data("sref");$.ajax({url:"/bouqueteditor/api/addprovidertobouquetlist",dataType:"json",cache:!0,data:{sProviderRef:t,mode:e.Mode,date:e.date},success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0]),e.getBouquets(e.showBouquets)}})},moveBouquet:function(e){$.ajax({url:"/bouqueteditor/api/movebouquet",dataType:"json",cache:!1,data:{sBouquetRef:e.sBouquetRef,mode:e.mode,position:e.position},success:function(){}})},addBouquet:function(){swal({title:tstr_bqe_name_bouquet,text:"",type:"input",showCancelButton:!0,closeOnConfirm:!0,animation:"slide-from-top",inputValue:"",input:"text"},function(t){if(!1===t)return!1;t.length&&$.ajax({url:"/bouqueteditor/api/addbouquet",dataType:"json",cache:!1,data:{name:t,mode:e.Mode},success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0]),e.getBouquets(e.showBouquets)}})})},renameBouquet:function(){if(1===$("#bql li.ui-selected").length){var t=$("#bql li.ui-selected"),a=(t.index(),t.text()),s=$.trim(a.replace(/^list/,"").replace(/done$/,"")),n=t.data("sref");swal({title:tstr_bqe_rename_bouquet,text:"",type:"input",showCancelButton:!0,closeOnConfirm:!0,animation:"slide-from-top",inputValue:s,input:"text"},function(t){if(!1===t||t===a)return!1;t.length&&$.ajax({url:"/bouqueteditor/api/renameservice",dataType:"json",cache:!1,data:{sRef:n,mode:e.Mode,newName:t},success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0]),e.getBouquets(e.showBouquets)}})})}},deleteBouquet:function(){if(1===$("#bql li.ui-selected").length){var t=$("#bql li.ui-selected").text(),a=$("#bql li.ui-selected").data("sref");swal({title:tstr_bqe_del_bouquet_question,text:t.replace(/^list/,"").replace(/done$/,"")+" ?",type:"warning",showCancelButton:!0,confirmButtonColor:"#DD6B55",confirmButtonText:tstrings_yes_delete+" !",cancelButtonText:tstrings_no_cancel+" !",closeOnConfirm:!0,closeOnCancel:!0},function(t){t&&$.ajax({url:"/bouqueteditor/api/removebouquet",dataType:"json",cache:!1,data:{sBouquetRef:a,mode:e.Mode},success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0]),e.getBouquets(e.showBouquets)}})})}},setChannelButtons:function(){var e=0==$("#channels li.ui-selected").length;$("#btn-channel-add").prop("disabled",e),$("#btn-alternative-add").prop("disabled",e)},setBouquetChannelButtons:function(){var e=$("#bqs li.ui-selected"),t=0==e.length;$("#btn-channel-delete").prop("disabled",t),$("#btn-marker-add").prop("disabled",t),$("#btn-spacer-add").prop("disabled",t),t=1!=e.length||1!=e.data("ismarker"),$("#btn-marker-group-rename").prop("disabled",t)},moveChannel:function(t){$.ajax({url:"/bouqueteditor/api/moveservice",dataType:"json",cache:!1,data:{sBouquetRef:t.sBouquetRef,sRef:t.sRef,mode:t.mode,position:t.position},success:e.renumberChannel})},renumberChannel:function(){},addChannel:function(){var t=[],a=$("#bql li.ui-selected").data("sref"),s=$("#bqs li.ui-selected").data("sref")||"";$("#channels li.ui-selected").each(function(){t.push($.ajax({url:"/bouqueteditor/api/addservicetobouquet",dataType:"json",cache:!1,data:{sBouquetRef:a,sRef:$(this).data("sref"),sRefBefore:s},success:function(){}}))}),0!==t.length&&$.when.apply($,t).then(function(){e.changeBouquet(a,e.showBouquetChannels)})},addAlternative:function(){alert("NOT implemented YET")},deleteChannel:function(){if(0!==$("#bqs li.ui-selected").length){var t=$("#bql li.ui-selected").data("sref"),a=[],s=[],n=[];$("#bqs li.ui-selected").each(function(){s.push($(this).text().replace(/^list/,"").replace(/done$/,"")),a.push($(this).text()),n.push({sBouquetRef:t,mode:e.Mode,sRef:$(this).data("sref")})}),swal({title:tstr_bqe_del_channel_question,text:s.join(", ")+" ?",type:"warning",showCancelButton:!0,confirmButtonColor:"#DD6B55",confirmButtonText:tstrings_yes_delete+" !",cancelButtonText:tstrings_no_cancel+" !",closeOnConfirm:!0,closeOnCancel:!0},function(a){if(a){var s=[];$.each(n,function(e,t){s.push($.ajax({url:"/bouqueteditor/api/removeservice",dataType:"json",cache:!1,data:t,success:function(){}}))}),0!==s.length&&$.when.apply($,s).then(function(){e.changeBouquet(t,e.showBouquetChannels)})}})}},addMarker:function(){e._addMarker(!1)},addSpacer:function(){e._addMarker(!0)},_addMarker:function(t){t||swal({title:tstr_bqe_name_marker,text:"",type:"input",showCancelButton:!0,closeOnConfirm:!0,animation:"slide-from-top",inputValue:"",input:"text"},function(a){if(!1===a)return!1;if(a.length||t){var s=$("#bql li.ui-selected").data("sref"),n=$("#bqs li.ui-selected").data("sref")||"",o={sBouquetRef:s,Name:a,sRefBefore:n};t&&(o={sBouquetRef:s,SP:"1",sRefBefore:n}),$.ajax({url:"/bouqueteditor/api/addmarkertobouquet",dataType:"json",cache:!1,data:o,success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0]),e.changeBouquet(s,e.showBouquetChannels)}})}})},renameMarkerGroup:function(){var t=$("#bqs li.ui-selected");if(1===t.length&&0!=t.data("ismarker")){t.index();var a=t.text(),s=($.trim(a.replace(/^list/,"").replace(/done$/,"")),t.data("sref")),n=$("#bql li.ui-selected").data("sref"),o=$("#bqs li.ui-selected").next().data("sref")||"";swal({title:tstr_bqe_rename_marker,text:"",type:"input",showCancelButton:!0,closeOnConfirm:!0,animation:"slide-from-top",inputValue:"",input:"text"},function(t){if(!1===t||t===a)return!1;t.length&&$.ajax({url:"/bouqueteditor/api/renameservice",dataType:"json",cache:!1,data:{sBouquetRef:n,sRef:s,newName:t,sRefBefore:o},success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0]),e.changeBouquet(n,e.showBouquetChannels)}})})}},searchChannel:function(t){var a=t.toLowerCase();e.filterChannelsCache=[],$.each(e.allChannelsCache,function(t,s){var n=s.servicename,o=s.servicereference.split(":")[2],i=s.provider;console.log(e.sType[o].indexOf(a)),(n.toLowerCase().indexOf(a)>=0||i.toLowerCase().indexOf(a)>=0||e.sType[o].toLowerCase().indexOf(a)>=0)&&e.filterChannelsCache.push({servicename:s.servicename,servicereference:s.servicereference,provider:s.provider,picon:s.picon})}),e.fillChannels(e.showChannels),e.setChannelButtons()},showError:function(e,t){t=void 0!==t?t:"False",$("#statustext").text(""),!0===t||"True"===t||"true"===t?($("#statusbox").removeClass("ui-state-error").addClass("ui-state-highlight"),$("#statusicon").removeClass("ui-icon-alert").addClass("ui-icon-info")):($("#statusbox").removeClass("ui-state-highlight").addClass("ui-state-error"),$("#statusicon").removeClass("ui-icon-info").addClass("ui-icon-alert")),$("#statustext").text(e),""!==e?$("#statuscont").show():$("#statuscont").hide()},exportBouquets:function(){var t=prompt(tstr_bqe_filename+": ","bouquets_backup");t&&$.ajax({url:"/bouqueteditor/api/backup",dataType:"json",cache:!1,data:{Filename:t},success:function(t){var a=t.Result;if(!1===a[0])e.showError(a[1],a[0]);else{var s="/bouqueteditor/tmp/"+a[1];window.open(s,"Download")}}})},importBouquets:function(){$("#rfile").trigger("click")},prepareRestore:function(){var t=$(this).val();t=t.replace("C:\\fakepath\\",""),!1!==confirm(tstr_bqe_restore_question+" ( "+t+") ?")&&($("form#uploadrestore").unbind("submit").submit(function(t){var a=new FormData(this);$.ajax({url:"/bouqueteditor/uploadrestore",type:"POST",data:a,mimeType:"multipart/form-data",contentType:!1,cache:!1,processData:!1,dataType:"json",success:function(t,a,s){var n=t.Result;n[0]?e.doRestore(n[1]):e.showError("Upload File: "+a)},error:function(t,a,s){e.showError("Upload File Error: "+s)}}),t.preventDefault();try{t.unbind()}catch(e){}}),$("form#uploadrestore").submit())},doRestore:function(t){t&&$.ajax({url:"/bouqueteditor/api/restore",dataType:"json",cache:!1,data:{Filename:t},success:function(t){var a=t.Result;2==a.length&&e.showError(a[1],a[0])}})},setup:function(){(e=this).Mode=0,e.cType=1,e.sType={1:"SD",2:"Radio",16:"SD4",19:"HD","1F":"UHD",D3:"OPT"},e.hovercls=getHoverCls(),e.activecls=getActiveCls(),$("#btn-provider-add").click(e.addProvider),$("#btn-channel-add").click(e.addChannel),$("#btn-alternative-add").click(e.addAlternative),$("#btn-bouquet-add").click(e.addBouquet),$("#btn-bouquet-rename").click(e.renameBouquet),$("#btn-bouquet-delete").click(e.deleteBouquet),$("#btn-channel-delete").click(e.deleteChannel),$("#btn-marker-add").click(e.addMarker),$("#btn-spacer-add").click(e.addSpacer),$("#btn-marker-group-rename").click(e.renameMarkerGroup),$("#provider").selectable({selected:function(t,a){$(a.selected).addClass("ui-selected").siblings().removeClass("ui-selected"),e.changeProvider($(a.selected).data("sref"),e.showChannels)},classes:{"ui-selected":e.activecls}}),$("#channels").selectable({stop:e.setChannelButtons,classes:{"ui-selected":e.activecls}}),$("#bql").sortable({handle:".handle",stop:function(t,a){var s=$(a.item).data("sref"),n=a.item.index();e.moveBouquet({sBouquetRef:s,mode:e.Mode,position:n})}}).selectable({filter:"li",cancel:".handle",selected:function(t,a){$(a.selected).addClass("ui-selected").siblings().removeClass("ui-selected"),e.changeBouquet($(a.selected).data("sref"),e.showBouquetChannels)},classes:{"ui-selected":e.activecls}}),$("#bqs").sortable({handle:".handle",stop:function(t,a){var s=$("#bql li.ui-selected").data("sref"),n=$(a.item).data("sref"),o=a.item.index();e.moveChannel({sBouquetRef:s,sRef:n,mode:e.Mode,position:o})}}).selectable({filter:"li",cancel:".handle",stop:e.setBouquetChannelButtons,classes:{"ui-selected":e.activecls}}),$("#toolbar-choose-tv").click(function(){e.setTvRadioMode(0)}),$("#toolbar-choose-radio").click(function(){e.setTvRadioMode(1)}),$("#toolbar-choose-satellites").click(function(){e.getSatellites(e.showProviders)}),$("#toolbar-choose-providers").click(function(){e.getProviders(e.showProviders)}),$("#toolbar-choose-channels").click(function(){$("#sel0").hide(),$("#btn-provider-add").hide(),e.getChannels(e.showChannels)}),$("#toolbar-bouquets-reload").click(function(){e.getBouquets(e.showBouquets)}),$("#toolbar-bouquets-export").click(e.exportBouquets),$("#toolbar-bouquets-import").click(e.importBouquets),$("#searchch").keyup(function(){$(this).data("val")!==this.value&&e.searchChannel(this.value),$(this).data("val",this.value)}),$("#rfile").change(e.prepareRestore),e.setTvRadioMode(3)},setHover:function(t){$(t+" li").hover(function(){$(this).addClass(e.hovercls)},function(){$(this).removeClass(e.hovercls)})},getNS:function(e){var t=e.toLowerCase();if(t.startsWith("ffff",0))return"DVB-C";if(t.startsWith("eeee",0))return"DVB-T";var a=parseInt(t,16)>>16&4095,s=" E";return a>1800&&(s=" W",a=3600-a),(a/10).toFixed(1).toString()+s}}},t=new Date;e.date=t.getFullYear()+"-"+(t.getMonth()+1)+"-"+t.getDate(),e.setup()}();
