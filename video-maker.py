#TODO: comment stuff on this program so its "readable".

import argparse, sys, string, time, os, shutil, praw, urllib.request, gtts, moviepy.editor, PIL.Image, PIL.ImageDraw, PIL.ImageFont

parser = argparse.ArgumentParser(description = 'A program that makes a video on posts from a subreddit.')
parser.add_argument('--subreddit', dest = 'subreddit', required = True, help = 'The subreddit that the video will be made on. EXAMPLE: "aviation".')
parser.add_argument('--limit', dest = 'limit', required = True, help = 'The amount of posts that will be in the video. EXAMPLE: "10".')
parser.add_argument('--sortby', dest = 'sortby', required = True, help = 'What page the posts will be pulled from. Options are ["hot", "new", "rising", "controversial", "top"].')
parser.add_argument('--allow-nsfw', dest = 'allow_nsfw', required = False, help = 'Whether or not nsfw content will be allowed in the video. Options are ["y", "n"].')
arguments = parser.parse_args()

class program:
    class utils:
        def getCurrentFileNumberCount() -> int:
            try:
                number = int(str(open('./counters/general-file-number.txt').read()))
            except:
                number = 0
            number += 1
            file = open('./counters/general-file-number.txt', 'w')
            file.write(str(number))
            file.close()
            return number
        def println(string) -> None:
            print(program.utils.makeAsciiFriendly(string))
        def log(string) -> None:
            print('{} | {}'.format(program.utils.formatTimeString('%month%/%day%/%year%-%hour24%:%minute%:%second%'), program.utils.makeAsciiFriendly(string)))
        def makeAsciiFriendly(string, unknownCharFiller = '?') -> str:
            newString = ''
            string = str(string)
            for each in string:
                if (each.lower() in program.presets.normalAsciiChars):
                    pass
                else:
                    each = unknownCharFiller
                newString += each
            return newString
        def localtime() -> dict:
            ENDTIMEDICT = {}
            LOCALTIME = time.localtime()
            for partition in range(len(LOCALTIME)):
                if (partition == 0):
                    ENDTIMEDICT['year'] = LOCALTIME[partition]
                elif (partition == 1):
                    ENDTIMEDICT['month'] = LOCALTIME[partition]
                elif (partition == 2):
                    ENDTIMEDICT['day'] = LOCALTIME[partition]
                elif (partition == 3):
                    ENDTIMEDICT['hour_24HR'] = LOCALTIME[partition]
                    ENDTIMEDICT['hour_12HR'] = int(LOCALTIME[partition])
                    if (int(ENDTIMEDICT['hour_24HR'] > 12)):
                        ENDTIMEDICT['hour_12HR'] = int(LOCALTIME[partition]) - 12
                        ENDTIMEDICT['pm/am'] = 'pm'
                    else:
                        ENDTIMEDICT['pm/am'] = 'am'
                elif (partition == 4):
                    ENDTIMEDICT['minute'] = LOCALTIME[partition]
                elif (partition == 5):
                    ENDTIMEDICT['second'] = LOCALTIME[partition]
                elif (partition == 6):
                    ENDTIMEDICT['weekday'] = LOCALTIME[partition]
                elif (partition == 7):
                    ENDTIMEDICT['yearday'] = LOCALTIME[partition]
                elif (partition == 8):
                    ENDTIMEDICT['daylightsavingtime'] = bool(int(LOCALTIME[partition]))
            return ENDTIMEDICT
        def formatTimeString(string) -> str:
            timeNow = program.utils.localtime()
            if (len(str(timeNow['second'])) == 1):
                timeNow['second'] = '0' + str(timeNow['second'])
            if (len(str(timeNow['minute'])) == 1):
                timeNow['minute'] = '0' + str(timeNow['minute'])
            replaceWith = [
                ['%year%', timeNow['year']],
                ['%month%', timeNow['month']],
                ['%day%', timeNow['day']],
                ['%hour%', timeNow['hour_12HR']],
                ['%hour24%', timeNow['hour_24HR']],
                ['%pm/am%', timeNow['pm/am']],
                ['%minute%', timeNow['minute']],
                ['%second%', timeNow['second']],
                ['%weekday%', timeNow['weekday']],
                ['%yearday%', timeNow['yearday']],
                ['%dst%', timeNow['daylightsavingtime']],
            ]
            for each in range(len(replaceWith)):
                string = string.replace(str(replaceWith[each][0]), str(replaceWith[each][1]))
            return string
    class presets:
        sortby = 'hot' #the page that the program will sort for the posts by
        subreddit = 'aviation' #the subreddit that the program is fetching posts from
        limit = 10 #the max amount of posts that the program will fetch
        allowNsfw = False #whether or not to allow nsfw content
        normalAsciiChars = [*list(string.ascii_lowercase), *list(string.digits), *list(string.punctuation), *list(string.whitespace)] #for making stuff printable so that it doesnt raise any unicode encode/decode errors
    class reddit:
        reddit = None #the praw session
        def downloadImagePostsFromReddit(subreddit, limit, allow_nsfw, sortby) -> list:
            #this function will download posts from reddit.com and paste them into ./tmp
            paths = []
            posts = eval('program.reddit.reddit.subreddit("{}").{}(limit = {})'.format(subreddit, sortby, limit))
            imageFormats = ['png', 'jpg']
            for submission in posts:
                fileExtension = submission.url.split('.')[-1].split('?')[0].lower()
                if (submission.is_self == False and fileExtension in imageFormats):
                    if ((submission.over_18 and allow_nsfw) or submission.over_18 == False):
                        filePath = './tmp/{}.{}'.format(program.utils.getCurrentFileNumberCount(), fileExtension)
                        paths.append([filePath, submission])
                        urllib.request.urlretrieve(submission.url, filePath)
            return paths
    class images:
        def makeImageFrame(imagePath, postData, bgcolor = '#ffffff', fgcolor = '#000000', dimensions = [1920, 1080]) -> str:
            #make it so that it only displays the first 50-70 characters of the title and then cuts it off with "..."
            mainImage = PIL.Image.new('RGB', (dimensions[0], dimensions[1]), bgcolor)
            font = PIL.ImageFont.truetype('./default-font.ttf', int(dimensions[1] / 30))
            draw = PIL.ImageDraw.Draw(mainImage)
            title = 'Title: {}'.format(postData.title)
            textSize = draw.textsize(title, font = font)
            textCoords = [int(mainImage.size[0] - textSize[0]), 0]
            draw.text(textCoords, title, fgcolor, font = font)
            author = 'Author: u/{}'.format(postData.author)
            textSize2 = draw.textsize(author, font = font)
            textCoords2 = [int(mainImage.size[0] - textSize2[0]), int(textSize[1])]
            draw.text(textCoords2, author, fgcolor, font = font)
            memeImage = PIL.Image.open(imagePath)
            aspectRatio = memeImage.size[1] / memeImage.size[0]
            memeImageSize = [int(dimensions[1] / aspectRatio), int(dimensions[1])]
            memeImage = memeImage.resize(memeImageSize, PIL.Image.ANTIALIAS)
            mainImage.paste(memeImage, (0, 0))
            mainImage.save(imagePath)
            return imagePath
    class tts:
        def makeTTSFile(text, language = 'en') -> str:
            filePath = './tmp/{}-tts.mp3'.format(program.utils.getCurrentFileNumberCount())
            textToSpeech = gtts.gTTS(text = str(text), lang = str(language))
            textToSpeech.save(filePath)
            return filePath

