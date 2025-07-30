# main.py

import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler
from influxdb import InfluxDBClient


def init_influxdb(config):
    influx_config = config.get("influxdb", {})
    client = InfluxDBClient(
        host=influx_config.get("host", "localhost"),
        port=influx_config.get("port", 8086),
        username=influx_config.get("username", "root"),
        password=influx_config.get("password", "root"),
        database=influx_config.get("database", "network_traffic")
    )

    return client


def poll_client(client_url):
    try:
        response = requests.get(f"{client_url}/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def send_to_influxdb(client, metrics):
    device_id = metrics.get("device_id", "unknown_device")
    timestamp = metrics.get("timestamp", None)
    
    time_precision = "s"
    if timestamp:
        time_precision = "ms"
        influx_time = timestamp
    else:
        influx_time = None

    base_metric = {
        "measurement": "network_metrics",
        "tags": {
            "device_id": device_id
        },
        "fields": {
            "incoming_traffic": metrics.get("incoming_traffic", 0),
            "outgoing_traffic": metrics.get("outgoing_traffic", 0),
            "active_tcp_connections": metrics.get("active_tcp_connections", 0),
            "active_udp_connections": metrics.get("active_udp_connections", 0)
        }
    }

    if influx_time:
        base_metric["time"] = influx_time

    points = [base_metric]

    ip_traffic = metrics.get("ip_traffic", {})
    for item in ip_traffic:
        ip_metric = {
            "measurement": "ip_traffic",
            "tags": {
                "device_id": device_id,
                "ip_address": item.get("ip_address")
            },
            "fields": {
                "sent": item.get("sent", 0),
                "received": item.get("received", 0),
                "total": item.get("total", 0)
            }
        }

        if influx_time:
            ip_metric["time"] = influx_time

        points.append(ip_metric)

    try:
        client.write_points(points, time_precision=time_precision)
    except Exception as e:
        print(f"InfluxDB write error: {str(e)}")


def start_polling(config):
    interval = config.get("client_polling_interval_seconds", 15)
    clients = config.get("clients", [])

    influx_client = init_influxdb(config)

    print("Starting client polling...")
    print(f"Polling interval: {interval} seconds")
    print(f"Target database: {config.get('influxdb', {}).get('database', 'traffic_db')}")
    print(f"Clients: {', '.join(clients)}\n")

    def job():
        for client_url in clients:
            metrics = poll_client(client_url)
            if metrics:
                send_to_influxdb(influx_client, metrics)

    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', seconds=interval)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.shutdown()
