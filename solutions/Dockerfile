FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /uvx /bin/
#COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-cache

COPY app/ .

USER 10001:10001

EXPOSE 8000

ENTRYPOINT ["uv", "run", "gunicorn", "--access-logfile", "-", "app:app"]
CMD [ "--bind", "0.0.0.0:8000", "--workers", "2" ]
