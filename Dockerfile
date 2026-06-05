FROM python:3.12-slim
RUN apt-get update && apt-get install -y python3-tk && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install poetry==2.4.1
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
COPY . .
RUN poetry install --only main --no-interaction --no-ansi -vvv
CMD ["python3", "app/ui/main.py"]