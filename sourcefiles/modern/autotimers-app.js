/*x-eslint-env x-browser*/
/*x-global x-swal*/

//******************************************************************************
//* at.js: openwebif AutoTimer plugin
//* Version 3.0
//******************************************************************************
//* Authors: Web Dev Ben <https://github.com/wedebe>
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************

// for future use (read autotimer.xml into json)
// https://www.npmjs.com/package/xml2json-light-es6module
function xml2json(xmlStr){return xml2jsonRecurse(xmlStr=cleanXML(xmlStr),0)} function xml2jsonRecurse(xmlStr){for(var obj={},tagName,indexClosingTag,inner_substring,tempVal,openingTag;xmlStr.match(/<[^\/][^>]*>/);)tagName=(openingTag=xmlStr.match(/<[^\/][^>]*>/)[0]).substring(1,openingTag.length-1),-1==(indexClosingTag=xmlStr.indexOf(openingTag.replace("<","</")))&&(tagName=openingTag.match(/[^<][\w+$]*/)[0],-1==(indexClosingTag=xmlStr.indexOf("</"+tagName))&&(indexClosingTag=xmlStr.indexOf("<\\/"+tagName))),tempVal=(inner_substring=xmlStr.substring(openingTag.length,indexClosingTag)).match(/<[^\/][^>]*>/)?xml2json(inner_substring):inner_substring,void 0===obj[tagName]?obj[tagName]=tempVal:Array.isArray(obj[tagName])?obj[tagName].push(tempVal):obj[tagName]=[obj[tagName],tempVal],xmlStr=xmlStr.substring(2*openingTag.length+1+inner_substring.length);return obj} function cleanXML(xmlStr){return xmlStr=replaceAttributes(xmlStr=replaceAloneValues(xmlStr=replaceSelfClosingTags(xmlStr=(xmlStr=(xmlStr=(xmlStr=(xmlStr=xmlStr.replace(/<!--[\s\S]*?-->/g,"")).replace(/\n|\t|\r/g,"")).replace(/ {1,}<|\t{1,}</g,"<")).replace(/> {1,}|>\t{1,}/g,">")).replace(/<\?[^>]*\?>/g,""))))} function replaceSelfClosingTags(xmlStr){var selfClosingTags=xmlStr.match(/<[^/][^>]*\/>/g);if(selfClosingTags)for(var i=0;i<selfClosingTags.length;i++){var oldTag=selfClosingTags[i],tempTag=oldTag.substring(0,oldTag.length-2);tempTag+=">";var tagName=oldTag.match(/[^<][\w+$]*/)[0],closingTag="</"+tagName+">",newTag="<"+tagName+">",attrs=tempTag.match(/(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?/g);if(attrs)for(var j=0;j<attrs.length;j++){var attr=attrs[j],attrName=attr.substring(0,attr.indexOf("=")),attrValue;newTag+="<"+attrName+">"+attr.substring(attr.indexOf('"')+1,attr.lastIndexOf('"'))+"</"+attrName+">"}newTag+=closingTag,xmlStr=xmlStr.replace(oldTag,newTag)}return xmlStr} function replaceAloneValues(xmlStr){var tagsWithAttributesAndValue=xmlStr.match(/<[^\/][^>][^<]+\s+.[^<]+[=][^<]+>{1}([^<]+)/g);if(tagsWithAttributesAndValue)for(var i=0;i<tagsWithAttributesAndValue.length;i++){var oldTag=tagsWithAttributesAndValue[i],oldTagName,oldTagValue,newTag=oldTag.substring(0,oldTag.indexOf(">")+1)+"<_@ttribute>"+oldTag.substring(oldTag.indexOf(">")+1)+"</_@ttribute>";xmlStr=xmlStr.replace(oldTag,newTag)}return xmlStr} function replaceAttributes(xmlStr){var tagsWithAttributes=xmlStr.match(/<[^\/][^>][^<]+\s+.[^<]+[=][^<]+>/g);if(tagsWithAttributes)for(var i=0;i<tagsWithAttributes.length;i++){var oldTag=tagsWithAttributes[i],tagName,newTag="<"+oldTag.match(/[^<][\w+$]*/)[0]+">",attrs=oldTag.match(/(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?/g);if(attrs)for(var j=0;j<attrs.length;j++){var attr=attrs[j],attrName=attr.substring(0,attr.indexOf("=")),attrValue;newTag+="<"+attrName+">"+attr.substring(attr.indexOf('"')+1,attr.lastIndexOf('"'))+"</"+attrName+">"}xmlStr=xmlStr.replace(oldTag,newTag)}return xmlStr}

(function () {
  // TODO: move to owif.js utils
	const regexDateFormat = new RegExp(/\d{4}-\d{2}-\d{2}/);

  // TODO: move to owif.js utils
	const debugLog = (...args) => {
    console.debug(...args);
	};

  // TODO: move to owif.js utils
  // convert html date input format (yyyy-mm-dd) to serial
	const toUnixDate = (date) => (Date.parse(`${date}Z`)) / 1000; // Z is intentional

  // TODO: move to owif.js utils
  const apiRequest = async (url, options = { method: 'get', ...{} }) => {
    try {
      const response = await fetch(url, options);

      if (response.ok) {
        const contentType = response.headers.get('content-type');
        debugLog(contentType);
        if (!!contentType && contentType.includes('application/json')) {
          const responseJson = await response.json();
          return responseJson;
        } else {
          // eg. application/xhtml+xml
          const responseText = await response.text();
          return responseText;
        }

      } else {
        throw new Error(response.statusText || response.status);
      }
    } catch (ex) {
      throw new Error(ex);
    };
};

  // TODO: move to owif.js utils
  // 1:134:1 is bouquetroot
  const isBouquet = (sref) => (!sref.startsWith('1:134:1') && sref.includes('FROM BOUQUET'));

  const AutoTimers = function () {
    // keep reference to object.
    let self;

    const atForm = document.getElementById('atform');

    const addDependentSectionTogglers = (data = {}) => {
      // set up show/hide checkboxes
      data['_timespan'] = !!data.timespanFrom || !!data.timespanTo;
      data['_after'] = !!data.after;
      data['_before'] = !!data.before;
      data['_timerOffset'] = !!data.timerOffsetAfter || !!data.timerOffsetBefore;
      data['timeSpanAE'] = !!data.afterevent;
      data['_location'] = !!data.location;
      data['_tags'] = !!(data.Tags && data.Tags.length);
      data['_channels'] = !!(data.Channels && data.Channels.length);
      data['_bouquets'] = !!(data.Bouquets && data.Bouquets.length);

      return data;
    };

    // const transformInputs = (data) => {
    //   CurrentAT.justplay = $('#justplay').val();
    //   if(CurrentAT.justplay=="2")
    //   {
    //     reqs += "&justplay=0&always_zap=1";
    //   }
    //   else
    //     reqs += "&justplay=" + CurrentAT.justplay;
    // };

    const addCell = (rowRef, content ='') => {
      const newCell = rowRef.insertCell();
      newCell.innerHTML = content;
      return newCell;
    };

    const addRow = (tableRef, item) => {
      const newRow = tableRef.insertRow();

      const e2state = item['e2state'];
      const e2stateCell = addCell(newRow, e2state);
      e2stateCell.title = (e2state === 'Skip' ? item['e2message'] : '');

      addCell(newRow, item['e2autotimername']);
      addCell(newRow, item['e2name']);
      addCell(newRow, item['e2servicename']);

      const e2timebegin = item['e2timebegin'];
      const e2timebeginCell = addCell(newRow, owif.utils.getStrftime(e2timebegin));
      e2timebeginCell.style.textAlign = 'right';

      const e2timeend = item['e2timeend'];
      const e2timeendCell = addCell(newRow, owif.utils.getToTimeText(e2timebegin, e2timeend));
      e2timeendCell.style.textAlign = 'right';
    };

    return {
      getAll: async () => {
        const responseContent = await apiRequest('/autotimer');
        const data = xml2json(responseContent)['autotimer'];

console.log('response: ', data);
// console.log('defaults: ', data['default']);
// console.log('timer: ', data['timer']);
window.atList = data['timer'] || [];
if (!Array.isArray(window.atList)) {
  window.atList = [data['timer']];
}

aem = {
  'shutdown': 'deepstandby',
}

        window.atList.map((ati) => {
          if (ati['from']) {
            ati['timespanFrom'] = ati['from'];
          }
          if (ati['to']) {
            ati['timespanTo'] = ati['to'];
          }
          if (ati['after']) {
            const afterDate = new Date(parseInt(ati['after']) * 1000);
            ati['after'] = afterDate.toISOString().split('T')[0];
          }
          if (ati['before']) {
            const beforeDate = new Date(parseInt(ati['before']) * 1000);
            ati['before'] = beforeDate.toISOString().split('T')[0];
          }
          // if (!!ati['offset']) {
          //   ati['offset'].split(',');
          // }
          if (!!ati['afterevent']) {
            ati['afterevent']['from'] && (ati['aftereventFrom'] = ati['afterevent']['from']);
            ati['afterevent']['to'] && (ati['aftereventTo'] = ati['afterevent']['to']);
            ati['afterevent'] = aem[ati['afterevent']['_@ttribute']] || ati['afterevent']['_@ttribute'] || aem[ati['afterevent']] || ati['afterevent'];
          }
          if (ati['e2service'] && ati['e2service'].length) {
            ati['Bouquets'] = [];
            ati['Channels'] = [];
            (ati['e2service'] || []).forEach(function (service, index) {
              const bouquetsOrChannels = (isBouquet(service['e2servicereference'])) ? 'Bouquets' : 'Channels';
              ati[bouquetsOrChannels].push(service['e2servicereference']);
            });
          }
          return ati;
        });

        return window.atList;
      },

      populateList: () => {
        document.getElementById('at__edit').classList.toggle('hidden', true);
        window.scroll({top: 0, left: 0, behavior: 'smooth'});
        const listEl = document.getElementById('at__list');
        listEl.innerHTML = "";
        document.getElementById('at__foo').classList.toggle('hidden', false);
        const templateEl = document.getElementById('autotimer-item-template');
        self.getAll()
          .then(jsonResponse => {
            jsonResponse.forEach((atItem, index) => {
              const searchType = valueLabelMap.autoTimers.searchType[atItem['searchType']] || '';
              const newNode = templateEl.content.firstElementChild.cloneNode(true);
              const editEl = newNode.querySelector('a[href="#at/edit/{{id}}"]');
              newNode.dataset['atId'] = `${atItem['id']}`;
              // newNode.onclick = (evt) => {
              //   (evt || window.event).stopPropogation();
              //   self.editEntry(atItem['id']);
              // }
              editEl.href = editEl.href.replace('{{id}}', atItem['id']);
              editEl.onclick = (evt) => {
                self.editEntry(atItem['id']);
                return false;
              }
              // newNode.querySelector('button[name="disable"]').onclick = (evt) => self.disableEntry(atItem['id']);
              newNode.querySelector('button[name="delete"]').onclick = (evt) => self.deleteEntry(atItem['id']);
              newNode.querySelector('slot[name="autotimer-name"]').innerHTML = atItem['name'];
              newNode.querySelector('slot[name="autotimer-searchType"]').innerHTML = (searchType) ? `${searchType}:` : '';
              newNode.querySelector('slot[name="autotimer-match"]').innerHTML = atItem['match'];

              listEl.appendChild(newNode);
            });
          });
      },

      getSettings: async () => {
        return await apiRequest('/autotimer/get');
      },

      saveSettings: async (params) => {
        return await apiRequest(`/autotimer/set?${params}`);
      },

      preview: async () => {
        document.getElementById('at-preview__progress').classList.toggle('hidden', false);
        document.getElementById('at-preview__no-results').classList.toggle('hidden', true);
        const responseContent = await apiRequest('/autotimer/test');
        const data = xml2json(responseContent)['e2autotimertest'];
        const autotimers = data['e2testtimer'] || [];
        const previewTbodyEl = document.getElementById('at-preview__list');
        const newNode = document.createElement('tbody');
        document.getElementById('at-preview__progress').classList.toggle('hidden', true);
        autotimers.forEach((autotimer) => {
          addRow(newNode, autotimer);
        });
        if (autotimers.length) {
          previewTbodyEl.innerHTML = newNode.cloneNode(true).innerHTML;
        } else {
          document.getElementById('at-preview__no-results').classList.toggle('hidden', false);
        }
      },

      populateForm: (data) => {
        const allChannels = autoTimerOptions['channels']['_currentState']['choices'];
        const allBouquets = autoTimerOptions['bouquets']['_currentState']['choices'];

        const { elements } = atForm;
        document.getElementById('at__foo').classList.toggle('hidden', true);
        atForm.reset();
        window.scroll({top: 0, left: 0, behavior: 'smooth'});
        document.getElementById('at__edit').classList.toggle('hidden', false);

        /**
e2tags -> tags
e2service{
  e2servicename
  e2servicereference
}
always_zap
from
to
         **/

        data = addDependentSectionTogglers(data);

        for (let [key, value] of Object.entries(data)) {
          const field = elements.namedItem(key);
          if (field) {
            debugLog(`[${field.type}]`, key, value);
            switch (field.type) {
              case 'checkbox':
                field.checked = value;
                break;
              default:
                field.value = value;
                break;
            }
            try {
              field.dispatchEvent(new Event('change'));
            } catch(ex) {
console.log(field, ex);
            }
          } else {
            debugLog('%c[N/A]', 'color: red', key, value);
          }
        }
        let tagOpts = [];
        try {
          tagOpts = window.tagList.map(function (item) {
            let allTags = autoTimerOptions['tags']['_currentState']['choices'];
            let isFound = false;
            allTags.forEach(function (tg) {
              if (item === tg.value) {
                isFound = true;
              }
            });
            return (isFound) ? false : {
              value: item,
              label: item,
            }
          });
          tagOpts.push(data.Tags);
        } catch(e) {
          console.debug('Failed to process tag options');
        }

        // autoTimerOptions['tags']
        //   .setChoices(tagOpts, 'value', 'label', false)
        //   .removeActiveItems()
        //   .setChoiceByValue(data.Tags);

        autoTimerOptions['channels']
          .setChoices(allChannels, 'value', 'label', false)
          .removeActiveItems()
          .setChoiceByValue(data.Channels);

        autoTimerOptions['bouquets']
          .setChoices(allBouquets, 'value', 'label', false)
          .removeActiveItems()
          .setChoiceByValue(data.Bouquets);
      },

      // .then(response => response.formData())

      deleteEntry: async (atId = -1) => {
        (atId !== -1) && swal({
          title: tstr_del_autotimer,
          text: 'CurrentAT.name',
          type: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#dd6b55',
          confirmButtonText: tstrings_yes_delete,
          cancelButtonText: tstrings_no_cancel,
          closeOnConfirm: true,
          closeOnCancel: true,
          animation: 'none',
        }, async (userConfirmed) => {
          if (userConfirmed) {
            // TODO: parse response
            const xml = await apiRequest(`/autotimer/remove?id=${atId}`)
            var state=$(xml).find("e2state").first();
            var txt=$(xml).find("e2statetext").first();

            swal(state.text(), txt.text(), 'error');

            self.populateList();
          } else {
            swal(tstrings_cancelled, 'CurrentAT.name', 'error');
          }
        });
      },

      disableEntry: async (atId = -1) => {
        console.log(`Disable AT with ID ${atId}`);
      },

      editEntry: async (atId = -1) => {
        const entry = window.atList.find(autotimer => autotimer['id'] == atId);
        self.populateForm(entry);
      },

      saveEntry: (extraParams = '') => {
        const formData = new FormData(atForm);
        const formDataObj = Object.fromEntries(formData);

        Object.entries(formDataObj).forEach(([name, value]) => {
          debugLog(name, value);
          if (name === 'id' && value === '') {
            // remove empty value (empty id causes server error, but missing id does not)
            formData.delete(name); // TODO: check iOS compatibility
          } else if (regexDateFormat.test(value)) {
            formData.set(name, toUnixDate(value));
          } else if (name !== 'tag') {
            // join multiple param= values into an array
            formData.set(name, formData.getAll(name));
          }
        });

        apiRequest(`/autotimer/edit?${extraParams}`, { method: 'post', body: formData })
          .then(responseText => {
            const responseXml = new DOMParser().parseFromString(responseText, 'application/xml');
            const status = responseXml.getElementsByTagName('e2state')[0].textContent || '';
            const message = responseXml.getElementsByTagName('e2statetext')[0].textContent || '';

            if (status === true || status.toString().toLowerCase() === 'true') {
              swal({
                title: message,
                text: '',
                type: 'success',
                animation: 'none',
              });
            } else {
              throw new Error(message);
            }
          })
          .catch((ex) => {
            let message = ex.message;
            message = message.charAt(0).toUpperCase() + message.slice(1);
            swal({
              title: message,
              text: '',
              type: 'error',
              animation: 'none',
            });
          });
      },

      initEventHandlers: () => {
        // create a failsafe element to assign event handlers to
        let nullEl = document.createElement('input');

        (document.getElementById('atform') || nullEl).onsubmit = () => {
          window.saveAT();
          return false;
        }
        (document.querySelector('button[name="cancel"]') || nullEl).onclick = self.populateList;
        (document.querySelector('button[name="create"]') || nullEl).onclick = () => window.addAT();
        (document.querySelector('button[name="reload"]') || nullEl).onclick = self.populateList;
        (document.querySelector('button[name="process"]') || nullEl).onclick = () => window.parseAT();
        (document.querySelector('button[name="preview"]') || nullEl).onclick = self.preview;
        (document.querySelector('button[name="timers"]') || nullEl).onclick = () => window.listTimers();
        (document.querySelector('button[name="settings"]') || nullEl).onclick = () => window.getAutoTimerSettings();
        (document.querySelector('button[name="addFilter"]') || nullEl).onclick = () => window.AddFilter('', '', '');

        (document.getElementById('_timespan') || nullEl).onchange = (input) => {
          document.getElementById('timeSpanE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_after') || nullEl).onchange = (input) => {
          document.getElementById('timeFrameE').classList.toggle('dependent-section', !input.target.checked);
          // document.getElementById('timeFrameAfterCheckBox').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_before') || nullEl).onchange = (input) => {
          document.getElementById('beforeE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_timerOffset') || nullEl).onchange = (input) => {
          document.getElementById('timerOffsetE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.querySelector('[name="afterevent"]') || nullEl).onchange = (input) => {
          document.getElementById('AftereventE').classList.toggle('dependent-section', !input.target.value);
        };
        (document.getElementById('timeSpanAE') || nullEl).onchange = (input) => {
          document.getElementById('timeSpanAEE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_location') || nullEl).onchange = (input) => {
          document.getElementById('LocationE').classList.toggle('dependent-section', !input.target.checked);
        };
        (document.getElementById('_tags') || nullEl).onchange = (input) => {
          document.getElementById('TagsE').classList.toggle('dependent-section', !input.target.checked);
          // if (!input.target.checked) {
          //   try {
          //     autoTimerOptions['tags'].removeActiveItems();
          //   } catch(e){}
          // }
        };
        (document.getElementById('_bouquets') || nullEl).onchange = (input) => {
          document.getElementById('BouquetsE').classList.toggle('dependent-section', !input.target.checked);
          // if (!input.target.checked) {
          //   try {
          //     autoTimerOptions['bouquets'].removeActiveItems();
          //   } catch(e){}
          // }
        };
        (document.getElementById('_channels') || nullEl).onchange = (input) => {
          document.getElementById('ChannelsE').classList.toggle('dependent-section', !input.target.checked);
          // if (!input.target.checked) {
          //   try {
          //     autoTimerOptions['channels'].removeActiveItems();
          //   } catch(e){}
          // }
        };
        (document.getElementById('beforeevent') || nullEl).onchange = (input) => {
          document.getElementById('BeforeeventE').toggle(!!input.target.value);
        };
        (document.getElementById('afterevent') || nullEl).onchange = (input) => {
          // document.getElementById('AftereventE').toggle(!!input.target.value);
        };
        (document.getElementById('counter') || nullEl).onchange = (input) => {
          //document.getElementById('CounterE').toggle(!!input.target.value);
        };
        (document.getElementById('vps') || nullEl).onchange = (input) => {
          document.getElementById('vpsE').classList.toggle('dependent-section', !input.target.checked);
        };

        nullEl = null;
      },

      init: function () {
        self = this;

        self.populateList(); //check if we've got data to add a new AT with
        self.initEventHandlers(self);
      },
    };
  };

  window.autoTimers = new AutoTimers();
  window.autoTimers.init();
})();
