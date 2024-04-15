FROM python:slim

RUN pip install --upgrade pip && pip install pdm
RUN apt update
RUN apt install -y uvicorn

WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
COPY pdm.lock /app/pdm.lock
COPY ./src/freeaskinternet /app/freeaskinternet
RUN pdm install
EXPOSE 8000

ENTRYPOINT ["pdm", "run", "python", "-m", "uvicorn", "freeaskinternet.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
