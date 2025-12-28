# Electron app

to install deps and build windows installer:

```shell
cd app/electron
npm install
npm run dist   # Create .exe build which is available under host:port/download
```

# Fastapi webserver + websockets

To run application

```shell
uvicorn app.webserver_app:init_app --host=0.0.0.0 --port=7790
```

# Input controller for windows and linux

```shell
PYTHONPATH="." python app/controller.py
```

Select the window for which to allow input, if this window is not in focus, inputs are ignored.
Some games with anticheat disable this input completely (like LoL or Elden Ring with multiplayer enabled).
You can mod Elden Ring to disable anti-cheat and only play offline instead to make this work.

Tested with
- Elden Ring
- No Man's Sky