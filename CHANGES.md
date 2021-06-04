## Version 1.4.8
## (in development)
* add recording type to timer api

## Version 1.4.7
* add filter paramter to ipkg api

## Version 1.4.6
* fix memory leak in movielist by using internal code #751

## Version 1.4.5
* fix sleeptimer #1295
* fix terminal for VTi #1293

## Version 1.4.4
* improve api movielist recursive #1241

## Version 1.4.3
* improve ipkg
* use responsive UI for mobile devices

## Version 1.4.2
* add new api getpicon

## Version 1.4.1
* add new api getserviceref

## Version 1.4.0
* support python 3
* huge update for the responsive UI by wedebe

## Version 1.3.9
* fix #1016,#1017

## Version 1.3.8
* BQE: import bouquets via json
* moviedetails api
* epgsearch orbital info #994
* fix #967,#980

## Version 1.3.7
* fix channel numbering #939
* fix timer addTimerByEventId #946
* improve iptv support

## Version 1.3.6
* add new movieinfo api to modify recording info (tags, title, cuts)
* deprecate movietag api

## Version 1.3.5
* add picon value to getservices request #849
* add genre to epg result #847
* add mount info for xml results #850

## Version 1.3.4
* Autotimer backup/restore

## Version 1.3.3
* get group members of alternative group in servicelist of bqe
* improve channel numbering for bqe

## Version 1.3.2
* reorg i18n
* move some code to new defaults controller
* optimize web api for UI settings

## Version 1.3.1
* add net api mount manager
* fix encoding issue #772
* add settings to modify recording locations / bookmarks
* add timer sort feature #697
* fix edit timer tags #732

## Version 1.3.0
* add responsive design from VTi Team
* RESTful API with OpenAPI specification
* new config api

## Version 1.2.8
* new file api
* new RESTful API with OpenAPI specification
* allow timers for IPTV / #715

## Version 1.2.7
* improve file api
* use sass for css
* improve css files
* improve picon path handling

## Version 1.2.6
* improve recording move to trash / #633
* improve edit timer / #631
* fix some bandit issues

## Version 1.2.5
* improve remote control / #603
* app timeshift api / #551
* show filesize / #493
* show weekday for timer and recording / #541
* improve edit timer / #463
* show date on mobile epg info / #366
* fix edit timer / #624
* improve now/next api
* fix CVE 2017-9807 / #620
* improve package manager / #608

## Version 1.2.4
* show boxname in title / #528
* fix autotimer preview / #589
* fix autotimer create / #581
* fix several box pictures and remote controls
* fix timer epg encoding bug 
* update locale
* add removeFolder to removelocations / #593
* improve bqe channel numbering / #239

## Version 1.2.1
* fix shift detection on standby button
* add missing theme images

## Version 1.1.0
* reduce package size
* allow remove mobile, webtv, themes without any impact to reduce the package size again
-> remove the folder /public/webtv and/or mobile and/or themes 
* add fancontrol2 webif to extras / #453
* improve mutliepg / #462
* improve channel list / #461
* now button in timeline multiepg / #466
* show timer in timeline multiepg / #460

### TODO
* powertimer api
* improve package manager

## Version 1.0.4
* improve access security
* add package manager
* use jquery UI offline

## Version 1.0.3
* add web tv / #422
* improve timer conflicts / #339
* improve movielist api
* improve box info

## Version 1.0.2
* add conflict info to add timer api
* fix timer conflicts / #339
* fix display tuner state in box info / #204
* update mobile webinterface / #350
* improve bouquet editor / #419
* minor UI fixes / #421

## Version 1.0.1
* improve theme support
* update translations
* fix settings
* new second multiepg / #36 #267
* show orbital position in current info / #188
* fix very old timer list issue / #410 , #411

## Version 1.0.0
**FEATURES**
* removed "Smart services renaming for XBMC" and replaced with url parameter "renameserviceforxmbc=1" for getallservices 
* new theme setting
* allow sort recordings
* update jQuery and jQuery UI
* use fontawesome for some images
* add oscam webif to extras
* allow open (tv,radio,recording,timer,multiepg) with direct link
* fix settings save issue
* improve bouquet editor
* reorg main menu
* quit support for very old browser (with no html5 support)
Thanks to MDXDave for some ideas to improve the UI

