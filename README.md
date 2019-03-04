[![Build status](https://teamcity.sadovskiy.net/guestAuth/app/rest/builds/buildType:(id:GoodlineIptv_Build)/statusIcon.svg)](https://teamcity.sadovskiy.net/viewType.html?buildTypeId=GoodlineIptv_Build)

# Goodline TV channels parser and converter
Playlist, icons and EPG capturer and converter for Goodline "BolshoeTV".

## Usage on command-line
`import_goodline_iptv.py --out-dir /tmp/goodline --encoding cp1251 --timezone +0700 --pretty-xmltv --verbosity 3 `

## Docker
`docker run -it --rm --name proba -e LOG_LEVEL=3 -v /store/app/goodline_iptv/out:/var/lib/goodline_iptv docker.sadovskiy.net/goodline_iptv`

## Docker-compose by cron

`0 * * * * /usr/local/bin/docker-compose -f /store/app/goodline_iptv/docker-compose.yml --project-directory /store/app/goodline_iptv/ up > /dev/null 2>&1`