#tell the user that the program is beginning
program.utils.log('Starting program.')

#check if ./tmp is a folder that exists, if it is there then delete it
if ('tmp' in os.listdir('.')):
    shutil.rmtree('tmp')
    program.utils.log('TMP folder was found and deleted.')

#make the temporary directory for images and audio files
os.mkdir('tmp')
program.utils.log('TMP folder was created.')

#parse the arguments for the program
program.presets.subreddit = str(arguments.subreddit)
program.presets.sortby = str(arguments.sortby)
if (program.presets.sortby not in ['hot', 'new', 'rising', 'controversial', 'top']):
    program.utils.log('Got an invalid argument for "--sortby". Value must be in ["hot", "new", "rising", "controversial", "top"]. Quitting.')
    exit()
try:
    program.presets.limit = int(arguments.limit)
except ValueError:
    program.utils.log('Got an invalid arument for "--limit". Value must be an integer. Quitting.')
    exit()
program.presets.allowNsfw = False
if (arguments.allow_nsfw):
    if (arguments.allow_nsfw.lower() in ['y', 'n']):
        if (arguments.allow_nsfw.lower() == 'y'):
            program.presets.allowNsfw = True
    else:
        program.utils.log('Got an invalid argument for  "--allow-nsfw". Value must be in ["y", "n"].')

#display the parsed arguments
program.utils.log('Program starting with sortby={}'.format(program.presets.sortby))
program.utils.log('Program starting with subreddit={}'.format(program.presets.subreddit))
program.utils.log('Program starting with limit={}'.format(program.presets.limit))

#initialize the praw session
try:
    program.reddit.reddit = praw.Reddit('bot1', user_agent = 'bot1 user agent')
except:
    program.utils.log('Could not start a praw.Reddit session. Try checking that your praw.ini file is configured correctly. Quitting.')
program.utils.log('PRAW bot was successfully initialized.')

#get the posts from the subreddit
program.utils.log('Getting {} posts from the {} section of r/{}'.format(program.presets.limit, program.presets.sortby, program.presets.subreddit))
imagePathsForRedditPosts = program.reddit.downloadImagePostsFromReddit(program.presets.subreddit, program.presets.limit, program.presets.allowNsfw, program.presets.sortby)
program.utils.log('Got {} posts from the subreddit.'.format(len(imagePathsForRedditPosts)))

#edit the image files
for each in imagePathsForRedditPosts:
    program.utils.log('Editing {}.'.format(each[0]))
    program.images.makeImageFrame(each[0], each[1])

#make tts files for the titles
ttsPaths = []
for each in range(len(imagePathsForRedditPosts)):
    program.utils.log('Making TTS file {}/{}.'.format(str(each + 1), str(len(imagePathsForRedditPosts))))
    title = str(imagePathsForRedditPosts[each][1].title)
    ttsPaths.append(program.tts.makeTTSFile(title))
program.utils.log('TTS paths: {}'.format(str(ttsPaths)))

#make the tts files longer and add images to them
videoFilePaths = []
for each in range(len(ttsPaths)):
    program.utils.log('Editing TTS file {}/{}.'.format(str(each + 1), str(len(ttsPaths))))
    filePath1 = './tmp/{}-tts-enlongated.mp4'.format(program.utils.getCurrentFileNumberCount())
    videoFilePaths.append(filePath1)
    os.system('ffmpeg.exe -loop 1 -i {} -i {} -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest {}'.format(str(imagePathsForRedditPosts[each][0]), str(ttsPaths[each]), str(filePath1)))

videoFileList = []
for each in videoFilePaths:
    videoFileList.append(moviepy.editor.VideoFileClip(each))
finalVideo = moviepy.editor.concatenate_videoclips(videoFileList)
finalVideo.write_videofile('./outputs/render-{}.mp4'.format(program.utils.getCurrentFileNumberCount()))

#delete all the temporary files
shutil.rmtree('tmp')