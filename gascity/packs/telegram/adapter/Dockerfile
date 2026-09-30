FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bridge.py factory_router.py github_delivery.py weaver_client.py factory.py ./

CMD ["python3", "-u", "bridge.py"]
