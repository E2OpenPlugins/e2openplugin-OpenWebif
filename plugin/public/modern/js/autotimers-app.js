parcelRequire=function(e,r,t,n){var i,o="function"==typeof parcelRequire&&parcelRequire,u="function"==typeof require&&require;function f(t,n){if(!r[t]){if(!e[t]){var i="function"==typeof parcelRequire&&parcelRequire;if(!n&&i)return i(t,!0);if(o)return o(t,!0);if(u&&"string"==typeof t)return u(t);var c=new Error("Cannot find module '"+t+"'");throw c.code="MODULE_NOT_FOUND",c}p.resolve=function(r){return e[t][1][r]||r},p.cache={};var l=r[t]=new f.Module(t);e[t][0].call(l.exports,p,l,l.exports,this)}return r[t].exports;function p(e){return f(p.resolve(e))}}f.isParcelRequire=!0,f.Module=function(e){this.id=e,this.bundle=f,this.exports={}},f.modules=e,f.cache=r,f.parent=o,f.register=function(r,t){e[r]=[function(e,r){r.exports=t},{}]};for(var c=0;c<t.length;c++)try{f(t[c])}catch(e){i||(i=e)}if(t.length){var l=f(t[t.length-1]);"object"==typeof exports&&"undefined"!=typeof module?module.exports=l:"function"==typeof define&&define.amd?define(function(){return l}):n&&(this[n]=l)}if(parcelRequire=f,i)throw i;return f}({"Tkyz":[function(require,module,exports) {
function e(e){return r(e)||n(e)||p(e)||t()}function t(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}function n(e){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e))return Array.from(e)}function r(e){if(Array.isArray(e))return g(e)}function o(e,t,n,r,o,a,i){try{var c=e[a](i),u=c.value}catch(e){return void n(e)}c.done?t(u):Promise.resolve(u).then(r,o)}function a(e){return function(){var t=this,n=arguments;return new Promise(function(r,a){function i(e){o(u,r,a,i,c,"next",e)}function c(e){o(u,r,a,i,c,"throw",e)}var u=e.apply(t,n);i(void 0)})}}function i(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function c(e,t){for(var n,r=0;r<t.length;r++)(n=t[r]).enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}function u(e,t,n){return t&&c(e.prototype,t),n&&c(e,n),e}function s(e,t){return m(e)||f(e,t)||p(e,t)||l()}function l(){throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}function f(e,t){if("undefined"!=typeof Symbol&&Symbol.iterator in Object(e)){var n=[],r=!0,o=!1,a=void 0;try{for(var i,c=e[Symbol.iterator]();!(r=(i=c.next()).done)&&(n.push(i.value),!t||n.length!==t);r=!0);}catch(e){o=!0,a=e}finally{try{r||null==c.return||c.return()}finally{if(o)throw a}}return n}}function m(e){if(Array.isArray(e))return e}function d(e,t){var n;if("undefined"==typeof Symbol||null==e[Symbol.iterator]){if(Array.isArray(e)||(n=p(e))||t&&e&&"number"==typeof e.length){n&&(e=n);var r=0,o=function(){};return{s:o,n:function(){return r>=e.length?{done:!0}:{done:!1,value:e[r++]}},e:function(e){throw e},f:o}}throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}var a=!0,i=!1;return{s:function(){n=e[Symbol.iterator]()},n:function(){var e=n.next();return a=e.done,e},e:function(e){i=!0,e},f:function e(){try{a||null==n.return||n.return()}finally{if(i)throw e}}}}function p(e,t){if(e){if("string"==typeof e)return g(e,t);var n=Object.prototype.toString.call(e).slice(8,-1);return"Object"===n&&e.constructor&&(n=e.constructor.name),"Map"===n||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?g(e,t):void 0}}function g(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=Array(t);n<t;n++)r[n]=e[n];return r}!function(){function t(){var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:"",t=document.createElement("textarea");return t.innerHTML=e,t.value}function n(e){document.querySelectorAll(e).forEach(function(e){e.remove()})}function r(e,t,n,r){var o=t.namedItem(n);if(o)if(owif.utils.debugLog("[".concat(o.type,"]"),o,n,r),o instanceof RadioNodeList){var a,i=r.split(","),c=d(o.entries());try{for(c.s();!(a=c.n()).done;){var u=s(a.value,2),l=u[0],f=u[1];f.value=i[l]||"";try{f.dispatchEvent(new Event("change"))}catch(e){owif.utils.debugLog(n,r,e)}}}catch(e){c.e(e)}finally{c.f()}}else{switch(o.type){case"checkbox":r=!0===r||"True"===r||r.toString()===o.value,o.checked=r;break;case"select-multiple":try{var m=r.map(function(e){return e.sRef});e.autoTimerChoices[n].setChoices(r,"sRef","name",!1).setChoices(r,"label","value",!1).removeActiveItems().setChoiceByValue(r).setChoiceByValue(m)}catch(e){owif.utils.debugLog(n,r,e)}break;default:o.value=r}try{o.dispatchEvent(new Event("change"))}catch(e){owif.utils.debugLog(n,r,e)}}else owif.utils.debugLog("%c[N/A]","color: red",n,r)}var o=function(){function e(n){i(this,e);var r=this;if(Object.assign(r,n),r.name=t(r.name),r.match=t(r.match),r.tag=[],r.bouquets=[],r.services=[],r.filters={include:[],exclude:[]},r.enabled="yes"===r.enabled?1:0,r.from&&(r.timespanFrom=r.from,delete r.from),r.to&&(r.timespanTo=r.to,delete r.to),r.after){var o=new Date(1e3*parseInt(r.after));r.after=o.toISOString().split("T")[0]}if(r.before){var a=new Date(1e3*parseInt(r.before));r.before=a.toISOString().split("T")[0]}if(r.afterevent){var c=r.afterevent.from,u=r.afterevent.to,s=r.afterevent["_@ttribute"];c&&(r.aftereventFrom=c),u&&(r.aftereventTo=u),s&&(r.afterevent={shutdown:"deepstandby"}[s]||s)}if(r.e2service){Array.isArray(r.e2service)||(r.e2service=[r.e2service]);var l=!1;r.e2service.forEach(function(e){var t=owif.utils.isBouquet(e.e2servicereference)?"bouquets":"services";r[t].push({sRef:e.e2servicereference,name:e.e2servicename,selected:!0}),l=!e.e2servicename}),r.hasMismatchedService=l,delete r.e2service}r.e2tag&&(!Array.isArray(r.e2tag)&&(r.e2tag=[r.e2tag]),r.tag=r.e2tag,delete r.e2tag),!r.tag&&r.e2tags&&(r.tag=r.e2tags.split(" "),delete r.e2tags),r.include&&(!Array.isArray(r.include)&&(r.include=[r.include]),r.filters.include=r.include,delete r.include),r.exclude&&(!Array.isArray(r.exclude)&&(r.exclude=[r.exclude]),r.filters.exclude=r.exclude,delete r.exclude)}return u(e,[{key:"bouquetSRefs",get:function(){return this.bouquets.map(function(e){return e.sRef})}},{key:"bouquetNames",get:function(){return this.bouquets.map(function(e){return e.name})}},{key:"channelSRefs",get:function(){return this.services.map(function(e){return e.sRef})}},{key:"channelNames",get:function(){return this.services.map(function(e){return e.name})}}]),e}();(new function(){var t,i=document.querySelector('form[name="atedit"]'),c=document.querySelector('form[name="atsettings"]'),u=function(){var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:{};return e._timespan=!!e.timespanFrom||!!e.timespanTo,e._after=!!e.after,e._before=!!e.before,e._timerOffset=!!e.offset,e.timeSpanAE=!!e.afterevent,e._location=!!e.location,e},l=function(e){var t=1<arguments.length&&void 0!==arguments[1]?arguments[1]:"",n=e.insertCell();return n.innerHTML=t,n},f=function(e,t){var n=e.insertRow(),r=t.e2state;l(n,r).title="Skip"===r?t.e2message:"",l(n,t.e2autotimername),l(n,t.e2name),l(n,t.e2servicename);var o=t.e2timebegin;l(n,owif.utils.getStrftime(o)).style.textAlign="right";var a=t.e2timeend;l(n,owif.utils.getToTimeText(o,a)).style.textAlign="right"};return{getAll:function(){var e=a(regeneratorRuntime.mark(function e(){var t,n;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,owif.utils.fetchData("/autotimer");case 2:return t=e.sent,n=xml2json(t).autotimer,window.atList=n.timer||[],Array.isArray(window.atList)||(window.atList=[n.timer]),window.atList.map(function(e){return new o(e)}),e.abrupt("return",window.atList);case 8:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),populateList:function(){var r=document.getElementById("at__list");n(".at__item"),document.getElementById("at__page--edit").classList.toggle("hidden",!0),window.scroll({top:0,left:0,behavior:"smooth"}),document.getElementById("at__page--list").classList.toggle("hidden",!1);var a=document.getElementById("autotimer-list-item-template"),i=[],c=[];t.getAll().then(function(n){n.forEach(function(e){(e=new o(e)).location&&i.push(e.location),c=c.concat(e.tag);var n=valueLabelMap.autoTimers.searchType[e.searchType]||"",u=a.content.firstElementChild.cloneNode(!0),s=u.querySelector('a[href="#at/edit/{{id}}"]');s.href=s.href.replace("{{id}}",e.id),s.onclick=function(){return t.editEntry(e.id),!1},u.querySelector('button[name="delete"]').onclick=function(){return t.deleteEntry(e.id)},u.querySelector('slot[name="autotimer-name"]').innerHTML=e.name,u.querySelector('slot[name="autotimer-searchType"]').innerHTML=n?"".concat(n,":"):"",e.timespanFrom&&(u.querySelector('slot[name="autotimer-timespan"]').innerHTML="~ ".concat(e.timespanFrom||""," - ").concat(e.timespanTo||"")),u.querySelector('slot[name="autotimer-channels"]').innerHTML=e.channelNames.join(", "),e.bouquetNames.length&&(u.querySelector('slot[name="autotimer-bouquets"]').innerHTML="<br> ".concat(e.bouquetNames.join(", "))),u.querySelector('slot[name="autotimer-match"]').innerHTML='"'.concat(e.match,'"'),r.appendChild(u)}),t.allLocations=e(new Set(t.availableLocations.concat(i))).sort()||[],t.allTags=e(new Set(t.availableTags.concat(c))).sort()||[]})},getSettings:function(){var e=a(regeneratorRuntime.mark(function e(){var n,o,a,i,u,l,f;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return n="config.plugins.autotimer.",e.next=3,owif.utils.fetchData("/autotimer/get");case 3:for(o=e.sent,a=xml2json(o).e2settings.e2setting,i=c.elements,a=a.filter(function(e){return e.e2settingname.startsWith(n)}).map(function(e){for(var t=0,r=Object.entries(e);t<r.length;t++){var o=s(r[t],2),a=o[0],i=o[1];e[a.replace("e2setting","")]=i,delete e[a]}return e.name=e.name.replace(n,""),e}),u=0,l=Object.values(a);u<l.length;u++)f=l[u],r(t,i,f.name,f.value);case 8:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),saveSettings:function(){var e=a(regeneratorRuntime.mark(function e(){var t,n,r,o,a,i,u,l,f;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:for(t=new FormData(c),n=0,r=Object.entries(c);n<r.length;n++)o=s(r[n],2),o[0],"checkbox"!==(a=o[1]).type||t.has(a.name)||t.set(a.name,"");return e.prev=3,e.next=6,owif.utils.fetchData("/autotimer/set",{method:"post",body:t});case 6:if(i=e.sent,u=xml2json(i).e2simplexmlresult,l=u.e2state,f=u.e2statetext,f="".concat(f.charAt(0).toUpperCase()).concat(f.slice(1)),!0!==l&&"true"!==l.toString().toLowerCase()){e.next=14;break}e.next=15;break;case 14:throw new Error(f);case 15:e.next=20;break;case 17:e.prev=17,e.t0=e.catch(3),swal({title:"Oops...",text:e.t0,type:"error",animation:"none"});case 20:case"end":return e.stop()}},e,null,[[3,17]])}));return function(){return e.apply(this,arguments)}}(),preview:function(){var e=a(regeneratorRuntime.mark(function e(){var t,n,r,o,a;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return document.getElementById("at-preview__progress").classList.toggle("hidden",!1),document.getElementById("at-preview__no-results").classList.toggle("hidden",!0),e.next=4,owif.utils.fetchData("/autotimer/test");case 4:t=e.sent,n=xml2json(t).e2autotimertest,r=n.e2testtimer||[],o=document.getElementById("at-preview__list"),a=document.createElement("tbody"),document.getElementById("at-preview__progress").classList.toggle("hidden",!0),r.forEach(function(e){f(a,e)}),r.length?o.innerHTML=a.cloneNode(!0).innerHTML:document.getElementById("at-preview__no-results").classList.toggle("hidden",!1);case 12:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),prepareChoices:function(){t.allTags=t.allTags.map(function(e){return{value:e,label:e}}),t.autoTimerChoices.tag.setChoices(t.allTags,"value","label",!0),t.autoTimerChoices.bouquets.setChoices(t.availableServices.bouquets,"sRef","name",!0),t.autoTimerChoices.services.setChoices(t.availableServices.channels,"sRef","extendedName",!0)},populateForm:function(){var e=a(regeneratorRuntime.mark(function e(){var a,c,l,f,m,p,g,v,h,y,w,b=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:a=0<b.length&&void 0!==b[0]?b[0]:{},c=i.elements,i.reset(),n(".at__filter__line"),document.getElementById("at__page--list").classList.toggle("hidden",!0),window.scroll({top:0,left:0,behavior:"smooth"}),document.getElementById("at__page--edit").classList.toggle("hidden",!1),a=new o(a),a=u(a),t.prepareChoices(),l=d(t.allLocations);try{for(l.s();!(f=l.n()).done;)m=f.value,(p=document.createElement("option")).appendChild(document.createTextNode(m)),p.value=m,document.querySelector('select[name="location"] optgroup[name="more"').appendChild(p),jQuery("select[name=location]").selectpicker("refresh")}catch(t){l.e(t)}finally{l.f()}for(g=0,v=Object.entries(a);g<v.length;g++)h=s(v[g],2),y=h[0],w=h[1],r(t,c,y,w);t.populateFilters(a.filters);case 14:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),deleteEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:-1!==(n=0<r.length&&void 0!==r[0]?r[0]:-1)&&swal({title:tstr_del_autotimer,type:"warning",showCancelButton:!0,confirmButtonColor:"#dd6b55",confirmButtonText:tstrings_yes_delete,cancelButtonText:tstrings_no_cancel,closeOnConfirm:!0,closeOnCancel:!0,animation:"none"},function(){var e=a(regeneratorRuntime.mark(function e(r){var o,a,i,c;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:if(!r){e.next=12;break}return e.next=3,owif.utils.fetchData("/autotimer/remove?id=".concat(n));case 3:o=e.sent,a=xml2json(o).e2simplexmlresult,i=a.e2state,c=a.e2statetext,c="".concat(c.charAt(0).toUpperCase()).concat(c.slice(1)),!0===i||"true"===i.toString().toLowerCase()?swal({title:tstrings_deleted,text:c,type:"success",animation:"none"}):swal({title:"Oops...",text:c,type:"error",animation:"none"}),t.populateList(),e.next=13;break;case 12:swal({title:tstrings_cancelled,type:"error",animation:"none"});case 13:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}());case 2:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),disableEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var t=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:0<t.length&&void 0!==t[0]?t[0]:-1,owif.utils.debugLog("disableEntry: id ".concat(entry));case 2:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),createEntry:function(){return t.populateForm()},editEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r,o=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:n=0<o.length&&void 0!==o[0]?o[0]:-1,r=window.atList.find(function(e){return e.id==n}),owif.utils.debugLog("editEntry: ".concat(r)),t.populateForm(r);case 4:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),saveEntry:function(){var e=a(regeneratorRuntime.mark(function e(){var n,r,o,a,c,u,l,f=arguments;return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return n=0<f.length&&void 0!==f[0]?f[0]:"",r=new FormData(i),o=Object.fromEntries(r),window.disableFilterEditing&&["title","shortdescription","description","dayofweek","!title","!shortdescription","!description","!dayofweek"].forEach(function(e){r.delete(e)}),["_filterpredicate","_filterwhere"].forEach(function(e){r.delete(e)}),Object.entries(o).forEach(function(e){var t=s(e,2),n=t[0],o=t[1];owif.utils.debugLog(n,o),["offset","services","bouquets"].includes(n)&&r.set(n,r.getAll(n)),""===o||","===o?r.delete(n):owif.utils.regexDateFormat.test(o)&&r.set(n,owif.utils.toUnixDate(o))}),["offset","services","bouquets"].forEach(function(e){r.has(e)||r.set(e,"")}),e.next=9,owif.utils.fetchData("/autotimer/edit?".concat(n),{method:"post",body:r});case 9:a=e.sent,c=xml2json(a).e2simplexmlresult,u=c.e2state,l=c.e2statetext,l="".concat(l.charAt(0).toUpperCase()).concat(l.slice(1)),!0===u||"true"===u.toString().toLowerCase()?t.populateList():swal({title:"Oops...",text:l,type:"error",animation:"none"});case 15:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}(),cancelEntry:function(){swal({title:"Are you sure you want to discard your changes?",type:"warning",showCancelButton:!0,confirmButtonColor:"#dd6b55",confirmButtonText:tstrings_yes_delete,cancelButtonText:tstrings_no_cancel,closeOnConfirm:!0,closeOnCancel:!0,animation:"none"},function(){var e=a(regeneratorRuntime.mark(function e(n){return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:n&&t.populateList();case 1:case"end":return e.stop()}},e)}));return function(){return e.apply(this,arguments)}}())},populateFilters:function(e){e.exclude.forEach(function(e){e.predicate="!",e.value=e["_@ttribute"],delete e["_@ttribute"],t.addFilter(e)}),e.include.forEach(function(e){e.predicate="",e.value=e["_@ttribute"],delete e["_@ttribute"],t.addFilter(e)})},addFilter:function(){var e=0<arguments.length&&void 0!==arguments[0]?arguments[0]:{predicate:"",where:"title",value:""},n=document.getElementById("autotimer-filter-template").content.firstElementChild.cloneNode(!0),r=document.getElementById("foo"),o=n.querySelector('select[name="_filterpredicate"]'),a=n.querySelector('select[name="_filterwhere"]'),i=n.querySelector('input[type="text"]'),c=n.querySelector('select[name="dayofweek"]'),u=function(){"dayofweek"===a.value?(c.name="".concat(o.value).concat(a.value),i.value=""):(i.name="".concat(o.value).concat(a.value),c.value="")};if(n.querySelector('button[name="removeFilter"]').onclick=t.removeFilter,o.onchange=function(){u()},a.onchange=function(e){var t=e.target,n=t.closest("fieldset"),r="dayofweek"===t.value;n.querySelector(".filter-value--dayofweek").classList.toggle("hidden",!r),n.querySelector(".filter-value--text").classList.toggle("hidden",r),u()},o.value=e.predicate,a.value=e.where,"dayofweek"===e.where){selectedOptions=e.value.split(",");var s,l=d(c);try{for(l.s();!(s=l.n()).done;)option=s.value,option.selected=selectedOptions.includes(option.value)}catch(t){l.e(t)}finally{l.f()}a.dispatchEvent(new Event("change"))}else i.value=e.value;u(),r.appendChild(n),jQuery.AdminBSB.select.activate()},removeFilter:function(){event.target.closest("fieldset.at__filter__line").remove()},initEventHandlers:function(){var e=document.createElement("input");(document.querySelector('form[name="atedit"]')||e).onsubmit=function(e){e.preventDefault(),t.saveEntry()},(document.querySelector('button[name="create"]')||e).onclick=t.createEntry,(document.querySelector('a[href="#at/new"]')||e).onclick=function(e){e.preventDefault(),t.createEntry()},(document.querySelector('button[name="reload"]')||e).onclick=t.populateList,(document.querySelector('button[name="process"]')||e).onclick=function(){return window.parseAT()},(document.querySelector('button[name="preview"]')||e).onclick=t.preview,(document.querySelector('button[name="timers"]')||e).onclick=function(){return window.listTimers()},(document.querySelector('button[name="settings"]')||e).onclick=t.getSettings,(document.querySelector('button[name="saveSettings"]')||e).onclick=t.saveSettings,(document.querySelector('button[name="addFilter"]')||e).onclick=function(){return t.addFilter()},(document.querySelector('button[name="cancel"]')||e).onclick=t.cancelEntry,(document.getElementById("_timespan")||e).onchange=function(e){document.getElementById("timeSpanE").classList.toggle("dependent-section",!e.target.checked)},(document.getElementById("_after")||e).onchange=function(e){document.getElementById("timeFrameE").classList.toggle("dependent-section",!e.target.checked)},(document.getElementById("_before")||e).onchange=function(e){document.getElementById("beforeE").classList.toggle("dependent-section",!e.target.checked)},(document.getElementById("_timerOffset")||e).onchange=function(e){document.getElementById("timerOffsetE").classList.toggle("dependent-section",!e.target.checked)},(document.querySelector('[name="afterevent"]')||e).onchange=function(e){document.getElementById("AftereventE").classList.toggle("dependent-section",!e.target.value)},(document.getElementById("timeSpanAE")||e).onchange=function(e){document.getElementById("timeSpanAEE").classList.toggle("dependent-section",!e.target.checked)},(document.getElementById("_location")||e).onchange=function(e){document.getElementById("LocationE").classList.toggle("dependent-section",!e.target.checked)},(document.getElementById("beforeevent")||e).onchange=function(e){document.getElementById("BeforeeventE").toggle(!!e.target.value)},(document.getElementById("afterevent")||e).onchange=function(){},(document.getElementById("counter")||e).onchange=function(){},(document.getElementById("vps")||e).onchange=function(e){document.getElementById("vpsE").classList.toggle("dependent-section",!e.target.checked)},e=null},init:function(){var e=a(regeneratorRuntime.mark(function e(){return regeneratorRuntime.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return t=this,!0,e.next=4,owif.api.getAllServices(!0);case 4:return t.availableServices=e.sent,t.availableLocations=[],e.next=8,owif.api.getTags();case 8:t.availableTags=e.sent,t.autoTimerChoices=owif.gui.preparedChoices(),t.populateList(),t.initEventHandlers(t);case 12:case"end":return e.stop()}},e,this)}));return function(){return e.apply(this,arguments)}}()}}).init()}();
},{}],"CKu5":[function(require,module,exports) {
require("./js/autotimers.js");
},{"./js/autotimers.js":"Tkyz"}]},{},["CKu5"], null)
//# sourceMappingURL=/autotimers-app.js.map