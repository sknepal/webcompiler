import tornado.web
from tornado.ioloop import IOLoop
from terminado import TermSocket, UniqueTermManager
import os,sys
pid = str(os.getpid())
pidfile = "/home/try/xterm.pid"
file(pidfile, 'w').write(pid)
if __name__ == '__main__':
    term_manager = UniqueTermManager(shell_command=["firejail","--quiet","--seccomp=rmdir,exit","--nosound","--caps.drop=all","--name=code-playground","--rlimit-fsize=5000000","--rlimit-nofile=50","--private=/tmp","--net=none","--blacklist=/usr/bin/man","--blacklist=/bin/ps","--blacklist=/usr/bin/passwd","rbash"])
    handlers = [
                 (r"/websocket", TermSocket, {'term_manager': term_manager}),
                 (r"/()", tornado.web.StaticFileHandler, {'path':'/home/try/compiler/index.html'}),
                 (r"/(.*)", tornado.web.StaticFileHandler, {'path':'/home/try/compiler/.'})
               ]
    app = tornado.web.Application(handlers)
    app.listen(8079)
    try:
        IOLoop.current().start()
    finally:
        term_manager.shutdown()
        os.unlink(pidfile)
