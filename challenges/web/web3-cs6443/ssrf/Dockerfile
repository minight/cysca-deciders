FROM python:3.6-alpine3.7

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.7/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.7/community" >> /etc/apk/repositories

RUN \
 echo "**** install build packages ****" && \
 apk add --no-cache --virtual=build-dependencies \
	autoconf \
	automake \
	freetype-dev \
	g++ \
	gcc \
	jpeg-dev \
	lcms2-dev \
	libffi-dev \
	libpng-dev \
	libwebp-dev \
	linux-headers \
	make \
	openjpeg-dev \
	python3-dev \
	tiff-dev \ 
	zlib-dev && \
 echo "**** install runtime packages ****" && \
 apk add --no-cache \
	curl \
	freetype \
	git \
	lcms2 \
	libjpeg-turbo \
	libwebp \
	openjpeg \
	p7zip \
	py3-lxml \
	python3 \
	tar \
	tiff \
	unrar \
	unzip \
	vnstat \
	wget \
    uwsgi-python3 \
	xz \
    musl-dev \
	zlib && \
# fuck this noise i have to recompile the entire thing
apk add --no-cache \ 
    postgresql-dev  && \
 echo "**** use ensure to check for pip and link /usr/bin/pip3 to /usr/bin/pip ****" && \
 python3 -m ensurepip && \
 rm -r /usr/lib/python*/ensurepip && \
 if \
	[ ! -e /usr/bin/pip ]; then \
	ln -s /usr/bin/pip3 /usr/bin/pip ; fi && \
 echo "**** install pip packages ****" && \
 pip install --no-cache-dir -U \
	pip \
	setuptools && \
 pip install --no-cache-dir -U \
	configparser \
    dumb-init \
	ndg-httpsclient \
	notify \
	paramiko \
	pillow \
	psutil \
	requests \
	setuptools \
	urllib3 \
    psycopg2 \
	virtualenv && \
 echo "**** clean up ****" && \
 apk del --purge \
	build-dependencies && \
 rm -rf \
	/root/.cache \
	/tmp/*

COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

ENV UWSGI_INI /app/uwsgi.ini

EXPOSE 80

COPY app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

COPY app /app
RUN pip3 install --no-cache-dir -e .

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]

CMD ["ash", "/wait-for-postgres.sh", "db:5432", "--", "uwsgi", "--ini", "/etc/uwsgi/uwsgi.ini", \
              "--die-on-term"]


