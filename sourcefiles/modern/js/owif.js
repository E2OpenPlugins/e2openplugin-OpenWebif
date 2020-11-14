'use strict';

const debugTagStyle = 'color: #fff; font-weight: bold; background-color: #333; padding: 2px 4px 1px; border-radius: 2px;';

const debugMsg = (msg) => {
  console.info('%cOWIF', debugTagStyle, msg);
}
class Utils { 
  constructor() {}

  getStrftime(epoch = new Date()) {
    const theDate = new Date(Math.round(epoch) * 1000);
    let theTime = strftime('%X', theDate);
    // strip seconds without affecting localised am/pm
    theTime = theTime.match(/\d{2}:\d{2}|[^:\d]+/g).join(' ');
    return strftime('%a %x', theDate) + ' ' + theTime;
  }

  getToTimeText(beginTime, endTime) {
    const oneDayInMs = 86400000;
    const msDifference = (endTime - beginTime);
    const fullDaysDifference = Math.floor(msDifference / oneDayInMs);

    const beginDay = new Date(Math.round(beginTime) * 1000).getDay();
    const endDay = new Date(Math.round(endTime) * 1000).getDay();

    let diffString = '';
    if (msDifference === 0) {
      diffString = '-'; // eg. zap timer
    } else {
      let endTimeOnly = strftime('%X', new Date(Math.round(endTime) * 1000));
      endTimeOnly = endTimeOnly.match(/\d{2}:\d{2}|[^:\d]+/g).join(' ');
      if (fullDaysDifference < 1 && (endDay - beginDay === 0)) {
        diffString = 'same day - ' + endTimeOnly;
      } else if (fullDaysDifference < 2 && (endDay - beginDay === 1)) {
        diffString = 'next day - ' + endTimeOnly;
      } else {
        diffString = this.getStrftime(endTime);
      }
    }

    return diffString;
  }
}

class STB { 
  constructor() {}
}

class API { 
  constructor() {}

  async getStatusInfo() {
    let response = await fetch('/api/statusinfo');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      const jsonResponse = await response.json();
      return await jsonResponse;
    }
  }

  async getTags() {
    let response = await fetch('/api/gettags');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      const jsonResponse = await response.json();
      return await jsonResponse['tags'];
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
            bouquetName: bouquet['servicename'],
            extendedName: name + '<small>' + bouquet['servicename'] + '</small>',
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
    searchResultLimit: 100,
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
      if (el.getAttribute(`${selectChoicesAttr}`) === 'tags') {
        // this.choicesConfig.addItems = true;
        // this.choicesConfig.editItems = true;
        this.choicesConfig.shouldSort = true;
      } else {
        this.choicesConfig.shouldSort = false;
      }
      // this.choicesConfig.addItems = true;
      // this.choicesConfig.editItems = true;
      populatedChoices[el.getAttribute(`${selectChoicesAttr}`)] = new Choices(el, this.choicesConfig);
    });

    api.getTags().then((result) => {
      result.sort();
      const opts = result.map((tag) => {
        return {
          value: tag,
          label: tag,
        }
      });
      populatedChoices['tags'].setChoices(
        opts,
        'value',
        'label',
        false,
      );
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
        'extendedName', //'name',
        false,
      );
    }).catch(e => console.warn(e));

    return populatedChoices;
  }
} 

class OWIF { 
  constructor() {
    this.utils = new Utils();
    this.stb = new STB();
    this.api = new API();
    this.gui = new GUI();
  }
}

window.owif = new OWIF();