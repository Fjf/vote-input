const host = location.host.startsWith('file') || location.host === '' ? 'localhost:7790' : location.host;
const ws = new WebSocket(`ws://${host}/listen`);

ws.onopen = () => {
    document.getElementById('output').textContent = 'Connected – waiting for updates...';
};

ws.onmessage = (event) => {
    const data = event.data;
    document.getElementById('output').textContent = `Current voting state:\n${data}`;
};

ws.onclose = () => {
    document.getElementById('output').textContent = 'Connection closed.';
};

ws.onerror = (err) => {
    console.error('WebSocket error:', err);
};