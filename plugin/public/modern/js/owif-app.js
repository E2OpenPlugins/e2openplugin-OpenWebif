"use strict";(self.webpackChunkopenwebif_modern_assets=self.webpackChunkopenwebif_modern_assets||[]).push([[598],{8789:function(e,t,n){n(5666),n(1930)},1930:function(e,t,n){function r(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function a(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?r(Object(n),!0).forEach((function(t){f(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):r(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t,n,r,a,o,c){try{var s=e[o](c),i=s.value}catch(e){return void n(e)}s.done?t(i):Promise.resolve(i).then(r,a)}function c(e){return function(){var t=this,n=arguments;return new Promise((function(r,a){var c=e.apply(t,n);function s(e){o(c,r,a,s,i,"next",e)}function i(e){o(c,r,a,s,i,"throw",e)}s(void 0)}))}}function s(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function i(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}function u(e,t,n){return t&&i(e.prototype,t),n&&i(e,n),e}function f(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}n.r(t),n(5666),n(2759),n(2077),n(895),n(938),n(5623),n(1514),n(3238),n(1418),n(5613),n(1203),n(1013),n(3938),n(2482),n(911),n(5849),n(8410),n(2571),n(5901),n(8010),n(252),n(4009);var l=function(e){console.info("%cOWIF","color: #fff; font-weight: bold; background-color: #333; padding: 2px 4px 1px; border-radius: 2px;",e)},h=function(){function e(){s(this,e),f(this,"debugLog",(function(){var e;return(e=console).debug.apply(e,arguments)})),f(this,"regexDateFormat",new RegExp(/\d{4}-\d{2}-\d{2}/)),f(this,"toUnixDate",(function(e){return Date.parse("".concat(e,"Z"))/1e3})),f(this,"isBouquet",(function(e){return!e.startsWith("1:134:1")&&e.includes("FROM BOUQUET")})),f(this,"fetchData",function(){var e=c(regeneratorRuntime.mark((function e(t){var n,r,o,c,s,i=arguments;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return n=i.length>1&&void 0!==i[1]?i[1]:a({method:"get"},{}),e.prev=1,e.next=4,fetch(t,n);case 4:if(!(r=e.sent).ok){e.next=21;break}if(o=r.headers.get("content-type"),self.debugLog(o),!o||!o.includes("application/json")){e.next=15;break}return e.next=11,r.json();case 11:return c=e.sent,e.abrupt("return",c);case 15:return e.next=17,r.text();case 17:return s=e.sent,e.abrupt("return",xml2json(s));case 19:e.next=22;break;case 21:throw new Error(r.statusText||r.status);case 22:e.next=27;break;case 24:throw e.prev=24,e.t0=e.catch(1),new Error(e.t0);case 27:case 28:case"end":return e.stop()}}),e,null,[[1,24]])})));return function(t){return e.apply(this,arguments)}}()),self=this}return u(e,[{key:"getStrftime",value:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:new Date,t=new Date(1e3*Math.round(e)),n=strftime("%X",t);return n=n.match(/\d{2}:\d{2}|[^:\d]+/g).join(" "),strftime("%a %x",t)+" "+n}},{key:"getToTimeText",value:function(e,t){var n=t-e,r=Math.floor(n/864e5),a=new Date(1e3*Math.round(e)).getDay(),o=new Date(1e3*Math.round(t)).getDay(),c="";if(0===n)c="-";else{var s=strftime("%X",new Date(1e3*Math.round(t)));s=s.match(/\d{2}:\d{2}|[^:\d]+/g).join(" "),c=r<1&&o-a==0?"same day - "+s:r<2&&o-a==1?"next day - "+s:this.getStrftime(t)}return c}}]),e}(),p=function e(){s(this,e)},d=function(){function e(){s(this,e)}var t,n,r;return u(e,[{key:"getStatusInfo",value:(r=c(regeneratorRuntime.mark((function e(){var t,n;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,fetch("/api/statusinfo");case 2:if((t=e.sent).ok){e.next=7;break}throw new Error("HTTP error! status: ".concat(t.status));case 7:return e.next=9,t.json();case 9:return n=e.sent,e.next=12,n;case 12:return e.abrupt("return",e.sent);case 13:case"end":return e.stop()}}),e)}))),function(){return r.apply(this,arguments)})},{key:"getTags",value:(n=c(regeneratorRuntime.mark((function e(){var t,n;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,fetch("/api/gettags");case 2:if((t=e.sent).ok){e.next=7;break}throw new Error("HTTP error! status: ".concat(t.status));case 7:return e.next=9,t.json();case 9:return n=e.sent,e.next=12,n.tags;case 12:return e.abrupt("return",e.sent);case 13:case"end":return e.stop()}}),e)}))),function(){return n.apply(this,arguments)})},{key:"getAllServices",value:(t=c(regeneratorRuntime.mark((function e(t){var n,r,a,o,c;return regeneratorRuntime.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return n=1==t?"&noiptv=1":"",e.next=3,fetch("/api/getallservices?nolastscanned=1"+n);case 3:if((r=e.sent).ok){e.next=8;break}throw new Error("HTTP error! status: ".concat(r.status));case 8:return e.next=10,r.json();case 10:return a=e.sent,o=[],c=a.services.map((function(e){var t=e.subservices.map((function(t){var n=t.servicename,r=t.servicereference,a=r.indexOf("1:64:")>-1;return{name:n,sRef:r,bouquetName:e.servicename,extendedName:n+"<small>"+e.servicename+"</small>",disabled:a}}));return o=o.concat(t),{name:e.servicename,sRef:e.servicereference,channels:t}})),e.next=15,{channels:o,bouquets:c};case 15:return e.abrupt("return",e.sent);case 16:case"end":return e.stop()}}),e)}))),function(e){return t.apply(this,arguments)})}]),e}(),v=function(){function e(){s(this,e),f(this,"choicesConfig",{removeItemButton:!0,duplicateItemsAllowed:!1,resetScrollPosition:!1,shouldSort:!1,searchResultLimit:100,placeholder:!0,itemSelectText:""}),this.initEventHandlers()}return u(e,[{key:"initEventHandlers",value:function(){var e=this,t=new RegExp(/#\/?(.*)\??(.*)/gi);window.onhashchange=function(e){var n=e.target.location.hash.replace("#/","#").split("/")[0],r=n.replace(t,"/ajax/$1");n&&load_maincontent_spin(r)},document.querySelectorAll('input[name="skinpref"]').forEach((function(t){t.onchange=function(){e.skinPref=event.target.value}}))}},{key:"fullscreen",value:function(e,t){!0===e?screenfull.request(t).then((function(){l("GUI:fullscreen activated")})):!1===e?screenfull.exit().then((function(){l("GUI:fullscreen deactivated")})):screenfull.toggle(t).then((function(){l("GUI:fullscreen toggled")}))}},{key:"skinPref",get:function(){return document.body.dataset.skinpref||""},set:function(e){var t="skin--",n=this.skinPref;fetch("/api/setskincolor?skincolor=".concat(e)),document.body.classList.replace("".concat(t).concat(n),"".concat(t).concat(e)),document.body.dataset.skinpref=e}},{key:"preparedChoices",value:function(){var e=this,t={},n="data-choices-select";return document.querySelectorAll("[".concat(n,"]")).forEach((function(r){var a=r.dataset.choicesConfig||"{}";a=a?JSON.parse(a):{},a=Object.assign({},e.choicesConfig,a),t[r.getAttribute("".concat(n))]=new Choices(r,a)})),t}}]),e}();window.owif=new function e(){s(this,e),this.utils=new h,this.stb=new p,this.api=new d,this.gui=new v}}},function(e){e.O(0,[216],(function(){return 8789,e(e.s=8789)})),e.O()}]);