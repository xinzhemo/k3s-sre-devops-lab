#!/usr/bin/env python3
import os
import time
import socket
from kubernetes import client, config
from prometheus_client import start_http_server, Gauge, Counter

PORT = int(os.getenv('METRICS_PORT', '9100'))

PROBE_SUCCESS = Counter('tcp_probe_success_total', 'TCP probe success', ['target_service', 'target_pod'])
PROBE_FAILURE = Counter('tcp_probe_failure_total', 'TCP probe failure', ['target_service', 'target_pod', 'reason'])
PROBE_LATENCY = Gauge('tcp_probe_latency_ms', 'TCP probe latency', ['target_service', 'target_pod'])

def get_services():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    v1 = client.CoreV1Api()
    services = []
    for svc in v1.list_service_for_all_namespaces().items:
        if svc.spec.type == 'ClusterIP' and svc.metadata.namespace in ['dev', 'staging']:
            endpoints = v1.read_namespaced_endpoints(svc.metadata.name, svc.metadata.namespace)
            if endpoints.subsets:
                for subset in endpoints.subsets:
                    for addr in subset.addresses:
                        for port in subset.ports:
                            services.append({
                                'name': f"{svc.metadata.namespace}/{svc.metadata.name}",
                                'pod': addr.target_ref.name if addr.target_ref else 'unknown',
                                'ip': addr.ip,
                                'port': port.port
                            })
    return services

def probe_target(target):
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((target['ip'], target['port']))
        latency = (time.time() - start) * 1000
        if result == 0:
            PROBE_SUCCESS.labels(target['name'], target['pod']).inc()
            PROBE_LATENCY.labels(target['name'], target['pod']).set(latency)
            print(f"✓ {target['name']} ({target['pod']}) - {latency:.1f}ms")
        else:
            PROBE_FAILURE.labels(target=target["name"], pod=target["pod"], reason=f"connect_failed_{result}").inc()
            print(f"✗ {target['name']} ({target['pod']}) - failed: {result}")
        sock.close()
    except Exception as e:
        PROBE_FAILURE.labels(target=target["name"], pod=target["pod"], reason=str(e)).inc()
        print(f"✗ {target['name']} ({target['pod']}) - error: {e}")

def main():
    # 尝试绑定端口，失败则重试
    while True:
        try:
            start_http_server(PORT)
            print(f"Probe agent started on :{PORT}")
            break
        except OSError as e:
            print(f"Port {PORT} in use, retrying in 5s... ({e})")
            time.sleep(5)

    while True:
        targets = get_services()
        print(f"Found {len(targets)} targets")
        for t in targets:
            probe_target(t)
        time.sleep(30)

if __name__ == '__main__':
    main()
