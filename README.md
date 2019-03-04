[![Build status](https://teamcity.sadovskiy.net/guestAuth/app/rest/builds/buildType:(id:GoodlineIptv_Build)/statusIcon.svg)](https://teamcity.sadovskiy.net/viewType.html?buildTypeId=GoodlineIptv_Build)

# Goodline TV channels parser and converter
Playlist, icons and EPG capturer and converter for Goodline "BolshoeTV".

## Usage on command-line
`import_goodline_iptv.py --out-dir /tmp/goodline --encoding cp1251 --timezone +0700 --pretty-xmltv --verbosity 3 `

## Usage on Docker
`docker exec -it goodline_iptv -e LOG_LEVEL=3`
