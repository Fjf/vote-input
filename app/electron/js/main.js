import {randomString} from './randomString.js';

const userId = randomString(16);
let ws = null;

function connect(ipAddress) {
    const host = ipAddress.includes(':')
        ? ipAddress
        : `${ipAddress}:7790`;

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
    connect(ip);
});

/* -------------------------------------------------------------
   State & throttling logic
   ------------------------------------------------------------- */
let lastEmitTime = 0;            // timestamp of the last send
let tracking = true;  // Do we listen to user?
let mouseTracking = true;
let connected = false;
``
const EMIT_INTERVAL_MS = 100;    // 10 times per second = 100 ms

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
        console.log(json_input);
        ws.send(json_input
        );
        mouseDelta.xDelta = 0;
        mouseDelta.yDelta = 0;
        lastEmitTime = now;
    }
}

const trackButton = document.getElementById('tracking-button');
trackButton.addEventListener('click', () => {
    tracking = !tracking;
    trackButton.innerHTML = 'Switch to ' + (tracking ? 'not' : '') + ' Tracking';
})


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
    pressedKeys.add(e.code);
    updateInnerTracking();

    // e.preventDefault();
    // e.stopPropagation();
});


document.addEventListener('keyup', (e) => {
    if (!tracking) return;
    pressedKeys.delete(e.code);
    updateInnerTracking();

    // e.preventDefault();
    // e.stopPropagation();
});
document.addEventListener('mousedown', (e) => {
    if (!mouseTracking) return;
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
})

const mouseTrackButton = document.getElementById('tracking-mouse-button');
mouseTrackButton.addEventListener('click', () => {
    mouseTrackButton.requestPointerLock();
})

let mouseDelta = {
    'xDelta': 0,
    'yDelta': 0,
};


