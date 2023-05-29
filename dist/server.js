"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const ws_1 = __importDefault(require("ws"));
const ws = new ws_1.default('ws://localhost');
ws.on('error', console.error);
ws.on('open', function open() {
    ws.send('something');
});
ws.on('message', function message(data) {
    console.log('received: %s', data);
});
