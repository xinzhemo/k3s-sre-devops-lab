# 项目二：K8s 集群服务网络质量拨测系统

## 项目概述
通过 DaemonSet 部署的 Python Agent，通过 K8s API 自动发现 Service，做 TCP 探测，暴露 Prometheus 指标。

## 技术栈
Python + kubernetes-client + prometheus-client + DaemonSet + Prometheus

## 核心能力
1. 自动服务发现（Watch Service/Endpoints，无需手动配置）
2. TCP 连通性探测（成功率 + 延迟）
3. Prometheus 指标暴露（probe_success / probe_duration / probe_total）
4. 告警规则（企业微信推送）

## 与 Blackbox Exporter 区别
| 对比项 | Blackbox | 本方案 |
|--------|----------|--------|
| 配置 | 手动 | 自动发现 |
| 扩缩容 | 手动更新 | 自动感知 |

## 快速开始
```bash
kubectl apply -f probe-daemonset.yaml
kubectl get pods -n monitoring | grep probe
kubectl port-forward -n monitoring svc/probe-agent 19100:19100
curl http://localhost:19100/metrics | grep probe_
