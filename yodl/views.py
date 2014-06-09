import hashlib
import json

from celery import chain
from tornado import web, websocket, escape
from tornado.options import options

from yodl import Enviroment
from yodl.tasks import get_info, download_audio


def generate_id(url):
    return hashlib.md5(url).hexdigest()


def status():
    downloaded = []
    keys = Enviroment.database.keys('yodl:downloaded:*')
    if keys is not None:
        for key in keys:
            data = Enviroment.database.get(key)
            if data is not None:
                data = json.loads(data)
                downloaded.append(data)
    return {
        'status': 'ok',
        'downloaded': downloaded,
    }


class WSConnection(websocket.WebSocketHandler):
    cl = []

    @classmethod
    def broadcast(cls, msg):
        for x in cls.cl:
            x.write_message(json.dumps(msg))

    def open(self):
        if self not in self.cl:
            self.cl.append(self)

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in self.cl:
            self.cl.remove(self)


class ListUrlHandler(web.RequestHandler):
    def get(self):
        self.write(status())

    def post(self):
        data = escape.json_decode(self.request.body)
        url = data["url"]
        if not url:
            self.write({'status': 'error', 'error': 'Malformed request'})
        else:
            download_id = generate_id(url)
            info = Enviroment.database.get('yodl:downloaded:%s' % download_id)
            if info is None:
                Enviroment.database.set('yodl:downloading:%s' % download_id,
                                        url)
                WSConnection.broadcast({"event": "add", "data": url})
                chain(
                    get_info.s(url),
                    download_audio.s(options.download, download_id)
                ).delay()
            self.write(status())
