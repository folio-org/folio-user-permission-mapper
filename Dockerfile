FROM python:3.12 AS builder

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install "poetry==1.8.5" \
    && python -m pip install "packaging>=24.2" "pkginfo>=1.12"

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
ENTRYPOINT ["folio-permission-migration-cli"]
