/*x-eslint-env x-browser*/
/*x-global x-swal*/

/**
 * --------------------------------------------------------------------------
 * AutoTimers plugin for OpenWebif
 * @version 3.0
 * @license GPL-3
 * https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
 * 
 * @see https://github.com/oe-alliance/enigma2-plugins/tree/master/autotimer
 * --------------------------------------------------------------------------
 * 
 * @author Web Dev Ben <https://github.com/wedebe>; 2020, 2021
 * @contributors 
 * 
 * 3.0 - complete overhaul
 * 
 * @todo fix tag population
 * @todo fix offset population
 * @todo write filtering
 * @todo write get/set settings
 * @todo fix zap/rec/zaprec
 * @todo fix vps etc.
 * @todo JSDoc https://jsdoc.app/index.html
 * --------------------------------------------------------------------------
 */

//******************************************************************************
//* at.js: openwebif AutoTimer plugin
//* Version 3.0
//******************************************************************************
//* Authors: Web Dev Ben <https://github.com/wedebe>
//*
//* V 3.0 - complete overhaul
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*
//* TODO:
//* - fix tag population
//* - fix offset population
//* - move fn to utils
//* - write filtering
//* - write get/set settings
//* - fix zap/rec/zaprec
//* - fix vps etc.
//*******************************************************************************

