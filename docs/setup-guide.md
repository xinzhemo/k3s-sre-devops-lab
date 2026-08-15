# K3s 集群环境搭建指南

## 硬件要求

- 2 台 Linux 主机（Ubuntu 20.04+ 或 CentOS 7+）
- 每台至少 2 核 4GB 内存
- 内网互通

## 1. 基础配置（所有节点执行）

```bash
# 关闭防火墙（实验环境）
sudo ufw disable

# 设置 hostname
sudo hostnamectl set-hostname k3s-master   # Master 节点
sudo hostnamectl set-hostname k3s-worker   # Worker 节点

# 配置 hosts
echo "192.168.1.10 k3s-master" | sudo tee -a /etc/hosts
echo "192.168.1.11 k3s-worker" | sudo tee -a /etc/hosts

# 安装 Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
sudo usermod -aG docker $USER
