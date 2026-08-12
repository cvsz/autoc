FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY app.py gui.py monitor_core.py realtime_monitor.py ./

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["autoc-web", "--host", "0.0.0.0", "--port", "8000"]
