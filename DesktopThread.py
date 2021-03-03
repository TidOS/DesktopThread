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

captchatime = 20
config = configparser.ConfigParser()
config.read("desktopthread.cfg")
    
parser = argparse.ArgumentParser(description='Post desktop on /g/')
parser.add_argument("-G", "-g", "--gold",              help="sign into 4chan gold", action="store_true")
parser.add_argument("-F", "-f", "--file",    type=str, help="absolute path to file for upload, overrides config file")
parser.add_argument("-N", "-n", "--name",    type=str, help="Name to use when posting")
parser.add_argument("-S", "-s", "--sub",     type=str, help="Subject to use if a new thread is made")
parser.add_argument("-C", "-c", "--comment", type=str, help="Comment to use when posting")
parser.add_argument("-T", "-t", "--new",               help="Post a new thread even if one exists", action="store_true")
parser.add_argument("-X", "-x", "--headless",          help="Enable headless mode for webdriver", action="store_true")
parser.add_argument("-D", "-d", "--debug",             help="Enable debug messages", action="store_true")
args = parser.parse_args()

messagemode = False
if "y" in config['system']['debug'].lower() or args.debug:
    messagemode = True

if args.gold:
    if messagemode:
        print("gold account usage requested")

#find our file name
filename = ""
if args.file:
    filename = args.file
else:
    if config['top']['staticfile'].lower == "yes":
            filename = config['top']['staticpath']
    else:
        os.system(config['top']['scrot-cmd'])
        filename = config['top']['scrot-file']


if(config['system']['webdriver'].lower() == "chromedriver"):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    if not args.gold:
        if args.headless or config['system']['headless']:
           print("WARNING: you cannot use headless mode without a gold account")
        chrome_options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2})
        browser = webdriver.Chrome('chromedriver',options=chrome_options)
    else:
        if args.headless or config['system']['headless']:
            if messagemode:
                print("headless mode and gold mode")
            chrome_options.add_argument("--headless")
        browser = webdriver.Chrome('chromedriver',options=chrome_options)

elif config['system']['webdriver'].lower() == "geckodriver":
    from selenium.webdriver.firefox.options import Options
    browser = webdriver.Firefox()
else:
    print("incorrect webdriver value in desktopthread.cfg, use chromedriver or geckodriver")
    exit(1)

#4chan gold account sign-in, message if no-gold
golduser = False
if args.gold or "y" in config['pass']['gold'].lower():
    golduser = True
    if messagemode:
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
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'msg-success'))
        WebDriverWait(browser, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load or login failed?")

#browser.get('https://boards.4chan.org/g')
if messagemode:
    print("on /g/, about to look for desktop thread")

#load up all threads on board using json api
#currently we look for OP posts containing "desktop thread"
#the first such thread we take as our thread - in the future
#we could look at all threads that match and choose the best 
#one based on current replies (is one about to die or was the
# one we found started prematurely?)
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
    sub = get_threads('sub')
    no = get_threads('no')
    #desktop thread search string
    if "desktop thread" in com.lower()or "desktop thread" in sub.lower():
        if messagemode:
            if not args.new or "y" in config['post']['forcenewthread'].lower():
                print("desktop thread found at " + str(no))
        if args.new or "y" in config['post']['forcenewthread'].lower():
            if messagemode:
                print("found a thread but starting a new one anyway")
            break
        found = True
        break


#fill comment field
#note, the command to capture the screen is above, search for
#"scrot-command" to find it above
comment=""
subject="Desktop Thread"
#desktop thread was found
if found:
    if   args.comment:
        comment = args.comment
    else:
        comment = config['post']['oldthreadcomment']
    browser.get("https://boards.4channel.org/g/thread/" + str(no))
    browser.find_element_by_id("togglePostFormLink").click()
#no desktop thread was found
else:
    if messagemode:
        if not args.new or "y" in config['post']['forcenewthread'].lower():
            print("no desktop thread found, going to /g/ main page")
    browser.get("https://boards.4channel.org/g/")
    browser.find_element_by_id("togglePostFormLink").click()
    if args.comment:
        comment = args.comment
    else:
        comment = config['post']['newthreadcomment']
    if args.sub:
        subject = args.sub
    else:
        subject = config['post']['subject']
    #subject field only available if making new thread
    browser.find_element_by_name("sub").send_keys(subject)
#comment field always available so it's outside loop above
browser.find_element_by_name("com").send_keys(comment)


#fill name field
name="Anonymous"
if args.name:
    name = args.name
else:
    name = config['post']['name']
browser.find_element_by_name("name").send_keys(name)

#fill file field
if messagemode:
    print("going to upload" + filename)
uploader = browser.find_element_by_name("upfile")
uploader.send_keys(filename)

#this section waits for an entry in the recaptcha verification box
#if we're a gold user we skip this and go straight to posting
if not golduser:
    if messagemode:
        print("waiting for captcha response for " + str(captchatime))
    
    WebDriverWait(browser, captchatime).until(lambda driver: 
    browser.find_element_by_xpath("//*[@id=\"g-recaptcha-response\"]").get_attribute("value").strip() != '')
    
    if messagemode:
        print("received key")


#IMPORTANT - commented to avoid posting while testing
if messagemode:
    print("posting!")

#uncomment to actually post
browser.find_element_by_name("post").submit()

#currently will only work if a new thread is found, 
#TODO:  fix that, just get address from the new thread
#should be easy
if "y" in config['system']['openbrowserafterpost'].lower():
    os.system(config['system']['mybrowserpath'] + " https://boards.4channel.org/g/thread/" + str(no))