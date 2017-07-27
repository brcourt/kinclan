#!venv/bin/python
from app import app
from flask_socketio import SocketIO, emit


# :::WARNING:::
# This should only be used to launch the development version


# app.debug = False
# app.run(host='0.0.0.0', port=5000)
async_mode = None

socketio = SocketIO(app, async_mode=async_mode)
socketio.run(app, debug=True)
