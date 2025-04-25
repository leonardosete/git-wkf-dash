# Etapa 1: Build do frontend com Vite
FROM node:20 AS frontend

WORKDIR /app

# Copiar arquivos de dependência
COPY package.json package-lock.json ./
RUN npm install

# Copiar os arquivos restantes
COPY . .

# Build do frontend
RUN npm run build

# Etapa 2: Backend com Streamlit
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl tzdata && \
    ln -snf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código backend
COPY . .

# Copiar build do frontend
COPY --from=frontend /app/dist ./frontend_dist

EXPOSE 8000

CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
