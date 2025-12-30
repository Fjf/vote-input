const {app, BrowserWindow, ipcMain} = require('electron');
const {join} = require("node:path");
const {spawn} = require('child_process');
const {existsSync} = require("node:fs");

let win;

function createWindow() {
    win = new BrowserWindow({
        fullscreen: false,
        width: 1728.0,
        height: 972.0,
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        resizable: false,
        hasShadow: false,
        webPreferences: {
            preload: join(__dirname, 'preload.js'),
            contextIsolation: false,
            nodeIntegration: true,
            pointerLock: true
        }
    });
    win.webContents.openDevTools();
    win.loadFile('index.html');
}

ipcMain.on('start-stream', (_, ip) => {
    const ffmpegPath = join(__dirname, 'resources', 'ffmpeg.exe');
    const args = [
        '-i', `rtmp://${ip}:1935/live`,
        '-fflags', 'nobuffer',
        '-flags', 'low_delay',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-vf', 'scale=1920:1080',
        '-'
    ];

    const ffmpeg = spawn(ffmpegPath, args);

    ffmpeg.stdout.on('data', chunk => {
        if (win && !win.isDestroyed()) {
            win.webContents.send('video-frame', chunk); // send to renderer
        }
    });
    ffmpeg.stderr.on('data', data => console.log(`ffmpeg stderr: ${data}`));
    ffmpeg.on('close', code => console.log(`ffmpeg exited with code ${code}`));
});

app.whenReady().then(createWindow);


app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
