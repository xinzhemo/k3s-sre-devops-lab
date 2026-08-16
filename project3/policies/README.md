# 项目三：NetworkPolicy 网络隔离与故障演练

## 项目概述

在 K3s 集群上通过 NetworkPolicy 实现零信任网络隔离，并通过故障演练验证策略有效性。

> **注意**：K3s 默认 CNI（Flannel）不支持 NetworkPolicy，需切换至 Calico。

## 核心能力

### 1. 策略设计

| 策略 | 作用 |
| :--- | :--- |
| `deny-all` | 默认拒绝所有入站流量 |
| `allow-demo-app` | 白名单放行特定应用访问 |

### 2. 故障演练场景

| 场景 | 操作 | 观测方式 |
| :--- | :--- | :--- |
| 策略误配置 | 写错 selector | 项目二拨测告警触发 |
| 恢复放行 | 修正策略 | 告警恢复 |

## 快速开始

```bash
# 应用策略
kubectl apply -f policies/deny-all.yaml -n dev
kubectl apply -f policies/allow-demo-app.yaml -n dev

# 查看策略
kubectl get networkpolicy -n dev

# 测试（预期失败）
kubectl run test --image=busybox --rm -it -n dev -- wget -qO- --timeout=3 http://myapp:5000/
