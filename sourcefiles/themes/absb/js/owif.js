'use strict';

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
        console.log('GUI:fullscreen activated');
      });
    } else if (state === false) {
      screenfull.exit().then(() => {
        console.log('GUI:fullscreen deactivated');
      });
    } else {
      screenfull.toggle(el).then(() => {
        console.log('GUI:fullscreen toggled');
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
