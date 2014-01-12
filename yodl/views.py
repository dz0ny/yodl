import hashlib
import json

from tornado import web, websocket, escape
from tornado.options import options
from yodl import tasks, Enviroment


def status():
    downloaded = []
    downloading = []

    keys = Enviroment.database.keys('yodl:downloading:*')
    if keys is not None:
        for key in keys:
            downloading.append(Enviroment.database.get(key))

    keys = Enviroment.database.keys('yodl:downloaded:*')
    if keys is not None:
        for key in keys:
            download_id = ("%s" % key).replace("yodl:downloaded:", "")
            data = Enviroment.database.get(key)
            if data is not None:
                data = json.loads(data)

                downloaded.append({
                    'title': data['fulltitle'],
                    'data': data,
                    'id': download_id,
                    'stream': '/stream/%s.mp3' % download_id
                })
    return {
        'status': 'ok',
        'downloaded': downloaded,
        'downloading': downloading
    }


class WSConnection(websocket.WebSocketHandler):

    cl = []

    @classmethod
    def broadcast(self, msg):
        for x in self.cl:
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

    def generateId(self, url):
        return hashlib.md5(url).hexdigest()

    def get(self):
        self.write(status())

    def post(self):
        data = escape.json_decode(self.request.body)
        url = data["url"]
        if not url:
            self.write({'status': 'error', 'error': 'Malformed request'})
        else:
            download_id = self.generateId(url)
            info = Enviroment.database.get('yodl:downloaded:%s' % download_id)
            if info is None:
                Enviroment.database.set('yodl:downloading:%s' % download_id, url)
                WSConnection.broadcast({"event": "add", "data": url})
                tasks.transcode.delay(
                    url,
                    self.request.headers.get('User-Agent'),
                    options.download
                )
            self.write(status())

class EventHandler(web.RequestHandler):

    def post(self):
        data = escape.json_decode(self.request.body)
        WSConnection.broadcast(data)
        self.write("event ok")

class RootHandler(web.RequestHandler):

    @web.asynchronous
    def get(self):
        self.redirect('/index.html', True)
