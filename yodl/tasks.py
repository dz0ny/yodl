from __future__ import absolute_import
import json
import os

from celery import Task
import pafy

from yodl import Enviroment

from celery import current_app as app


class DebugTask(Task):
    abstract = True

    def after_return(self, *args, **kwargs):
        print('Task returned: {0!r}'.format(self.request))


@app.task(base=DebugTask)
def get_info(url):
    video = pafy.new(url)
    return {
        'title': video.title,
        'duration': video.duration,
        'thumb': video.bigthumb,
        'url': url
    }


@app.task(base=DebugTask)
def download_audio(info, path, vid):
    yt = pafy.new(info.get('url')).getbestaudio()
    path = os.path.join(path, '%s.%s' % (vid, yt.extension))
    yt.download(path, quiet=True)
    info['stream'] = '/stream/%s.%s' % (vid, yt.extension)
    info['bitrate'] = yt.bitrate
    info['filesize'] = yt.get_filesize()
    Enviroment.database.set(
        'yodl:downloaded:%s' % vid, json.dumps(info)
    )
    return info
