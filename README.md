[![Build Status](https://travis-ci.org/E2OpenPlugins/e2openplugin-OpenWebif.svg?branch=master)](https://travis-ci.org/E2OpenPlugins/e2openplugin-OpenWebif)

# OpenWebif
Open Source Web Interface for E2 based Linux set-top box

## Screenshots
[Link](screenshots/SCREENSHOTS.md)

## Latest [Bandit](https://wiki.openstack.org/wiki/Security/Projects/Bandit) Report
[Link](http://e2openplugins.github.io/e2openplugin-OpenWebif/bandit.html) 


## License
Licensed under the GNU General Public License, Version 3. See [LICENSE](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/master/LICENSE.txt) for more details.

## Latest Package

The most recent package may be downloaded from [here](https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/tree/gh-pages) (ipk package).

### Installation

```bash
# Remotely logged in via Telnet/SSH to enigma2 device
cd /tmp
init 4                    # graceful enigma2 shutdown
wget '<URL of .ipk file>' # e.g. https://github.com/E2OpenPlugins/e2openplugin-OpenWebif/blob/gh-pages/enigma2-plugin-extensions-openwebif_1.2.7-e2openpluginsgit20171014_all.ipk
opkg install <.ipk file>  # e.g. enigma2-plugin-extensions-openwebif_1.2.7-e2openpluginsgit20171014_all.ipk
init 3                    # start enigma2 again
```

## Development Information

## Changelog
[Link](CHANGES.md)

### Dependencies

    python-pprint
    python-cheetah
    python-json
    python-unixadmin
    python-misc
    python-twisted-web
    python-pyopenssl
    python-compression
    python-ipaddress
