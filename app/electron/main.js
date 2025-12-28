const {app, BrowserWindow} = require('electron');

function createWindow() {
    const win = new BrowserWindow({
        fullscreen: false,
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        resizable: false,
        hasShadow: false,
        webPreferences: {
            contextIsolation: true, nodeIntegration: false, pointerLock: true
        }
    });

    // Disable esc to close input capturing
    win.webContents.on("before-input-event", (event, input) => {
        if (input.key === "Escape") {
            event.preventDefault();
        }
        // F1 releases mouse control
        if (input.key === "F1" && mouseLocked) {
            event.preventDefault();
            mouseLocked = false;

            win.webContents.executeJavaScript(`
        document.exitPointerLock();
        window.dispatchEvent(new Event("game-unlock"));
      `);
        }
    });

    win.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
