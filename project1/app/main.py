from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify(
        status="ok",
        version=os.getenv("APP_VERSION", "v1"),
        env=os.getenv("ENV", "dev"),
        pod=socket.gethostname()
    )

@app.route('/')
def index():
    return jsonify(
        service="demo",
        env=os.getenv("ENV", "dev"),
        version=os.getenv("APP_VERSION", "v1")
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
