FROM python:3.13-slim-bookworm AS prod

WORKDIR /app/src

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y gcc


RUN pip install poetry

RUN poetry install --no-root

RUN poetry config virtualenvs.create false

RUN apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Копируем приложение
COPY . .

CMD ["python", "-m", "discordbottest"]