FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY prober/ ./prober/
ENV PYTHONUNBUFFERED=1
ENV AUTO_HEAL_ENABLED=false
WORKDIR /app/prober
CMD ["python", "main.py"]