## Version 0.4.9
**FEATURES**
* new api call epgservicelistnownext

## Version 0.4.8
**FEATURES**
* get movie text info
* improve movie trash
* improve timers for radio
* deprecated -> "Smart services renaming for XBMC" use url parameter "renameserviceforxmbc=1" for getallservices instead 

## Version 0.4.7
**FEATURES**
* improve edit movie tags

## Version 0.4.6
**FEATURES**
* add more supported box models

**FIXES**
* translations
* encoding problems
* owbranding
* streaming problems
* parental control

## Version 0.4.5
**FEATURES**
* add movie trash features
* improve movie move and rename
* epg search as modal dialog
* channel epg as modal dialog
* add vps option to timer dialog

## Version 0.4.4
**FEATURES**
* add vps channel api
* improve file security

## Version 0.4.3
**FEATURES**
* add epgsearch endtime option
* add svenska language
* update french language
* add new timer type
* add toggle timer api

**FIXES**
* satlist orbital sort

## Version 0.4.2
**FEATURES**
* ipkg add full package list api
* full add full movie list api

**FIXES**
* sleeptimer crash

## Version 0.4.1
**FEATURES**
* show lastseen postion for recordings
* autotimer settings editor
* epgrefresh webif

**FIXES**
* autotimer editor
* delete timer

## Version 0.4.0
**FEATURES**
* bouqueteditor webif
* autotimer webif
* new recording list design
* new timer list design
* several css and html performance optimizations
* extend movietags api
* use gzip encoding for large lists

**FIXES**
* edit timer

## Version 0.3.0
**FEATURES**
* mobile interface timer add/delete
* spanish translation
* prepare autotimer API
* prepare bouqueteditor API

**FIXES**
* vps plugin API
* epgrefresh API
* mobile interface zap channel

## Version 0.2.9
**FEATURES**
* add gzip high speed epg requests

**FIXES**
* fix settings
* show full recording description

## Version 0.2.8
**FEATURES**
* add gzip high speed opkg list command

**FIXES**
* fix bouqueteditior backup/restore

## Version 0.2.7
**FEATURES**
* update transcoding API to latest transcoding features

## Version 0.2.6
**FEATURES**
* add translation support
* display standby / recording state in header

**FIXES**
* improve current info while movie playing
* fix standby state info
* fix currently playing info at header

## Version 0.2.5
**FEATURES**
* support movielist subfolders
* support movielist zip dump
* support vps plugin api

## Version 0.2.4
**FEATURES**
* support multiple DVB streams at the same time

## Version 0.2.3
**FEATURES**
* add API to use STB as WOL "client" to send MagicPackets
* add API for WOLSetup plugin

## Version 0.2.2
**FEATURES**
* add API for transcoding plugin

## Version 0.2.1
**FEATURES**
* add bouqueteditior plugin api support
* add full interface option for mobile devices
* add radio bouquet on mobile interface
* add parental control for zap and stream in channel list

## Version 0.2.0
**FEATURES**
* add preparations bouqueteditior plugin api support
* add autotimer plugin api support
* add epgrefresh plugin api support
* add preparations for IPV6 support (Needs IPv6 in Python and probably newer Twisted)

## Version 0.1.8
**FEATURES**
* add alternative channels to epgnownext

**FIXES**
* Fix channel list in "Add Timer" not filling - Refs #73
* Fix all known problems with Alternatives (Issue #18 and more)

## Version 0.1.7
**FEATURES**
* add movie rename
* add movie move

**FIXES**
* playable services

## Version 0.1.6
**CHANGES**
* some images to lower size

## Version 0.1.5
**FIXES**
* parental control
* playlist remove non existing file

## Version 0.1.4
**FEATURES**
* Support more box types
* message answer
* limit file access
* update SSL support

**FIXES**
* stream sub service
* ET4000 remote

## Version 0.1.3
**FEATURES**
* Stream Port Settings
* IPKG Interface
* german "umlaute" in epgsearch

**FIXES**
* stream sub service

## Version 0.1.2
**FEATURES**
* ... TODO ...

**FIXES**
* ... TODO ...

