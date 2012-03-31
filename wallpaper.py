#!/usr/bin/env python

# Created 6 January 2012
# By: Andreas Damgaard Pedersen
#
# This program goes on Reddit and finds a wallpaper from
# one of the wallpaper related subreddits that I like.
# It then update my desktop bagground with the new image.
# 
# This program is set to run every time I login. This was
# done by editing $HOME/.profile to include a command line
# about starting this program.
#
# ===========
# Potential features to add
# ===========
#
# Allow calling with non-defulat subreddits by giving them as args 
# 	while calling the program
# Allow to get from top pictures instead of just hot
# Save info in SQL rather than txt
# Flag whether to allow NSFW pics

import reddit
import random
from urllib2 import urlopen
from urllib import urlretrieve
import os, sys
import commands

# Maximum submissions to look at from each subreddit
MAX_SUBS = 8

default_subreddits = ['skyporn', 'spaceporn', 'earthporn', 'waterporn', 'wallpapers', 'wallpaper']

root = os.path.realpath(os.path.dirname(sys.argv[0]))
dbFile = "%s/WP_Data.txt" % root
out_folder = "%s/images" % root
debugFile = "%s/WP_Debug.txt" % root

def debug(title, domain, e):
	"""Store debug info"""
	debug = open(debugFile, 'a')
	debug.write("Title: %s\n" % title)
	debug.write("Domain: %s\n " % domain)
	debug.write("Full Error: %s\n" % str(e))
	debug.close()

def notUsedBefore(sub):
	"""Have we used this Reddit submission before?"""
	with open(dbFile, 'r') as db:
		database = db.read()
	return not (str(sub.id) in database)

def updateDB(sub):
	"""Update Database over submissions we've seen before"""
	with open(dbFile, 'a') as db:
		db.write(sub.id + "\n")

def preventBadFileName(filename):
	"""Strips any illegal or unwanted chars from a proposed filename"""
	# List of illegal chars is taken from what I'm certain is wrong
	# plus a few extra just to be sure. But since I couldn't
	# find an official list of bad chars, some illegal chars may
	# have slipped through.
	# Also strips out chars I dislike in filenames
	illegalChars = ["[", "]", "(", ")", ".", ",", "/", "\\", "'", "!", " ", "#"]
	for ch in illegalChars:
		filename = filename.replace(ch, "")
	return filename

# Should be split into two functions. GetImg and saveImg
def getFile(sub, subreddit):
	"""Get image linked to by a reddit submission, save to subfolder 'subreddit'"""
	fil = preventBadFileName(sub.title)
	ids = sub.id
	print "Fil: %s" % fil
	print "ID: %s" % ids
	filename = "%s-%s.jpg" % (fil, ids)
	outWPFolder = os.path.join(out_folder, subreddit)

	if not os.path.exists(out_folder):
		os.mkdir(out_folder)
		os.mkdir(outWPFolder)
	elif not os.path.exists(outWPFolder):
		os.mkdir(outWPFolder)

	outpath = os.path.join(outWPFolder, filename)
	urlretrieve(sub.url, outpath)
	print "New Desktop Image: %s" % sub.title
	print "From: %s" % subreddit
	updateDB(sub)
	updateBG(outpath)

def updateBG(path):
	"""Update Desktop Background with image at 'path'"""
	command = "gconftool-2 -t str --set /desktop/gnome/background/picture_filename '"
	print "BG Path: %s" % os.path.abspath(path)
	f = command + "%s%s'" % (command, os.path.abspath(path))
	f = f.encode('utf-8')
	command += str(os.path.abspath(path)) + "'"
	status, output = commands.getstatusoutput(command)  # status=0 if success
	return True

def getNew(subreddits):
	"""Get a image submission from the new queue"""
	while len(subreddits) != 0:
		subreddit = subreddits.pop()
		submissions = r.get_subreddit(subreddit).get_hot(limit=MAX_SUBS)
		for sub in submissions:
			if 'imgur.com' in sub.domain and notUsedBefore(sub) and '.jpg' in sub.url:
				try:
					getFile(sub, subreddit)
					return True
				except Exception, e:
				#	raise Exception
					debug(sub.title, sub.domain, e)
					print "Whoops, that didn't work. Lets try something else"

	return False

if __name__ == "__main__":
	r = reddit.Reddit(user_agent='Wallpaper by _Daimon_')
	random.shuffle(default_subreddits)

	if not getNew(default_subreddits):
		print "We ran out of subreddits, before we could find a suitable wallpaper :("
