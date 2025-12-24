import { randomString } from './randomString.js';

const userId = randomString(16);
// Open a WebSocket connection to the server (user‑specific endpoint)
const ws = new WebSocket(`ws://${location.host}/ws/${userId}`);

// When a message is received, display it in the output div
ws.onmessage = (event) => {
    const outputDiv = document.getElementById('output');
    outputDiv.innerText = event.data;
};

/* -------------------------------------------------------------
   State & throttling logic
   ------------------------------------------------------------- */
let lastSentKey = null;          // last key value that was actually sent
let pendingKey = null;           // most recent key value to be sent
let lastEmitTime = 0;            // timestamp of the last send
const EMIT_INTERVAL_MS = 100;    // 10 times per second = 100 ms

// Set of keys currently held down
const pressedKeys = new Set();

/**
 * Determine the key that should be considered “active”.
 * Returns the most recently pressed key, or `null` if none.
 */
function updatePendingKey() {
    // If there are still pressed keys, pick the last one added.
    // Since Set preserves insertion order, we can take the last element.
    if (pressedKeys.size === 0) {
        pendingKey = null;
    } else {
        // Convert to array to get the last element (most recent)
        const keysArray = Array.from(pressedKeys);
        pendingKey = keysArray[keysArray.length - 1];
    }
}

/**
 * Attempt to emit the pending key if it differs from the last sent key
 * and the minimum interval has elapsed.
 */
function tryEmit() {
    const now = Date.now();
    if (pendingKey !== lastSentKey && now - lastEmitTime >= EMIT_INTERVAL_MS) {
        ws.send(JSON.stringify({ key: pendingKey }));
        lastSentKey = pendingKey;
        lastEmitTime = now;
    }
}

// Run the throttling check regularly (e.g., every 50 ms)
setInterval(tryEmit, 50);

/* -------------------------------------------------------------
   UI event listeners – maintain `pressedKeys` and update `pendingKey`
   ------------------------------------------------------------- */
document.addEventListener('keydown', (e) => {
    // Add the key to the set (duplicates are ignored)
    pressedKeys.add(e.key);
    updatePendingKey();
});

document.addEventListener('keyup', (e) => {
    // Remove the released key
    pressedKeys.delete(e.key);
    updatePendingKey();
});