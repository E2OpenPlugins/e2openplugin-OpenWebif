(TODO: this page is somewhat out of date, but will give a decent reference to start from!)

### Compiling Assets (mainly Modern interface)

If you haven't already, you'll need to [install npm](https://www.npmjs.com/get-npm)

If this is your first time working with assets on OpenWebIf, you'll
need to `cd` to the repo root, then run
`(cd ./sourcefiles/ && npm install)`
which will download and install all required dependencies.

*JavaScript Files*
Found at `./sourcefiles/modern/js`, built using the command
```
(cd ./sourcefiles/ && npm run build-js)
```
which minifies and writes to
```
./plugin/public/modern/js/
```
Upload these files to 
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/modern/js/
```

*CSS files*
Found at `sourcefiles/modern/css`, built using the command
```
(cd ./sourcefiles/ && npm run build-css)
```
which minifies and writes to
```
./plugin/public/modern/css/
```
Upload these files to 
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/modern/css/
```

Simply reloading the browser page will be enough, there's no need to restart 
Twisted server or enigma2!

---

### Compiling Assets (Classic interface)

For the classic/old interface:

*JavaScript Files*
Found at `./sourcefiles/js`, built using the command
```
(cd ./sourcefiles/ && npm run build-classic-js)
```
which minifies and writes to
```
./plugin/public/js/
```
Upload these files to 
```
/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/public/js/
```

### Compiling CSS Files

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
