#!/bin/bash

# Created  by Andreas Damgaard Pedersen
# 28 March 2012
#
# Gets the latest xkcd comic (now always in png format)
# and sets it as the desktop wallpaper

wget `lynx --dump "http://xkcd.com" | grep png`
file=`pwd`"/"`ls -o *{png,jpg,jpeg,img,bmp} 2> /dev/null | sort -d | awk '{print $7}' | head -n 1 `
gconftool-2 -t str --set /desktop/gnome/background/picture_filename "$file"
gconftool-2 -t str --set /desktop/gnome/background/picture_options "scaled"
