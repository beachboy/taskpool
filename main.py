from taskpool.server.server import Server
from werkzeug.wsgi import SharedDataMiddleware
import os
import redis

def create_app(with_static=True):
    config = {
        'backend': redis.Redis()
    }
    app = Server(config)
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('localhost', 5000, app, use_debugger=True, use_reloader=True)
