Project 1：基于 K3s GitOps 微服务持续交付平台
📌 项目介绍
针对传统交付模式存在的 多环境配置混乱、手动部署易错、版本发布风险高、无法灰度、资源无法自适应流量 等问题，模拟企业微服务研发交付与运维完整场景,基于轻量生产级 K3s 集群搭建一套 GitOps 全自动持续交付体系。
项目整合 Kustomize 多环境配置治理、GitHub Actions 持续构建、ArgoCD 自动部署、Argo Rollouts 金丝雀灰度发布、HPA 弹性伸缩，完整实现从代码提交、镜像构建、自动部署、灰度上线到弹性运维的全链路工程化能力。
🛠 技术栈
表格
分类	技术
业务服务	Python Flask
容器技术	Docker、K3s containerd
编排与配置	K3s、Kustomize
持续集成	GitHub Actions
持续交付	ArgoCD（GitOps 自动同步、配置自愈、资源修剪）
灰度发布	Argo Rollouts（金丝雀渐进式发布）
弹性运维	Kubernetes HPA 自动扩缩容
📁 项目目录结构
plaintext
```
project1/
├── app/                                   # 微服务业务源码与镜像构建
│   ├── app.py                             # 主服务，提供健康检查能力
│   ├── Dockerfile                         # 容器构建脚本
│   └── requirements.txt                   # Python依赖管理
├── k8s/                                   # Kustomize 业务资源（GitOps 核心配置）
│   ├── base/                              # 全环境通用基础配置
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── overlays/                          # 多环境差异化配置
│       ├── dev/                           # 开发环境（低配置、迭代环境）
│       └── staging/                       # 预发布环境（准生产、灰度验证）
├── manifests/                             # 组件安装与运维资源清单
│   ├── install.yaml                       # ArgoCD 安装文件
│   ├── argocd-application.yaml            # GitOps 同步规则
│   ├── argo-rollouts-install.yaml         # 灰度组件安装
│   ├── rollout.yaml                       # 金丝雀发布策略
│   ├── hpa.yaml                           # 弹性伸缩规则
│   └── load-deployment.yaml               # 压测负载
├── .github/workflows/                     # CI 自动构建流水线
├── screenshots/                           # 项目效果截图
├── local-ci.sh                            # 本地 CI 模拟脚本
└── README.md
```
✨ 核心项目能力
1. 标准化多环境配置治理
使用 Kustomize base + overlays 架构，实现配置复用 + 环境解耦。
统一基础部署模板，通过补丁区分开发、预发布环境的副本数、资源限制、环境变量，解决传统 YAML 冗余、多环境不一致、维护成本高的问题。
2. 全自动 CI 镜像构建
代码提交自动触发 GitHub Actions 流水线，完成代码打包、镜像构建、推送 DockerHub，同时生成 latest 和 commit‑sha 双版本标签，保障迭代版本可追溯。
3. GitOps 声明式自动交付
以 Git 为唯一可信源，ArgoCD 实时监听配置变更，30 秒内自动同步集群。
开启配置自愈与资源修剪，自动修复集群人为改动、清理冗余资源，保证集群状态与 Git 严格一致。
4. 生产级金丝雀灰度发布
基于 Argo Rollouts 替代原生滚动更新，支持 20% → 50% → 100% 流量分批放量。
支持发布暂停、手动晋升、异常回滚，小流量验证新版本，大幅降低生产发布风险。
5. 流量驱动弹性伸缩
配置 HPA 基于 CPU 使用率自动扩缩容，业务压力上涨自动扩容抗压，流量低谷自动缩容释放资源，实现服务稳定性与资源利用率平衡。
🚀 快速部署与使用
1. 部署多环境业务
bash
# 创建环境命名空间
kubectl create namespace dev
kubectl create namespace staging

# 部署开发环境
kubectl apply -k k8s/overlays/dev

# 部署预发布环境
kubectl apply -k k8s/overlays/staging
2. 服务健康校验
bash
kubectl port-forward svc/dev-demo-service 8080:80 -n dev
curl http://localhost:8080/health
3. 部署 GitOps 核心组件
bash
# 安装 ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f manifests/install.yaml

# 安装 Argo Rollouts
kubectl apply -f manifests/argo-rollouts-install.yaml
4. 开启自动同步流水线
bash
kubectl apply -f manifests/argocd-application.yaml
5. 灰度发布运维
bash
# 触发灰度更新
kubectl argo rollouts set image demo-app demo=<新镜像> -n staging

# 观察发布进度
kubectl argo rollouts get rollout demo-app -n staging -w
6. 弹性伸缩压测
bash
kubectl apply -f manifests/hpa.yaml
kubectl apply -f manifests/load-deployment.yaml
📷 项目效果展示
集群与环境状态

服务与配置验证

CI/CD 自动化效果

金丝雀灰度发布

HPA 弹性伸缩效果

🔧 项目难点与解决方案
K3s 无法识别 Docker 镜像：通过 docker save + ctr import 手动导入镜像，适配 K3s containerd 运行时。
Python 容器日志不输出：开启无缓冲启动参数，解决日志缓冲区导致的日志缺失问题。
ArgoCD 拉取 GitHub 超时：将 HTTPS 协议替换为 SSH 部署密钥，提升同步稳定性。
金丝雀发布暂停卡住：熟悉 Rollouts 发布生命周期，手动 promote 推进灰度流程。
CI 镜像推送失败：配置 DockerHub 密钥认证，实现流水线自动鉴权推送。

📎 参考文档
ArgoCD 官方文档
Argo Rollouts 官方文档
Kustomize 官方文档
K3s 官方文档
