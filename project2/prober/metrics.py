from prometheus_client import Counter, Gauge

# TCP 探测成功计数
PROBE_SUCCESS = Counter(
    'tcp_probe_success_total',
    'Total TCP probe success count',
    ['target_service', 'target_pod']
)

# TCP 探测失败计数
PROBE_FAILURE = Counter(
    'tcp_probe_failure_total',
    'Total TCP probe failure count',
    ['target_service', 'target_pod', 'reason']
)

# TCP 探测延迟（毫秒）
PROBE_LATENCY = Gauge(
    'tcp_probe_latency_ms',
    'TCP probe latency in milliseconds',
    ['target_service', 'target_pod']
)

# 探测目标总数
PROBE_TARGETS = Gauge(
    'tcp_probe_targets_total',
    'Total number of probe targets',
    ['namespace']
)
