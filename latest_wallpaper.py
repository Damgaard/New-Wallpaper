#!/usr/bin/env python

"""
Created 6 January 2012
By: Andreas Damgaard Pedersen

This program goes on praw and finds a wallpaper from
one of the wallpaper related subreddits that I like.
It then update my desktop bagground with the new image.
Updating of background only on a linux running gnome desktop
 
 ===========
 Potential features to add
 ===========

Allow to get from top pictures instead of just hot
Save info in SQL rather than txt
Flag whether to allow NSFW pics
"""

from os import mkdir
from urllib import urlretrieve
import commands
import ctypes
import os.path
import pycurl
import random
import re
import sys
import urllib2

import praw

from settings import (DB_FILE, IMG_DIR,
                      MAX_SUBS, DEFAULT_SUBREDDIT,
                      IMG_TYPES)

def get_HTML(url):
    strio=StringIO.StringIO()
    curlobj=pycurl.Curl()
    curlobj.setopt(pycurl.URL, url)
    curlobj.setopt(pycurl.WRITEFUNCTION, strio.write)
    curlobj.perform()
    curlobj.close()
    return strio.getvalue()

def used(sub):
    """Have we used this praw submission before?"""
    with open(DB_FILE, 'r') as db:
        return str(sub.id) in db.read()

def update_DB(sub):
    """
    Update Database over submissions we've seen before.

    Strips any illegal or unwanted chars from a proposed filename
    """
    with open(DB_FILE, 'a') as db:
        db.write(sub.id + "\n")

def prevent_bad_name(filename):
    """Sanitize filename by removing bad chars."""
    filename = filename.replace(" ", "_")
    return re.sub("[\[\]\(\),\.;:'\"!]", "", filename)

def get_image(sub, subreddit):
    """
    Get image linked to by a praw submission, save to cwd/IMG_DIR/'subreddit'. Creates the folders if they don't exist.'
    """
    # By updating db early, we make sure that we only call an error
    # creating sub once.
    update_DB(sub)
    fil = prevent_bad_name(sub.title)
    ids = sub.id
    filename = "%s-%s.jpg" % (fil, ids)
    outWPdir = os.path.join(IMG_DIR, subreddit)
    if not os.path.exists(IMG_DIR):
        os.mkdir(IMG_DIR)
        os.mkdir(outWPdir)
    elif not os.path.exists(outWPdir):
        os.mkdir(outWPdir)
    outpath = os.path.join(outWPdir, filename)
    urlretrieve(sub.url, outpath)
    print "New Desktop Image: %s" % sub.title
    update_BG(outpath)

def update_BG(path):
    """
    Update the desktop background, with the image located at the relative path. Can currenlty only do this on gnome and ldxe (with Nathans wallpaper setter installed).
    """
    path = os.path.abspath(path)
    gnome_bg_img = "/desktop/gnome/background/picture_filename"
    command_for = {"gnome": "gconftool-2 -t str --set %s '%s'"
                    % (path, gnome_bg_img), "ldxe": "wallpaper %s" % path}
    if os.platform.startswith('win'):
        # Windows system
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoA(SPI_DESKWALLPAPER, 0, path)
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        # Desktop enviroment is gnome
        commands.getstatusoutput(command_for["gnome"])
    else:
        # Assume ldxe
        commands.getstatusoutput(command_for["ldxe"])
        # I need to get the status to ensure everything went okay
    print "BG Path: %s" % path

img_host = {"imgur.com": '(?<=<link rel="image_src" href=").*?(?=")'}

def get_path(url, domain, regex):
    if domain in "imgur.com":
        return re.search().group()

def direct_link(url):
    return url.split(".")[-1] in IMG_TYPES

def get_new(subreddits):
    """Get a image submission from the new queue"""
    while len(subreddits):
        subreddit = subreddits.pop()
        submissions = r.get_subreddit(subreddit).get_hot(limit=MAX_SUBS)
        for sub in submissions:
            if used(sub):
                continue

            if direct_link(sub.url):
                img_path = sub.url

            elif sub.domain in img_host.keys():
                urllib.urlretrieve(sub.url, "tmp.txt")
                with open("tmp.txt", "r") as website:
                    html = website.read()

                img_path = re.search(
                print img_path
                # Turn last condition into a function that
                # also allows other formats

                # Need a function to get image from imgur no matter
                # if it is direct link, indirect or album. Download
                # all but only set first in that case

                # update_DB(sub)
                return True
            else:
                print "Unknown image hoster for url %s" % sub.url
        return False

if __name__ == "__main__":
    try:
        r = praw.Reddit(user_agent='Wallpaper by _Daimon_')
        DEFAULT_subredditS = ["wallpaper"]
        MAX_SUBS = 100
        subreddits = DEFAULT_SUBREDDITS if len(sys.argv) == 1 else \
                         sys.argv[1:]
        random.shuffle(subreddits)
        if not get_new(subreddits):
            print "We ran out of subreddits, before we could find a suitable wallpaper :("
    except urllib2.URLError:
        print "Error. No internet access."
