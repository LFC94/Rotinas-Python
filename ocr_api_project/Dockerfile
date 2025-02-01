# Use uma imagem oficial do Python como base
FROM python:3.9-slim

# Instale o Tesseract-OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o Pipfile e o Pipfile.lock para o container
COPY Pipfile Pipfile.lock /app/

# Instale as dependências do Python usando Pipenv
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copie o código-fonte da API para o container
COPY . /app

# Exponha a porta que o Flask usará
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["pipenv", "run", "python", "app.py"]
