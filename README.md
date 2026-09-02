# SRE DevOps Lab · 云原生运维工程实战项目集

基于轻量化 K3s 生产级集群搭建的全链路云原生 SRE/DevOps 工程实践项目。项目围绕持续交付、可观测治理、网络安全管控三大运维核心场景，落地 GitOps 持续部署、服务主动拨测告警、集群网络最小权限隔离与南北流量治理能力，构建标准化、可落地、可自愈的 Kubernetes 服务稳定性运维闭环。

---

## 📌 项目概述

在本地虚拟化环境中，基于 3 节点 Ubuntu 22.04 部署生产级 K3s 集群，以此为基础实践 SRE 稳定性工程体系，落地三大核心工程模块，覆盖代码交付、服务观测、网络安全、流量治理、故障自愈全流程能力,还原云原生运维工作流。

三大子项目各司其职、相互联动，形成完整的运维工程闭环：

| 项目模块 | 业务定位 | 核心工程能力 |
|----------|----------|--------------|
| 项目一：微服务持续交付平台 | 标准化研发交付体系落地 | GitOps 声明式部署、灰度金丝雀发布、业务负载弹性伸缩、多环境隔离治理 |
| 项目二：集群服务拨测与自愈系统 | 服务稳定性可观测与故障自愈 | 集群服务自动发现、TCP 连通性主动探测、指标监控采集、告警 Webhook 联动、自动化故障处置 |
| 项目三：集群网络安全与流量治理 | 集群网络权限管控与流量标准化接入 | CNI 网络架构升级、东西向流量最小权限隔离、南北向流量统一接入、网络故障演练与流量溯源 |

---

## 🏗️ 整体架构

项目整体遵循外部流量接入 → 集群网络管控 → 服务交付运行 → 监控自愈兜底的企业运维架构设计，实现全链路可控、可观测、可自愈。

```
外部用户/公网流量
        │
        ▼
Nginx Ingress Controller（统一南北流量入口）
        │
        ▼
K3s 生产集群（3 节点高可用）
├─ 持续交付体系：GitHub Actions + ArgoCD + Argo Rollouts + HPA
├─ 稳定性观测体系：服务自动拨测 + Prometheus 指标采集 + 告警自愈
└─ 网络安全体系：Calico CNI + NetworkPolicy 精细化流量隔离
        │
        ▼
可观测运维底座：Prometheus + Grafana（指标可视化、故障溯源）
```

---

## 📁 项目目录结构

```
k3s-sre-devops-lab/
├── project1-cicd-rollouts/        # 微服务持续交付与灰度扩容模块
├── project2-network-prober/       # 集群服务拨测与故障自愈模块
├── project3-network-policy/       # 集群网络隔离与Ingress流量治理模块
├── docs/                          # 项目运维文档与故障复盘手册
├── .github/workflows/             # 自动化CI构建流水线
└── README.md                      # 项目总览文档
```

---

## 🛠️ 核心技术栈（工程化）

| 技术分类 | 组件 | 工程用途 |
|----------|------|----------|
| 基础设施 | K3s、containerd、Ubuntu 22.04 | 构建轻量、高可用、生产兼容的 Kubernetes 运行集群 |
| 容器与镜像 | Docker、镜像加速 | 标准化镜像构建、国内环境镜像拉取优化 |
| 持续交付 | GitHub Actions、ArgoCD、Kustomize | 实现代码提交到集群更新的全自动化 GitOps 交付 |
| 发布治理 | Argo Rollouts、HPA | 灰度金丝雀发布规避变更风险，负载自动弹性伸缩保障服务容量 |
| 网络架构 | Calico、Nginx Ingress | 支撑网络策略隔离、统一南北流量入口，标准化流量治理 |
| 运维观测 | Prometheus、Grafana、自研拨测Agent | 服务可用性探测、指标采集、可视化监控、故障告警 |
| 故障验证 | tcpdump、Busybox | 流量链路溯源、网络连通性校验、故障场景复盘验证 |

