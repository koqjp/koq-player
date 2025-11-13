FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# The installer requires curl (and certificates) to download the release archive
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends curl zip unzip ca-certificates ffmpeg \
    && curl -fsSL https://deno.land/x/install/install.sh | sh \
    && apt-get -qq remove curl zip unzip \
    && apt-get -qq remove --purge -y curl zip unzip \
    && apt-get -qq -y autoremove \
    && apt-get -qq clean \
    && echo 'export DENO_INSTALL="/root/.deno"' >> ~/.bash_profile \
    && echo 'export PATH="$DENO_INSTALL/bin:$PATH"' >> ~/.bash_profile

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