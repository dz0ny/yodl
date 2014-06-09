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
        'downloading': Enviroment.database.lrange('yodl:downloading', 0, -1),
    }

CONNECTED_CLIENTS = []
class WSConnection(websocket.WebSocketHandler):

    @classmethod
    def broadcast(cls, msg):
        for x in CONNECTED_CLIENTS:
            x.write_message(json.dumps(msg))

    def open(self):
        CONNECTED_CLIENTS.append(self)

    def on_message(self, message):
        print(message)

    def on_close(self):
        CONNECTED_CLIENTS.remove(self)

def on_success(sender, task_id, data):
    Enviroment.database.lrem('yodl:downloading', 0, task_id)
    WSConnection.broadcast({'event':'finished', 'url': task_id})

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
                chain_id = chain(
                    get_info.s(url, download_id),
                    download_audio.s(options.download, download_id)
                ).delay()
                Enviroment.database.lpush('yodl:downloading', chain_id)
                Enviroment.database.ltrim('yodl:downloading', 0, 10)
            self.write(status())
