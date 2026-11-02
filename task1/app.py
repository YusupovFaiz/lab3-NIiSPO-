import os
import time
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/checkout')
def checkout():
    try:
        r = requests.get('https://httpbin.org/delay/0.5', timeout=5)
        upstream_status = r.status_code
    except Exception:
        upstream_status = 500
    time.sleep(0.1)
    return jsonify(order='A-1001', upstream=upstream_status)

@app.route('/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)