(function () {

  class AutoTimer {
    constructor (autoTimerObj) {
      const self = this;
      Object.assign(self, autoTimerObj);

      self['bouquets'] = [];
      self['services'] = [];
      self['filters'] = {};

      if (self['from']) {
        self['timespanFrom'] = self['from'];
        delete self['from'];
      }

      if (self['to']) {
        self['timespanTo'] = self['to'];
        delete self['to'];
      }

      if (self['after']) {
        const afterDate = new Date(parseInt(self['after']) * 1000);
        self['after'] = afterDate.toISOString().split('T')[0];
      }

      if (self['before']) {
        const beforeDate = new Date(parseInt(self['before']) * 1000);
        self['before'] = beforeDate.toISOString().split('T')[0];
      }

      // if (!!ati['offset']) {
      //   ati['offset'].split(',');
      // }

      // if (!!ati['afterevent']) {
      //   ati['afterevent']['from'] && (ati['aftereventFrom'] = ati['afterevent']['from']);
      //   ati['afterevent']['to'] && (ati['aftereventTo'] = ati['afterevent']['to']);
      //   ati['afterevent'] = aem[ati['afterevent']['_@ttribute']] || ati['afterevent']['_@ttribute'] || aem[ati['afterevent']] || ati['afterevent'];
      // }

      if (self['e2service']) {
        if (!Array.isArray(self['e2service'])) {
          // we expect an array
          self['e2service'] = [self['e2service']];
        }
        self['e2service'].forEach((service, index) => {
          const bouquetsOrChannels = (owif.utils.isBouquet(service['e2servicereference'])) ? 'bouquets' : 'services';
          self[bouquetsOrChannels].push({
            'sRef': service['e2servicereference'],
            'name': service['e2servicename'],
            'selected': true,
          });
        });
        delete self['e2service'];
      }

      if (self['include']) {
        self['filters']['include'] = self['include'];
        delete self['include'];
      }

      if (self['exclude']) {
        self['filters']['exclude'] = self['exclude'];
        delete self['exclude'];
      }
    };

    get bouquetSRefs() {
      return this['bouquets'].map(entry => entry['sRef']);
    };

    get bouquetNames() {
      return this['bouquets'].map(entry => entry['name']);
    };

    get channelSRefs() {
      return this['services'].map(entry => entry['sRef']);
    };

    get channelNames() {
      return this['services'].map(entry => entry['name']);
    };
  };

  const AutoTimers = function () {
    // keep reference to object.
    let self;

    const atFormEl = document.getElementById('atform');

    const addDependentSectionTogglers = (data = {}) => {
      // set up show/hide checkboxes
      data['_timespan'] = !!data.timespanFrom || !!data.timespanTo;
      data['_after'] = !!data.after;
      data['_before'] = !!data.before;
      data['_timerOffset'] = !!data.timerOffsetAfter || !!data.timerOffsetBefore;
      data['timeSpanAE'] = !!data.afterevent;
      data['_location'] = !!data.location;

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
        const responseContent = await owif.utils.fetchData('/autotimer');
        const data = xml2json(responseContent)['autotimer'];

// console.log('response: ', data);
// console.log('defaults: ', data['default']);
// console.log('timer: ', data['timer']);
window.atList = data['timer'] || [];
if (!Array.isArray(window.atList)) {
  window.atList = [data['timer']];
}

aem = {
  'shutdown': 'deepstandby',
}
// TRANSFORMRESPONSE
//atListCache

        window.atList.map((itm) => {
          itm = new AutoTimer(itm);
        });
// console.log('wat', window.atList[358]);
        return window.atList;
      },

      populateList: () => {
        document.getElementById('at__page--edit').classList.toggle('hidden', true);
        window.scroll({top: 0, left: 0, behavior: 'smooth'});
        const listEl = document.getElementById('at__list');
        listEl.innerHTML = "";
        document.getElementById('at__page--list').classList.toggle('hidden', false);
        const templateEl = document.getElementById('autotimer-list-item-template');
        self.getAll()
          .then(jsonResponse => {
            // TODO:
            // sort by name
            // build found tags
            // build found locations
            jsonResponse.forEach((atItem, index) => {
              atItem = new AutoTimer(atItem);
              const searchType = valueLabelMap.autoTimers.searchType[atItem['searchType']] || '';
              const newNode = templateEl.content.firstElementChild.cloneNode(true);

              const editEl = newNode.querySelector('a[href="#at/edit/{{id}}"]');
              editEl.href = editEl.href.replace('{{id}}', atItem.id);
              editEl.onclick = (evt) => {
                self.editEntry(atItem.id);
                return false;
              }
              // newNode.querySelector('button[name="disable"]').onclick = (evt) => self.disableEntry(atItem['id']);
              newNode.querySelector('button[name="delete"]').onclick = (evt) => self.deleteEntry(atItem.id);

              // newNode.dataset['atId'] = atItem.id;
              newNode.querySelector('slot[name="autotimer-name"]').innerHTML = atItem.name;
              newNode.querySelector('slot[name="autotimer-searchType"]').innerHTML = (searchType) ? `${searchType}:` : '';
              atItem.timespanFrom && (newNode.querySelector('slot[name="autotimer-timespan"]').innerHTML = `~ ${atItem.timespanFrom || ''} - ${atItem.timespanTo || ''}`);
              newNode.querySelector('slot[name="autotimer-channels"]').innerHTML = atItem.channelNames.join(', ');
              atItem.bouquetNames.length && (newNode.querySelector('slot[name="autotimer-bouquets"]').innerHTML = `<br> ${atItem.bouquetNames.join(', ')}`);
              newNode.querySelector('slot[name="autotimer-match"]').innerHTML = `"${atItem.match}"`;
// console.log(atItem);
              listEl.appendChild(newNode);
            });
          });
      },

      getSettings: async () => {
        return await owif.utils.fetchData('/autotimer/get');
      },

      saveSettings: async (params) => {
        return await owif.utils.fetchData(`/autotimer/set?${params}`);
      },

      preview: async () => {
        document.getElementById('at-preview__progress').classList.toggle('hidden', false);
        document.getElementById('at-preview__no-results').classList.toggle('hidden', true);
        const responseContent = await owif.utils.fetchData('/autotimer/test');
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

      populateForm: async (data = {}) => {
        const { elements } = atFormEl;

        document.getElementById('at__page--list').classList.toggle('hidden', true);
        atFormEl.reset();
        window.scroll({top: 0, left: 0, behavior: 'smooth'});
        document.getElementById('at__page--edit').classList.toggle('hidden', false);

        data = new AutoTimer(data);
        data = addDependentSectionTogglers(data);

        self.autoTimerChoices['bouquets'].setChoices(self.availableServices['bouquets'], 'sRef', 'name', false);
        self.autoTimerChoices['services'].setChoices(self.availableServices['channels'], 'sRef', 'extendedName', true);

        /**
e2tags -> tags

always_zap
from
to
         **/

// console.log('sac', self.availableServices['channels']);

        for (let [key, value] of Object.entries(data)) {
          const field = elements.namedItem(key);
          if (field) {
            owif.utils.debugLog(`[${field.type}]`, key, value);
            switch (field.type) {
              case 'checkbox':
                field.checked = value;
                break;
              case 'select-multiple':
                const valuesOnly = value.map(entry => entry['sRef']);
                self.autoTimerChoices[key]
                  .setChoices(value, 'sRef', 'name', false)
                  .removeActiveItems()
                  .setChoiceByValue(valuesOnly);
                break;
              default:
                field.value = value;
                break;
            }
            try {
              field.dispatchEvent(new Event('change'));
            } catch(ex) {
// console.log(field, ex);
            }
          } else {
            //TODO add hidden
            owif.utils.debugLog('%c[N/A]', 'color: red', key, value);
          }
        }
        let tagOpts = [];
        try {
          tagOpts = window.tagList.map(function (item) {
            let allTags = autoTimerChoices['tags']['_currentState']['choices'];
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
            const xml = await owif.utils.fetchData(`/autotimer/remove?id=${atId}`)
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

      createEntry: () => self.populateForm(),

      editEntry: async (atId = -1) => {
        const entry = window.atList.find(autotimer => autotimer['id'] == atId);
        console.log(entry);
        self.populateForm(entry);
      },

      saveEntry: (extraParams = '') => {
        const formData = new FormData(atFormEl);
        const formDataObj = Object.fromEntries(formData);

        Object.entries(formDataObj).forEach(([name, value]) => {
          owif.utils.debugLog(name, value);
          if (value === '') {
            // remove empty value (eg. empty `id` value causes server error, but missing `id` param does not)
            formData.delete(name); // TODO: check iOS compatibility
          } else if (owif.utils.regexDateFormat.test(value)) {
            formData.set(name, owif.utils.toUnixDate(value));
          } else if (name !== 'tag') {
            // join multiple param= values into an array
            formData.set(name, formData.getAll(name));
          }
        });
        // AutoTimer doesn't remove some values unless they're set to empty
        if (!formData.has('services')) {
          formData.set('services', '');
        }
        if (!formData.has('bouquets')) {
          formData.set('bouquets', '');
        }

        owif.utils.fetchData(`/autotimer/edit?${extraParams}`, { method: 'post', body: formData })
          .then(responseText => {
            // TODO: jsonify
            const responseXml = new DOMParser().parseFromString(responseText, 'application/xml');
            const status = responseXml.getElementsByTagName('e2state')[0].textContent || '';
            const message = responseXml.getElementsByTagName('e2statetext')[0].textContent || '';

            if (status === true || status.toString().toLowerCase() === 'true') {
              self.populateList();
            } else {
              throw new Error(message);
            }
          })
          .catch((ex) => {
            let message = ex.message;
            message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;
            swal({
              title: message,
              text: '',
              type: 'error',
              animation: 'none',
            });
          });
      },

      addFilter: () => {
        const templateEl = document.getElementById('autotimer-filter-template');
        const newNode = templateEl.content.firstElementChild.cloneNode(true);
        const filterListEl = document.getElementById('foo');

        newNode.querySelector('button[name="removeFilter"]').onclick = self.removeFilter;
        newNode.querySelector('select[name="filter[\'name\']"]').onchange = (evt) => {
          const filterNameEl = evt.target;
          const fieldSetEl = filterNameEl.closest('fieldset');
          const isDayOfWeekFilter = (filterNameEl.value === 'dayofweek');

          fieldSetEl.querySelector('.filter-value--dayofweek').classList.toggle('hidden', !isDayOfWeekFilter);
          fieldSetEl.querySelector('.filter-value--text').classList.toggle('hidden', isDayOfWeekFilter);
        };
        filterListEl.appendChild(newNode);

        jQuery.AdminBSB.select.activate();
      },

      removeFilter: () => {
        const fieldSetEl = event.target.closest('fieldset.at__filter__line');
        fieldSetEl.remove();
      },

      initEventHandlers: () => {
        // create a failsafe element to assign event handlers to
        let nullEl = document.createElement('input');

        (document.getElementById('atform') || nullEl).onsubmit = (evt) => {
          evt.preventDefault();
          self.saveEntry();
        }
        (document.querySelector('button[name="create"]') || nullEl).onclick = self.createEntry;
        (document.querySelector('a[href="#at/new"]') || nullEl).onclick = (evt) => {
          evt.preventDefault();
          self.createEntry();
        }
        (document.querySelector('button[name="reload"]') || nullEl).onclick = self.populateList;
        (document.querySelector('button[name="process"]') || nullEl).onclick = () => window.parseAT();
        (document.querySelector('button[name="preview"]') || nullEl).onclick = self.preview;
        (document.querySelector('button[name="timers"]') || nullEl).onclick = () => window.listTimers();
        (document.querySelector('button[name="settings"]') || nullEl).onclick = () => window.getAutoTimerSettings();
        (document.querySelector('button[name="addFilter"]') || nullEl).onclick = self.addFilter;
        (document.querySelector('button[name="cancel"]') || nullEl).onclick = self.populateList; // TODO: prompt first

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

      init: async function () {
        self = this;

        const excludeIptv = true;
        self.availableServices = await owif.api.getAllServices(excludeIptv);
        self.autoTimerChoices = owif.gui.preparedChoices();

        self.populateList(); //check if we've got data to add a new AT with
        self.initEventHandlers(self);
      },
    };
  };

  window.autoTimers = new AutoTimers();
  window.autoTimers.init();
})();
