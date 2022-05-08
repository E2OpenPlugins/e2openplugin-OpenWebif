'use strict';

import screenfull from 'screenfull';

const debugTagStyle = 'color: #fff; font-weight: bold; background-color: #333; padding: 2px 4px 1px; border-radius: 2px;';

const debugMsg = (msg) => {
  console.info('%cOWIF', debugTagStyle, msg);
}
class Utils { 
  constructor() {
    self = this;
  }

  // TODO: honour owif log setting
	debugLog = (...args) => console.debug(...args);

	regexDateFormat = new RegExp(/\d{4}-\d{2}-\d{2}/);

  // convert html date input format (yyyy-mm-dd) to serial
  // JSDoc
  // /**
  //  * Convert a string containing two comma-separated numbers into a point.
  //  * @param {string} str - The string containing two comma-separated numbers.
  //  * @return {Point} A Point object.
  //  */
	toUnixDate = (date) => (Date.parse(`${date}Z`)) / 1000; // `Z` is UTC designator

  // 1:134:1 is bouquetroot
  isBouquet = (sref) => (!sref.startsWith('1:134:1') && sref.includes('FROM BOUQUET'));

  fetchData = async (url, options = { method: 'get', ...{} }) => {
    try {
      const response = await fetch(url, options);

      if (response.ok) {
        const contentType = response.headers.get('content-type');
        self.debugLog(contentType);
        if (!!contentType && contentType.includes('application/json')) {
          const responseJson = await response.json();
          return responseJson;
        } else {
          // eg. application/xhtml+xml
          const responseText = await response.text();
          return xml2json(responseText);
        }

      } else {
        throw new Error(response.statusText || response.status);
      }
    } catch (ex) {
      throw new Error(ex);
    };
  }

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

  async getAllServices(noiptv,cuttitle) {
    let niptv = (noiptv==true) ? "&noiptv=1" : "";
    let response = await fetch('/api/getallservices?nolastscanned=1' + niptv);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      const jsonResponse = await response.json();
      let allChannels = [];
      const bouquets = jsonResponse['services'].map((bouquet) => {
        const bouquetChannels = bouquet['subservices'].map((channel) => {
          const name = channel['servicename'];
          let sRef = channel['servicereference'];
          const isMarker = (sRef.indexOf('1:64:') > -1);
					if(cuttitle) {
						const li = sRef.lastIndexOf("::");
						if(li>0) {
							sRef = sRef.substring(0,li-1);
						}
					}
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

  async sendKeyboardText(text) {
    const response = (typeof text == 'undefined') ? {'ok': false, 'status': 'Empty request'} : await fetch(`/api/remotecontrol?text=${text}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    } else {
      const jsonResponse = await response.json();
      callScreenShot(); // TODO: modernise
      return jsonResponse;
    }
  }

}

class GUI { 
  constructor() {
    this.initEventHandlers();
  }

  /* TODO: i10n */
  choicesConfig = {
    removeItemButton: true,
    duplicateItemsAllowed: false,
    resetScrollPosition: false,
    shouldSort: false,
    searchResultLimit: 100,
    placeholder: true,
    // renderSelectedChoices: 'always',
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

  initEventHandlers() {
    const self = this;

    const re = new RegExp(/#\/?(.*)\??(.*)/gi);
  
    function locationHashChanged(evt) {
      const hash = evt.target.location.hash;
      // TODO: transition all hash urls to #/ format
			const targetPage = hash.replace('#/', '#').split('/')[0];
			const targetUrl = targetPage.replace(re, '\/ajax/$1');
      targetPage && load_maincontent_spin(targetUrl);
    } 
  
    window.onhashchange = locationHashChanged;  

    document.querySelectorAll('input[name="skinpref"]').forEach((input) => {
      input.onchange = () => {
        self.skinPref = event.target.value;
      }
    });
  }
  
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

  get skinPref() {
    return document.body.dataset.skinpref || '';
  }

  set skinPref(newValue) {
    const self = this;
    const cssClassPrefix = 'skin--';
    const oldValue = self.skinPref;

    // TODO: success/failure message
    fetch(`/api/setskincolor?skincolor=${newValue}`);

    document.body.classList.replace(`${cssClassPrefix}${oldValue}`, `${cssClassPrefix}${newValue}`);
    document.body.dataset.skinpref = newValue;
  }

  preparedChoices() {
    const populatedChoices = {};
    const selectChoicesAttr = 'data-choices-select';
    const selectChoicesElements = document.querySelectorAll(`[${selectChoicesAttr}]`);

    selectChoicesElements.forEach((el) => {
      let elConfig = el.dataset['choicesConfig'] || '{}';
      elConfig = (elConfig) ? JSON.parse(elConfig) : {};
      elConfig = Object.assign({}, this.choicesConfig, elConfig);
      populatedChoices[el.getAttribute(`${selectChoicesAttr}`)] = new Choices(el, elConfig);
    });

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