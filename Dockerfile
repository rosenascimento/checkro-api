FROM python:3.11

# Cria pasta de trabalho
WORKDIR /app

# Copia tudo (inclusive Dockerfile, .env etc)
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta
EXPOSE 8000

# Comando para rodar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
