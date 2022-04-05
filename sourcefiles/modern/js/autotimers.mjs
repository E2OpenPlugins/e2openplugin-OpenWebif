/**
 * ----------------------------------------------------------------------------
 * AutoTimers plugin for OpenWebif
 *
 * @license GPL-3
 * https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
 *
 * @see https://github.com/oe-alliance/enigma2-plugins/tree/master/autotimer
 *
 * ----------------------------------------------------------------------------
 * Formatting applied:
 * @prettier
 *
 * @author Web Dev Ben <https://github.com/wedebe>; 2020, 2021
 * @contributors ...
 *
 * @version 3.0
 * 3.0 - complete overhaul
 *
 * ----------------------------------------------------------------------------
 * @todo fix dropdown styling
 * @todo add hashchange listener for better back/fwd nav experience
 * @todo code parse/process functionality
 * @todo check/fix iptv exclusion
 * @todo apply decodeHtml to filters?
 * @todo handle defaults? (maybe show as [value])
 * @todo consolidate e2simplexmlresult handling
 * @todo sort allAutoTimers by name/date added/enabled etc
 * @toto better handle `tstr_` and `tstrings_` (global change)
 * @todo JSDoc https://jsdoc.app/index.html
 *
 * ----------------------------------------------------------------------------
 */


  // handle `'`, `&` etc
  function decodeHtml(html = '') {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
  }

  function forceToArray(value) {
    let arr = [];
    if (Array.isArray(value)) {
        arr = value;
    } else if (typeof value !== 'undefined') {
        arr = [value];
    }
    return arr;
  }

  function keyValueSortWeight(key, order = 'asc') {
    return function innerSort(a, b) {
      if (!a.hasOwnProperty(key) || !b.hasOwnProperty(key)) {
        // key doesn't exist on either object
        return 0;
      }
  
      const varA = (typeof a[key] === 'string') ? a[key].toUpperCase() : a[key];
      const varB = (typeof b[key] === 'string') ? b[key].toUpperCase() : b[key];
  
      let weight = 0;
      if (varA > varB) {
        weight = 1;
      } else if (varA < varB) {
        weight = -1;
      }

      return (order === 'desc') ? (weight * -1) : weight;
    };
  }

  function getAdjustedTimeString(timeString, adjustment) {
    const { hours = 0, minutes = 0 } = adjustment;
    try {
      const hoursMinutes = timeString.split(':');
      const hrs = parseInt(hoursMinutes[0]);
      const mns = parseInt(hoursMinutes[1]);
      const dt = new Date(0, 0, 0, hrs, mns);
      dt.setHours(hrs + hours);
      dt.setMinutes(mns + minutes);

      return dt.toLocaleTimeString([], {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (ex) {
      return timeString;
    }
  }

  function removeNodesBySelector(selector) {
    document.querySelectorAll(selector).forEach((node) => {
      node.remove();
    });
  }

  function populateFormControl(self, formControls, name, value) {
    const field = formControls.namedItem(name);
    if (field) {
      owif.utils.debugLog(`[${field.type}]`, field, name, value);
      if (field instanceof RadioNodeList) {
        const csv = value.split(',');
        for (const [index, node] of field.entries()) {
          node.value = csv[index] || '';
          try {
            node.dispatchEvent(new Event('change'));
          } catch (ex) {
            owif.utils.debugLog(name, value, ex);
          }
        }
      } else {
        switch (field.type) {
          case 'checkbox':
            value = value === true || value === 'True' || value.toString() === field.value;
            field.checked = value;
            break;
          case 'select-multiple':
            try {
              const valuesOnly = value.map((entry) => entry['sRef']);
              self.autoTimerChoices[name]
                .setChoices(value, 'sRef', 'name', false)
                .setChoices(value, 'label', 'value', false)
                .removeActiveItems()
                .setChoiceByValue(value)
                .setChoiceByValue(valuesOnly);
            } catch (ex) {
              owif.utils.debugLog(name, value, ex);
            }
            break;
          default:
            field.value = value;
            break;
        }
        try {
          field.dispatchEvent(new Event('change'));
        } catch (ex) {
          owif.utils.debugLog(name, value, ex);
        }
      }
    } else {
      // we haven't found a formControl to populate
      owif.utils.debugLog('%c[N/A]', 'color: red', name, value);
      // filters are handled differently
      if (name !== 'filters') {
        const hiddenFormControl = document.createElement('input');
        hiddenFormControl.type = 'hidden';
        hiddenFormControl.name = name;
        hiddenFormControl.value = value;
        hiddenFormControl.dataset['valueType'] = typeof value;
        formControls[0].form.prepend(hiddenFormControl);
      }
    }
  }

  function toggleFormSection(section, disabled) {
    try {
      section.classList.toggle('dependent-section--disabled', disabled);
      section.querySelectorAll('input, select').forEach((formControl) => {
        formControl.disabled = disabled;
      });
    } catch (ex) {}
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
    constructor(autoTimerObj) {
      const self = this;
      Object.assign(self, autoTimerObj);

      self['name'] = decodeHtml(self['name']);
      self['match'] = decodeHtml(self['match']);

      self['tag'] = [];
      self['bouquets'] = [];
      self['services'] = [];
      self['filters'] = {
        include: [],
        exclude: [],
      };

      self['enabled'] = self['enabled'] === 'yes' ? 1 : 0;

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

      if (!!self['afterevent']) {
        const aeValueMap = {
          shutdown: 'deepstandby',
        };
        const aeFrom = self['afterevent']['from'];
        const aeTo = self['afterevent']['to'];
        const aeAction = self['afterevent']['_@ttribute'];

        aeFrom && (self['aftereventFrom'] = aeFrom);
        aeTo && (self['aftereventTo'] = aeTo);
        aeAction && (self['afterevent'] = aeValueMap[aeAction] || aeAction);
      }

      if (self['e2service']) {
        let hasMismatchedService = false;
        forceToArray(self['e2service']).forEach((service, index) => {
          const bouquetsOrChannels = owif.utils.isBouquet(service['e2servicereference']) ? 'bouquets' : 'services';
          self[bouquetsOrChannels].push({
            sRef: service['e2servicereference'],
            name: service['e2servicename'],
            selected: true,
          });
          hasMismatchedService = !service['e2servicename'];
        });
        self['hasMismatchedService'] = hasMismatchedService; // use this to find services no longer in lamedb
        delete self['e2service'];
      }

      if (self['e2tag']) {
        self['tag'] = forceToArray(self['e2tag']);
        delete self['e2tag'];
      }

      // fallback to (incorrectly) space-separated values
      if (self['e2tags']) {
        if (!self['tag']) {
          self['tag'] = self['e2tags'].split(' ');
        }
        delete self['e2tags'];
      }

      if (self['include']) {
        self['filters']['include'] = forceToArray(self['include']);
        delete self['include'];
      }

      if (self['exclude']) {
        self['filters']['exclude'] = forceToArray(self['exclude']);
        delete self['exclude'];
      }

      // Plugins
      self['vps_safemode'] = !self['vps_overwrite'];
    }

    get bouquetSRefs() {
      return this['bouquets'].map((entry) => entry['sRef']);
    }

    get bouquetNames() {
      return this['bouquets'].map((entry) => entry['name']);
    }

    get channelSRefs() {
      return this['services'].map((entry) => entry['sRef']);
    }

    get channelNames() {
      return this['services'].map((entry) => entry['name']);
    }

    get isRestrictedByDay() {
      const numDaysIncluded = this['filters']['include'].filter((item) => item['where'] === 'dayofweek').length;
      const numDaysExcluded = this['filters']['exclude'].filter((item) => item['where'] === 'dayofweek').length;

      return numDaysIncluded + numDaysExcluded > 0;
    }
  }

  export const AutoTimersApp = function () {
    // keep reference to object
    let self;

    const atEditForm = document.querySelector('form[name="atedit"]');
    const atSettingsForm = document.querySelector('form[name="atsettings"]');

    const addDependentSectionTogglers = (data = {}) => {
      // set up show/hide checkboxes
      data['_timespan'] = !!data.timespanFrom || !!data.timespanTo;
      data['_datespan'] = !!data.after || !!data.before;
      data['_after'] = !!data.after;
      data['_before'] = !!data.before;
      data['_timerOffset'] = !!data.offset;
      data['timeSpanAE'] = !!data.afterevent;
      data['_location'] = !!data.location;

      return data;
    };

    const addCell = (rowRef, content = '') => {
      const newCell = rowRef.insertCell();
      newCell.innerHTML = content;
      return newCell;
    };

    const addRow = (tableRef, item) => {
      const newRow = tableRef.insertRow();

      const e2state = item['e2state'];
      const e2stateCell = addCell(newRow, e2state);
      e2stateCell.title = e2state === 'Skip' ? item['e2message'] : '';

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
        const data = responseContent['autotimer'];
        owif.utils.debugLog(data);
        self.allAutoTimers = forceToArray(data['timer']);
        self.allAutoTimers.map((itm) => new AutoTimer(itm));
        self.allAutoTimers.sort(keyValueSortWeight('name'));

        return self.allAutoTimers;
      },

      populateList: () => {
        const listEl = document.getElementById('at__list');
        removeNodesBySelector('.at__item');
        document.getElementById('at__page--edit').classList.toggle('hidden', true);
        window.scroll({ top: 0, left: 0, behavior: 'smooth' });
        document.getElementById('at__page--list').classList.toggle('hidden', false);
        const templateEl = document.getElementById('autotimer-list-item-template');
        // reset collections
        let collatedLocations = [];
        let collatedTags = [];

        self.getAll().then((jsonResponse) => {
          jsonResponse.forEach((atItem, index) => {
            atItem = new AutoTimer(atItem);

            // collect values
            atItem.location && collatedLocations.push(atItem.location);
            collatedTags = collatedTags.concat(atItem.tag);

            const searchType = valueLabelMap.autoTimers.searchType[atItem['searchType']] || '';
            const newNode = templateEl.content.firstElementChild.cloneNode(true);

            newNode.querySelector('[name="preview"]').onclick = (evt) => self.preview(atItem.id);
            newNode.querySelector('[name="rename"]').onclick = (evt) => self.renameEntry(atItem.id, atItem.name);

            const editEl = newNode.querySelector('a[href="/#/at/edit?id={{id}}"]');
            editEl.href = editEl.href.replace('{{id}}', atItem.id);
            editEl.onclick = (evt) => {
              self.editEntry(atItem.id);
              // return false;
            };
            newNode.querySelector('button[name="toggle"]').onclick = (evt) =>
              self.toggleEntryEnabled(atItem.id, atItem.enabled);
            newNode.querySelector('button[name="delete"]').onclick = (evt) => self.deleteEntry(atItem.id);

            // newNode.dataset['atId'] = atItem.id;
            newNode.querySelector('slot[name="autotimer-name"]').innerHTML = atItem.name;
            newNode.querySelector('.icon__state').textContent = atItem.enabled ? 'av_timer' : 'highlight_off';
            newNode.querySelector('slot[name="autotimer-searchType"]').innerHTML = searchType ? `${searchType}:` : '';
            atItem.timespanFrom &&
              (newNode.querySelector('slot[name="autotimer-timespan"]').innerHTML = `~ ${atItem.timespanFrom || ''} - ${
                atItem.timespanTo || ''
              }`);
            atItem.isRestrictedByDay &&
              (newNode.querySelector('slot[name="autotimer-filters"]').innerHTML = 'Certain days'); // TODO: i10n
            newNode.querySelector('slot[name="autotimer-channels"]').innerHTML = atItem.channelNames.join(', ');
            atItem.bouquetNames.length &&
              (newNode.querySelector('slot[name="autotimer-bouquets"]').innerHTML = `<br> ${atItem.bouquetNames.join(
                ', '
              )}`);
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
        const settingsNamespace = 'config.plugins.autotimer.';
        const responseContent = await owif.utils.fetchData('/autotimer/get');
        let settings = responseContent['e2settings']['e2setting'];
        const { elements } = atSettingsForm;

        settings = settings
          .filter((setting) => setting['e2settingname'].startsWith(settingsNamespace))
          .map((setting) => {
            for (const [key, value] of Object.entries(setting)) {
              setting[key.replace('e2setting', '')] = value;
              delete setting[key];
            }
            setting['name'] = setting['name'].replace(settingsNamespace, '');
            return setting;
          });

        for (let entry of Object.values(settings)) {
          populateFormControl(self, elements, entry.name, entry.value);
        }
      },

      saveSettings: async () => {
        const formData = new FormData(atSettingsForm);

        // add unchecked checkboxes to payload
        for (const [index, formControl] of Object.entries(atSettingsForm)) {
          if (formControl.type === 'checkbox' && !formData.has(formControl.name)) {
            formData.set(formControl.name, '');
          }
        }

        try {
          const responseContent = await owif.utils.fetchData(`/autotimer/set`, { method: 'post', body: formData });
          const data = responseContent['e2simplexmlresult'];
          const status = data['e2state'];
          let message = data['e2statetext'];
          message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

          if (status === true || status.toString().toLowerCase() === 'true') {
            // ok
          } else {
            throw new Error(message);
          }
        } catch (ex) {
          swal({
            title: tstr_oops,
            text: ex,
            type: 'error',
            animation: 'none',
          });
        }
      },

      process: async () => {
        try {
          owif.utils.debugLog('`process` started, this could take a while...');
          const responseContent = await owif.utils.fetchData('/autotimer/parse');
          const data = responseContent['e2simplexmlresult'];
          const status = data['e2state'];
          let message = data['e2statetext'];
          message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

          if (status === true || status.toString().toLowerCase() === 'true') {
            swal({
              title: 'result',
              text: message,
              type: 'info',
              animation: 'none',
            });
          } else {
            throw new Error(message);
          }
        } catch (ex) {
          swal({
            title: tstr_oops,
            text: ex.message,
            type: 'error',
            animation: 'none',
          });
        }
      },

      previewAll: () => {
        self.preview();
      },

      preview: async (id = '') => {
        const previewResultsEl = document.getElementById('at-preview__list');
        const previewNoResultsEl = document.getElementById('at-preview__no-results');
        const previewProgressEl = document.getElementById('at-preview__progress');
        previewResultsEl.querySelectorAll('tr').forEach(tr => tr.remove());
        previewNoResultsEl.classList.toggle('hidden', true);
        previewProgressEl.classList.toggle('hidden', false);
        
        const command = (id && `test?id=${id}`) || 'simulate';
        const responseContent = await owif.utils.fetchData(`/autotimer/${command}`);
        const data = responseContent['e2autotimersimulate'] || responseContent['e2autotimertest'];
        const autotimers = data['e2simulatedtimer'] || data['e2testtimer'] || [];
        const newNode = document.createElement('tbody');
        previewProgressEl.classList.toggle('hidden', true);
        autotimers.forEach((autotimer) => {
          addRow(newNode, autotimer);
        });
        if (autotimers.length) {
          previewResultsEl.innerHTML = newNode.cloneNode(true).innerHTML;
        } else {
          previewNoResultsEl.classList.toggle('hidden', false);
        }
      },

      prepareChoices: () => {
        self.allTags = self.allTags.map((tag) => {
          return {
            value: tag,
            label: tag,
          };
        });

        self.autoTimerChoices['tag'].setChoices(self.allTags, 'value', 'label', true);
        self.autoTimerChoices['bouquets'].setChoices(self.availableServices['bouquets'], 'sRef', 'name', true);
        self.autoTimerChoices['services'].setChoices(self.availableServices['channels'], 'sRef', 'extendedName', true);
      },

      populateForm: async (data = {}) => {
        owif.utils.debugLog(data);
        const { elements } = atEditForm;
        atEditForm.reset();
        removeNodesBySelector('.at__filter__line');
        document.getElementById('at__page--list').classList.toggle('hidden', true);
        window.scroll({ top: 0, left: 0, behavior: 'smooth' });
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

        for (let [name, value] of Object.entries(data)) {
          populateFormControl(self, elements, name, value);
        }

        self.populateFilters(data.filters);
      },

      deleteEntry: async (atId = -1) => {
        atId !== -1 &&
          swal(
            {
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
            },
            async (userConfirmed) => {
              if (userConfirmed) {
                const responseContent = await owif.utils.fetchData(`/autotimer/remove?id=${atId}`);
                const data = responseContent['e2simplexmlresult'];
                const status = data['e2state'];
                let message = data['e2statetext'];
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
                    title: tstr_oops,
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
            }
          );
      },

      toggleEntryEnabled: async (atId = -1, currentState) => {
        const newState = currentState == 1 ? 0 : 1; // loose equivalence intentional
        try {
          const responseContent = await owif.utils.fetchData(`/autotimer/change?id=${atId}&enabled=${newState}`);

          const data = responseContent['e2simplexmlresult'];
          const status = data['e2state'];
          let message = data['e2statetext'];
          message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

          if (status === true || status.toString().toLowerCase() === 'true') {
            swal.close();
            self.populateList();
            owif.utils.debugLog(`toggleEntryEnabled [id ${atId}] from ${currentState} to ${newState} successful`);
          } else {
            throw new Error(message);
          }
        } catch (ex) {
          swal({
            title: tstr_oops,
            text: ex.message,
            type: 'error',
            animation: 'none',
          });
        }
      },

      createEntry: () => self.populateForm(),

      renameEntry: (atId = -1, currentName, newName = '') => {
        const doRenameRequest = async (atId, newName) => {
          try {
            const responseContent = await owif.utils.fetchData(`/autotimer/change?id=${atId}&name=${newName}`);

            const data = responseContent['e2simplexmlresult'];
            const status = data['e2state'];
            let message = data['e2statetext'];
            message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

            if (status === true || status.toString().toLowerCase() === 'true') {
              swal.close();
              self.populateList();
              owif.utils.debugLog(`renameEntry [id ${atId}] from ${currentName} to ${newName} successful`);
            } else {
              throw new Error(message);
            }
          } catch (ex) {
            swal({
              title: tstr_oops,
              text: ex.message,
              type: 'error',
              animation: 'none',
            });
          }
        };

        if (newName) {
          doRenameRequest(atId, newName);
        } else {
          swal(
            {
              title: tstr_rename,
              text: '',
              type: 'input',
              showCancelButton: true,
              closeOnConfirm: false,
              inputValue: currentName,
              input: 'text',
              animation: 'none',
            },
            (userInput) => {
              if (userInput && userInput.length) {
                doRenameRequest(atId, userInput);
              }
            }
          );
        }
      },

      editEntry: async (atId = -1) => {
        const entry = self.allAutoTimers.find((autotimer) => autotimer['id'] == atId);
        owif.utils.debugLog(`editEntry: ${entry}`);
        self.populateForm(entry);
      },

      transformFormData: () => {
        const formData = new FormData(atEditForm);
        const formDataObj = Object.fromEntries(formData);
        const paramsNotToSend = [
          'hasMismatchedService',
          '_before',
          '_after',
          '_type',
          '_filterpredicate',
          '_filterwhere',
        ];
        const filteringParamNames = [
          'title',
          'shortdescription',
          'description',
          'dayofweek',
          '!title',
          '!shortdescription',
          '!description',
          '!dayofweek',
        ];
        // TODO: tags?
        const paramsToSendIfEmpty = filteringParamNames.concat(['enabled', 'offset', 'services', 'bouquets', 'vps_enabled']);
        const paramsToConsolidate = ['offset', 'services', 'bouquets'];

        if (window.disableFilterEditing) {
          filteringParamNames.forEach((param) => formData.delete(param));
        }

        paramsNotToSend.forEach((param) => formData.delete(param));

        Object.entries(formDataObj).forEach(([name, value]) => {
          owif.utils.debugLog(name, value);
          if (paramsToConsolidate.includes(name)) {
            // join multiple param=a&param=b values into one param=[a,b]
            // this should not be applied to `tags`
            formData.set(name, formData.getAll(name));
          }
          if (value === '' || value === ',') {
            // TODO: this may no longer be needed
            // remove empty value (eg. empty `id` value causes server error,
            // whereas missing `id` param does not (treated as a new autotimer))
            formData.delete(name); // TODO: check iOS compatibility
          } else if (owif.utils.regexDateFormat.test(value)) {
            formData.set(name, owif.utils.toUnixDate(value));
          }
        });
        // AutoTimer doesn't remove some timer values unless they're sent as empty
        paramsToSendIfEmpty.forEach((param) => {
          if (!formData.has(param)) {
            formData.set(param, '');
          }
        });

        return formData;
      },

      saveEntry: async (extraParams = '') => {
        const responseContent = await owif.utils.fetchData(`/autotimer/edit?${extraParams}`, {
          method: 'post',
          body: self.transformFormData(),
        });

        const data = responseContent['e2simplexmlresult'];
        const status = data['e2state'];
        let message = data['e2statetext'];
        message = `${message.charAt(0).toUpperCase()}${message.slice(1)}`;

        if (status === true || status.toString().toLowerCase() === 'true') {
          self.populateList();
        } else {
          // throw new Error(message);
          swal({
            title: tstr_oops,
            text: message,
            type: 'error',
            animation: 'none',
          });
        }
      },

      cancelEntry: () => {
        swal(
          {
            title: tstr_prompt_save_changes,
            // text: '',
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dd6b55',
            confirmButtonText: tstrings_yes,
            cancelButtonText: tstrings_no_cancel,
            closeOnConfirm: false,
            closeOnCancel: true,
            animation: 'none',
          },
          function (userConfirmed) {
            if (userConfirmed) {
              self.saveEntry();
            } else {
              window.location.hash = '/at';
              self.populateList();
            }
          }
        );
      },

      populateFilters: (filters) => {
        filters['exclude'].forEach((f) => {
          f['predicate'] = '!';
          f['value'] = f['_@ttribute'];
          delete f['_@ttribute'];
          self.addFilter(f);
        });

        filters['include'].forEach((f) => {
          f['predicate'] = '';
          f['value'] = f['_@ttribute'];
          delete f['_@ttribute'];
          self.addFilter(f);
        });
      },

      addFilter: (filter = { predicate: '', where: 'title', value: '' }) => {
        const templateEl = document.getElementById('autotimer-filter-template');
        const newNode = templateEl.content.firstElementChild.cloneNode(true);
        const filterListEl = document.getElementById('atform__filters-container');

        const filterPredicate = newNode.querySelector('select[name="_filterpredicate"]');
        const filterWhere = newNode.querySelector('select[name="_filterwhere"]');
        const filterText = newNode.querySelector('input[type="text"]');
        const filterDayOfWeek = newNode.querySelector('select[name="dayofweek"]');

        const updateValueFields = () => {
          const isDayOfWeekSelected = filterWhere.value === 'dayofweek';

          if (isDayOfWeekSelected) {
            filterDayOfWeek.name = `${filterPredicate.value}${filterWhere.value}`;
            filterText.value = '';
          } else {
            filterText.name = `${filterPredicate.value}${filterWhere.value}`;
            filterDayOfWeek.value = '';
          }
        };

        newNode.querySelector('button[name="removeFilter"]').onclick = self.removeFilter;

        filterPredicate.onchange = (evt) => {
          updateValueFields();
        };

        filterWhere.onchange = (evt) => {
          const formControl = evt.target;
          const container = formControl.closest('fieldset');
          const isDayOfWeekFilter = formControl.value === 'dayofweek';

          container.querySelector('.filter-value--dayofweek').classList.toggle('hidden', !isDayOfWeekFilter);
          container.querySelector('.filter-value--text').classList.toggle('hidden', isDayOfWeekFilter);
          updateValueFields();
        };

        filterPredicate.value = filter['predicate'];
        filterWhere.value = filter['where'];
        if (filter['where'] === 'dayofweek') {
          const selectedOptions = filter['value'].split(',');
          for (let option of filterDayOfWeek) {
            option.selected = selectedOptions.includes(option.value);
          }
          filterWhere.dispatchEvent(new Event('change'));
        } else {
          filterText.value = filter['value'];
        }

        updateValueFields();
        filterListEl.appendChild(newNode);

        jQuery.AdminBSB.select.activate();
      },

      removeFilter: () => {
        const target = event.target;
        const container = target.closest('fieldset.at__filter__line');
        container.remove();
      },

      initEventHandlers: () => {
        // create a failsafe element to assign event handlers to
        let nullEl = document.createElement('input');

        /* autotimer list */
        // (document.querySelector('button[name="create"]') || nullEl).onclick = self.createEntry;
        (document.querySelector('button[name="reload"]') || nullEl).onclick = self.populateList;
        (document.querySelector('button[name="process"]') || nullEl).onclick = self.process;
        (document.querySelector('button[name="previewAll"]') || nullEl).onclick = self.previewAll;
        (document.querySelector('button[name="timers"]') || nullEl).onclick = () => window.listTimers();
        (document.querySelector('button[name="settings"]') || nullEl).onclick = self.getSettings;
        (document.querySelector('button[name="saveSettings"]') || nullEl).onclick = self.saveSettings;
        (document.querySelector('a[href="/#/at/new"]') || nullEl).onclick = self.createEntry;

        /* autotimer edit - buttons */
        (document.querySelector('button[name="addFilter"]') || nullEl).onclick = () => self.addFilter();
        (document.querySelector('button[name="cancel"]') || nullEl).onclick = self.cancelEntry;

        /* autotimer edit - inputs */
        (document.querySelector('form[name="atedit"]') || nullEl).onsubmit = (evt) => {
          evt.preventDefault();
          self.saveEntry();
        };
        // at least one option must be checked
        (document.querySelectorAll('input[name="justplay"], input[name="always_zap"]') || nullEl).forEach((node) => {
          node.onchange = (input) => {
            const checkedInputs = document.querySelectorAll(
              'input[name="justplay"]:checked, input[name="always_zap"]:checked'
            );
            checkedInputs.length < 1 && (event.target.checked = !event.target.checked);
          };
        });

        /* autotimer edit - show/hide */
        (document.getElementById('_timespan') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('_timespan_'), !input.target.checked);
        };
        (document.getElementById('_datespan') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('_datespan_'), !input.target.checked);
        };
        (document.getElementById('_timerOffset') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('_timerOffset_'), !input.target.checked);
        };
        (document.querySelector('[name="afterevent"]') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('AftereventE'), !input.target.value);
        };
        (document.getElementById('timeSpanAE') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('timeSpanAEE'), !input.target.checked);
        };
        (document.getElementById('_location') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('_location_'), !input.target.checked);
        };
        (document.getElementById('beforeevent') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('BeforeeventE'), !input.target.checked);
        };
        (document.querySelector('[name="vps_enabled"]') || nullEl).onchange = (input) => {
          toggleFormSection(document.getElementById('vps_enabled_'), !input.target.checked);
        };
        (document.querySelector('[name="vps_safemode"]') || nullEl).onchange = (input) => {
          (document.querySelector('[name="vps_overwrite"]') || nullEl).value = input.target.checked ? 0 : 1;
        };
      },

      init: async function () {
        self = this;

        const excludeIptv = true;
        const CutTitle = true;
        self.allAutoTimers = [];
        self.availableServices = await owif.api.getAllServices(excludeIptv, CutTitle);
        self.availableLocations = []; // these are already server-rendered
        self.allLocations = [];
        self.availableTags = await owif.api.getTags();
        self.allTags = [];
        self.autoTimerChoices = owif.gui.preparedChoices();

        const hash = window.location.hash;
        if (hash.startsWith('/#/at/new')) {
          const searchParams = new URLSearchParams(hash.split('?')[1] || '');
          const data = Object.fromEntries(searchParams);
          data['timespanFrom'] && (data['timespanFrom'] = getAdjustedTimeString(data['timespanFrom'], { hours: -1 }));
          data['timespanTo'] && (data['timespanTo'] = getAdjustedTimeString(data['timespanTo'], { hours: 1 }));
          data['sref'] && (data['e2service'] = { e2servicereference: data['sref'] });
          self.populateForm(data);
        } else if (hash.startsWith('/#/at/edit')) {
          const searchParams = new URLSearchParams(hash.split('?')[1] || '');
          self.editEntry(searchParams.get('id'));
        } else {
          self.populateList();
        }

        self.initEventHandlers(self);
      },
    };
  };
