#!python
from flup.server.fcgi import WSGIServer

from kickup import app

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/tmp/kickup-fcgi.sock').run()
