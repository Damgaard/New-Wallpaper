from os.path import dirname, realpath

ROOT_DIR = realpath(dirname(__file__))
DB_FILE = "%s/WP_Data.txt" % ROOT_DIR
DEBUG_FILE = "%s/WP_Debug.txt" % ROOT_DIR
DEFAULT_SUBREDDITS = ['skyporn', 'spaceporn', 'earthporn', 'waterporn', 
                      'wallpapers', 'wallpaper']
IMG_DIR = "%s/images" % ROOT_DIR
MAX_SUBS = 12
IMG_TYPES = ("jpg", "jpeg", "png", "bmp", "gif", "img")
