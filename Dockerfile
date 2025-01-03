FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

CMD ["sh", "-c", "if [ ! -d 'migrations' ]; then flask db init; fi && flask db migrate -m 'Auto migration' && flask db upgrade && python create_admin.py && python app/main.py"]
