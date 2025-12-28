const {app, BrowserWindow} = require('electron');


function createWindow() {
    const win = new BrowserWindow({
        fullscreen: false,
        width: 500,
        height: 500,
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        resizable: false,
        hasShadow: false,
        webPreferences: {
            contextIsolation: true, nodeIntegration: false, pointerLock: true
        }
    });

    win.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
