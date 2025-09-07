FROM python:3-slim-trixie

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates ffmpeg

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# packages install
WORKDIR /app

ENV UV_SYSTEM_PYTHON=true \ 
    UV_COMPILE_BYTCODE=1 \
    UV_CAHE_DIR=/root/.cache/uv \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock run.py settings.toml /app/
COPY ./koq /app/koq

RUN uv export --frozen --no-dev --format requirements-txt > requirements.txt \ 
    && uv pip install -r requirements.txt

CMD ["uv", "run", "--no-dev", "run.py"]