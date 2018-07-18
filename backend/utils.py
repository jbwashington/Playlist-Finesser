import youtube_dl

class MyLogger(object):
    """logs output from youtube """
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
        'logger'                     : MyLogger(), # logs output by youtubedl
        'progress_hooks'             : [my_hook], # tells status in console
        # 'default-search'           : 'ytsearch', # search youtube if error in with url
        'youtube-skip-dash-manifest' : True, # skip recommended videos
        'restrict-filenames'         : True, # no ASCII ampersands or spaces
        'download'                   : False, # no download for test purposes
        'format'                     : 'bestaudio/best[ext!=webm]', # get the best quality
        'extractaudio'               : True,  # only keep the audio
        'audioformat'                : 'mp3',  # convert to mp3
        'outtmpl'                    : '%(id)s',    # name the file the ID of the video
        'noplaylist'                 : True,    # only download single song, not playlist
        }

def get_track(title):

    title = "ytsearch:" + title

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:

        track = ydl.download([title])

        meta = ydl.extract_info(title)

        return track


def get_info(title):

    title = "ytsearch:" + title

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(title)

        return info





# brazy = get_song('young thug - brazy')
# brazy_info = get_meta('young thug - brazy')

# print(brazy_info)
# entries = brazy_info["entries"]

# for song in entries:
#     song_id = song['id']
#     thumbnail = song['thumbnail']
#     artist = song['creator']
#     title = song['title']
#     print(song_id + '\n', thumbnail + '\n', artist + '\n', title)
