#!/usr/bin/env python

"""
Created 6 January 2012
By: Andreas Damgaard Pedersen

This program goes on Reddit and finds a wallpaper from
one of the wallpaper related subreddits that I like.
It then update my desktop bagground with the new image.
Updating of background only on a linux running gnome desktop
 
 ===========
 Potential features to add
 ===========

Allow to get from top pictures instead of just hot
Save info in SQL rather than txt
Implement argument parser
"""

from os import mkdir
from urllib import urlretrieve
import urllib2
import commands
import os.path
import random
import re
import sys

import reddit

from settings import (DB_FILE, DEBUG_FILE, IMG_DIR, 
                     MAX_SUBS, DEFAULT_SUBREDDITS, 
                     IMG_TYPES)

def debug(title, domain, e):
    """Store debug info"""
    with open(DEBUG_FILE, 'a') as debug:
        debug.write("Title: %s\n" % title)
        debug.write("Domain: %s\n " % domain)
        debug.write("Full Error: %s\n" % str(e))

def used(sub):
    """Have we used this Reddit submission before?"""
    with open(DB_FILE, 'r') as db:
        return str(sub.id) in db.read()

def update_DB(sub):
    """Update Database over submissions we've seen before
       Strips any illegal or unwanted chars from a proposed filename"""
    with open(DB_FILE, 'a') as db:
        db.write(sub.id + "\n")

def prevent_bad_name(filename):
    """Removes any char from the filename that might create
       a bad filename or create filename format I don't like"""
    filename = filename.replace(" ", "_")
    return re.sub("[\[\]\(\),\.;:'\"!]", "", filename)

def get_image(sub, subreddit):
    """Get image linked to by a reddit submission, 
        save to cwd/IMG_DIR/'subreddit'. Creates the folders
        if they don't exist.'"""
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
    """Update the desktop background, with the image located at the 
       relative path. Can currenlty only do this on gnome and ldxe
       (with Nathans wallpaper setter installed)."""
    path = os.path.abspath(path)
    gnome_bg_img = "/desktop/gnome/background/picture_filename"
    command_for = {"gnome": "gconftool-2 -t str --set %s '%s'"
                        % (path, gnome_bg_img),
                    "ldxe": "wallpaper %s" % path}
    if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        # Desktop enviroment is gnome
        commands.getstatusoutput(command_for["gnome"])
    else:
        # Assume ldxe
        commands.getstatusoutput(command_for["ldxe"])
        # I need to get the status to ensure everything went okay
    print "BG Path: %s" % path

def get_new(subreddits):
    """Get a image submission from the new queue"""
    while len(subreddits):
        subreddit = subreddits.pop()
        submissions = r.get_subreddit(subreddit).get_hot(limit=MAX_SUBS)
        for sub in submissions:
            if 'imgur.com' in sub.domain and not used(sub) and \
                                             sub.url.endswith(".jpg"):
                try:
                    get_image(sub, subreddit)
                    return True
                except Exception, e:
                    raise e
                    #debug(sub.title, sub.domain, e)
                    print "Whoops, that didn't work. Lets try something else"
                return True
        return False

if __name__ == "__main__":
    try:
        r = reddit.Reddit(user_agent='Wallpaper by _Daimon_')
        if not os.path.exists(DB_FILE):
            new_db_file = open(DB_FILE, "w")
            new_db_file.close()
        subreddits = DEFAULT_SUBREDDITS if len(sys.argv) == 1 else \
                         sys.argv[1:]
        random.shuffle(subreddits)
        if not get_new(subreddits):
            print "We ran out of subreddits, before we could find a suitable wallpaper :("
    except urllib2.URLError:
        print "Error. No internet access."
