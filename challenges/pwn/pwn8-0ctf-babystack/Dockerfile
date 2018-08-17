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

# Add the ctf dir
RUN mkdir /home/ctf

RUN chmod 775 /home/ctf

# Add the ctf user
RUN useradd -M -U\
    -d /home/ctf \
    ctf

RUN chown ctf:ctf /home/ctf
RUN dpkg --add-architecture i386
RUN apt-get update
RUN apt-get install libc6-i386

# Add the content
COPY ./binary /home/ctf/pwn
COPY xinetd.conf /etc/xinetd.conf
COPY flag /flag

# Make the binary
WORKDIR /home/ctf

# Expose the service port
EXPOSE 9091

# Clean up setup files
RUN ["chmod","775","/flag"]
RUN ["chmod","775","/home/ctf/pwn"]

CMD ["script", "-c", "xinetd -d -dontfork"]

