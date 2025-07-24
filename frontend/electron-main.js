const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let trainProcess;
let serveProcess;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
}

function startBackends() {
  const python = process.env.PYTHON || 'python';
  const backendDir = path.join(__dirname, '..', 'backend');

  trainProcess = spawn(python, [path.join(backendDir, 'train.py')], {
    stdio: 'inherit',
  });

  serveProcess = spawn(python, [path.join(backendDir, 'serve.py')], {
    stdio: 'inherit',
  });

  process.on('exit', () => {
    trainProcess && trainProcess.kill();
    serveProcess && serveProcess.kill();
  });
}

app.whenReady().then(() => {
  startBackends();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
