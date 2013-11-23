from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from yodl.__init__ import Enviroment


class MyHTTPTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application(Enviroment.handlers)

    def test_homepage(self):
        # The following two lines are equivalent to
        #   response = self.fetch('/')
        # but are shown in full here to demonstrate explicit use
        # of self.stop and self.wait.
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        self.assertEquals(response, "")
        # test contents of response