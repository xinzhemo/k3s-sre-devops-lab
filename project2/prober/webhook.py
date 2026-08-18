from flask import Flask, request, jsonify
import subprocess
import threading
import logging
import json

logger = logging.getLogger(__name__)
app = Flask(__name__)

# 自愈功能开关（默认关闭，避免误操作）
AUTO_HEAL_ENABLED = False

@app.route('/webhook', methods=['POST'])
def handle_alert():
    """
    接收 Alertmanager 告警，触发自动处置逻辑
    """
    try:
        data = request.get_json()
        alerts = data.get('alerts', [])
        
        for alert in alerts:
            status = alert.get('status')
            labels = alert.get('labels', {})
            
            if status == 'firing' and labels.get('alertname') == 'ServiceDown':
                service = labels.get('target_service', 'unknown')
                logger.info(f"Alert triggered for service: {service}")
                
                if AUTO_HEAL_ENABLED:
                    # 调用自动隔离逻辑
                    isolate_service(service)
                else:
                    logger.info(f"Auto-heal disabled, manual intervention required for {service}")
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def isolate_service(service):
    """自动隔离故障服务（通过 NetworkPolicy 或 标签）"""
    try:
        namespace = service.split('/')[0] if '/' in service else 'default'
        logger.info(f"Attempting to isolate service: {service} in namespace: {namespace}")
        
        # 方案1：给 Pod 添加隔离标签（需要配合 NetworkPolicy）
        cmd = f"kubectl label pods -n {namespace} -l app=demo isolated=true --overwrite"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        logger.info(f"Isolation result: {result.stdout}")
        
        # 方案2：直接删除 Pod（风险更高，慎用）
        # 这里只做演示，不实际执行
        logger.info("Isolation action completed (simulated)")
    except Exception as e:
        logger.error(f"Isolation failed: {e}")

def start_webhook(port):
    """启动 Webhook 服务"""
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
