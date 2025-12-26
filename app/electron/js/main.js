import {randomString} from './randomString.js';

const userId = randomString(16);
// Open a WebSocket connection to the server (user‑specific endpoint)
const host = location.host.startsWith('file') || location.host === '' ? 'localhost:7790' : location.host;
const ws = new WebSocket(`ws://${host}/ws/${userId}`);
ws.onopen = () => {
    connected = true;
};

/* -------------------------------------------------------------
   State & throttling logic
   ------------------------------------------------------------- */
let lastEmitTime = 0;            // timestamp of the last send
let tracking = true;  // Do we listen to user?
let mouseTracking = false;
let connected = false;``
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
        ws.send(
            JSON.stringify({
                key: Array.from(pressedKeys).sort().join(','),
                mouseButton: Array.from(pressedMouseButtons).sort().join(','),
                mouseDelta: mouseDelta
            })
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
});


document.addEventListener('keyup', (e) => {
    if (!tracking) return;
    pressedKeys.delete(e.code);
    updateInnerTracking();
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
    if (!tracking) return;
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


const mouseTrackButton = document.getElementById('tracking-mouse-button');
mouseTrackButton.addEventListener('click', () => {
    mouseTracking = !mouseTracking;
    mouseTrackButton.requestPointerLock();
})

let mouseDelta = {
    'xDelta': 0,
    'yDelta': 0,
};

document.addEventListener('mousemove', (e) => {
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    mouseDelta.xDelta += e.movementX / viewportWidth;
    mouseDelta.yDelta += e.movementY / viewportHeight;
})

function onReturnToPage() {
    mouseTracking = false;
}

document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        onReturnToPage();
    }
});

window.addEventListener('focus', () => {
    onReturnToPage();
});