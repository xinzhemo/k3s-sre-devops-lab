import time
import socket
import logging

logger = logging.getLogger(__name__)

def probe_target(target, timeout=5):
    """
    TCP 连通性探测
    返回 (是否成功, 延迟毫秒数)
    """
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target['ip'], target['port']))
        latency = (time.time() - start) * 1000
        sock.close()
        return result == 0, latency
    except socket.timeout:
        return False, 0
    except Exception as e:
        logger.error(f"Probe error for {target['name']}: {e}")
        return False, 0
