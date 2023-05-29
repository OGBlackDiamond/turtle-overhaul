import { Server, WebSocketServer } from 'ws';
import { connect } from 'ngrok';

const wss = new Server({ port: 8080 });

wss.on('connection', function connection(ws) {
    console.log("Server online");
    ws.on('error', function error(err) {
        console.log(err);
    });

    ws.on('message', function incoming(data) {
        console.log('received: %s', data);
    });

    ws.on('request', function request(data) {
        console.log('request: %s', data)
    })

    ws.on('ping', function ping(data) {
        console.log("pong");
    })

    ws.send('something');
});

(async ()  => {
    const url = await connect(8080);
    console.log(url);
})();