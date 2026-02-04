FROM lscr.io/linuxserver/calibre-web:latest

WORKDIR /app/calibre-web

COPY . /app/calibre-web

RUN chown -R abc:abc /app/calibre-web
