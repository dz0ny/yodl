from __future__ import absolute_import
import hashlib
import json
import os.path
import time
from tornado.httpclient import HTTPRequest, HTTPClient
from youtube_dl import _real_main as downloadFromService
from yodl.__init__ import Enviroment
from yodl.celeryapp import app

# Patch exit function
import sys
import os


sys.exit = lambda *x: True


@app.task
def transcode(url, user_agent, store):

    # https://github.com/rg3/youtube-dl/blob/master/youtube_dl/__init__.py
    file_id = hashlib.md5(url).hexdigest()
    raw_file = os.path.join(store, file_id)
    args = [
        '-k',
        '--extract-audio',
        '--audio-format', 'mp3',
        '--audio-quality', '0',
        '--user-agent', user_agent,
        '--rate-limit', '2M'
        '--no-progress',
        '--write-info-json',

        '--output', raw_file + '.%(ext)s',

        url
    ]

    downloadFromService(args)
    Enviroment.database.delete('yodl:downloading:%s' % file_id)

    with open('%s.info.json' % raw_file) as f:
        data = json.loads(f.read())
        data["added"] = int(time.time())
        Enviroment.database.set(
            'yodl:downloaded:%s' % file_id, json.dumps(data))

        orginal = '%s.%s' % (raw_file, data["ext"])
        jsoninfo = '%s.info.json' % raw_file
        if os.path.isfile(orginal) and data["ext"] is not "mp3":
            print("removing", orginal)
            os.remove(orginal)
        if os.path.isfile(jsoninfo):
            print("removing", jsoninfo)
            os.remove(jsoninfo)

        json_data = {
                    'title': data['fulltitle'],
                    'data': data,
                    'id': file_id,
                    'stream': '/stream/%s.mp3' % file_id
                }
        request = HTTPRequest(
            headers={"Content-Type": "application/json"},
            url="http://localhost:8888/event",
            method="POST",
            body=json.dumps({"event": "downloaded", "data": json_data}))
        try:
            httpclient = HTTPClient()
            response = httpclient.fetch(request)
            print response.body
            httpclient.close()
        except httpclient.HTTPError as e:
            print "Error:", e



