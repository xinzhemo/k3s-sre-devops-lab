# Network Prober · 集群网络拨测系统

基于 Kubernetes API 的主动式集群网络可观测性组件，实现 Service 级 TCP 连通性探测、延迟监控与告警自愈框架。

## 📌 项目介绍
Kubernetes 集群内部网络缺乏主动探测能力，Service 级网络抖动、端口异常等问题仅能依赖被动告警发现，故障感知滞后，定位效率低。

Network Prober 通过自研拨测 Agent，实现对集群内 Service 的**主动、持续、可观测**的 TCP 连通性探测，并将结果标准化接入 Prometheus 监控体系，同时提供告警 Webhook 接收端与自动处置框架，补齐集群网络可观测性的最后闭环。

## 🛠 技术栈
| 分类 | 组件 | 说明 |
|------|------|------|
| 开发语言 | Python 3.9 | 核心逻辑与 API 交互 |
| K8s 交互 | kubernetes-client | Service 发现与 RBAC 认证 |
| 指标暴露 | prometheus-client | 标准化 /metrics 端点 |
| Web 服务 | Flask | 告警 Webhook 接收端 |
| 部署模型 | DaemonSet + RBAC | 每节点一个 Agent，最小权限授权 |
| 监控接入 | Prometheus + Grafana | 指标采集与可视化 |

## 📁 项目目录结构
```plaintext
仓库根目录
├── .github/workflows/                     # CI自动构建流水线（仓库根目录，GitHub识别）
│   └── ci.yml
├── docs/
└── project2/                              # 项目源码目录
    ├── prober/
    │   ├── config.py                      # 配置管理（端口、间隔、命名空间）
    │   ├── discover.py                    # K8s Service 自动发现
    │   ├── probe.py                       # TCP 连通性探测
    │   ├── metrics.py                     # Prometheus 指标定义
    │   ├── webhook.py                     # Alertmanager 告警接收 + 自愈框架
    │   └── main.py                        # 程序入口
    ├── k8s/
    │   ├── daemonset.yaml                 # DaemonSet + ServiceAccount + ClusterRole
    │   └── service.yaml                   # Service（暴露 metrics 端口）
    ├── Dockerfile
    ├── requirements.txt
    └── README.md
```
✨ 核心能力
1. 自动服务发现
通过 list_service_for_all_namespaces 动态获取 dev/staging 下的所有 ClusterIP Service，自动解析 Endpoint 并生成探测目标列表。全程无需人工配置探测 IP / 端口。
2. TCP 连通性探测
对每个目标执行 TCP 四层握手探测，记录连接延迟（毫秒）与成功 / 失败状态。支持超时控制（默认 5s）和异常捕获，保证单点故障不影响整体探测任务。
3. Prometheus 指标暴露
标准化 /metrics 端点，提供以下核心指标：
表格
指标名	类型	标签	说明
tcp_probe_success_total	Counter	target_service, target_pod	累计成功探测次数
tcp_probe_failure_total	Counter	target_service, target_pod, reason	累计失败探测次数
tcp_probe_latency_ms	Gauge	target_service, target_pod	最近一次探测延迟（ms）
tcp_probe_targets_total	Gauge	namespace	当前探测目标总数
4. 告警自愈框架（可选）
提供 Flask Webhook 接收端，接收 Alertmanager 的 ServiceDown 告警。内置 AUTO_HEAL_ENABLED 开关，开启后可自动执行隔离逻辑（通过 kubectl label 标记故障 Pod），实现监控→告警→自动处置的 SRE 闭环。
## 🚀 快速部署与使用
### 1. 构建镜像
```bash
docker build -t probe_agent:v3 .
2. 导入到 K3s containerd
bash
sudo docker save probe_agent:v3 | sudo k3s ctr images import -
3. 部署到集群
bash
# 创建命名空间
kubectl create namespace monitoring

# 部署 DaemonSet + RBAC
kubectl apply -f k8s/daemonset.yaml
kubectl apply -f k8s/service.yaml
4. 验证运行状态
bash
# 检查 Pod 状态
kubectl get pods -n monitoring -l app=probe-agent

# 查看探测日志
kubectl logs -n monitoring -l app=probe-agent --tail=30
5. 验证指标采集
bash
kubectl port-forward svc/probe-agent 19100:19100 -n monitoring &
curl http://localhost:19100/metrics | grep tcp_probe
6. 验证 Webhook 端点
bash
kubectl port-forward svc/probe-agent 5000:5000 -n monitoring &
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"alerts":[{"status":"firing","labels":{"alertname":"ServiceDown","target_service":"dev/demo-service"}}]}'
# 预期返回: {"status":"ok"}
```
### ⚙️ 配置参数
| 环境变量 | 默认值 | 说明 |
| ---- | ---- | ---- |
| METRICS_PORT | 19100 | Prometheus 指标暴露端口 |
| WEBHOOK_PORT | 5000 | Webhook 服务端口 |
| PROBE_INTERVAL | 30 | 探测间隔（秒） |
| NAMESPACES | dev,staging | 目标命名空间（逗号分隔） |
| PROBE_TIMEOUT | 5 | TCP 连接超时（秒） |
| AUTO_HEAL_ENABLED | False | 自动处置开关 |

### 🔧 项目难点与解决方案
- K3s 容器内访问 K8s API：挂载 ServiceAccount Token，使用 `load_incluster_config()`
- Python 日志缓冲导致 kubectl logs 无输出：设置 `PYTHONUNBUFFERED=1`
- 端口复用冲突：通过 METRICS_PORT 环境变量动态指定
- 模块化代码组织：按职责拆分为 config/discover/probe/metrics/webhook/main

### 📷 项目效果展示
- 集群与环境状态
- 服务与配置验证
- CI/CD 自动化效果
- 告警自愈执行效果

### 📎 相关文档
- https://github.com/kubernetes-client/python
- https://github.com/prometheus/client_python
- https://prometheus.io/docs/alerting/latest/configuration/#webhook_config
