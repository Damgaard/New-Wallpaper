#!/usr/bin/env python

"""
Created 6 January 2012
By: Andreas Damgaard Pedersen

This program goes on reddit and finds a wallpaper from a list of subreddits
given on the command line. Then updates the desktop bagground with the new
image.

 ===========
 Potential features to add
 ===========

Allow to get from top pictures instead of just hot
"""

from os import mkdir
from random import shuffle
from urllib import urlretrieve
import argparse
import commands
import ctypes
import os.path
import re
import sys

import praw

from settings import (DB_FILE, DEBUG_FILE, IMG_DIR, 
                      MAX_SUBS, DEFAULT_SUBREDDITS)

def used(sub):
    """Have we used this submission before?"""
    with open(DB_FILE, 'r') as db:
        return str(sub.id) in db.read()

def update_DB(sub):
    """Update Database over submissions we've seen before."""
    with open(DB_FILE, 'a') as db:
        db.write(sub.id + "\n")

def prevent_bad_name(filename):
    """Cleans and return a usable filename."""
    filename = re.sub("[ -]", "_", filename)
    filename = re.sub("[^a-zA-Z_]", "", filename)
    return filename.encode('ascii', 'replace')

def get_image(sub, subreddit):
    """
    Download image linked to by a reddit submission,

    Save to module_folder/IMG_DIR/'subreddit. Create folder if it doesn't exist
    already.
    """
    # By updating db early, we make sure that we only call an error
    # creating submission once.
    update_DB(sub)
    filename = "%s-%s" % (sub.title, sub.id)
    filename = prevent_bad_name(filename) + ".jpg"
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
    Update the desktop background wallpaper.
   
    Use the image located at the relative path. Can currently only do this on 
    windows, gnome and ldxe (with Nathans wallpaper setter installed) Desktops.
    """
    path = os.path.abspath(path)
    if sys.platform.startswith('win'):
        # Windows system
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0,
                                                   path)
    else:
        gnome_bg_img = "/desktop/gnome/background/picture_filename"
        command_for = {"gnome": "gconftool-2 -t str --set %s '%s'"
                       % (path, gnome_bg_img), "ldxe": "wallpaper %s" % path}
        if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            # Desktop enviroment is gnome
            status, output = commands.getstatusoutput(command_for["gnome"])
        else:
            # Assume ldxe
            status, output = commands.getstatusoutput(command_for["ldxe"])

def get_new(subreddits, nsfw):
    """Get a image submission from the new queue."""
    while len(subreddits):
        subreddit = subreddits.pop()
        submissions = r.get_subreddit(subreddit).get_hot(limit=MAX_SUBS)
        for sub in submissions:
            if ('imgur.com' in sub.domain and not used(sub) and 
                        sub.url.endswith(".jpg") and 
                        (nsfw or not sub.over_18)):
                get_image(sub, subreddit)
                return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
                """
                Get a new desktop wallpaper from Reddit.

                It only looks at either the subreddits the program is called
                with, or the 6 default subreddits. It is able to set the
                desktop wallpaper on windows, gnome or ldxe desktops.

                Current host able to get images from: imgur.com
                """)
    parser.add_argument('subreddits', metavar='N', type=str, nargs='*',
                default=DEFAULT_SUBREDDITS, help='Subreddits to process')
    parser.add_argument('--nsfw', '--NSFW', dest='show_nsfw',
                action='store_true', help='Should we take NSFW images')
    args = parser.parse_args()
    r = praw.Reddit(user_agent='Wallpaper downloader program 1.1 by '
                               '/u/_Daimon_')
    if not os.path.exists(DB_FILE):
        open(DB_FILE, "w").close()
    shuffle(args.subreddits)
    if not get_new(args.subreddits, args.show_nsfw):
        print ("We ran out of subreddits, before we could find a suitable "
               "wallpaper :(")
