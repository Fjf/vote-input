import {randomString} from './randomString.js';

const userId = randomString(16);
// Open a WebSocket connection to the server (user‑specific endpoint)
const ws = new WebSocket(`ws://${location.host}/ws/${userId}`);


/* -------------------------------------------------------------
   State & throttling logic
   ------------------------------------------------------------- */
let lastEmitTime = 0;            // timestamp of the last send
let tracking = true;  // Do we listen to user?
let mouseTracking = false;
const EMIT_INTERVAL_MS = 100;    // 10 times per second = 100 ms

// Set of keys currently held down
const pressedKeys = new Set();


/**
 * Attempt to emit the pending key if it differs from the last sent key
 * and the minimum interval has elapsed.
 */
function tryEmit() {
    const now = Date.now();
    if (now - lastEmitTime >= EMIT_INTERVAL_MS) {
        console.log("trying emit")
        ws.send(
            JSON.stringify({key: Array.from(pressedKeys), mouseDelta: mouseDelta})
        );
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

/* -------------------------------------------------------------
   UI event listeners – maintain `pressedKeys` and update `pendingKey`
   ------------------------------------------------------------- */
document.addEventListener('keydown', (e) => {
    if (!tracking) return;
    pressedKeys.add(e.code);
    document.getElementById('current-tracking').innerHTML = Array.from(pressedKeys).join(',') || "NONE";
    return false;

});


document.addEventListener('keyup', (e) => {
    if (!tracking) return;
    pressedKeys.delete(e.code);
    document.getElementById('current-tracking').innerHTML = Array.from(pressedKeys).join(',') || "NONE";
    return false;

});
document.addEventListener('mousedown', (e) => {
    if (!tracking) return;
    if (e.buttons & 1) pressedKeys.add('LeftMouseButton')
    if (e.buttons & 2) pressedKeys.add('RightMouseButton')
    if (e.buttons & 4) pressedKeys.add('MiddleMouseButton')
    if (e.buttons & 8) pressedKeys.add('PgUpMouseButton')
    if (e.buttons & 16) pressedKeys.add('PgDnMouseButton')

    document.getElementById('current-tracking').innerHTML = Array.from(pressedKeys).join(',') || "NONE";
    e.preventDefault();
    e.stopPropagation();
});
document.addEventListener('mouseup', (e) => {
    if (!tracking) return;
    if (!(e.buttons & 1)) pressedKeys.delete('LeftMouseButton')
    if (!(e.buttons & 2)) pressedKeys.delete('RightMouseButton')
    if (!(e.buttons & 4)) pressedKeys.delete('MiddleMouseButton')
    if (!(e.buttons & 8)) pressedKeys.delete('PgUpMouseButton')
    if (!(e.buttons & 16)) pressedKeys.delete('PgDnMouseButton')
    document.getElementById('current-tracking').innerHTML = Array.from(pressedKeys).join(',') || "NONE";
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
    const viewportWidth  = window.innerWidth;
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