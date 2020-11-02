'use strict';

const debugTagStyle = 'color: #fff; font-weight: bold; background-color: #333; padding: 2px 4px 1px; border-radius: 2px;';

const debugMsg = (msg) => {
  console.info('%cOWIF', debugTagStyle, msg);
}

class STB { 
  constructor() {}
}

class API { 
  constructor() {}

  async getTags() {
    let response = await fetch('/api/gettags');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      return await response.json();
    }
  }

  async getAllServices() {
    let response = await fetch('/api/getallservices');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      const jsonResponse = await response.json();
      let allChannels = [];
      const bouquets = jsonResponse['services'].map((bouquet) => {
        const bouquetChannels = bouquet['subservices'].map((channel) => {
          const name = channel['servicename'];
          const sRef = channel['servicereference'];
          const isMarker = (sRef.indexOf('1:64:') > -1);
          /*
            1:0: - tv?
            4097: - url?
            1:134:1 - (encodeURIComponent)
          */
          return {
            name: name,
            sRef: sRef,
            disabled: isMarker,
          }
        });

        allChannels = allChannels.concat(bouquetChannels);

        return {
          name: bouquet['servicename'],
          sRef: bouquet['servicereference'],
          channels: bouquetChannels,
        }
      });

      return await {
        channels: allChannels,
        bouquets: bouquets,
      };
    }
  }

}

class GUI { 
  constructor() {}

  /* TODO: i10n */
  choicesConfig = {
    removeItemButton: true,
    duplicateItemsAllowed: false,
    resetScrollPosition: false,
    shouldSort: false,
    placeholder: true,
    renderSelectedChoices: 'always',
    itemSelectText: '',
    /*
      loadingText: 'Loading...',
      placeholderValue: null,
      searchPlaceholderValue: null,
      noResultsText: 'No results found',
      notagChoicesext: 'No choices to choose from',
      callbackOnInit: null,
    */
  };
  
  fullscreen(state, el) {
    if (state === true) {
      screenfull.request(el).then(() => {
        debugMsg('GUI:fullscreen activated');
      });
    } else if (state === false) {
      screenfull.exit().then(() => {
        debugMsg('GUI:fullscreen deactivated');
      });
    } else {
      screenfull.toggle(el).then(() => {
        debugMsg('GUI:fullscreen toggled');
      });
    }
  } 

  populateAutoTimerOptions() {
    const populatedChoices = {};
    const selectChoicesAttr = 'data-select-choices';
    const selectChoicesElements = document.querySelectorAll(`[${selectChoicesAttr}]`);
    const api = new API();

    selectChoicesElements.forEach((el) => {
      populatedChoices[el.getAttribute(`${selectChoicesAttr}`)] = new Choices(el, this.choicesConfig);
    });

    api.getTags().then((result) => {
      populatedChoices['tags'].setChoices([]);
    }).catch(e => console.warn(e));
    
    api.getAllServices().then((result) => {
      const opts = result['bouquets'].map((bouquet) => {
        return {
          label: bouquet.name,
          choices: bouquet.channels,
        }
      });
      populatedChoices['bouquets'].setChoices(
        result['bouquets'],
        'sRef',
        'name',
        false,
      );
      populatedChoices['channels'].setChoices(
        opts,
        'sRef',
        'name',
        false,
      );
    }).catch(e => console.warn(e));

    return populatedChoices;
  }
} 

class OWIF { 
  constructor() {
    this.stb = new STB();
    this.api = new API();
    this.gui = new GUI();
  }
}

window.owif = new OWIF();
