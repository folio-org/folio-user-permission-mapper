FROM python:3.14 AS builder

RUN apt-get update && apt-get -y upgrade && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
WORKDIR /build
COPY . ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
RUN poetry build -f wheel

FROM python:3.14-slim AS runtime

RUN apt-get update && apt-get -y upgrade && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /build/dist/*.whl /app/

# Install the wheel without cache
RUN pip install --no-cache-dir /app/*.whl && rm /app/*.whl
ENTRYPOINT ["folio-permission-migration-cli"]
