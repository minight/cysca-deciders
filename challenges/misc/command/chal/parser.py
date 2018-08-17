#!/usr/bin/env python2
# coding=utf-8
# Mostly copied from pwnable.kr CMD3 but made slightly easier
import base64, random, math
import os, sys, time, string
from threading import Timer

TIME = 60
class MyTimer():
	global filename
        timer=None
        def __init__(self):
                self.timer = Timer(TIME, self.dispatch, args=[])
                self.timer.start()
        def dispatch(self):
                print 'time expired! bye!'
		sys.stdout.flush()
                os._exit(0)

def filter(cmd):
	blacklist = '` !&|"\'*'
	for c in cmd:
		if ord(c)>0x7f or ord(c)<0x20: return False
		if c.isalnum(): return False
		if c in blacklist: return False
	return True

if __name__ == '__main__':
        MyTimer()
        sys.stdout.write('? ')
        sys.stdout.flush()
        cmd = raw_input()
        #¯\_(ツ)_/¯
        if(cmd != "¯\_(ツ)_/¯"):
            os._exit(0)
	os.system("ls -al")
	os.system("ls -al jail")
	try:
		while True:
			sys.stdout.write('$ ')
			sys.stdout.flush()
			cmd = raw_input()
			if filter(cmd) is False:
				print 'caught by filter!'
				sys.stdout.flush()
				raise 1

			os.system('echo "{0}" | base64 -d - | env -i PATH=jail /bin/rbash'.format(cmd.encode('base64')))
			sys.stdout.flush()
	except:
		os._exit(0)
		
