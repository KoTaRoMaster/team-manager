FROM python:3.14 as migration-base
ENV PYTHONPATH=/workspace
WORKDIR /workspace

COPY ./req-migrate.txt .
RUN pip install --no-cache-dir -r req-migrate.txt

COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini ./alembic.ini


# -----------------------------
FROM python:3.14 as app-base

ENV PYTHONPATH=/workspace

WORKDIR /workspace

COPY ./req-app.txt ./req.txt
RUN pip install --no-cache-dir -r ./req.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
