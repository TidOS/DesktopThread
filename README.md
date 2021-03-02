# DesktopThread
DesktopThread is a python script that uses Selenium to post in desktop threads on 4channel's /g/ board (could be any board really)

# Setup

 1. First, copy sample.cfg to desktopthread.cfg
 2. Edit desktopthread.cfg to suit your tastes  
    	 - TODO:  add explanations for options, make configurator
    	 - NOTE:  config file subject to change version to version until the program is "done".  At present, not all options in the config file may be implemented in the script
 3. Get [chromedriver](https://chromedriver.chromium.org) and make sure it is in your PATH variable, make sure chrome is installed
	 - I expect to support geckodriver in the future but for now I'm not testing it
	 - TODO: Possibly automate this sometime - download to current directory and use?
4. Install the required modules with pip
`pip install -r requirements.txt`
5. Uncomment the last line of the script.  If you don't, nothing will be posted.  Leave it commented while you see if everything is working then uncomment when you're confident you're making the post you mean to make.

# Usage
As of now...

        usage: DesktopThread.py [-h] [-G] [-F FILE] [-N NAME] [-S SUB] [-C COMMENT] [-T] [-X] [-D]  
      
    Post desktop on /g/  
      
    optional arguments:  
    -h, --help show this help message and exit  
    -G, -g, --gold sign into 4chan gold  
    -F FILE, -f FILE, --file FILE  
    absolute path to file for upload, overrides config file  
    -N NAME, -n NAME, --name NAME  
    Name to use when posting  
    -S SUB, -s SUB, --sub SUB  
    Subject to use if a new thread is made  
    -C COMMENT, -c COMMENT, --comment COMMENT  
    Comment to use when posting  
    -T, -t, --new Post a new thread even if one exists  
    -X, -x, --headless Enable headless mode for webdriver  
    -D, -d, --debug Enable debug messages
Generally, items in your config file should be overridden by the commandline flags.  If it's not working correctly, set the option in the config file and do not use commandline flag.  Headless mode can only be used when using a 4chan pass.  If you use it without using the "gold" account, the browser will open non-headless so you can solve the captcha.
