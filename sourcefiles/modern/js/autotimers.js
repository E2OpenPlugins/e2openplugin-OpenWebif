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
 * @contributors ...
 * 
 * 3.0 - complete overhaul
 * 
 * @todo fix offset population
 * @todo write filtering
 * @todo write get/set settings
 * @todo fix zap/rec/zaprec params
 * @todo fix vps etc. params
 * @todo fix alternatives checkbox click 
 * @todo handle defaults
 * @todo sort by name/date added/enabled etc
 * @todo JSDoc https://jsdoc.app/index.html
 * --------------------------------------------------------------------------
 */


(function () {
  // handle `'`, `&` etc
  function decodeHtml(html = '') {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
  }

  /*
  class AutoTimerList {
    constructor () {};

    add = ((autotimer) => {});

    delete = ((atId) => {});

    render = ((targetElement) => {});

    sort = (() => {});

    filter = (() => {});
  }
  */

  class AutoTimer {
    constructor (autoTimerObj) {
      const self = this;
      Object.assign(self, autoTimerObj);

      self['name'] = decodeHtml(self['name']);
      self['match'] = decodeHtml(self['match']);
      // TODO: apply to filters too

      self['tag'] = [];
      self['bouquets'] = [];
      self['services'] = [];
      self['filters'] = {};

      self['enabled'] = (self['enabled'] === 'yes') ? 1 : 0;

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
        let hasMismatchedService = false;
        self['e2service'].forEach((service, index) => {
          const bouquetsOrChannels = (owif.utils.isBouquet(service['e2servicereference'])) ? 'bouquets' : 'services';
          self[bouquetsOrChannels].push({
            'sRef': service['e2servicereference'],
            'name': service['e2servicename'],
            'selected': true,
          });
          hasMismatchedService = !service['e2servicename'];
        });
        self['hasMismatchedService'] = hasMismatchedService;
        delete self['e2service'];
      }

      if (self['e2tag']) {
        if (!Array.isArray(self['e2tag'])) {
          // we expect an array
          self['e2tag'] = [self['e2tag']];
        }
        self['tag'] = self['e2tag'];
        delete self['e2tag'];
      }

      // fallback to (incorrectly) space-separated values
      if (self['e2tags']) {
        self['tag'] = self['e2tags'].split(' ');
        delete self['e2tags'];
      }

      if (self['include']) {
        self['filters']['include'] = self['include'];
        delete self['include'];
      }

      if (self['exclude']) {
        self['filters']['exclude'] = self['exclude'];
        delete self['exclude'];
      }

      // maybe try utilise response.formData()
    }

    get bouquetSRefs() {
      return this['bouquets'].map(entry => entry['sRef']);
    }

    get bouquetNames() {
      return this['bouquets'].map(entry => entry['name']);
    }

    get channelSRefs() {
      return this['services'].map(entry => entry['sRef']);
    }

    get channelNames() {
      return this['services'].map(entry => entry['name']);
    }
  }

  const AutoTimersApp = function () {
    // keep reference to object
    let self;

    const atFormEl = document.getElementById('atform');

    const addDependentSectionTogglers = (data = {}) => {
      // set up show/hide checkboxes
      data['_timespan'] = !!data.timespanFrom || !!data.timespanTo;
      data['_after'] = !!data.after;
      data['_before'] = !!data.before;
      data['_timerOffset'] = !!data.offset;
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
        let responseContent = await owif.utils.fetchData('/autotimer');
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

        window.atList.map((itm) => new AutoTimer(itm));

        return window.atList;
      },

      populateList: () => {
        document.getElementById('at__page--edit').classList.toggle('hidden', true);
        window.scroll({top: 0, left: 0, behavior: 'smooth'});
        const listEl = document.getElementById('at__list');
        listEl.innerHTML = "";
        document.getElementById('at__page--list').classList.toggle('hidden', false);
        const templateEl = document.getElementById('autotimer-list-item-template');
        // reset collections
        let collatedLocations = [];
        let collatedTags = [];

        self.getAll()
          .then(jsonResponse => {
            // TODO:
            // sort by name
            // build found locations
            jsonResponse.forEach((atItem, index) => {
              atItem = new AutoTimer(atItem);

              // collect values
              atItem.location && (collatedLocations.push(atItem.location));
              collatedTags = collatedTags.concat(atItem.tag);

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

              // future use (filter AutoTimer entries with no matching service in lamedb)
              // atItem['hasMismatchedService'] && listEl.appendChild(newNode);
              // future use (filter by state)
              // !atItem['enabled'] && listEl.appendChild(newNode);
              listEl.appendChild(newNode);
            });

            // unique values only
            // https://dev.to/clairecodes/how-to-create-an-array-of-unique-values-in-javascript-using-sets-5dg6
            self.allLocations = [...new Set(self.availableLocations.concat(collatedLocations))].sort() || [];
            self.allTags = [...new Set(self.availableTags.concat(collatedTags))].sort() || [];
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

      prepareChoices: () => {
        self.allTags = self.allTags.map((tag) => {
          return {
            value: tag,
            label: tag,
          }
        });

        self.autoTimerChoices['tag'].setChoices(self.allTags, 'value', 'label', true);
        self.autoTimerChoices['bouquets'].setChoices(self.availableServices['bouquets'], 'sRef', 'name', true);
        self.autoTimerChoices['services'].setChoices(self.availableServices['channels'], 'sRef', 'extendedName', true);
      },

      populateForm: async (data = {}) => {
        const { elements } = atFormEl;

        document.getElementById('at__page--list').classList.toggle('hidden', true);
        atFormEl.reset();
        window.scroll({top: 0, left: 0, behavior: 'smooth'});
        document.getElementById('at__page--edit').classList.toggle('hidden', false);

        data = new AutoTimer(data);
        data = addDependentSectionTogglers(data);

        self.prepareChoices();
    
        for (let loc of self.allLocations) {
          const newItem = document.createElement('option');

          newItem.appendChild(document.createTextNode(loc));
          newItem.value = loc;
          document.querySelector('select[name="location"] optgroup[name="more"').appendChild(newItem);
          jQuery('select[name=location]').selectpicker('refresh');
        }

        /**
always_zap
from
to
         **/

        for (let [key, value] of Object.entries(data)) {
          const field = elements.namedItem(key);
          if (field) {
            owif.utils.debugLog(`[${field.type}]`, field, key, value);
            if (field instanceof RadioNodeList) {
              const csv = value.split(',');
              for (const [index, node] of field.entries()) {
                node.value = csv[index] || '';
                try {
                  node.dispatchEvent(new Event('change'));
                } catch(ex) {
                  owif.utils.debugLog(key, value, ex);
                }
              }
            } else {
              switch (field.type) {
                case 'checkbox':
                  field.checked = value;
                  break;
                case 'select-multiple':
                  try {
                  const valuesOnly = value.map(entry => entry['sRef']);
                  self.autoTimerChoices[key]
                    .setChoices(value, 'sRef', 'name', false)
                    .setChoices(value, 'label', 'value', false)
                    .removeActiveItems()
                    .setChoiceByValue(value)
                    .setChoiceByValue(valuesOnly);
                  } catch (ex) {
                    owif.utils.debugLog(key, value, ex);
                  }
                  break;
                default:
                  field.value = value;
                  break;
              }
              try {
                field.dispatchEvent(new Event('change'));
              } catch(ex) {
                owif.utils.debugLog(key, value, ex);
              }
            }
          } else {
            //TODO add hidden
            owif.utils.debugLog('%c[N/A]', 'color: red', key, value);
          }
        }
      },

      deleteEntry: async (atId = -1) => {
        (atId !== -1) && swal({
          title: tstr_del_autotimer,
          // text: 'CurrentAT.name',
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
            const responseContent = await owif.utils.fetchData(`/autotimer/remove?id=${atId}`);
            const responseAsJson = xml2json(responseContent)['e2simplexmlresult'];
            const status = responseAsJson['e2state'];
            let message = responseAsJson['e2statetext'];
            message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

            if (status === true || status.toString().toLowerCase() === 'true') {
              swal({
                title: tstrings_deleted, 
                text: message,
                type: 'success',
                animation: 'none',
              });
            } else {
              // throw new Error(message);
              swal({
                title: 'Oops...', // TODO: i10n
                text: message,
                type: 'error',
                animation: 'none',
              });
            }

            self.populateList();
          } else {
            swal({
              title: tstrings_cancelled, 
              // text: 'CurrentAT.name',
              type: 'error',
              animation: 'none',
            });
          }
        });
      },

      // not implemented
      disableEntry: async (atId = -1) => {
        owif.utils.debugLog(`disableEntry: id ${entry}`);
      },

      createEntry: () => self.populateForm(),

      editEntry: async (atId = -1) => {
        const entry = window.atList.find(autotimer => autotimer['id'] == atId);
        owif.utils.debugLog(`editEntry: ${entry}`);
        self.populateForm(entry);
      },

      saveEntry: async (extraParams = '') => {
        const formData = new FormData(atFormEl);
        const formDataObj = Object.fromEntries(formData);

        Object.entries(formDataObj).forEach(([name, value]) => {
          owif.utils.debugLog(name, value);
          if (['tag'].indexOf(name) === -1) {
            // join multiple param=a&param=b values into one param=[a,b]
            // this should not be applied to `tags`
            formData.set(name, formData.getAll(name));
          }
          if (value === '' || value === ',') {
            // remove empty value (eg. empty `id` value causes server error, 
            // whereas missing `id` param does not (treated as a new autotimer))
            formData.delete(name); // TODO: check iOS compatibility
          } else if (owif.utils.regexDateFormat.test(value)) {
            formData.set(name, owif.utils.toUnixDate(value));
          }
        });
        // AutoTimer doesn't remove some timer values unless they're sent as empty
        ['offset', 'services', 'bouquets'].forEach((param) => {
          if (!formData.has(param)) {
            formData.set(param, '');
          }
        });

        const responseContent = await owif.utils.fetchData(`/autotimer/edit?${extraParams}`, { method: 'post', body: formData });
        const responseAsJson = xml2json(responseContent)['e2simplexmlresult'];
        const status = responseAsJson['e2state'];
        let message = responseAsJson['e2statetext'];
        message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

        if (status === true || status.toString().toLowerCase() === 'true') {
          self.populateList();
        } else {
          // throw new Error(message);
          swal({
            title: 'Oops...', // TODO: i10n
            text: message,
            type: 'error',
            animation: 'none',
          });
        }
      },

      cancelEntry: () => {
        swal({
          title: 'Are you sure you want to discard your changes?',
          // text: '',
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
            self.populateList();
          }
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
        (document.querySelector('button[name="cancel"]') || nullEl).onclick = self.cancelEntry;

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
        self.availableLocations = []; // these are already server-rendered
        self.availableTags = await owif.api.getTags();
        self.autoTimerChoices = owif.gui.preparedChoices();

        self.populateList(); //check if we've got data to add a new AT with
        self.initEventHandlers(self);
      },
    };
  }

  const autoTimersApp = new AutoTimersApp();
  autoTimersApp.init();
})();
