import {randomString} from './randomString.js';
import * as listen from "./listen.js";
const { ipcRenderer } = require('electron');
const userId = randomString(16);
let ws = null;
let escapeButton = localStorage.getItem('escapeButton')

function connect(host) {
    ws = new WebSocket(`ws://${host}/ws/${userId}`);

    ws.onopen = () => {
        connected = true;
        document.getElementById('output').innerText = 'Connected';
    };

    ws.onclose = () => {
        connected = false;
        document.getElementById('output').innerText = 'Disconnected';
    };

    ws.onerror = () => {
        connected = false;
        document.getElementById('output').innerText = 'Connection error';
    };
}

const connectButton = document.getElementById('connect-button');
const serverIpInput = document.getElementById('server-ip');

connectButton.addEventListener('click', () => {
    const ip = serverIpInput.value.trim() || '127.0.0.1';
    const host = ip.includes(':') ? ip : `${ip}:7790`;

    connect(host);
    listen.connect(`ws://${host}/listen`);
    console.log("starting stream")
    ipcRenderer.send('start-stream', ip); // ask main to start ffmpeg
    tracking = true;
});

/* -------------------------------------------------------------
   State & throttling logic
   ------------------------------------------------------------- */
let tracking = false;
let connected = false;

let lastEmitTime = 0;
const EMITS_PER_SECOND = 30;
const EMIT_INTERVAL_MS = 1000 / EMITS_PER_SECOND;

// Set of keys currently held down
const pressedKeys = new Set();
const pressedMouseButtons = new Set();


/**
 * Attempt to emit the pending key if it differs from the last sent key
 * and the minimum interval has elapsed.
 */
function tryEmit() {
    if (!connected) return
    const now = Date.now();
    if (now - lastEmitTime >= EMIT_INTERVAL_MS) {
        const keys = Array.from(pressedKeys).sort().join(',');
        const pmb = Array.from(pressedMouseButtons).sort().join(',');
        const json_input = JSON.stringify({
            key: keys !== '' ? keys : null,
            mouseButton: pmb !== '' ? pmb : null,
            mouseDelta: mouseDelta
        })
        ws.send(json_input);
        mouseDelta.xDelta = 0;
        mouseDelta.yDelta = 0;
        lastEmitTime = now;
    }
}

// Run the throttling check regularly (e.g., every 50ms)
setInterval(tryEmit, 50);

function updateInnerTracking() {
    let array = Array.from(pressedKeys).concat(Array.from(pressedMouseButtons))
    document.getElementById('current-tracking').innerHTML = array.join(',') || "NONE";
}

/* -------------------------------------------------------------
   UI event listeners – maintain `pressedKeys` and update `pendingKey`
   ------------------------------------------------------------- */
document.addEventListener('keydown', (e) => {
    if (!tracking) return;

    if (e.code === escapeButton) {
        pressedKeys.add('Escape')
    } else {
        pressedKeys.add(e.code);
    }

    updateInnerTracking();

    e.preventDefault();
    e.stopPropagation();
});


document.addEventListener('keyup', (e) => {
    if (!tracking) return;

    if (e.code === escapeButton) {
        pressedKeys.delete('Escape')
    } else {
        pressedKeys.delete(e.code);
    }
    updateInnerTracking();

    e.preventDefault();
    e.stopPropagation();
});

document.addEventListener('mousedown', (e) => {
    if (!tracking) return;
    if (e.buttons & 1) pressedMouseButtons.add('LeftMouseButton')
    if (e.buttons & 2) pressedMouseButtons.add('RightMouseButton')
    if (e.buttons & 4) pressedMouseButtons.add('MiddleMouseButton')
    if (e.buttons & 8) pressedMouseButtons.add('PgUpMouseButton')
    if (e.buttons & 16) pressedMouseButtons.add('PgDnMouseButton')

    updateInnerTracking();
    e.preventDefault();
    e.stopPropagation();
});
document.addEventListener('mouseup', (e) => {
    if (!(e.buttons & 1)) pressedMouseButtons.delete('LeftMouseButton')
    if (!(e.buttons & 2)) pressedMouseButtons.delete('RightMouseButton')
    if (!(e.buttons & 4)) pressedMouseButtons.delete('MiddleMouseButton')
    if (!(e.buttons & 8)) pressedMouseButtons.delete('PgUpMouseButton')
    if (!(e.buttons & 16)) pressedMouseButtons.delete('PgDnMouseButton')
    updateInnerTracking();
    e.preventDefault();
    e.stopPropagation();
});
document.addEventListener('contextmenu', (e) => {
    e.preventDefault()
});

document.addEventListener('mousemove', (e) => {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    mouseDelta.xDelta += e.movementX / viewportWidth;
    mouseDelta.yDelta += e.movementY / viewportHeight;

    e.preventDefault();
    e.stopPropagation();
})

const mouseTrackButton = document.getElementById('tracking-mouse-button');
mouseTrackButton.addEventListener('click', () => {
    mouseTrackButton.requestPointerLock();
})

let mouseDelta = {
    'xDelta': 0,
    'yDelta': 0,
};

const escapeRebindingButton = document.getElementById('escape-rebinding-button');
escapeRebindingButton.addEventListener('click', () => {
    escapeRebindingButton.innerText = `Waiting for next input...`

    function fn(e) {
        escapeRebindingButton.innerText = `Current Esc = ${e.code}`
        localStorage.setItem('escapeButton', e.code);
        escapeButton = e.code;
        document.removeEventListener('keydown', fn);
    }

    document.addEventListener('keydown', fn)
})


