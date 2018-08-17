# Basic Xinetd Docker Container
# Useful for anyting binary / requiring netcat

FROM debian

# Apt-get update
RUN apt-get update

# Install xinetd
RUN apt-get install -y xinetd
RUN update-rc.d xinetd disable

# Install nc for debugging
RUN apt-get install -y netcat

RUN apt-get install -y python3 python3-crypto

# Add the ctf dir
RUN mkdir /home/ctf

RUN chmod 775 /home/ctf

# Add the ctf user
RUN useradd -M -U\
    -d /home/ctf \
    ctf

RUN chown ctf:ctf /home/ctf

# Add the content
COPY binary.py /home/ctf/pwn
COPY another.py /home/ctf/fmac.py
COPY xinetd.conf /etc/xinetd.conf
COPY flag /flag.txt

# Make the binary
WORKDIR /home/ctf

# Expose the service port
EXPOSE 9091

# Clean up setup files
RUN ["chmod","775","/flag.txt"]
RUN ["chmod","775","/home/ctf/pwn"]
RUN ["chmod","775","/home/ctf/fmac.py"]

CMD ["script", "-c", "xinetd -d -dontfork"]

