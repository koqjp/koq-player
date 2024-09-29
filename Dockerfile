FROM --platform=linux/amd64 python:3-slim AS builder

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    PYSETUP_PATH="/opt/pysetup"

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && \
    apt-get install --no-install-recommends -y curl ffmpeg && \
    apt-get clean

RUN curl -sSL https://install.python-poetry.org/ | python -

# packages install
RUN mkdir /app
WORKDIR /app
COPY ./pyproject.toml /app/pyproject.toml
RUN poetry install --only main

# Python script
COPY ./koq /app/koq
COPY ./run.py /app/run.py
COPY settings.toml /app/settings.toml

CMD ["poetry", "run", "python", "run.py"]