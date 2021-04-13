
[![Build Python2](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/actions/workflows/python2.yml/badge.svg)](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/actions/workflows/python2.yml)
[![Build Python3](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/actions/workflows/python3.yml/badge.svg)](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/actions/workflows/python3.yml)

# OpenWebif
OpenWebif is an open source web interface for Enigma2-based set-top boxes (STBs).

## Documentation
[e2openplugin-OpenWebif’s documentation](https://e2openplugins.github.io/e2openplugin-OpenWebif/)

## Found a Problem / Issue / Bug / Missing Feature?
See if it's already been [logged](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/issues)
Otherwise, feel free to log a new issue or request.

Please provide as much information as possible!

You'll need to enable `Debug - Display Tracebacks in browser` either
- from `OpenWebif configuration`, which can be found in your receiver's `Plugins` page.
or 
- by adding `config.OpenWebif.displayTracebacks=true` to `/etc/enigma2/settings`

Along with the steps you took that lead to the issue, the following are useful:
- Your OS or device (macOS / Win / Android / Apple ...)
- OS or device version (High Sierra / Win10 / Android 11 / iOS12 ...)
- Browser (Brave / Chrome / Firefox / Safari / Edge ...)

*Remember - the more ~money we get~ info we have, the quicker we'll be able to troubleshoot!*

We don't have every variation of setup at our disposable, so...

If possible, even more useful to include are:
- Whether the problem is constant or intermittent
- Whether the issue happens on just one or several browsers
- Screenshots - A picture really is worth a thousand words!!

## Want to Help Translate?
Feel free to update an existing [language file](locale/) or create a new one by using
the [template](locale/OpenWebif.pot)

## API Wiki
[Link](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/wiki/OpenWebif-API-documentation)

## Screenshots
[Link](screenshots/SCREENSHOTS.md)

## Latest [Bandit](https://wiki.openstack.org/wiki/Security/Projects/Bandit) Report
[Link](https://e2openplugins.github.io/e2openplugin-OpenWebif/bandit.html) 

## Latest [JSHint](http://jshint.com/) Reports
[Link1](https://e2openplugins.github.io/e2openplugin-OpenWebif/jshint1_report.txt)
[Link2](https://e2openplugins.github.io/e2openplugin-OpenWebif/jshint2_report.txt)

## Latest [Flake8](http://flake8.pycqa.org/) Report
[Link](https://e2openplugins.github.io/e2openplugin-OpenWebif/flake8_report.txt)

## License
Licensed under the GNU General Public License, Version 3. See [LICENSE](LICENSE.txt) for more details.

## Latest Package

Download the most recent [OpenWebif ipk package](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/tree/gh-pages)

### Installation

```bash
# Remotely logged in via Telnet/SSH to enigma2 device
cd /tmp
init 4                        # graceful enigma2 shutdown
# fetching -- wget '<URL of .ipk file>'
# example:
wget 'https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/raw/gh-pages/enigma2-plugin-extensions-openwebif_1.4.0-latest_all.ipk'
# installing -- opkg install <.ipk file>
# example:
opkg install ./enigma2-plugin-extensions-openwebif_1.4.0-latest_all.ipk
init 3                        # start enigma2 again
```

## Development Information

The **Changelog** is available [here](CHANGES.md).

### Dependencies
The following additional packages need to be installed:

    python-pprint
    python-cheetah
    python-json
    python-unixadmin
    python-misc
    python-twisted-web
    python-pyopenssl
    python-compression
    python-ipaddress
	python-six (>= 1.14)

_(Dependencies should be handled by using ipkg/opkg packages)_

### File Paths ###
OpenWebif files are located on the Enigma2 box at `/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif`

On non-dev builds, `.tmpl` files will need to be generated to .py 
- connect to the stb (eg. `ssh root@boxip`)
- manually delete the .pyc/.pyo file(s) associated with the 
  template(s) you've modified (enigma2 will regenerate them)
`cheetah compile --nobackup --iext=.tmpl -R /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/`
- restart Twisted server by going to `/web/restarttwisted` in the browser
or
- restart Enigma2 `init 4 && init 3`

---

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
Twisted server or Enigma2!

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
