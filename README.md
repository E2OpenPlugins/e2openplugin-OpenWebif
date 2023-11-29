
[![Build](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/actions/workflows/build.yml/badge.svg)](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/actions/workflows/build.yml)

# OpenWebif
OpenWebif is an open source browser-based interface for Enigma2-based set-top boxes (STBs).

## Screenshots
[Classic interface](screenshots/SCREENSHOTS.md)

(TODO: add Modern interface screenshots)

## Usage
To find out how to access it from your browser, go to OpenWebif's configuration via your receiver's Plugins page. You'll see the `http...` address to use at the bottom.

## Documentation
Read the [e2openplugin OpenWebif documentation](https://e2openplugins.github.io/e2openplugin-OpenWebif/).

Browse [OpenWebif API Wiki](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/wiki/OpenWebif-API-documentation).

## Found a Problem / Issue / Bug / Missing Feature?
First, check whether it's [already been logged](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/issues).

Otherwise, feel free to log a new issue or request.

** **Always try the most recent build first to see if this solves the issue!** **

If that doesn't help, please provide as much information as possible!

You'll need to enable the `Debug | Display Tracebacks in browser` setting, either:
- through `OpenWebif configuration`, which can be found via your receiver's `Plugins` page

or 

- by adding the line `config.OpenWebif.displayTracebacks=true` to your receiver's `/etc/enigma2/settings` file

Along with the information on the steps you took that caused the issue, the following will be very useful:
- whether the issue is constant or intermittent
- if it has just recently started happening (perhaps after an update)
- screenshots - a picture really is worth a thousand words!
- whether the issue happens on just one or several browsers
  - try with a mainstream browser (Brave / Chrome / Firefox / Safari / Edge)
  - try disabling browser extensions & plugins
- if you've installed any plugins which could be related to the issue

** **Note that the more detail we get, the sooner we'll be able to investigate!** **

We have limited free time and often only have one configuration at our disposable, so...

If possible, even more helpful details to include are:
- device type and OS (Mac OS / Windows / Android / Apple ...)
- OS or device version (Monterey / Win10 / Android 11 / iOS12 ...)
- browser (Brave / Chrome / Firefox / Safari / Edge ...)

## Latest Reports

[[Bandit]](https://wiki.openstack.org/wiki/Security/Projects/Bandit):
[OpenWebif Bandit Report](https://e2openplugins.github.io/e2openplugin-OpenWebif/bandit.html) 

[[Flake8]](http://flake8.pycqa.org/):
[OpenWebif Flake8 report](https://e2openplugins.github.io/e2openplugin-OpenWebif/flake8_report.txt)

[[JSHint]](http://jshint.com/):
[Modern interface report](https://e2openplugins.github.io/e2openplugin-OpenWebif/jshint2_report.txt)
|
[Classic interface report](https://e2openplugins.github.io/e2openplugin-OpenWebif/jshint1_report.txt)

## License
OpenWebif is [licensed](LICENSE.txt) under the [GNU General Public License, Version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Latest Package

Download the most recent [OpenWebif ipk package](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/tree/gh-pages)

---

## Installation

OpenWebif is installed by default on a number of enigma2 images  

* [OpenWebif ipk full](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/raw/gh-pages/enigma2-plugin-extensions-openwebif_latest_all.ipk)

* [OpenWebif ipk vti](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/raw/gh-pages/enigma2-plugin-extensions-openwebif_latest_vti.ipk)

* [OpenWebif deb](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/raw/gh-pages/enigma2-plugin-extensions-openwebif_latest_all.deb)

To install the plugin manually:
```bash
## connect to your enigma2 device via SSH/Telnet, (eg. `ssh root@boxip`), then

# change to the temp directory
cd /tmp

# shut down enigma2 gracefully
init 4

# fetch OpenWebif ipk
wget -O openwebif.ipk https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/raw/gh-pages/enigma2-plugin-extensions-openwebif_latest_all.ipk

# install downloaded ipk file
opkg install openwebif.ipk

# restart enigma2
init 3
```

---

## Custom SSL Certificate

If you want to use your own certificate, then replace both `/etc/enigma2/key.pem` and `/etc/enigma2/cert.pem` with your own key and cert, in PEM format.

Restart Enigma2 after replacing those files.

### Using your own CA

You can also put the ca cert as `/etc/enigma2/ca.pem` and enable HTTPS Client Cert auth in settings you can even login using Client certs signed by the same CA auth.

It doesn't bypass the password login yet and you should of course use your own CA, because else any client with a key signed by that CA auth can login, as there is no option to limit access to certain users (yet, and probably newer will be).

See also #215

### Problems with a custom Certificate

Creating key and cert is beyond the scope of this readme.
I found [Ivan Ristić's openssl cookbook](https://www.feistyduck.com/books/openssl-cookbook/) helpful.

FWIW, an `ecparam` `secp384r1` key and a `ecdsa-with-SHA256` cert with 4 SAN worked just fine on the following;

```bash
root@vuduo4kse:~# date ; cat /etc/os-release 
Wed Nov 29 22:58:24 CET 2023
ID=openbh
NAME="openbh"
VERSION="5.1"
VERSION_ID=5.1
PRETTY_NAME="openbh 5.1"
```

---

## Development Information

See what's been happening, check out the [OpenWebif changelog](CHANGES.md)

### Dependencies
The following additional packages need to be installed:  
_(dependencies should be handled by using ipkg/opkg packages)_

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


### File Paths ###
The OpenWebif plugin's files are located on the enigma2 box at `/usr/lib/enigma2/python/Plugins/Extensions/OpenWebif`

On non-dev builds, `.tmpl` files will need to be generated to .py 
- connect to the stb (eg. `ssh root@boxip`)
- manually delete the .pyc/.pyo file(s) associated with the 
  template(s) you've modified (enigma2 will regenerate them)
`cheetah compile --nobackup --iext=.tmpl -R /usr/lib/enigma2/python/Plugins/Extensions/OpenWebif/controllers/views/`
- restart Twisted server by going to `/web/restarttwisted` in the browser
or
- restart enigma2 `init 4 && init 3`

---

### Updating Assets
Find out how to [make changes to OpenWebif's JS & CSS assets](sourcefiles/README.md).

