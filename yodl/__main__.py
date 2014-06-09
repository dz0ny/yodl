# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

import tornado
from tornado.options import define, options
from tornado.web import Application, StaticFileHandler

from yodl.views import ListUrlHandler, WSConnection


define("port", default=8888, type=int)
define("config_file", default="app_config.yml", help="app_config file")
define("download", default=os.path.join(
    os.getcwdu(), 'data'), help="download folder")


def main():
    tornado.options.parse_command_line()
    app = Application([
        (r"/ws", WSConnection),
        (r"/stream/(.+)", StaticFileHandler, {
            'path': options.download
        }),
        (r'/api/downloads', ListUrlHandler),
        (r"/(.+)", StaticFileHandler, {
            'path': os.path.join(os.path.dirname(__file__), 'static'),
            'default_filename': 'index.html'
        }),
    ])
    app.listen(options.port)
    logging.info("Application ready and listening @ %i" % options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
