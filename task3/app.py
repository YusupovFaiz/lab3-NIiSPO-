import os
import time
import logging
from flask import Flask, jsonify, request
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from prometheus_client import start_http_server
import requests

# Создаём директорию для логов
os.makedirs('/app/logs', exist_ok=True)

# Настройка логирования в файл
logging.basicConfig(
    filename='/app/logs/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

start_http_server(8000)

reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader], resource=Resource.create({"service.name": "lab3-task3"}))
set_meter_provider(provider)

meter = metrics.get_meter("lab3.meter")

request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)
request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration",
    unit="s"
)

app = Flask(__name__)

@app.before_request
def before_request():
    request.start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        request_duration.record(duration, {"route": request.path, "method": request.method})
    request_counter.add(1, {"route": request.path, "method": request.method, "status": str(response.status_code)})
    logger.info(f"Response: {request.method} {request.path} -> {response.status_code}")
    return response

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