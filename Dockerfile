FROM python:3.7 as build

WORKDIR /urs/src/goodline_iptv

COPY . .

RUN python3 ./setup.py sdist


FROM python:3.7

ENV LOG_LEVEL=0

COPY --from=build /urs/src/goodline_iptv/dist/goodline-iptv-0.2.0.tar.gz /usr/local/src/

RUN pip install --no-cache-dir /usr/local/src/goodline-iptv-0.2.0.tar.gz

CMD /usr/local/bin/import_goodline_iptv.py --out-dir /var/lib/goodline_iptv --verbosity $LOG_LEVEL
