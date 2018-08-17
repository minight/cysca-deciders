from ubuntu:16.04


RUN apt-get update && apt-get install -y \
	socat \
	python

RUN useradd -r chal
USER chal
COPY chal /chal

WORKDIR "/chal"
ENTRYPOINT ["./socat.sh"]
EXPOSE 9999
