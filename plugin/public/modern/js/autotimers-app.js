parcelRequire=function(e,r,t,n){var i,o="function"==typeof parcelRequire&&parcelRequire,u="function"==typeof require&&require;function f(t,n){if(!r[t]){if(!e[t]){var i="function"==typeof parcelRequire&&parcelRequire;if(!n&&i)return i(t,!0);if(o)return o(t,!0);if(u&&"string"==typeof t)return u(t);var c=new Error("Cannot find module '"+t+"'");throw c.code="MODULE_NOT_FOUND",c}p.resolve=function(r){return e[t][1][r]||r},p.cache={};var l=r[t]=new f.Module(t);e[t][0].call(l.exports,p,l,l.exports,this)}return r[t].exports;function p(e){return f(p.resolve(e))}}f.isParcelRequire=!0,f.Module=function(e){this.id=e,this.bundle=f,this.exports={}},f.modules=e,f.cache=r,f.parent=o,f.register=function(r,t){e[r]=[function(e,r){r.exports=t},{}]};for(var c=0;c<t.length;c++)try{f(t[c])}catch(e){i||(i=e)}if(t.length){var l=f(t[t.length-1]);"object"==typeof exports&&"undefined"!=typeof module?module.exports=l:"function"==typeof define&&define.amd?define(function(){return l}):n&&(this[n]=l)}if(parcelRequire=f,i)throw i;return f}({"Tkyz":[function(require,module,exports) {
function e(e){return r(e)||n(e)||v(e)||t()}function t(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}function n(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}function r(e){if(Array.isArray(e))return g(e)}function o(e,t,n,r,o,a,i){try{var c=e[a](i),u=c.value}catch(e){return void n(e)}c.done?t(u):Promise.resolve(u).then(r,o)}function a(e){return function(){var t=this,n=arguments;return new Promise(function(r,a){function i(e){o(u,r,a,i,c,"next",e)}function c(e){o(u,r,a,i,c,"throw",e)}var u=e.apply(t,n);i(void 0)})}}function i(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function c(e,t){for(var n,r=0;r<t.length;r++)(n=t[r]).enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}function u(e,t,n){return t&&c(e.prototype,t),n&&c(e,n),e}function s(e){return(s="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function l(e,t){return d(e)||m(e,t)||v(e,t)||f()}function f(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}function m(e,t){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e)){var n=[],r=!0,o=!1,a=void 0;try{for(var i,c=e[Symbol.iterator]();!(r=(i=c.next()).done)&&(n.push(i.value),!t||n.length!==t);r=!0);}catch(e){o=!0,a=e}finally{try{r||null==c.return||c.return()}finally{if(o)throw a}}return n}}function d(e){if(Array.isArray(e))return e}function p(e,t){var n;if("undefined"==typeof Symbol||null==e[Symbol.iterator]){if(Array.isArray(e)||(n=v(e))||t&&e&&"number"==typeof e.length){n&&(e=n);var r=0,o=function(){};return{s:o,n:function(){return r>=e.length?{done:!0}:{done:!1,value:e[r++]}},e:function(e){throw e},f:o}}throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}var a=!0,i=!1;return{s:function(){n=e[Symbol.iterator]()},n:function(){var e=n.next();return a=e.done,e},e:function(e){i=!0,e},f:function e(){try{a||null==n.return||n.return()}finally{if(i)throw e}}}}function v(e,t){if(e){if("string"==typeof e)return g(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?g(e,t):void 0}}function g(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=Array(t);n<t;n++)r[n]=e[n];return r}!function(){function t(){var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:"",t=document.createElement("textarea");return t.innerHTML=e,t.value}function n(e){return Array.isArray(e)?e:[e]}function r(e){document.querySelectorAll(e).forEach(function(e){e.remove()})}function o(e,t,n,r){var o=t.namedItem(n);if(o)if(owif.utils.debugLog("[".concat(o.type,"]"),o,n,r),o instanceof RadioNodeList){var a,i=r.split(","),c=p(o.entries());try{for(c.s();!(a=c.n()).done;){var u=l(a.value,2),f=u[0],m=u[1];m.value=i[f]||"";try{m.dispatchEvent(new Event("change"))}catch(e){owif.utils.debugLog(n,r,e)}}}catch(e){c.e(e)}finally{c.f()}}else{switch(o.type){case"checkbox":r=!0===r||"True"===r||r.toString()===o.value,o.checked=r;break;case"select-multiple":try{var d=r.map(function(e){return e.sRef});e.autoTimerChoices[n].setChoices(r,"sRef","name",!1).setChoices(r,"label","value",!1).removeActiveItems().setChoiceByValue(r).setChoiceByValue(d)}catch(e){owif.utils.debugLog(n,r,e)}break;default:o.value=r}try{o.dispatchEvent(new Event("change"))}catch(e){owif.utils.debugLog(n,r,e)}}else if(owif.utils.debugLog("%c[N/A]","color: red",n,r),"filters"!==n){var v=document.createElement("input");v.type="hidden",v.name=n,v.value=r,v.dataset.valueType=s(r),t[0].form.prepend(v)}}function c(e,t){try{e.classList.toggle("dependent-section--disabled",t),e.querySelectorAll("input, select").forEach(function(e){e.disabled=t})}catch(e){}}var f=function(){function e(r){i(this,e);var o=this;if(Object.assign(o,r),o.name=t(o.name),o.match=t(o.match),o.tag=[],o.bouquets=[],o.services=[],o.filters={include:[],exclude:[]},o.enabled="yes"===o.enabled?1:0,o.from&&(o.timespanFrom=o.from,delete o.from),o.to&&(o.timespanTo=o.to,delete o.to),o.after){var a=new Date(1e3*parseInt(o.after));o.after=a.toISOString().split("T")[0]}if(o.before){var c=new Date(1e3*parseInt(o.before));o.before=c.toISOString().split("T")[0]}if(o.afterevent){var u=o.afterevent.from,s=o.afterevent.to,l=o.afterevent["_@ttribute"];u&&(o.aftereventFrom=u),s&&(o.aftereventTo=s),l&&(o.afterevent={shutdown:"deepstandby"}[l]||l)}if(o.e2service){var f=!1;n(o.e2service).forEach(function(e){var t=owif.utils.isBouquet(e.e2servicereference)?"bouquets":"services";o[t].push({sRef:e.e2servicereference,name:e.e2servicename,selected:!0}),f=!e.e2servicename}),o.hasMismatchedService=f,delete o.e2service}o.e2tag&&(o.tag=n(o.e2tag),delete o.e2tag),o.e2tags&&(!o.tag&&(o.tag=o.e2tags.split(" ")),delete o.e2tags),o.vps_safemode=!o.vps_overwrite,o.include&&(o.filters.include=n(o.include),delete o.include),o.exclude&&(o.filters.exclude=n(o.exclude),delete o.exclude)}return u(e,[{key:"bouquetSRefs",get:function(){return this.bouquets.map(function(e){return e.sRef})}},{key:"bouquetNames",get:function(){return this.bouquets.map(function(e){return e.name})}},{key:"channelSRefs",get:function(){return this.services.map(function(e){return e.sRef})}},{key:"channelNames",get:function(){return this.services.map(function(e){return e.name})}}]),e}();(new function(){var t,i=document.querySelector('form[name="atedit"]'),u=document.querySelector('form[name="atsettings"]'),s=function(){var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:{};return e._timespan=!!e.timespanFrom||!!e.timespanTo,e._datespan=!!e.after||!!e.before,e._after=!!e.after,e._before=!!e.before,e._timerOffset=!!e.offset,e.timeSpanAE=!!e.afterevent,e._location=!!e.location,e},m=function(e){var t=1<arguments.length&&void 0!==arguments[1]?arguments[1]:"",n=e.insertCell();return n.innerHTML=t,n},d=function(e,t){var n=e.insertRow(),r=t.e2state;m(n,r).title="Skip"===r?t.e2message:"",m(n,t.e2autotimername),m(n,t.e2name),m(n,t.e2servicename);var o=t.e2timebegin;m(n,owif.utils.getStrftime(o)).style.textAlign="right";var a=t.e2timeend;m(n,owif.utils.getToTimeText(o,a)).style.textAlign="right"};return{getAll:function(){var e=a(regeneratorRuntime.mark(function e(){var t,r;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,owif.utils.fetchData("/autotimer");case 2:return t=e.sent,r=t.autotimer,console.log("response: ",r),window.atList=n(r.timer),window.atList.map(function(e){return new f(e)}),e.abrupt("return",window.atList);case 8:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),populateList:function(){var n=document.getElementById("at__list");r(".at__item"),document.getElementById("at__page--edit").classList.toggle("hidden",!0),window.scroll({top:0,left:0,behavior:"smooth"}),document.getElementById("at__page--list").classList.toggle("hidden",!1);var o=document.getElementById("autotimer-list-item-template"),a=[],i=[];t.getAll().then(function(r){r.forEach(function(e){(e=new f(e)).location&&a.push(e.location),i=i.concat(e.tag);var r=valueLabelMap.autoTimers.searchType[e.searchType]||"",c=o.content.firstElementChild.cloneNode(!0);c.querySelector('[name="rename"]').onclick=function(){return t.renameEntry(e.id,e.name,"")};var u=c.querySelector('a[href="#at/edit/{{id}}"]');u.href=u.href.replace("{{id}}",e.id),u.onclick=function(){return t.editEntry(e.id),!1},c.querySelector('button[name="delete"]').onclick=function(){return t.deleteEntry(e.id)},c.querySelector('slot[name="autotimer-name"]').innerHTML=e.name,c.querySelector('slot[name="autotimer-searchType"]').innerHTML=r?"".concat(r,":"):"",e.timespanFrom&&(c.querySelector('slot[name="autotimer-timespan"]').innerHTML="~ ".concat(e.timespanFrom||""," - ").concat(e.timespanTo||"")),c.querySelector('slot[name="autotimer-channels"]').innerHTML=e.channelNames.join(", "),e.bouquetNames.length&&(c.querySelector('slot[name="autotimer-bouquets"]').innerHTML="<br> ".concat(e.bouquetNames.join(", "))),c.querySelector('slot[name="autotimer-match"]').innerHTML='"'.concat(e.match,'"'),n.appendChild(c)}),t.allLocations=e(new Set(t.availableLocations.concat(a))).sort()||[],t.allTags=e(new Set(t.availableTags.concat(i))).sort()||[]})},getSettings:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r,a,i,c,s,f;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return n="config.plugins.autotimer.",e.next=3,owif.utils.fetchData("/autotimer/get");case 3:for(r=e.sent,a=r.e2settings.e2setting,i=u.elements,a=a.filter(function(e){return e.e2settingname.startsWith(n)}).map(function(e){for(var t=0,r=Object.entries(e);t<r.length;t++){var o=l(r[t],2),a=o[0],i=o[1];e[a.replace("e2setting","")]=i,delete e[a]}return e.name=e.name.replace(n,""),e}),c=0,s=Object.values(a);c<s.length;c++)f=s[c],o(t,i,f.name,f.value);case 8:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),saveSettings:function(){var e=a(regeneratorRuntime.mark(function e(){var t,n,r,o,a,i,c,s,f;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:for(t=new FormData(u),n=0,r=Object.entries(u);n<r.length;n++)o=l(r[n],2),o[0],"checkbox"!==(a=o[1]).type||t.has(a.name)||t.set(a.name,"");return e.prev=3,e.next=6,owif.utils.fetchData("/autotimer/set",{method:"post",body:t});case 6:if(i=e.sent,c=i.e2simplexmlresult,s=c.e2state,f=c.e2statetext,f="".concat(f.charAt(0).toUpperCase()).concat(f.slice(1)),!0!==s&&"true"!==s.toString().toLowerCase()){e.next=14;break}e.next=15;break;case 14:throw new Error(f);case 15:e.next=20;break;case 17:e.prev=17,e.t0=e.catch(3),swal({title:"Oops...",text:e.t0,type:"error",animation:"none"});case 20:case"end":return e.stop()}},e,null,[[3,17]])}));return function(){return e.apply(this,arguments)}}(),preview:function(){var e=a(regeneratorRuntime.mark(function e(){var t,n,r,o,a;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return document.getElementById("at-preview__progress").classList.toggle("hidden",!1),document.getElementById("at-preview__no-results").classList.toggle("hidden",!0),e.next=4,owif.utils.fetchData("/autotimer/test");case 4:t=e.sent,n=t.e2autotimertest,r=n.e2testtimer||[],o=document.getElementById("at-preview__list"),a=document.createElement("tbody"),document.getElementById("at-preview__progress").classList.toggle("hidden",!0),r.forEach(function(e){d(a,e)}),r.length?o.innerHTML=a.cloneNode(!0).innerHTML:document.getElementById("at-preview__no-results").classList.toggle("hidden",!1);case 12:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),prepareChoices:function(){t.allTags=t.allTags.map(function(e){return{value:e,label:e}}),t.autoTimerChoices.tag.setChoices(t.allTags,"value","label",!0),t.autoTimerChoices.bouquets.setChoices(t.availableServices.bouquets,"sRef","name",!0),t.autoTimerChoices.services.setChoices(t.availableServices.channels,"sRef","extendedName",!0)},populateForm:function(){var e=a(regeneratorRuntime.mark(function e(){var n,a,c,u,m,d,v,g,h,y,w,b=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:n=0<b.length&&void 0!==b[0]?b[0]:{},a=i.elements,i.reset(),r(".at__filter__line"),document.getElementById("at__page--list").classList.toggle("hidden",!0),window.scroll({top:0,left:0,behavior:"smooth"}),document.getElementById("at__page--edit").classList.toggle("hidden",!1),n=new f(n),n=s(n),t.prepareChoices(),c=p(t.allLocations);try{for(c.s();!(u=c.n()).done;)m=u.value,(d=document.createElement("option")).appendChild(document.createTextNode(m)),d.value=m,document.querySelector('select[name="location"] optgroup[name="more"').appendChild(d),jQuery("select[name=location]").selectpicker("refresh")}catch(t){c.e(t)}finally{c.f()}for(v=0,g=Object.entries(n);v<g.length;v++)h=l(g[v],2),y=h[0],w=h[1],o(t,a,y,w);t.populateFilters(n.filters);case 14:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),deleteEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:-1!==(n=0<r.length&&void 0!==r[0]?r[0]:-1)&&swal({title:tstr_del_autotimer,type:"warning",showCancelButton:!0,confirmButtonColor:"#dd6b55",confirmButtonText:tstrings_yes_delete,cancelButtonText:tstrings_no_cancel,closeOnConfirm:!0,closeOnCancel:!0,animation:"none"},function(){var e=a(regeneratorRuntime.mark(function e(r){var o,a,i,c;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:if(!r){e.next=12;break}return e.next=3,owif.utils.fetchData("/autotimer/remove?id=".concat(n));case 3:o=e.sent,a=o.e2simplexmlresult,i=a.e2state,c=a.e2statetext,c="".concat(c.charAt(0).toUpperCase()).concat(c.slice(1)),!0===i||"true"===i.toString().toLowerCase()?swal({title:tstrings_deleted,text:c,type:"success",animation:"none"}):swal({title:"Oops...",text:c,type:"error",animation:"none"}),t.populateList(),e.next=13;break;case 12:swal({title:tstrings_cancelled,type:"error",animation:"none"});case 13:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}());case 2:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),disableEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var t=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:0<t.length&&void 0!==t[0]?t[0]:-1,owif.utils.debugLog("disableEntry: id ".concat(entry));case 2:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),createEntry:function(){return t.populateForm()},renameEntry:function(e,n,r){var o=function(){var e=a(regeneratorRuntime.mark(function e(n,r){var o,a,i,c;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,e.next=3,owif.utils.fetchData("/autotimer/change?id=".concat(n,"&name=").concat(r));case 3:if(o=e.sent,a=o.e2simplexmlresult,i=a.e2state,c=a.e2statetext,c="".concat(c.charAt(0).toUpperCase()).concat(c.slice(1)),!0!==i&&"true"!==i.toString().toLowerCase()){e.next=13;break}swal.close(),t.populateList(),e.next=14;break;case 13:throw new Error(c);case 14:e.next=20;break;case 16:e.prev=16,e.t0=e.catch(0),console.log(e.t0),swal({title:"Oops...",text:e.t0.message,type:"error",animation:"none"});case 20:case"end":return e.stop()}},e,null,[[0,16]])}));return function(){return e.apply(this,arguments)}}();r?o(e,r):swal({title:"rename?",text:"subtext",type:"input",showCancelButton:!0,closeOnConfirm:!1,inputValue:n,input:"text",animation:"none"},function(t){t&&t.length&&o(e,t)})},editEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r,o=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:n=0<o.length&&void 0!==o[0]?o[0]:-1,r=window.atList.find(function(e){return e.id==n}),owif.utils.debugLog("editEntry: ".concat(r)),t.populateForm(r);case 4:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),transformFormData:function(){var e=new FormData(i),t=Object.fromEntries(e),n=["title","shortdescription","description","dayofweek","!title","!shortdescription","!description","!dayofweek"],r=n.concat(["offset","services","bouquets","vps_enabled"]),o=["offset","services","bouquets"];return window.disableFilterEditing&&n.forEach(function(t){return e.delete(t)}),["hasMismatchedService","_before","_after","_type","_filterpredicate","_filterwhere"].forEach(function(t){return e.delete(t)}),Object.entries(t).forEach(function(t){var n=l(t,2),r=n[0],a=n[1];owif.utils.debugLog(r,a),o.includes(r)&&e.set(r,e.getAll(r)),""===a||","===a?e.delete(r):owif.utils.regexDateFormat.test(a)&&e.set(r,owif.utils.toUnixDate(a))}),r.forEach(function(t){e.has(t)||e.set(t,"")}),e},saveEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r,o,a,i,c=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return n=0<c.length&&void 0!==c[0]?c[0]:"",e.next=3,owif.utils.fetchData("/autotimer/edit?".concat(n),{method:"post",body:t.transformFormData()});case 3:r=e.sent,o=r.e2simplexmlresult,a=o.e2state,i=o.e2statetext,i="".concat(i.charAt(0).toUpperCase()).concat(i.slice(1)),!0===a||"true"===a.toString().toLowerCase()?t.populateList():swal({title:"Oops...",text:i,type:"error",animation:"none"});case 9:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),cancelEntry:function(){swal({title:"Are you sure you want to discard your changes?",type:"warning",showCancelButton:!0,confirmButtonColor:"#dd6b55",confirmButtonText:tstrings_yes_delete,cancelButtonText:tstrings_no_cancel,closeOnConfirm:!0,closeOnCancel:!0,animation:"none"},function(){var e=a(regeneratorRuntime.mark(function e(n){return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:n&&t.populateList();case 1:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}())},populateFilters:function(e){e.exclude.forEach(function(e){e.predicate="!",e.value=e["_@ttribute"],delete e["_@ttribute"],t.addFilter(e)}),e.include.forEach(function(e){e.predicate="",e.value=e["_@ttribute"],delete e["_@ttribute"],t.addFilter(e)})},addFilter:function(){var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:{predicate:"",where:"title",value:""},n=document.getElementById("autotimer-filter-template").content.firstElementChild.cloneNode(!0),r=document.getElementById("atform__filters-container"),o=n.querySelector('select[name="_filterpredicate"]'),a=n.querySelector('select[name="_filterwhere"]'),i=n.querySelector('input[type="text"]'),c=n.querySelector('select[name="dayofweek"]'),u=function(){"dayofweek"===a.value?(c.name="".concat(o.value).concat(a.value),i.value=""):(i.name="".concat(o.value).concat(a.value),c.value="")};if(n.querySelector('button[name="removeFilter"]').onclick=t.removeFilter,o.onchange=function(){u()},a.onchange=function(e){var t=e.target,n=t.closest("fieldset"),r="dayofweek"===t.value;n.querySelector(".filter-value--dayofweek").classList.toggle("hidden",!r),n.querySelector(".filter-value--text").classList.toggle("hidden",r),u()},o.value=e.predicate,a.value=e.where,"dayofweek"===e.where){selectedOptions=e.value.split(",");var s,l=p(c);try{for(l.s();!(s=l.n()).done;)option=s.value,option.selected=selectedOptions.includes(option.value)}catch(t){l.e(t)}finally{l.f()}a.dispatchEvent(new Event("change"))}else i.value=e.value;u(),r.appendChild(n),jQuery.AdminBSB.select.activate()},removeFilter:function(){event.target.closest("fieldset.at__filter__line").remove()},initEventHandlers:function(){var e=document.createElement("input");(document.querySelector('button[name="reload"]')||e).onclick=t.populateList,(document.querySelector('button[name="process"]')||e).onclick=function(){return window.parseAT()},(document.querySelector('button[name="preview"]')||e).onclick=t.preview,(document.querySelector('button[name="timers"]')||e).onclick=function(){return window.listTimers()},(document.querySelector('button[name="settings"]')||e).onclick=t.getSettings,(document.querySelector('button[name="saveSettings"]')||e).onclick=t.saveSettings,(document.querySelector('a[href="#at/new"]')||e).onclick=function(e){e.preventDefault(),t.createEntry()},(document.querySelector('button[name="addFilter"]')||e).onclick=function(){return t.addFilter()},(document.querySelector('button[name="cancel"]')||e).onclick=t.cancelEntry,(document.querySelector('form[name="atedit"]')||e).onsubmit=function(e){e.preventDefault(),t.saveEntry()},(document.querySelectorAll('input[name="justplay"], input[name="always_zap"]')||e).forEach(function(e){e.onchange=function(){1>document.querySelectorAll('input[name="justplay"]:checked, input[name="always_zap"]:checked').length&&(event.target.checked=!event.target.checked)}}),(document.getElementById("_timespan")||e).onchange=function(e){c(document.getElementById("_timespan_"),!e.target.checked)},(document.getElementById("_datespan")||e).onchange=function(e){c(document.getElementById("_datespan_"),!e.target.checked)},(document.getElementById("_timerOffset")||e).onchange=function(e){c(document.getElementById("_timerOffset_"),!e.target.checked)},(document.querySelector('[name="afterevent"]')||e).onchange=function(e){c(document.getElementById("AftereventE"),!e.target.checked)},(document.getElementById("timeSpanAE")||e).onchange=function(e){c(document.getElementById("timeSpanAEE"),!e.target.checked)},(document.getElementById("_location")||e).onchange=function(e){c(document.getElementById("_location_"),!e.target.checked)},(document.getElementById("beforeevent")||e).onchange=function(e){c(document.getElementById("BeforeeventE"),!e.target.checked)},(document.querySelector('[name="vps_enabled"]')||e).onchange=function(e){c(document.getElementById("vps_enabled_"),!e.target.checked)},(document.querySelector('[name="vps_safemode"]')||e).onchange=function(t){(document.querySelector('[name="vps_overwrite"]')||e).value=t.target.checked?0:1}},init:function(){var e=a(regeneratorRuntime.mark(function e(){return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return t=this,!0,e.next=4,owif.api.getAllServices(!0);case 4:return t.availableServices=e.sent,t.availableLocations=[],e.next=8,owif.api.getTags();case 8:t.availableTags=e.sent,t.autoTimerChoices=owif.gui.preparedChoices(),t.populateList(),t.initEventHandlers(t);case 12:case"end":return e.stop()}},e,this)}));return function(){return e.apply(this,arguments)}}()}}).init()}();
},{}],"CKu5":[function(require,module,exports) {
require("./js/autotimers.js");
},{"./js/autotimers.js":"Tkyz"}]},{},["CKu5"], null)
//# sourceMappingURL=/autotimers-app.js.map