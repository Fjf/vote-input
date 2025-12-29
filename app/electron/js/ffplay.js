const path = require('path');
const { spawn } = require('child_process');

export function startStream(ip) {
    const ffplayPath = path.join(process.resourcesPath, 'resources', 'ffplay.exe');
    const args = [
      `rtmp://${ip}:1935/live`,
      '-fflags', 'nobuffer',
      '-flags', 'low_delay',
      '-fs'  // fullscreen
      // '-framedrop',
      // '-probesize', '32',
      // '-analyzeduration', '0'
    ];

    const ffplay = spawn(ffplayPath, args);

    ffplay.stdout.on('data', data => {
      console.log(`stdout: ${data}`);
    });

    ffplay.stderr.on('data', data => {
      console.log(`stderr: ${data}`);
    });

    ffplay.on('close', code => {
      console.log(`ffplay exited with code ${code}`);
    });
}