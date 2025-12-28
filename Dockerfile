# Use a imagem oficial do Python na versão 3.11
FROM python:3.13-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos do projeto para o contêiner
COPY requirements.txt /app/requirements.txt
COPY . /app

# Instalar ferramentas de compilação e dependências do Cairo (se necessário)
# RUN apt-get update && apt-get install -y \
#     gcc \
#     libcairo2-dev \
#     libffi-dev \
#     build-essential \
#     pkg-config \
#     --no-install-recommends && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Atualize o pip
RUN pip install --upgrade pip

# Instale as dependências
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponha a porta onde o Flask será executado
EXPOSE 5000

# Comando para iniciar o Flask
CMD ["gunicorn", "-w", "1", "--bind", "unix:/apps/delivery/delivery.sock", "wsgi:app"]
