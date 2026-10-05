FROM python:3.14

# Переменная окружения, которая заставляет Python искать модули в текущей папке
ENV PYTHONPATH=/workspace

# Делаем корневую папку для проекта внутри Docker
WORKDIR /workspace

# Копируем зависимости из локальной папки app
COPY ./requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir -r ./app/requirements.txt

# Копируем ВСЮ локальную папку app в папку app внутри контейнера
COPY app ./app

# Запуск модуля в правильном формате (через точку, без .py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
