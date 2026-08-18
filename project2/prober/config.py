import os

# Prometheus 指标暴露端口
METRICS_PORT = int(os.getenv('METRICS_PORT', '19100'))

# 探测间隔（秒）
PROBE_INTERVAL = int(os.getenv('PROBE_INTERVAL', '30'))

# Webhook 服务端口
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5000'))

# 需要探测的命名空间（逗号分隔）
NAMESPACES = os.getenv('NAMESPACES', 'dev,staging').split(',')

# 探测超时时间（秒）
PROBE_TIMEOUT = int(os.getenv('PROBE_TIMEOUT', '5'))