---

## 🚀 核心模块工程能力详解

### 一、微服务持续交付平台（项目一）

聚焦研发交付标准化、变更风险可控、资源弹性调度，搭建企业级 GitOps 交付体系，替代传统手动发布模式。

**核心工程能力：**

- **全自动化 GitOps 闭环**：代码推送触发 CI 镜像构建、自动推送镜像仓库，ArgoCD 实时监听配置变更，实现集群资源无感知自动同步。
- **可控灰度发布**：基于 Argo Rollouts 实现分阶段金丝雀放量（20%→50%→100%），支持发布暂停、回滚、强制全量，有效规避版本上线风险。
- **负载弹性伸缩**：配置 HPA 基于 CPU 利用率自动扩缩容，根据业务负载动态调整 Pod 副本数量，平衡服务稳定性与资源利用率。
- **多环境治理**：通过 Kustomize 实现开发、预发环境配置隔离，基础配置复用、环境差异化配置独立管理，符合企业多环境交付规范。

**工程难点与落地方案：**

- 解决 K3s containerd 与 Docker 镜像兼容问题，实现镜像跨引擎导入部署。
- 优化国内网络环境，通过 SSH 密钥协议解决 ArgoCD 拉取远程仓库超时问题。

---

### 二、集群服务拨测与自愈系统（项目二）

面向服务可用性常态化巡检、故障主动发现、自动化处置，自研集群主动拨测运维组件，补齐集群服务监控盲区。

**核心工程能力：**

- **集群服务自动发现**：调用 Kubernetes 原生 API，自动遍历指定命名空间下所有业务 Service，无需手动配置探测目标。
- **常态化连通性探测**：以 DaemonSet 全局部署，每 30 秒发起 TCP 连通性探测，精准采集服务连通状态与响应延迟。
- **标准化指标暴露**：对外暴露 Prometheus 规范指标，包含服务成功数、失败数、延迟指标，支撑监控大盘可视化与告警规则配置。
- **告警自愈联动**：实现 Alertmanager 标准 Webhook 接收端，内置 AUTO_HEAL_ENABLED 开关，开启后自动执行 kubectl label 隔离故障 Pod。开关默认关闭,通过测试告警验证，生产环境可一键开启。

**工程难点与落地方案：**

- 配置容器非缓冲日志输出，解决容器日志无打印问题，保障运维日志可观测。
- 基于 ServiceAccount 与 RBAC 权限体系，实现容器内安全访问集群 API，遵循最小权限原则。

---

### 三、集群网络安全与流量治理（项目三）

聚焦集群网络安全加固、微服务访问权限管控、南北流量标准化治理，解决 K8s 默认全网互通的安全风险，落地生产级网络安全规范。

**核心工程能力：**

- **网络架构升级**：完成集群 CNI 从 Flannel 到 Calico 迁移，开启 Kubernetes NetworkPolicy 网络隔离能力，满足生产安全基线要求。
- **东西向流量最小权限管控**：配置全局默认拒绝策略，结合精细化放行规则，实现跨命名空间、跨服务的访问权限严格管控，杜绝横向渗透风险。
- **南北向流量统一接入**：部署 Nginx Ingress 作为集群唯一流量入口，实现域名路由转发、流量统一管控，替代原生 NodePort 裸暴露的不规范模式。
- **网络故障演练与溯源**：通过错误策略注入模拟生产网络故障，验证故障发现、定位、恢复全流程；结合 tcpdump 抓包完成流量链路溯源，保障网络变更可验证、可复盘。

**工程难点与落地方案：**

- 配置多源镜像加速，解决 Calico 基础镜像国内拉取失败问题，保障网络组件稳定部署。
- 优化 Ingress 部署参数，禁用镜像拉取失败的准入 Webhook，适配国内网络环境。
- 放行集群 DNS 解析端口，解决网络策略过严导致的域名解析异常问题。

---
## 🔒 安全与容灾加固

