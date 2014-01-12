#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import tornado
from tornado.options import define, options
from tornado.web import Application, StaticFileHandler, os

from yodl.views import RootHandler, ListUrlHandler, WSConnection, EventHandler


define("port", default=8888, type=int)
define("config_file", default="app_config.yml", help="app_config file")
define("download", default=os.path.join(
    os.getcwdu(), 'data'), help="download folder")


def staticMap(folder):
    return dict(path=os.path.join(os.path.dirname(__file__), folder))


def main():
    tornado.options.parse_command_line()
    app = Application( [
        (r"/ws", WSConnection),
        (r"/event", EventHandler),
        (r"/stream/(.+)", StaticFileHandler, dict(path=options.download)),
        (r"/", RootHandler),
        (r'/api/downloads', ListUrlHandler),
        (r"/(.+)", StaticFileHandler, staticMap('static')),
    ])
    app.listen(options.port)
    logging.info("Application ready and listening @ %i" % options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
