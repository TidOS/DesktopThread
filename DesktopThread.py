#!/usr/bin/env python3
# A script to post in a desktop thread or start a new one if one isn't open
# Plan to support 4chan pass login
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import configparser
import os
import argparse
import time
import requests
import json
from pprint import pprint
from datetime import datetime as dt

captchatime = 0
config = configparser.ConfigParser()
config.read("desktopthread.cfg")
    
parser = argparse.ArgumentParser(description='Post desktop on /g/')
parser.add_argument("-G", "--gold", help="sign into 4chan gold", action="store_true")

args = parser.parse_args()
if args.gold:
    print ("gold account detected")
else:
    #how long to give poster to solve captcha
    captchatime = 20

if(config['system']['webdriver'].lower() == "chromedriver"):
    browser = webdriver.Chrome()
elif config['system']['webdriver'].lower() == "geckodriver":
    browser = webdriver.Firefox()
else:
    print("incorrect webdriver value in desktopthread.cfg, use chromedriver or geckodriver")
    exit(1)

if args.gold:
    print("signing into 4chan gold...")
    browser.get("https://sys.4channel.org/auth")
    token = browser.find_element_by_id("field-id")
    pin = browser.find_element_by_id("field-pin")
    token.send_keys(config['pass']['token'])
    pin.send_keys(config['pass']['pin'])
    pin.submit()
    #wait at most 5 seconds for the logout button to show up before moving on and
    #just going to /g/
    timeout = 5
    try:
        element_present = EC.presence_of_element_located((By.ID, 'logout-form'))
        WebDriverWait(browser, timeout).until(element_present)
    except TimeoutException:
        print =("Timed out waiting for page to load or login failed?")

#browser.get('https://boards.4chan.org/g')
print ("on /g/, about to look for desktop thread")

#going to use JSON API instead of this...
#searchbox = browser.find_element_by_id("search-box")
#searchbox.send_keys("desktop thread")
#searchbox.send_keys(Keys.ENTER)


r = requests.get('https://a.4cdn.org/g/catalog.json')
r = r.json()

def gen_chan():
    for idx, page in enumerate(r):
        for thread in r[idx]['threads']:
            yield thread

def get_threads(key: str, default='NaN'):
    return threads.get(key,default)
found = False
for threads in gen_chan():
    com = get_threads('com')
    no = get_threads('no')
    #print(str(no) + ": " + com)

    if "desktop thread" in com.lower():
        print("desktop thread found at " + str(no))
        found = True
        break

comment="is this the current desktop thread?"
if found:    
    browser.get("https://boards.4channel.org/g/thread/" + str(no))
else:
    print("no desktop thread found, going to /g/ main page")
    browser.get("https://boards.4channel.org/g/")
    comment = "this is the new desktop thread"

browser.find_element_by_id("togglePostFormLink").click()
browser.find_element_by_name("com").send_keys(comment)
