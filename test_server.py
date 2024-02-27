from tornado.httputil import HTTPServerRequest
from tornado.web import Application
import tornado.websocket

ws_clients = []

class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    
    # other methods
    def open(self):
        if self not in ws_clients:
            ws_clients.append(self)

    def on_close(self):
        if self in ws_clients:
            ws_clients.remove(self)

    def send_message():
        for c in ws_clients:
            c.write_message("print('please work')")
        
    
        
def main():
    # Create a web app whose only endpoint is a WebSocket, and start the web
    # app on port 8888.
    app = tornado.web.Application(
        [(r"", MyWebSocketHandler)],
        websocket_ping_interval=10,
        websocket_ping_timeout=30,
    )
    app.listen(3000)

    # Create an event loop (what Tornado calls an IOLoop).
    io_loop = tornado.ioloop.IOLoop.current()

    # Before starting the event loop, instantiate a RandomBernoulli and
    # register a periodic callback to write a sampled value to the WebSocket
    # every 100ms.
    periodic_callback = tornado.ioloop.PeriodicCallback(
        lambda: MyWebSocketHandler.send_message(), 100
    )
    periodic_callback.start()

    # Start the event loop.
    io_loop.start()

main()