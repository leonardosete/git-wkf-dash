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
    curl && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código backend
COPY . .

# Copiar build do frontend para uso com streamlit.components, se necessário
COPY --from=frontend /app/dist ./frontend_dist

# Expor porta do Streamlit
EXPOSE 8000

# Comando para rodar a app
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
