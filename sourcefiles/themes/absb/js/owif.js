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
}

class GUI { 
  constructor() {}
  
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
} 

class OWIF { 
  constructor() {
    this.stb = new STB();
    this.api = new API();
    this.gui = new GUI();
  }
}

const owif = new OWIF();
