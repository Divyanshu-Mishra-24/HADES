FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data && chmod 755 /app/data

RUN useradd -m -u 1000 honeypot && chown -R honeypot:honeypot /app
USER honeypot

EXPOSE 2222
EXPOSE 5000

CMD ["python", "start.py"]