### 密钥安全加密管理
集成 **Sealed-Secrets**，将敏感 Secret 加密后提交至 Git 仓库，原始密钥不进版本控制。只有集群内的 Controller 能解密，保障 GitOps 仓库的密钥管理安全。

### 控制面数据容灾
编写 K3s SQLite 数据库定时备份脚本，完整演练 **删除资源 → 停 K3s → 覆盖备份 → 重启 → 验证恢复** 全流程。理解 K3s 单节点默认使用 SQLite，备份恢复逻辑与 etcd 等价，生产环境多 Master 时可复用。

### 生产环境差距分析
编写 `production-gap.md` 文档，逐条分析本地环境与真实生产集群的差距（控制面高可用、持久化存储、外部 LB、日志系统、告警通道），并形成可落地的迁移路线图。

---

## 📊 整体 SRE 稳定性闭环

三大模块深度联动，形成交付可控、运行可管、异常可测、故障可自愈的完整云原生运维工程体系：

- **交付层**：CI/CD 自动化构建 + 灰度发布 + 弹性扩容，保障服务迭代安全、容量稳定。
- **网络层**：Ingress 统一流量入口 + NetworkPolicy 权限隔离，保障集群网络安全、流量规范。
- **观测层**：主动拨测 + 指标监控 + 告警联动，实时感知服务运行状态。
- **自愈层**：故障自动告警 + 自动化处置，缩短故障恢复时长，提升服务可用性。

---

## 📸 验证截图

### 金丝雀发布（项目一）
![金丝雀 20% 流量切换](./project1/screenshots/canary-20-percent.jpg)
*20% 流量切换至新版本，金丝雀发布进行中*

![金丝雀全量发布完成](./project1/screenshots/rollout-healthy.jpg)
*100% 流量切换完成，服务健康*

### 拨测指标采集（项目二）
![Prometheus 拨测指标](./screenshots/prometheus-metrics.jpg)
*拨测 Agent 暴露 tcp_probe_success_total 和 tcp_probe_latency_ms 指标*

### 网络隔离 + Ingress 验证（项目三）
![NetworkPolicy 放行](./screenshots/allow-policy-success.jpg)
*monitoring 命名空间成功访问 dev-demo-service，NetworkPolicy 生效*

![tcpdump 抓包验证 Ingress 流量](./screenshots/tcpdump-ingress.png)
*tcpdump 抓包确认 Ingress → Service → Pod 流量路径完整*

## 🔧 环境部署要求

适配企业测试/预发环境标准，硬件与软件环境要求如下：

- **虚拟化平台**：VMware Workstation
- **集群节点**：3 台 Ubuntu 22.04 虚拟机（4核4G/节点）
- **基础环境**：K3s v1.36+、Docker 20.10+、Helm v3.20+
- **硬件配置**：整机 8核CPU、16G 内存、60G+ 存储空间

---

## 📖 快速部署指南

### 1. 仓库拉取

```bash
git clone git@github.com:xinzhemo/k3s-sre-devops-lab.git
cd k3s-sre-devops-lab
```

### 2. 全模块部署

```bash
# 部署多环境业务服务
kubectl apply -k project1/k8s/overlays/dev
kubectl apply -k project1/k8s/overlays/staging

# 部署集群拨测自愈组件
kubectl apply -f project2/k8s/daemonset.yaml
kubectl apply -f project2/k8s/service.yaml

# 部署网络策略与Ingress流量规则
kubectl apply -f project3/policies/deny-all.yaml
kubectl apply -f project3/policies/allow-demo-app.yaml
kubectl apply -f project3/ingress.yaml
```

### 3. 服务有效性验证

```bash
# 查看全集群业务Pod运行状态
kubectl get pods -n dev
kubectl get pods -n staging
kubectl get pods -n monitoring

# 验证Ingress域名流量接入
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
curl -H "Host: demo.staging.local" http://${NODE_IP}:30080/health
```
