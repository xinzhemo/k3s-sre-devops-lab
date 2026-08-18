from kubernetes import client, config
import logging

logger = logging.getLogger(__name__)

def get_services(namespaces):
    """
    通过 K8s API 自动发现指定命名空间下的 ClusterIP Service
    返回 Service Endpoint 列表
    """
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()
    
    v1 = client.CoreV1Api()
    services = []
    
    for svc in v1.list_service_for_all_namespaces().items:
        if svc.spec.type == 'ClusterIP' and svc.metadata.namespace in namespaces:
            try:
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
            except Exception as e:
                logger.warning(f"Failed to get endpoints for {svc.metadata.name}: {e}")
                continue
    
    return services
