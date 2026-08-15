# 版本升级与回滚测试记录

## 测试环境
- K3s 一主一从集群
- 命名空间：dev
- 应用：myapp (Flask)

## 测试场景1：正常升级
| 步骤 | 操作 | 预期结果 | 实际结果 |
| :--- | :--- | :--- | :--- |
| 1 | 构建 v2 镜像并推送 | 镜像推送成功 | ✅ 成功 |
| 2 | `kubectl set image deployment/myapp myapp=demo-app:v2 -n dev` | 触发滚动更新 | ✅ 触发 |
| 3 | `kubectl rollout status deployment/myapp -n dev` | 新 Pod 全部 Running | ✅ 成功 |
| 4 | `curl /` 验证 | 返回 v2 版本号 | ✅ 成功 |

## 测试场景2：回滚到上一版本
| 步骤 | 操作 | 预期结果 | 实际结果 |
| :--- | :--- | :--- | :--- |
| 1 | `kubectl rollout history deployment/myapp -n dev` | 看到历史版本列表 | ✅ 显示 revision 1, 2 |
| 2 | `kubectl rollout undo deployment/myapp -n dev` | 回滚到上一版本 | ✅ 成功 |
| 3 | `kubectl rollout status deployment/myapp -n dev` | Pod 全部 Running | ✅ 成功 |
| 4 | `curl /` 验证 | 返回 v1 版本号 | ✅ 成功 |

## 测试场景3：回滚到指定版本
| 步骤 | 操作 | 预期结果 | 实际结果 |
| :--- | :--- | :--- | :--- |
| 1 | `kubectl rollout undo deployment/myapp -n dev --to-revision=1` | 回滚到 revision 1 | ✅ 成功 |

## 关键命令速查
```bash
# 查看部署状态
kubectl rollout status deployment/myapp -n dev

# 查看历史版本
kubectl rollout history deployment/myapp -n dev

# 回滚到上一版本
kubectl rollout undo deployment/myapp -n dev

# 回滚到指定版本
kubectl rollout undo deployment/myapp -n dev --to-revision=2

# 查看 Pod 状态
kubectl get pods -n dev

# 查看 Pod 日志
kubectl logs -f deployment/myapp -n dev
