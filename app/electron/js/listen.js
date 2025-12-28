function renderObject(obj) {
    const ul = document.createElement("ul");

    for (const [key, value] of Object.entries(obj)) {
        const li = document.createElement("li");

        if (typeof value === "object" && value !== null) {
            li.innerHTML = `<strong>${key}</strong>:`;
            li.appendChild(renderObject(value));
        } else {
            li.innerHTML = `<strong>${key}</strong>: ${value}`;
        }

        ul.appendChild(li);
    }

    return ul;
}


export function connect(url) {
    const ws = new WebSocket(url);
    ws.onopen = () => {
        document.getElementById('output').textContent = 'Connected – waiting for updates...';
    };

    ws.onmessage = (event) => {
        const data = event.data;
        const output = document.getElementById("output");

        output.innerHTML = "<h3>Current voting state</h3>";
        output.appendChild(renderObject(JSON.parse(data)));
    };

    ws.onclose = () => {
        document.getElementById('output').textContent = 'Connection closed.';
    };

    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
    };
}

