/*eslint-env browser*/
/*global swal, jQuery*/
/*global GetLSValue, jumper8001, zapChannel*/

//******************************************************************************
//* bqe.js: openwebif Bouqueteditor plugin
//* Version 3.0
//******************************************************************************
//* Copyright (C) 2014-2018 Joerg Bleyel
//* Copyright (C) 2014-2018 E2OpenPlugins
//*
//* Authors: Joerg Bleyel <jbleyel # gmx.net>
//*          Robert Damas <https://github.com/rdamas>
//*          Web Dev Ben <https://github.com/wedebe>
//*
//* V 2.0 - complete refactored
//* V 2.1 - theme support
//* V 2.2 - update status label
//* V 2.3 - fix #198
//* V 2.4 - improve search fix #419
//* V 2.5 - prepare support spacers #239
//* V 2.6 - improve spacers #239
//* V 2.7 - improve channel numbers
//* V 2.7.1 - added category icons, added channel picons
//* V 2.8.1 - show ns text #840
//* V 2.9.1 - fix ns text, show provider as tooltip #840
//* V 2.9.2 - search by servicetype (sd/hd/uhd/radio/...) or orbital
//* V 2.9.3 - added list counts, added `Loading...`, adjusted layout
//* V 3.0 - complete overhaul:
//*         reduced jQuery dependence, moved towards more recent js,
//*         added channel zap and stream buttons, bq playlist link,
//*         once-off dom element selections, button state improvements,
//*         `add spacer`, rename channels, distinguish marker style,
//*         'Any' channel filter type added to 'TV', 'Radio' options,
//*         search channels: ^ - starts with; ends with - $; accented characters
//*
//* License GPL V2
//* https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt
//*******************************************************************************
// TODO: alternatives


  String.prototype.customContainsText = function (text = '') {
    if (!text) {
      return false;
    }
    const thisText = this;
    let isFound = false;

    // simplified starts/ends with
    if (text.startsWith('^')) {
      isFound = thisText.startsWith(text.slice(1));
    } else if (text.endsWith('$')) {
      isFound = thisText.endsWith(text.slice(0, -1));
    } else {
      isFound = thisText.includes(text);
    }
    return isFound;
  };

  const apiRequest = (url, options = {}) => {
    return fetch(url, options)
      .then((response) => {
        if (response.ok) {
          return response.json()
            .then((data, res = data.Result) => {
              if (res) {
                console.debug(res[1], res[0]);
                return res;
              } else {
                return data;
              }
            })
        }
      })
      .catch((error) => {
        console.debug(`apiRequest error: ${error}`);
      });
  };

  const _serviceTypeMap = {
    '1':  'SD',
    '2':  'Radio',
    '16': 'SD4',
    '19': 'HD',
    '1F': 'UHD',
    'D3': 'OPT',
  }

  class Channel {
    constructor (serviceObj) {
      this.data = { ...serviceObj };
      this._sRefParts = this.data['servicereference'].split(':');
      this.data['_ns'] = this._getNS();
      this.data['_stype'] = _serviceTypeMap[this._sRefParts[2]] || 'Other';
      this.searchFields = {
        'servicename': this.normaliseText(this.data['servicename']),
        'provider': this.normaliseText(this.data['servicename']),
        '_stype': this.data['_stype'].toLowerCase(),
      };
    }

    normaliseText (text) {
      return text.trim()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();
    }

    containsText (t = '') {
      const text = t.trim().toLowerCase();
      return (
        this.searchFields['servicename'].customContainsText(text) ||
        this.searchFields['provider'].customContainsText(text) ||
        this.searchFields['_stype'].indexOf(text) >= 0
      );
    }

    _getNS () {
      let value = '';
      const _ns = this._sRefParts[6].toLowerCase();
      if (_ns.startsWith('ffff', 0)) {
        value = 'DVB-C';
      } else if (_ns.startsWith('eeee', 0)) {
        value = 'DVB-T';
      } else {
        let __ns = (parseInt(_ns, 16) >> 16) & 0xfff;
        let d = 'E';
        if (__ns > 1800) {
          d = 'W';
          __ns = 3600 - __ns;
        }
        const degValue = (__ns / 10).toFixed(1).toString();
        value = `${degValue}&deg;${d}`;
      }
      return value;
    }
  }

  class ListPanel {
    constructor (elementId) {
      this._panelEl = document.getElementById(elementId);
      this._jqEl = jQuery(this._panelEl);
      this._countEl = document.getElementById(`${elementId}__count`);
      this._templateEl = document.getElementById(`${elementId}-item-template`);
    }

    clearAll() {
      this._jqEl.empty();
    }

    addItem(item) {
      this._panelEl.appendChild(item);
    }

    populate(items = [], transformItem = (item) => item, selectFirstItem = false) {
      const panel = this;
      panel.clearAll();
      panel.itemCount = items.length;

      items.forEach((item) => {
        const newNode = panel._templateEl.content.firstElementChild.cloneNode(true);
        panel.addItem(transformItem(item, newNode));
      });

      panel.isLoading = false;
      if (selectFirstItem) {
        panel.selectFirstItem();
      }
    }

    selectFirstItem() {
      try {
        this._panelEl.firstElementChild.classList.add('ui-selected');
      } catch (ex) {
        // don't worry about this
      }
    }

    set isLoading(value) {
      if (!value) {
        this._panelEl.classList.remove('loading');
      } else {
        this._panelEl.classList.add('loading');
      }
    }

    set itemCount(value) {
      this._countEl.textContent = `( ${value} )`;
    }

    get selectedItems() {
      return this._panelEl.querySelectorAll('.ui-selected');
    }

    selectable(config) {
      return this._jqEl.selectable(config);
    }

    sortable(config) {
      return this._jqEl.sortable(config);
    }
  }

  export const BQE = function () {
    // keep reference to object.
    let self;

    let allChannelsCache;
    let filterChannelsCache;

    const cTypeInput = document.forms['listTypeSelector'].elements['cType'];
    const tvRadioInput = document.forms['listTypeSelector'].elements['tvRadioMode'];

    const providerPanel = new ListPanel('provider');
    const channelsPanel = new ListPanel('channels');
    const bqlPanel = new ListPanel('bql');
    const bqsPanel = new ListPanel('bqs');

    return {

      getPlaylistUrl: (service) => {
        const preferredPlaylistFormat = GetLSValue('pl', 'm3u');
        const bouquetRef = encodeURIComponent(service.servicereference);
        const bouquetName = encodeURIComponent(service.servicename);
        return `/web/services.${preferredPlaylistFormat}?bRef=${bouquetRef}&bName=${bouquetName}`;
      },

      buildUrl: (url = '', params = {}) => {
        url = `${url}?`;
        Object.keys(params).forEach((key) => {
          url = url.concat(`${key}=${encodeURIComponent(params[key])}&`);
        });
        return url;
      },

      // Build ref string for selecting services list
      // @param listType int which list to use
      // @return string
      buildRefStr: (listType) => {
        const tvRadioMode = self.getSelectedTvRadioMode();
        let refStr;
        switch (tvRadioMode) {
          case 0:
            refStr =
              '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) || (type == 22) || (type == 31) || (type == 211) ';
            break;
          case 1:
            refStr = '1:7:2:0:0:0:0:0:0:0:(type == 2) || (type == 10) ';
            break;
          default:
            refStr = '1:7:1:0:0:0:0:0:0:0: ';
        }

        switch (listType) {
          case 0:
            refStr = `${refStr} FROM BOUQUET "bouquets.${tvRadioMode <= 0 ? 'tv' : 'radio'}" ORDER BY bouquet`;
            break;
          case 1:
            refStr = `${refStr} FROM PROVIDERS ORDER BY name`;
            break;
          case 2:
            refStr = `${refStr} FROM SATELLITES ORDER BY satellitePosition`;
            break;
          case 3:
          default:
            refStr = `${refStr} ORDER BY name`;
        }
        return refStr;
      },

      getSelectedCType: () => parseInt(cTypeInput.value),
      getSelectedTvRadioMode: () => parseInt(tvRadioInput.value),

      // TV/Radio/Any radio input change
      changeTvRadioMode: () => {
        document.querySelector('input[name="searchChannelsQuery"]').value = '';

        self.getBouquets()
          .then((data) => self.populateBouquets(data));

        switch (self.getSelectedCType()) {
          case 1:
            self.getProviders()
              .then((data) => self.populateProviders(data));
            break;
          case 2:
            self.getSatellites()
              .then((data) => self.populateProviders(data));
            break;
          case 3:
            providerPanel.clearAll();
            providerPanel.itemCount = 'ALL';
            self.getChannels()
              .then((data) => self.populateChannels(data));
            break;
        }
      },

      // display satellites/providers panel content
      populateProviders: (providers) => {
        providerPanel.populate(providers, (provider, item) => {
          item.dataset.sref = provider['servicereference'];
          item.dataset.sname = provider['servicename'];
          item.dataset.satprov = provider['_satprov'];
          item.querySelector('slot[name="provider-name"]').innerHTML = provider['servicename'];

          return item;
        });

        self.setProviderButtonsState();
        self.getChannels()
          .then((data) => self.populateChannels(data));
      },

      // display satellite/provider channels panel content
      populateChannels: () => {
        channelsPanel.populate(self.filterChannelsCache, (channelObj, item) => {
          let channel = channelObj['data'];
          let channelName = channel['servicename'];
          if (channelName) {
            try {
              item.querySelector('.bqe__picon img').setAttribute('src', channel['picon']);
            } catch (ex) {
              // no picon
            }
            item.querySelector('slot[name="channel-name"]').innerHTML = channelName;
            item.querySelector('.item__metadata').setAttribute('title', channel['provider']);
            item.querySelector('.item__metadata').innerHTML = `${channel['_stype']} &bull; ${channel['_ns']}`;

            item.dataset.sref = channel['servicereference'];
            item.dataset.sname = channel['servicename'];

            item.querySelector('button[name="zap"]').onclick = () => {
              zapChannel(channel['servicereference'], channel['servicename']);
            };
          }

          return item;
        });

        self.setChannelButtonsState();
      },

      // display bouquets panel content
      populateBouquets: (bouquets) => {
        bqlPanel.populate(
          bouquets,
          (bouquet, item) => {
            item.dataset.sref = bouquet['servicereference'];
            item.dataset.sname = bouquet['servicename'];
            item.querySelector('slot[name="bouquet-name"]').innerHTML = bouquet['servicename'];
            item.querySelector('a[href="#playlistUrl"]').setAttribute('href', bouquet['playlistUrl']);

            return item;
          },
          true
        );

        self.changeBouquet(bqlPanel.selectedItems[0].dataset['sref'])
          .then((data) => {
            self.populateBouquetChannels(data);
          });
      },

      // display bouquet channels panel content
      populateBouquetChannels: (channels) => {
        bqsPanel.populate(channels, (channel, item) => {
          let channelName = channel['servicename'];
          if (channelName && channel.ismarker == 0) {
            try {
              item.querySelector('.bqe__picon img').setAttribute('src', channel['picon']);
            } catch (ex) {
              // no picon
            }
            channelName = `${channel['pos'].toString()} - ${channel['servicename']}`;
            if (channel['isprotected'] && channel['isprotected'] != 0) {
              item.classList.add('item--is-protected');
              item.querySelector('.item__protection').classList.remove('hidden');
            }

            const streamButton = item.querySelector('button[name="stream"]');
            streamButton.onclick = () => {
              jumper8001(channel['servicereference'], channel['servicename']);
            };
            streamButton.classList.remove('hidden');

            const zapButton = item.querySelector('button[name="zap"]');
            zapButton.onclick = () => {
              zapChannel(channel['servicereference'], channel['servicename']);
            };
            zapButton.classList.remove('hidden');
          } else {
            const marker = item.querySelector('.item__marker');
            item.classList.add('item--is-marker');
            switch (channel['ismarker']) {
              case '1':
                marker.textContent = '[ M ]';
                break;
              case '2':
                marker.textContent = '[ S ]';
                break;
            }
            marker.classList.remove('hidden');
          }
          item.querySelector(
            'slot[name="channel-name"]'
          ).innerHTML = channelName;

          item.dataset.sref = channel['servicereference'];
          item.dataset.sname = channel['servicename'];
          item.dataset.ismarker = channel['ismarker']; // needed for 'rename' test

          return item;
        });

        self.setBouquetChannelButtonsState();
      },

      // retrieve satellite list
      getSatellites: () => {
        return new Promise((resolve) => {
          channelsPanel.isLoading = true;

          const url = self.buildUrl('/api/getsatellites', {
            sRef: self.buildRefStr(2),
            stype: self.getSelectedTvRadioMode(),
          });

          apiRequest(url)
            .then((data) => {
              const services = (data['satellites'] || []).map((service) => {
                service['servicename'] = service['name'];
                service['servicereference'] = service['service'];
                service['_satprov'] = 'satellite';
                return service;
              });

              resolve(services);
            });
        });
      },

      // retrieve provider list
      getProviders: () => {
        return new Promise((resolve) => {
          channelsPanel.isLoading = true;

          const url = self.buildUrl('/api/getservices', {
            sRef: self.buildRefStr(1),
          });

          apiRequest(url)
            .then((data) => {
              const services = (data['services'] || []).map((service) => {
                service['servicename'] = service['servicename'].replace('\u00c2\u00b0', '\u00b0');
                service['_satprov'] = 'provider';
                return service;
              });

              resolve(services);
            });
        });
      },

      // retrieve satellite/provider channel list
      getChannels: () => {
        return new Promise((resolve) => {
          channelsPanel.isLoading = true;

          const url = self.buildUrl('/api/getservices', {
            sRef: self.buildRefStr(3),
            provider: 1,
            picon: 1,
          });

          apiRequest(url)
            .then((data) => {
              const services = (data['services'] || []).map((service) => new Channel(service));

              self.allChannelsCache = services;
              self.filterChannelsCache = services;

              resolve(services);
            });
        });
      },

      // retrieve bouquet list
      getBouquets: () => {
        return new Promise((resolve) => {
          const url = self.buildUrl('/bouqueteditor/api/getservices', {
            sRef: self.buildRefStr(0),
          });

          apiRequest(url)
            .then((data) => {
              const services = (data['services'] || []).map((bouquet) => {
                bouquet['servicename'] = bouquet['servicename'].replace('\u00c2\u00b0', '\u00b0');
                bouquet['playlistUrl'] = self.getPlaylistUrl(bouquet);
                return bouquet;
              });

              resolve(services);
            });
        });
      },

      // handle provider selection in providers panel
      // @param sRef string selected provider service reference string
      changeProvider: (sRef) => {
        return new Promise((resolve) => {
          channelsPanel.isLoading = true;

          const url = self.buildUrl('/api/getservices', {
            sRef: sRef,
            provider: 1,
            picon: 1,
          });

          apiRequest(url)
            .then((data) => {
              const services = (data['services'] || []).map((service) => new Channel(service));

              self.allChannelsCache = services;
              self.filterChannelsCache = services;

              resolve(services);
            });
        });
      },

      // handle bouquet selection in bouquets panel
      // @param bouquetRef string selected bouquet reference string
      changeBouquet: (bouquetRef) => {
        return new Promise((resolve) => {
          bqsPanel.isLoading = true;

          const url = self.buildUrl('/bouqueteditor/api/getservices', {
            sRef: bouquetRef,
            picon: 1,
          });

          apiRequest(url)
            .then((data) => {
              const services = (data['services'] || []);
              resolve(services);
            });
        });
      },

      // add selected provider in providers panel as new bouquet in bouquets panel
      addProviderAsBouquet: () => {
        const url = self.buildUrl(
          '/bouqueteditor/api/addprovidertobouquetlist', {
            sProviderRef: providerPanel.selectedItems[0].dataset.sref,
            mode: self.getSelectedTvRadioMode(),
          }
        );

        apiRequest(url)
          .then(() => {
            self.getBouquets()
              .then((data) => self.populateBouquets(data));
          });
      },

      // change bouquet position in bouquets panel
      moveBouquet: (item) => {
        const url = self.buildUrl('/bouqueteditor/api/movebouquet', {
          sBouquetRef: item.sBouquetRef,
          mode: item.mode,
          position: item.position,
        });

        apiRequest(url)
          .then(() => {
            self.getBouquets()
              .then((data) => self.populateBouquets(data));
          });
      },

      // add new bouquet to bouquets panel
      // Prompts for bouquet name
      addBouquet: function () {
        swal({
            title: tstr_bqe_name_bouquet,
            text: '',
            type: 'input',
            showCancelButton: true,
            closeOnConfirm: true,
            inputValue: '',
            input: 'text',
            animation: 'none',
          },
          (newName) => {
            if (!newName || !newName.length) {
              return false;
            }

            const url = self.buildUrl('/bouqueteditor/api/addbouquet', {
              name: newName,
              mode: self.getSelectedTvRadioMode(),
            });

            apiRequest(url)
              .then(() => {
                self.getBouquets()
                  .then((data) => self.populateBouquets(data));
              });
          }
        );
      },

      // rename selected bouquet in bouquets panel
      // Prompts for new bouquet name
      renameBouquet: () => {
        const selection = bqlPanel.selectedItems[0];
        const sName = selection.dataset.sname;

        swal({
            title: tstr_bqe_rename_bouquet,
            text: '',
            type: 'input',
            showCancelButton: true,
            closeOnConfirm: true,
            inputValue: sName,
            input: 'text',
            animation: 'none',
          },
          (newName) => {
            if (!newName || !newName.length || newName === sName) {
              return false;
            }

            const url = self.buildUrl('/bouqueteditor/api/renameservice', {
              sRef: selection.dataset.sref,
              mode: self.getSelectedTvRadioMode(),
              newName: newName,
            });

            apiRequest(url)
              .then(() => {
                self.getBouquets()
                  .then((data) => self.populateBouquets(data));
              });
          }
        );
      },

      // Delete selected bouquet(s) from bouquets panel
      // Prompts for confirmation
      deleteBouquet: () => {
        const selection = bqlPanel.selectedItems[0];

        swal({
            title: tstr_bqe_del_bouquet_question,
            text: selection.dataset.sname,
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dd6b55',
            confirmButtonText: tstrings_yes_delete,
            cancelButtonText: tstrings_no_cancel,
            closeOnConfirm: true,
            closeOnCancel: true,
            animation: 'none',
          },
          (userConfirmed) => {
            if (userConfirmed) {
              const url = self.buildUrl('/bouqueteditor/api/removebouquet', {
                sBouquetRef: selection.dataset.sref,
                mode: self.getSelectedTvRadioMode(),
              });

              apiRequest(url)
                .then(() => {
                  self.getBouquets()
                    .then((data) => self.populateBouquets(data));
                });
            }
          }
        );
      },

      // Disable/enable satellite/provider channel panel action buttons
      setProviderButtonsState: () => {
        const selection = providerPanel.selectedItems[0];
        const isActionable = selection && selection.dataset['satprov'] === 'provider';
        document.querySelector('button[name="createBqFromProvider"]').disabled = !isActionable;
      },

      // Disable/enable satellite/provider channel panel action buttons
      setChannelButtonsState: () => {
        const selection = channelsPanel.selectedItems;
        const isActionable = selection.length > 0;
        document.querySelector('button[name="addChannelToBq"]').disabled = !isActionable;
        // document.querySelector('button[name="addAlternative"]').disabled = !isActionable;
      },

      // Disable/enable bouquet panel action buttons
      setBouquetChannelButtonsState: () => {
        const selection = bqsPanel.selectedItems;
        const isActionable = selection.length > 0;
        const isRenamable = isActionable && selection.length === 1 && selection[0].dataset.ismarker !== 2;
        document.querySelector('button[name="removeService"]').disabled = !isActionable;
        document.querySelector('button[name="renameService"]').disabled = !isRenamable;
      },

      // Change channel order in bouquet channels panel
      moveChannel: (item) => {
        const url = self.buildUrl('/bouqueteditor/api/moveservice', {
          sBouquetRef: item.sBouquetRef,
          sRef: item.sRef,
          mode: item.mode,
          position: item.position,
        });

        apiRequest(url)
          .then(() => self.renumberChannel());
      },

      renumberChannel: () => {
        //TODO
      },

      // Add selected services in channels panel to bouquet channels panel
      // Will be added before the selected bouquet channel, or at end
      addChannel: () => {
        const selectedChannels = channelsPanel.selectedItems;
        const selectedBouquetRef = bqlPanel.selectedItems[0].dataset.sref;
        const selectedBouquetChannels = bqsPanel.selectedItems;
        const destRef = selectedBouquetChannels.length ? selectedBouquetChannels[0].dataset.sref : '';
        const reqUrls = [];

        selectedChannels.forEach((selection) => {
          const url = self.buildUrl('/bouqueteditor/api/addservicetobouquet', {
            sBouquetRef: selectedBouquetRef,
            sRef: selection.dataset.sref,
            sRefBefore: destRef,
          });

          reqUrls.push(url);
        });

        Promise.all(reqUrls.map((url) => apiRequest(url)))
          .then((responses) => Promise.all(responses))
          .then(() => {
            self.changeBouquet(selectedBouquetRef)
              .then((data) => self.populateBouquetChannels(data));
          });
      },

      // Delete selected channels from bouquet channels panel; prompts for confirmation
      deleteChannel: () => {
        const selection = bqsPanel.selectedItems;
        if (!selection.length) {
          return false;
        }

        const selectedBouquetRef = bqlPanel.selectedItems[0].dataset.sref;
        const sNames = [];
        const reqUrls = [];

        selection.forEach((item) => {
          sNames.push(item.dataset.sname);

          const url = self.buildUrl('/bouqueteditor/api/removeservice', {
            sBouquetRef: selectedBouquetRef,
            mode: self.getSelectedTvRadioMode(),
            sRef: item.dataset.sref,
          });

          reqUrls.push(url);
        });

        swal({
            title: tstr_bqe_del_channel_question,
            text: sNames.join(', '),
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dd6b55',
            confirmButtonText: tstrings_yes_delete,
            cancelButtonText: tstrings_no_cancel,
            closeOnConfirm: true,
            closeOnCancel: true,
            animation: 'none',
          },
          (userConfirmed) => {
            if (userConfirmed) {
              Promise.all(reqUrls.map((url) => apiRequest(url)))
                .then((responses) => Promise.all(responses))
                .then(() => {
                  self.changeBouquet(selectedBouquetRef)
                    .then((data) => self.populateBouquetChannels(data));
                });
            }
          }
        );
      },

      // TODO
      addAlternative: () => {
        alert('Not implemented yet!');
        return;
      },

      // Add IPTV/Url service to bouquet channels panel; prompts for url and name
      // Will be added before the selected bouquet channel, or at end
      addUrl: () => {
        swal({
            title: tstr_bqe_add_url,
            text: '',
            type: 'input',
            showCancelButton: true,
            closeOnConfirm: false,
            animation: 'fade',
            inputValue: '',
            input: 'text',
            animation: 'none',
          },
          (newUrl) => {
            if (!newUrl) {
              return false;
            }
            swal({
                title: tstr_bqe_name_url,
                text: '',
                type: 'input',
                showCancelButton: true,
                closeOnConfirm: true,
                inputValue: newUrl,
                input: 'text',
                animation: 'none',
              },
              (newName) => {
                if (!newUrl) {
                  return false;
                }
                const selectedBouquetRef = bqlPanel.selectedItems[0].dataset.sref;
                const selectedBouquetChannels = bqsPanel.selectedItems;
                const destRef = selectedBouquetChannels.length ? selectedBouquetChannels[0].dataset.sref : '';

                const url = self.buildUrl(
                  '/bouqueteditor/api/addservicetobouquet', {
                    sBouquetRef: selectedBouquetRef,
                    Name: newName,
                    sRefBefore: destRef,
                    sRefUrl: newUrl,
                  }
                );

                apiRequest(url)
                  .then(() => {
                    self.changeBouquet(selectedBouquetRef)
                      .then((data) => self.populateBouquetChannels(data));
                  });
              }
            );
          }
        );
      },

      // Add spacer to bouquet channels panel
      // Will be added before the selected bouquet channel, or at end
      addSpacer: () => {
        const selectedBouquetRef = bqlPanel.selectedItems[0].dataset.sref;
        const selectedBouquetChannels = bqsPanel.selectedItems;
        const destRef = selectedBouquetChannels.length ? selectedBouquetChannels[0].dataset.sref : '';

        const url = self.buildUrl('/bouqueteditor/api/addmarkertobouquet', {
          sBouquetRef: selectedBouquetRef,
          SP: '1',
          sRefBefore: destRef,
        });

        apiRequest(url)
          .then(() => {
            self.changeBouquet(selectedBouquetRef)
              .then((data) => self.populateBouquetChannels(data));
          });
      },

      // Add separator to bouquet channels panel; prompts for name
      // Will be added before the selected bouquet channel, or at end
      addMarker: () => {
        swal({
            title: tstr_bqe_name_marker,
            text: '',
            type: 'input',
            showCancelButton: true,
            closeOnConfirm: true,
            inputValue: '',
            input: 'text',
            animation: 'none',
          },
          (newName) => {
            if (!newName || !newName.length) {
              return false;
            }
            const selectedBouquetRef = bqlPanel.selectedItems[0].dataset.sref;
            const selectedBouquetChannels = bqsPanel.selectedItems;
            const destRef = selectedBouquetChannels.length ? selectedBouquetChannels[0].dataset.sref : '';

            const url = self.buildUrl('/bouqueteditor/api/addmarkertobouquet', {
              sBouquetRef: selectedBouquetRef,
              Name: newName,
              sRefBefore: destRef,
            });

            apiRequest(url)
              .then(() => {
                self.changeBouquet(selectedBouquetRef)
                  .then((data) => self.populateBouquetChannels(data));
              });
          }
        );
      },

      // rename service or marker in bouquet service panel
      // Prompts for new marker name.
      renameBouquetService: () => {
        const selection = bqsPanel.selectedItems;
        if (selection.length !== 1) {
          return false;
        }

        const item = selection[0];

        // TODO: rename group
        // spacers can't be renamed
        if (item.dataset.ismarker == 2) {
          return false;
        }

        const sName = item.dataset.sname;
        const sRef = item.dataset.sref;
        const destRef = jQuery(item).next().data('sref') || '';
        const selectedBouquetRef = bqlPanel.selectedItems[0].dataset.sref;

        swal({
            title: tstr_bqe_rename_marker,
            text: '',
            type: 'input',
            showCancelButton: true,
            closeOnConfirm: true,
            inputValue: sName,
            input: 'text',
            animation: 'none',
          },
          (newName) => {
            if (!newName || newName == sName) {
              return false;
            }

            const url = self.buildUrl('/bouqueteditor/api/renameservice', {
              sBouquetRef: selectedBouquetRef,
              sRef: sRef,
              newName: newName,
              sRefBefore: destRef,
            });

            apiRequest(url)
              .then(() => {
                self.changeBouquet(selectedBouquetRef)
                  .then((data) => self.populateBouquetChannels(data));
              });
          }
        );
      },

      // search satellite/provider channels by name, sd / hd / uhd, or provider
      searchChannels: (text) => {
        channelsPanel.isLoading = true;

        self.filterChannelsCache = self.allChannelsCache.filter((service) => {
          if (service.containsText(text)) {
            return service;
          }
        });

        self.populateChannels();
      },

      // Display success and errors for selected ajax functions
      // @param txt string success/error msg
      // @param st bool False: error, True: success
      showError: (txt, st) => {
        console.debug(txt, st);
        st = typeof st !== 'undefined' ? st : 'False';
        jQuery('#statustext').text('');

        if (st === true || st === 'True' || st === 'true') {
          jQuery('#statusbox')
            .removeClass('ui-state-error')
            .addClass('ui-state-highlight');
          jQuery('#statusicon')
            .removeClass('ui-icon-alert')
            .addClass('ui-icon-info');
        } else {
          jQuery('#statusbox')
            .removeClass('ui-state-highlight')
            .addClass('ui-state-error');
          jQuery('#statusicon')
            .removeClass('ui-icon-info')
            .addClass('ui-icon-alert');
        }
        jQuery('#statustext').text(txt);

        if (txt !== '') {
          jQuery('#statuscont').show();
        } else {
          jQuery('#statuscont').hide();
        }
      },

      // export bouquets
      // Prompts for backup file name
      exportBouquets: () => {
        swal({
            title: tstr_bqe_filename,
            text: '',
            type: 'input',
            showCancelButton: true,
            closeOnConfirm: true,
            inputValue: 'bouquets_backup',
            input: 'text',
            animation: 'none',
          },
          (fileName) => {
            if (!fileName) {
              return false;
            }

            const url = self.buildUrl('/bouqueteditor/api/backup', {
              Filename: fileName,
            });

            apiRequest(url)
              .then((res) => {
                window.open(`/bouqueteditor/tmp/${res[1]}`, 'Download')
              });
          }
        );
      },

      // import bouquets
      // Triggers file upload dialog
      importBouquets: () => {
        document.forms['uploadrestore'].elements['rfile'].click();
      },

      // Called after file upload dialog. Prompts for confirmation of upload,
      // uploads backup file.
      prepareRestore: (event) => {
        const fileUploadInput = event.target;
        const fileUploadForm = fileUploadInput.form;
        const fileName = fileUploadInput.value.replace('C:\\fakepath\\', '');

        swal({
            title: tstr_bqe_restore_question,
            text: fileName,
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dd6b55',
            confirmButtonText: tstrings_yes_delete,
            cancelButtonText: tstrings_no_cancel,
            closeOnConfirm: true,
            closeOnCancel: true,
            animation: 'none',
          },
          (userConfirmed) => {
            if (userConfirmed) {
              const formData = new FormData(fileUploadForm);

              apiRequest(fileUploadForm.action, {
                method: fileUploadForm.method,
                body: formData,
              })
                .then((res) => self.doRestore(res[1]));
            }
          }
        );
      },

      // restore uploaded bouquet backup file
      doRestore: (fileName) => {
        if (!fileName) {
          return false;
        }

        const url = self.buildUrl('/bouqueteditor/api/restore', {
          Filename: fileName,
        });

        apiRequest(url)
          .then(() => {
            self.getBouquets().then((data) => self.populateBouquets(data));
          });
      },

      initEventHandlers: () => {
        const bqeContentEl = document.getElementById('bqemain');

        // create a failsafe to assign click handlers to
        let nullEl = document.createElement('a');

        (document.getElementById('toolbar-bouquets-reload') || nullEl).onclick = () => {
          console.log('fixme');
          self.getBouquets().then((data) => self.populateBouquets(data));
        };
        (document.getElementById('toolbar-bouquets-export') || nullEl).onclick = self.exportBouquets;
        (document.getElementById('toolbar-bouquets-import') || nullEl).onclick = self.importBouquets;

        bqeContentEl.querySelectorAll('input[name="cType"]').forEach((input) => {
            input.onchange = () => self.changeTvRadioMode();
          });

        bqeContentEl.querySelectorAll('input[name="tvRadioMode"]').forEach((input) => {
            input.onchange = () => self.changeTvRadioMode();
          });

        (bqeContentEl.querySelector('button[name="createBqFromProvider"]') || nullEl).onclick = self.addProviderAsBouquet;

        (bqeContentEl.querySelector('button[name="addChannelToBq"]') || nullEl).onclick = self.addChannel;
        // (bqeContentEl.querySelector('button[name="addAlternative"]') || nullEl).onclick = (self.addAlternative);

        (bqeContentEl.querySelector('button[name="newBq"]') || nullEl).onclick = self.addBouquet;
        (bqeContentEl.querySelector('button[name="renameBq"]') || nullEl).onclick = self.renameBouquet;
        (bqeContentEl.querySelector('button[name="deleteBq"]') || nullEl).onclick = self.deleteBouquet;

        (bqeContentEl.querySelector('button[name="addUrl"]') || nullEl).onclick = self.addUrl;
        (bqeContentEl.querySelector('button[name="addMarker"]') || nullEl).onclick = self.addMarker;
        (bqeContentEl.querySelector('button[name="addSpacer"]') || nullEl).onclick = self.addSpacer;
        (bqeContentEl.querySelector('button[name="renameService"]') || nullEl).onclick = self.renameBouquetService;
        (bqeContentEl.querySelector('button[name="removeService"]') || nullEl).onclick = self.deleteChannel;

        (bqeContentEl.querySelector('input[name="searchChannelsQuery"]') || nullEl).addEventListener('keyup', (event) => {
          self.searchChannels(event.target.value);
        });

        nullEl = null;

        jQuery('#rfile').change(self.prepareRestore);
      },

      // Set up handlers, trigger building lists.
      // This is the starting point.
      init: function () {
        self = this;

        // satellite/providers panel setup, using jQueryUI widgets
        providerPanel.selectable({
          selected: (event, ui) => {
            self.changeProvider(jQuery(ui.selected).data('sref'))
              .then(() => self.populateChannels());
          },
          selecting: (event, ui) => {
            jQuery(ui.selecting).siblings().removeClass('ui-selecting');
          },
          stop: self.setProviderButtonsState,
        });

        // satellite/provider channels panel setup, using jQueryUI widgets
        channelsPanel.selectable({
          filter: 'li',
          stop: self.setChannelButtonsState,
        });

        // bouquets panel setup, using jQueryUI widgets
        bqlPanel.sortable({
            axis: 'y',
            handle: '.handle',
            stop: (event, ui) => {
              const sRef = jQuery(ui.item).data('sref');
              const position = jQuery(ui.item).index();
              self.moveBouquet({
                sBouquetRef: sRef,
                mode: self.getSelectedTvRadioMode(),
                position: position,
              });
            },
          })
          .selectable({
            filter: 'li',
            cancel: '.handle, a, button',
            selected: (event, ui) => {
              self.changeBouquet(jQuery(ui.selected).data('sref'))
                .then((data) => self.populateBouquetChannels(data));
            },
            selecting: (event, ui) => {
              jQuery(ui.selecting).siblings().removeClass('ui-selecting');
            },
          });

        // bouquet channels panel setup, using jQueryUI widgets
        bqsPanel.sortable({
            axis: 'y',
            handle: '.handle',
            stop: (event, ui) => {
              const bouquetRef = bqlPanel.selectedItems[0].dataset['sref'];
              const sRef = jQuery(ui.item).data('sref');
              const position = ui.item.index();
              self.moveChannel({
                sBouquetRef: bouquetRef,
                sRef: sRef,
                mode: self.getSelectedTvRadioMode(),
                position: position,
              });
            },
          })
          .selectable({
            filter: 'li',
            cancel: '.handle, a, button',
            stop: self.setBouquetChannelButtonsState,
          });

        self.initEventHandlers(self);
        self.changeTvRadioMode();
      },
    };
  };
