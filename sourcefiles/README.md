#Javascript, Styles, Fonts and Icons...

There's a choice of OpenWebif interfaces to choose from:
- `Modern` is suitable for mobile and desktop devices (also known as _responsive_)
- `Classic` is the original look and layout
- (`Mobile` will soon be removed in favour of the Modern interface)

There are a separate set of js and css files for each.

JS and CSS files are compiled and minified as part of the [CI process](CI/npm.sh).

This can also be done manually.

##Prerequisites

If you haven't already, you'll need to [install npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm#using-a-node-version-manager-to-install-nodejs-and-npm).

##Initial setup
If this is your first time working with assets on OpenWebif, you'll
need to download and install all required dependencies:

`cd` to the repo root, then run

`(cd ./sourcefiles/ && npm install)`

---

##Modern interface

```
MODERN:

/* source code */
/sourcefiles/modern
    /css/*.css
    /js/*.js and /js/*.mjs
    /fonts

/* output */
/plugin/public/modern
    /css/*.min.css
    /js/*.min.js or /js/*-app.js
    /fonts

/* browser url */
/modern
    /css/*.min.css
    /js/*.min.js or /js/*-app.js
    /fonts
```

jQuery and Bootstrap are currently used for some functionality, but the 
intention is to remove these dependencies completely from the Modern interface.

###Compile JS
`cd` to the repo root, then run

`(cd ./sourcefiles && npm run build-js)`

which minifies and saves the output to
```
/plugin/public/modern/js/
```
Upload these files to the receiver at
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/modern/js/
```

[`build-prod` (there's also a `build-dev` mode which doesn't minify output)]: #

###Compile CSS
`cd` to the repo root, then run

`(cd ./sourcefiles && npm run build-css)`

which minifies and saves the output to
```
/plugin/public/modern/css/
```
Upload these files to the receiver at
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/modern/css/
```

Simply reloading the browser page will be enough, there's no need to restart
Twisted server or enigma2!

###Fonts
The [Roboto](https://fonts.google.com/specimen/Roboto) font is served locally from 
`/modern/fonts/roboto`

###Icons
The [Material Icons font](https://fonts.google.com/icons?selected=Material+Icons) 
provides iconography, and is served locally from `/modern/fonts/materialicons`

Implementation details can be found at https://google.github.io/material-design-icons/

(Note that Material Icon versions on GitHub, NPM and the Google Fonts page are 
all out of sync. This is a [known issue](https://github.com/google/material-design-icons/issues/1284#issue-1181974345).)

---

##Classic interface

```
CLASSIC:

/* source code */
/sourcefiles
    /css
    /js
    /scss

/* output */
/plugin/public
    /css/*.min.css
    /js/*.min.js or

/* browser url */
/
    /css/*.min.css
    /js/*.min.js
```

###Compile JS
`cd` to the repo root, then run

`(cd ./sourcefiles && npm run build-classic-js)`

which minifies and saves the output to
```
/plugin/public/js/
```
Upload these files to the receiver at
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/js/
```

[`build-prod` (there's also a `build-dev` mode which doesn't minify output)]: #

###Compile CSS
`cd` to the repo root, then run

`(cd ./sourcefiles && npm run build-classic-css)`

which minifies and saves the output to
```
/plugin/public/css/
```
Upload these files to the receiver at
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/css/
```

Refresh the browser page to see any changes, there's no need to restart Twisted
server or enigma2!

### Compiling CSS Files

TODO: verify whether this information is still applicable.

The script `contrib/inotify_watcher.py` is used for compiling CSS files on
the developers host using [Sass](https://sass-lang.com/) . On linux you need to
have installed a package providing  `inotifywait` and a version that actually
supports inotify if one wants automatic compiling of CSS files on source
directory changes (For debian based distributions this would be `inotify-tools`).

macOS and Windows do not have inotify support thus the automatic compiling will
not work (yet). But if you [installed Sass](https://sass-lang.com/install) and
the `scss` binary/script is in your `PATH`, calling
`contrib/inotify_watcher.py --force-update` should work.
Alternatively, you may define environment variable `SCSS` in order to point to
the location of the scss binary/script.

Base command is

    scss -t compressed --unix-newlines --sourcemap=none "in.scss":"out.css"

---

##Mobile interface

😐
