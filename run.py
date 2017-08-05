#!venv/bin/python

# from flask import Flask, Blueprint
from app import app, socketio


# :::WARNING:::
# This should only be used to launch the development version


# app.debug = False
# app.run(host='0.0.0.0', port=5000)
async_mode = None

# socketio = SocketIO(app, async_mode=async_mode)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
