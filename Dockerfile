FROM python:3.12-slim

# Dependências do sistema + Xvfb
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala Playwright e dependências do sistema
RUN playwright install chromium
RUN playwright install-deps chromium

# Copia o projeto
COPY . .

# Cria pasta de output e logs
RUN mkdir -p /app/output /app/logs

# Permissão no entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["bash", "entrypoint.sh"]