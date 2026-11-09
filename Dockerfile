FROM python:3.14 AS builder

RUN apt-get update && apt-get -y upgrade && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry>=2.5,<3"
WORKDIR /build
COPY . ./

# Only the wheel is needed here; dependencies are resolved when the wheel is installed in the runtime stage
RUN poetry build -f wheel

FROM python:3.14-slim AS runtime

RUN apt-get update && apt-get -y upgrade && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder /build/dist/*.whl /app/

# Install the wheel without cache
RUN pip install --no-cache-dir /app/*.whl && rm /app/*.whl && chown app:app /app

USER app
ENTRYPOINT ["folio-permission-migration-cli"]
