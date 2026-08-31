# SLI / SLO 定义文档

## 服务名称
demo-app（示例微服务）

## SLI（Service Level Indicator）
| 指标 | 定义 | 测量方式 |
|------|------|----------|
| 请求成功率 | HTTP 200 响应数 / 总请求数 | Prometheus 查询：`sum(rate(flask_http_request_total{status!~"5.."}[5m])) / sum(rate(flask_http_request_total[5m]))` |
| 请求延迟（P95） | 95% 请求的响应时间 | Prometheus 查询：`histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket[5m])) by (le))` |

## SLO（Service Level Objective）
| 指标 | 目标值 | 衡量周期 |
|------|--------|----------|
| 请求成功率 | ≥ 99.5% | 30 天滚动窗口 |
| P95 延迟 | ≤ 100ms | 30 天滚动窗口 |

## 错误预算
- **计算公式**：1 - SLO = 0.5% 错误预算
- **消耗过快阈值**：5 分钟内错误率 > 0.5% 触发告警
