// preload.js or a script loaded before webgl.js
const { ipcRenderer } = require('electron');
const EventEmitter = require('events');

window.video = new EventEmitter();

// Receive frame data from main process
ipcRenderer.on('video-frame', (_, chunk) => {
    window.video.emit('frame', chunk);
});