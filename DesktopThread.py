#!/usr/bin/env python
# A script to post in a desktop thread or start a new one if one isn't open
# Plan to support 4chan pass login

import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import configparser
import os
import argparse
import time

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

browser=webdriver.Firefox()

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

browser.get('https://boards.4chan.org/g')

