# Network Security · 集群网络隔离与 Ingress 接入

基于 Calico CNI 与 Kubernetes NetworkPolicy 的集群网络管控实践，实现东西向微服务隔离与南北向流量统一接入。

---

## 📌 项目定位

Kubernetes 集群默认 Pod 间全互通，存在越权访问与横向渗透风险；同时集群内部服务缺少统一的南北向流量入口，外部访问能力薄弱。

本项目通过 **CNI 迁移（Flannel → Calico）** 落地 NetworkPolicy 网络隔离策略，实现东西向流量的最小权限管控；同时接入 **Nginx Ingress Controller** 提供统一的南北向流量入口，形成完整的集群网络治理闭环。

---

## 🔧 技术栈

| 分类 | 组件 | 说明 |
|------|------|------|
| CNI 插件 | Calico v3.26.1 | 支持 NetworkPolicy 的网络方案 |
| 网络策略 | Kubernetes NetworkPolicy | 东西向流量隔离控制 |
| 镜像加速 | registries.yaml | 解决国内 pause 镜像拉取问题 |
| Ingress Controller | Nginx Ingress (v1.10.0) | 南北向流量统一入口 |
| 流量验证 | tcpdump | 抓包验证流量路径 |
| 调试工具 | Busybox | 跨命名空间连通性测试 |

---

## 📁 目录结构
```text
project3/
├── policies/
│   ├── screenshots/                # 截图存放目录
│   ├── README.md                   # 项目说明文档
│   ├── allow-demo-app.yaml         # 精细化放行策略
│   └── deny-all.yaml               # 默认拒绝所有入站流量
├── deploy.yaml                     # 业务应用部署清单
├── ingress.yaml                    # Ingress访问规则
├── nginx-svc.yaml                  # Nginx服务资源
└── webhook-local.yaml              # webhook本地配置


```

## 🎯 核心能力

### 1. CNI 迁移：Flannel → Calico

| 阶段 | 操作 | 说明 |
|------|------|------|
| 迁移前 | K3s 默认 Flannel | 不支持 NetworkPolicy，Pod 全互通 |
| 迁移后 | Calico v3.26.1 | 支持 NetworkPolicy，具备网络隔离能力 |
| 关键挑战 | pause 镜像拉取失败 | 配置 `registries.yaml` 添加阿里云镜像加速解决 |

### 2. 东西向流量隔离（NetworkPolicy）

| 策略 | 作用 | 验证方式 |
|------|------|----------|
| `deny‑all` | 默认拒绝所有入站流量 | Busybox 跨 namespace 访问被拒绝 |
| `allow‑demo‑app` | 仅放行 monitoring 访问 demo‑app:5000 | Busybox 从 monitoring 访问成功 |
| DNS 放行 | 解决策略阻断 DNS 解析问题 | UDP 53 端口单独放行 |

### 3. 南北向流量接入（Nginx Ingress）

| 组件 | 说明 |
|------|------|
| Ingress Controller | NodePort 方式暴露（30080） |
| Ingress 规则 | `demo.staging.local` → `staging‑demo‑service:80` |
| 访问验证 | `curl -H "Host: demo.staging.local" http://<NodeIP>:30080/health` 返回 `OK` |

### 4. 故障演练（手动）

| 场景 | 操作 | 验证结果 |
|------|------|----------|
| 错误策略注入 | 应用 `wrong‑deny.yaml`（拒绝所有入站） | 拨测 Agent 探测失败 |
| 故障恢复 | 删除错误策略 | 拨测 Agent 探测成功，服务恢复 |
| 演练闭环 | 监控发现 → 定位 → 恢复 | SRE 稳定性闭环验证通过 |

### 5. 抓包验证（网络工程差异化）

通过 `tcpdump` 在宿主机抓包，验证 Ingress → Service → Pod 流量路径完整。

---

## 🚀 部署指南

### 安装 Calico
```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/calico.yaml
配置镜像加速（关键步骤）
sudo tee -a /etc/rancher/k3s/registries.yaml << 'EOF'
mirrors:
  docker.io:
    endpoint:
      - "https://registry.cn-hangzhou.aliyuncs.com"
      - "https://docker.m.daocloud.io"
EOF
sudo systemctl restart k3s

应用 NetworkPolicy
kubectl apply -f policies/deny-all.yaml
kubectl apply -f policies/allow-demo-app.yaml

验证策略
# 从 monitoring 访问（应该成功）
kubectl run test-pod --image=busybox -n monitoring --rm -it --restart=Never -- wget -O- http://dev-demo-service.dev.svc.cluster.local:80/health

# 从 staging 访问（应该被拒绝）
kubectl run test-pod --image=busybox -n staging --rm -it --restart=Never -- wget -O- --timeout=2 http://dev-demo-service.dev.svc.cluster.local:80/health

安装 Nginx Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  -n ingress-nginx --create-namespace \
  --set controller.image.repository=registry.aliyuncs.com/google_containers/nginx-ingress-controller \
  --set controller.image.tag=v1.10.0 \
  --set controller.image.digest="" \
  --set controller.resources.requests.memory="128Mi" \
  --set controller.resources.requests.cpu="100m" \
  --set controller.service.type=NodePort \
  --set admissionWebhooks.enabled=false \
  --set admissionWebhooks.patch.enabled=false

创建 Ingress 规则
kubectl apply -f ingress.yaml

验证访问
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
curl -H "Host: demo.staging.local" http://${NODE_IP}:30080/health
# 预期返回: OK


---
🔧 技术要点
挑战
解决方案
Calico pause 镜像拉取失败
配置 registries.yaml 阿里云镜像加速
NetworkPolicy 阻断 DNS 解析
放行 kube‑dns UDP 53 端口
Nginx Ingress webhook 镜像拉不到
禁用 admission webhook
Ingress 创建时 webhook 调用失败
删除残留的 ValidatingWebhookConfiguration
策略指向错误的命名空间
确认 Service 所在命名空间，重新创建 Ingress

---
📎 相关文档
- https://docs.tigera.io/calico/latest/about/
- https://kubernetes.io/docs/concepts/services-networking/network-policies/
- https://kubernetes.github.io/ingress-nginx/
- https://www.tcpdump.org/
