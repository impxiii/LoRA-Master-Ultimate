FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install flask
EXPOSE 5000
# Теперь запускаем новый веб-скрипт
CMD ["python", "app.py"]# Берем официальный легкий образ Python
FROM python:3.10-slim

# Указываем рабочую папку внутри контейнера
WORKDIR /app

# Копируем твой скрипт и файлы в контейнер
COPY . .

# Устанавливаем Flask (библиотека для веб-сервера)
RUN pip install flask

# Открываем порт 5000 для сайта
EXPOSE 5000

# Команда для запуска нашего будущего веб-сервера
CMD ["python", "app.py"]
