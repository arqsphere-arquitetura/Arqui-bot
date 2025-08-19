# Usa imagem oficial Python
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# Define variáveis de ambiente
ENV PORT=8080

# Comando de arranque
CMD ["python", "main.py"]
