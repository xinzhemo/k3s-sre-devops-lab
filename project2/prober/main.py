import time
import threading
import logging
import os
from prometheus_client import start_http_server

from config import METRICS_PORT, PROBE_INTERVAL, NAMESPACES, WEBHOOK_PORT, PROBE_TIMEOUT
from discover import get_services
from probe import probe_target
from metrics import PROBE_SUCCESS, PROBE_FAILURE, PROBE_LATENCY, PROBE_TARGETS
from webhook import start_webhook, AUTO_HEAL_ENABLED

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_probe_loop():
    """主探测循环"""
    while True:
        try:
            targets = get_services(NAMESPACES)
            logger.info(f"Found {len(targets)} targets in namespaces: {NAMESPACES}")
            
            # 更新目标总数指标
            PROBE_TARGETS.labels(namespace=','.join(NAMESPACES)).set(len(targets))
            
            for t in targets:
                success, latency = probe_target(t, PROBE_TIMEOUT)
                if success:
                    PROBE_SUCCESS.labels(t['name'], t['pod']).inc()
                    PROBE_LATENCY.labels(t['name'], t['pod']).set(latency)
                    logger.debug(f"✓ {t['name']} - {latency:.2f}ms")
                else:
                    PROBE_FAILURE.labels(t['name'], t['pod'], reason="timeout").inc()
                    logger.warning(f"✗ {t['name']} - timeout")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"Probe loop error: {e}")
        
        time.sleep(PROBE_INTERVAL)

def main():
    # 显示配置信息
    logger.info(f"Starting Probe Agent with config:")
    logger.info(f"  - Metrics port: {METRICS_PORT}")
    logger.info(f"  - Webhook port: {WEBHOOK_PORT}")
    logger.info(f"  - Probe interval: {PROBE_INTERVAL}s")
    logger.info(f"  - Namespaces: {NAMESPACES}")
    logger.info(f"  - Auto-heal: {AUTO_HEAL_ENABLED}")
    
    # 启动 Prometheus 指标服务
    start_http_server(METRICS_PORT)
    logger.info(f"Prometheus metrics exposed on :{METRICS_PORT}")
    
    # 启动 Webhook 服务（独立线程）
    webhook_thread = threading.Thread(
        target=start_webhook,
        args=(WEBHOOK_PORT,),
        daemon=True
    )
    webhook_thread.start()
    logger.info(f"Webhook server listening on :{WEBHOOK_PORT}")
    
    # 启动探测循环（主线程）
    run_probe_loop()

if __name__ == '__main__':
    main()
