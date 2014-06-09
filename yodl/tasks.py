from __future__ import absolute_import
import json
import logging
import os

from celery import Task
import pafy
from yodl.celeryapp import app

from yodl import Enviroment

class DebugTask(Task):
    abstract = True
    _db = None
    title = None

    def __call__(self, *args, **kwargs):
        """Create a TaskModel object and log start of task execution."""
        logging.info(
            'START {} (task id: {})'.format(self.name, self.request.id))
        return super(DebugTask, self).__call__(*args, **kwargs)

    @property
    def db(self):
        if self._db is None:
            self._db = Enviroment.database
        return self._db

    def after_return(self, *args, **kwargs):
        print('Task {} returned'.format(self.title))


@app.task(base=DebugTask, title='Get info about youtube url')
def get_info(url, vid):
    video = pafy.new(url)
    info = {
        'title': video.title,
        'duration': video.duration,
        'thumb': video.bigthumb,
        'url': url
    }
    get_info.db.set(
        'yodl:downloaded:%s' % vid, json.dumps(info)
    )
    return info


@app.task(base=DebugTask, title='Download video as audio file')
def download_audio(info, path, vid):
    yt = pafy.new(info.get('url')).getbestaudio()
    path = os.path.join(path, '%s.%s' % (vid, yt.extension))
    yt.download(path, quiet=True)
    info['stream'] = '/stream/%s.%s' % (vid, yt.extension)
    info['bitrate'] = yt.bitrate
    info['filesize'] = yt.get_filesize()
    download_audio.db.set(
        'yodl:downloaded:%s' % vid, json.dumps(info)
    )
    return info
