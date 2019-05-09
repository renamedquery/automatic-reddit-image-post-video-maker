import os, sys, zipfile, shutil
requiredModules = [
    'argparse',
    'pillow',
    'gtts',
    'moviepy',
    'praw',
]
for each in requiredModules:
    os.system('{} -m pip install {}'.format(str(sys.executable), str(each)))
file = open('./praw.ini', 'w')
file.write('''
[DEFAULT]
# A boolean to indicate whether or not to check for package updates.
check_for_updates=True

# Object to kind mappings
comment_kind=t1
message_kind=t4
redditor_kind=t2
submission_kind=t3
subreddit_kind=t5

# The URL prefix for OAuth-related requests.
oauth_url=https://oauth.reddit.com

# The URL prefix for regular requests.
reddit_url=https://www.reddit.com

# The URL prefix for short URLs.
short_url=https://redd.it

[bot1]
client_id=
client_secret=
password=
username=
''')
file.close()
os.mkdir('outputs')
os.mkdir('counters')
counterFiles = [
    './counters/general-file-number.txt'
]
for each in counterFiles:
    file = open(each, 'w')
    file.write('0')
    file.close()
zipf = zipfile.ZipFile('./ffmpeg.zip', 'r')
zipf.extractall('.')
zipf.close()
shutil.move('./ffmpeg/ffmpeg.exe', './ffmpeg.exe')
shutil.rmtree('ffmpeg')
os.remove('ffmpeg.zip')