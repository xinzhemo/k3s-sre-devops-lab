# k3s-sre-devops-lab
K3s · Kustomize · GitLab-CI · Prometheus · Argo Rollouts · NetworkPolicy | 微服务持续交付、集群网络质量观测与东西向流量安全隔离实践
# SRE DevOps Lab · 云原生运维实战项目集

> 基于 K3s 集群，从零构建的一套完整 DevOps 工具链演示项目。包含：微服务部署、GitOps 流水线、集群网络拨测、网络策略隔离及可观测性。

## 📌 项目背景
本项目模拟真实 SRE/DevOps 工作场景，在本地 VMware 虚拟化环境中，使用 3 台 Ubuntu 22.04 虚拟机搭建 K3s 集群。通过 **4 周时间**，落地了 3 个核心项目，旨在解决以下生产痛点：
- **发布效率**：如何标准化应用交付流程？
- **服务可用性**：如何主动发现集群内的网络故障？
- **集群安全**：如何通过 NetworkPolicy 实现微服务间的网络隔离？

## 🏗️ 集群架构
| 节点角色 | 主机名 | IP 地址 | 配置 |
| :--- | :--- | :--- | :--- |
| Master (Control Plane) | k3s-master | 192.168.56.10 | 2C 4G |
| Worker Node 1 | k3s-worker1 | 192.168.56.11 | 2C 4G |
| Worker Node 2 | k3s-worker2 | 192.168.56.12 | 2C 4G |

- **操作系统**：Ubuntu 22.04.5 LTS
- **Kubernetes 版本**：K3s v1.36.x
- **容器运行时**：containerd (K3s 内置)
- **CNI 插件**：默认 Flannel → 已迁移至 Calico (v3.26.1)

## 📂 项目结构详解

### 1️⃣ Project 1: 持续交付与金丝雀发布 (CI/CD & Rollouts)
- **业务代码**：`Flask` 微服务，提供 `/health` 和 `/` 接口，支持通过环境变量 `ENV` 和 `APP_VERSION` 区分环境。
- **多环境管理**：使用 **Kustomize** 管理 `dev` 和 `staging` 两套环境的配置差异（副本数、资源配额、环境变量）。
- **CI/CD 模拟**：编写了 `.gitlab-ci.yml` 标准流水线文件，并配套 `local-ci.sh` 脚本，模拟从 `git commit` → 镜像构建 (`docker build`) → 镜像导入 K3s (`ctr import`) → 更新 Staging 环境的完整过程。支持一键回滚 (`kubectl rollout undo`)。
- **弹性伸缩**：配置了 `HorizontalPodAutoscaler (HPA)`，基于 CPU 使用率自动扩缩容（副本数 1~5）。

### 2️⃣ Project 2: 集群网络拨测系统 (Network Prober)
- **核心逻辑**：通过 Python 调用 **Kubernetes API**，自动发现 `dev` 和 `staging` 命名空间下的所有 ClusterIP Service 及其 Endpoint。
- **主动探测**：对发现的目标进行 **TCP 连接探测**，计算连接延迟（Latency）。
- **指标暴露**：集成 `prometheus_client`，将探测成功率 (`tcp_probe_success_total`) 和延迟 (`tcp_probe_latency_ms`) 暴露为 Prometheus 指标。
- **部署形态**：以 **DaemonSet** 形式部署，确保每个节点运行一个 Agent。配置了完善的 RBAC 权限（ServiceAccount + ClusterRole）。

### 3️⃣ Project 3: 网络隔离与混沌演练 (NetworkPolicy)
- **CNI 迁移**：记录从 K3s 默认 Flannel 迁移至 **Calico** 的详细步骤与踩坑点（解决 containerd 镜像加速问题）。
- **策略编写**：
  - `deny-all`：默认拒绝所有入站流量。
  - `allow-demo-app`：仅允许 `monitoring` 命名空间访问 `demo-app` 的 5000 端口。
- **故障演练**：模拟“错误策略导致服务中断”和“数据库访问隔离”两个混沌场景，并记录恢复过程。

## 🚀 核心技术栈
| 分类 | 技术组件 |
| :--- | :--- |
| **编排调度** | Kubernetes (K3s), Kustomize, Helm |
| **可观测性** | Prometheus, Grafana, Loki |
| **网络与安全** | Calico, NetworkPolicy |
| **CI/CD 思想** | GitLab CI (流水线定义), Argo Rollouts (金丝雀理念) |
| **开发语言** | Python (Flask), Shell Script |

## 📝 如何快速验证
请参考 `docs/setup-guide.md` 完成集群初始化后，依次执行：
```bash
# 1. 部署项目1（多环境）
kubectl apply -k project-1-cicd-rollouts/k8s/overlays/dev

# 2. 运行本地 CI 模拟
cd project-1-cicd-rollouts && ./local-ci.sh

# 3. 部署项目2（拨测 Agent）
kubectl apply -f project-2-network-prober/k8s/daemonset.yaml

# 4. 部署项目3（网络策略）
kubectl apply -f project-3-network-policy/policies/allow-demo-app.yaml
