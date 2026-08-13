FROM python:3.9-slim
WORKDIR /app
RUN pip install kubernetes prometheus-client
COPY probe-agent.py .
CMD ["python", "probe-agent.py"]
