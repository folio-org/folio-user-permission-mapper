FROM python:3.12 AS builder

RUN pip install poetry
WORKDIR /build
COPY . ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
RUN poetry build -f wheel

FROM python:3.12-slim AS runtime

WORKDIR /app
COPY --from=builder /build/dist/*.whl /app/

# Install the wheel without cache
RUN pip install --no-cache-dir /app/*.whl && rm /app/*.whl
CMD ["folio-permission-migration-cli"]
